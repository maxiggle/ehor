from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from ehor.identity import KeyHandle
from ehor.identity.software import SoftwareSigner
from ehor.log.authorize import Decision
from ehor.log.entry import Entry, EntryContent, Kind
from ehor.log.roster import Member, Roster, RosterDevice, Trust
from ehor.log.verify import EntryVerifier
from ehor.store.ingest import Ingestor, Outcome
from ehor.store.local_log import LocalLog, NotAuthorizedError
from ehor.store.sqlite import SqliteStore


class FakeAuthorizer:
    """Allows listed authors; storing an entry from `granter` admits `grantee`."""

    def __init__(self) -> None:
        self.allowed: set[bytes] = set()
        self.denied: set[bytes] = set()
        self.grants: dict[bytes, bytes] = {}
        self.stored_ids: list[bytes] = []

    def authorize(self, entry: Entry) -> Decision:
        if entry.author in self.denied:
            return Decision.deny("denied")
        if entry.author in self.allowed:
            return Decision.allow()
        return Decision.wait("not yet")

    def accepted(self, entry: Entry) -> bool:
        self.stored_ids.append(entry.id)
        grantee = self.grants.get(entry.author)
        if grantee is None or grantee in self.allowed:
            return False
        self.allowed.add(grantee)
        return True


@pytest.fixture
def store(tmp_db: Path) -> Iterator[SqliteStore]:
    with SqliteStore(tmp_db) as store:
        yield store


@pytest.fixture
def authorizer() -> FakeAuthorizer:
    return FakeAuthorizer()


@pytest.fixture
def ingestor(store: SqliteStore, team: bytes, authorizer: FakeAuthorizer) -> Ingestor:
    return Ingestor(store, EntryVerifier(team), authorizer)


def _chain(
    make: Callable[..., EntryContent], signer: SoftwareSigner, key: KeyHandle
) -> list[Entry]:
    author = signer.public_key(key)
    entries: list[Entry] = []
    for seq in range(1, 4):
        prev = entries[-1].id if entries else None
        entries.append(make(author=author, seq=seq, prev=prev, ts=seq).sign(signer, key))
    return entries


def test_allowed_entries_are_stored(
    ingestor: Ingestor, authorizer: FakeAuthorizer, make_entry: Callable[..., Entry]
) -> None:
    entry = make_entry()
    authorizer.allowed.add(entry.author)
    assert ingestor.receive(entry.encode()).outcome is Outcome.STORED
    assert authorizer.stored_ids == [entry.id]


def test_denied_entries_are_rejected(
    ingestor: Ingestor,
    store: SqliteStore,
    authorizer: FakeAuthorizer,
    make_entry: Callable[..., Entry],
) -> None:
    entry = make_entry()
    authorizer.denied.add(entry.author)
    receipt = ingestor.receive(entry.encode())
    assert (receipt.outcome, receipt.reason) == (Outcome.REJECTED, "denied")
    assert not store.contains(entry.id)
    assert store.all_parked() == []


def test_waiting_entries_are_released_when_authorization_changes(
    ingestor: Ingestor,
    store: SqliteStore,
    authorizer: FakeAuthorizer,
    make_content: Callable[..., EntryContent],
    signer: SoftwareSigner,
    handle: KeyHandle,
    other_handle: KeyHandle,
) -> None:
    admin = _chain(make_content, signer, handle)
    newcomer = _chain(make_content, signer, other_handle)
    authorizer.allowed.add(admin[0].author)
    authorizer.grants[admin[0].author] = newcomer[0].author
    for entry in newcomer:
        receipt = ingestor.receive(entry.encode())
        assert receipt.outcome is Outcome.PARKED
    assert len(store.all_parked()) == 3
    receipt = ingestor.receive(admin[0].encode())
    assert receipt.outcome is Outcome.STORED
    assert set(receipt.released) == {entry.id for entry in newcomer}
    assert store.log(newcomer[0].author) == newcomer
    assert store.all_parked() == []


def test_local_log_refuses_unauthorized_writes(
    store: SqliteStore,
    authorizer: FakeAuthorizer,
    signer: SoftwareSigner,
    handle: KeyHandle,
    team: bytes,
    message: Callable[[str], bytes],
) -> None:
    local_log = LocalLog(store, signer, handle, team, EntryVerifier(team), authorizer=authorizer)
    with pytest.raises(NotAuthorizedError, match="not yet"):
        local_log.append("#backend", Kind.MESSAGE, message("hi"))
    assert store.head(local_log.author) is None
    authorizer.allowed.add(local_log.author)
    entry = local_log.append("#backend", Kind.MESSAGE, message("hi"))
    assert authorizer.stored_ids == [entry.id]


def _stranger_entries(
    make: Callable[..., EntryContent], signer: SoftwareSigner, key: KeyHandle, count: int
) -> list[Entry]:
    author = signer.public_key(key)
    return [
        make(author=author, seq=seq, prev=bytes(32), ts=seq).sign(signer, key)
        for seq in range(2, count + 2)
    ]


def test_a_stranger_cannot_park_more_than_the_per_author_cap(
    store: SqliteStore,
    team: bytes,
    authorizer: FakeAuthorizer,
    make_content: Callable[..., EntryContent],
    signer: SoftwareSigner,
    other_handle: KeyHandle,
) -> None:
    ingestor = Ingestor(store, EntryVerifier(team), authorizer, max_parked_per_author=2)
    flood = _stranger_entries(make_content, signer, other_handle, 5)
    outcomes = [ingestor.receive(entry.encode()).outcome for entry in flood]
    assert outcomes == [Outcome.PARKED] * 2 + [Outcome.DEFERRED] * 3
    assert store.all_parked() == flood[:2]
    assert ingestor.receive(flood[0].encode()).outcome is Outcome.PARKED


def test_strangers_cannot_park_more_than_the_total_cap(
    store: SqliteStore,
    team: bytes,
    authorizer: FakeAuthorizer,
    make_content: Callable[..., EntryContent],
    signer: SoftwareSigner,
    other_handle: KeyHandle,
    third_handle: KeyHandle,
) -> None:
    ingestor = Ingestor(store, EntryVerifier(team), authorizer, max_parked=3)
    first = _stranger_entries(make_content, signer, other_handle, 2)
    second = _stranger_entries(make_content, signer, third_handle, 2)
    outcomes = [ingestor.receive(entry.encode()).outcome for entry in [*first, *second]]
    assert outcomes == [Outcome.PARKED] * 3 + [Outcome.DEFERRED]
    assert store.parked_count() == 3


def test_a_full_park_does_not_turn_away_an_authorized_author(
    store: SqliteStore,
    team: bytes,
    authorizer: FakeAuthorizer,
    make_content: Callable[..., EntryContent],
    signer: SoftwareSigner,
    handle: KeyHandle,
    other_handle: KeyHandle,
) -> None:
    ingestor = Ingestor(store, EntryVerifier(team), authorizer, max_parked=2)
    for entry in _stranger_entries(make_content, signer, other_handle, 3):
        ingestor.receive(entry.encode())
    member = _chain(make_content, signer, handle)
    authorizer.allowed.add(member[0].author)
    assert ingestor.receive(member[1].encode()).outcome is Outcome.PARKED
    receipt = ingestor.receive(member[0].encode())
    assert (receipt.outcome, receipt.released) == (Outcome.STORED, (member[1].id,))


def test_a_deferred_entry_is_stored_once_it_can_be_placed(
    store: SqliteStore,
    team: bytes,
    authorizer: FakeAuthorizer,
    make_content: Callable[..., EntryContent],
    signer: SoftwareSigner,
    handle: KeyHandle,
) -> None:
    ingestor = Ingestor(store, EntryVerifier(team), authorizer, max_parked_per_author=1)
    chain = _chain(make_content, signer, handle)
    assert ingestor.receive(chain[0].encode()).outcome is Outcome.PARKED
    assert ingestor.receive(chain[1].encode()).outcome is Outcome.DEFERRED
    authorizer.allowed.add(chain[0].author)
    assert ingestor.receive(chain[0].encode()).outcome is Outcome.STORED
    assert ingestor.receive(chain[1].encode()).outcome is Outcome.STORED
    assert store.all_parked() == []


def test_authorized_rosters_are_parked_past_every_cap(
    store: SqliteStore,
    team: bytes,
    authorizer: FakeAuthorizer,
    make_content: Callable[..., EntryContent],
    signer: SoftwareSigner,
    handle: KeyHandle,
) -> None:
    ingestor = Ingestor(
        store, EntryVerifier(team), authorizer, max_parked=0, max_parked_per_author=0
    )
    admin = signer.public_key(handle)
    authorizer.allowed.add(admin)
    device = RosterDevice(admin, Trust.SOFTWARE, "laptop")
    body = Roster(1, None, "Acme", ("gef",), (Member("gef", (), ("*",), (device,)),)).encode()
    roster = make_content(seq=2, prev=bytes(32), channel="_team", kind=Kind.ROSTER, body=body)
    message = make_content(seq=3, prev=bytes(32))
    assert ingestor.receive(roster.sign(signer, handle).encode()).outcome is Outcome.PARKED
    assert ingestor.receive(message.sign(signer, handle).encode()).outcome is Outcome.DEFERRED
