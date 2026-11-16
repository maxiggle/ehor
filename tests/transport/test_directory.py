from collections.abc import Callable
from pathlib import Path

from ehor.identity import KeyHandle
from ehor.identity.software import SoftwareSigner
from ehor.log.entry import Kind
from ehor.log.roster import Member, Roster, RosterDevice, Trust
from ehor.log.verify import EntryVerifier
from ehor.store.ingest import Ingestor
from ehor.store.local_log import LocalLog
from ehor.store.sqlite import SqliteStore
from ehor.transport.directory import DirectoryExchange
from security_key_emulator import SoftwareAuthenticator


def _device(
    path: Path, folder: Path, signer: SoftwareSigner, handle: KeyHandle, team: bytes
) -> tuple[LocalLog, SqliteStore, DirectoryExchange]:
    store = SqliteStore(path)
    verifier = EntryVerifier(team)
    local_log = LocalLog(store, signer, handle, team, verifier)
    exchange = DirectoryExchange(folder, store, Ingestor(store, verifier), local_log.author)
    return local_log, store, exchange


def test_two_devices_exchange_through_a_folder(
    tmp_path: Path,
    signer: SoftwareSigner,
    handle: KeyHandle,
    other_handle: KeyHandle,
    team: bytes,
    message: Callable[[str], bytes],
) -> None:
    folder = tmp_path / "shared"
    log_a, store_a, sync_a = _device(tmp_path / "a.db", folder, signer, handle, team)
    log_b, store_b, sync_b = _device(tmp_path / "b.db", folder, signer, other_handle, team)
    first = log_a.append("#backend", Kind.MESSAGE, message("one"))
    second = log_a.append("#backend", Kind.MESSAGE, message("two"))
    reply = log_b.append("#backend", Kind.MESSAGE, message("three"))

    assert sync_a.sync() == 0
    assert sync_b.sync() == 2
    assert sync_a.sync() == 1
    assert store_b.log(log_a.author) == [first, second]
    assert store_a.log(log_b.author) == [reply]
    assert sync_a.sync() == 0
    assert sync_b.sync() == 0
    store_a.close()
    store_b.close()


def test_export_is_idempotent(
    tmp_path: Path,
    signer: SoftwareSigner,
    handle: KeyHandle,
    team: bytes,
    message: Callable[[str], bytes],
) -> None:
    folder = tmp_path / "shared"
    local_log, store, exchange = _device(tmp_path / "a.db", folder, signer, handle, team)
    local_log.append("#backend", Kind.MESSAGE, message("one"))
    assert exchange.export() == 1
    assert exchange.export() == 0
    assert not list((tmp_path / "shared").rglob("*.tmp"))
    store.close()


def test_tampered_files_are_not_stored(
    tmp_path: Path,
    signer: SoftwareSigner,
    handle: KeyHandle,
    other_handle: KeyHandle,
    team: bytes,
    message: Callable[[str], bytes],
) -> None:
    folder = tmp_path / "shared"
    log_a, store_a, sync_a = _device(tmp_path / "a.db", folder, signer, handle, team)
    _, store_b, sync_b = _device(tmp_path / "b.db", folder, signer, other_handle, team)
    log_a.append("#backend", Kind.MESSAGE, message("one"))
    sync_a.export()
    (path,) = folder.rglob("*.entry")
    raw = bytearray(path.read_bytes())
    raw[-1] ^= 0x01
    path.write_bytes(bytes(raw))
    assert sync_b.sync() == 0
    assert store_b.log(log_a.author) == []
    store_a.close()
    store_b.close()


def test_missing_folder_is_not_an_error(
    tmp_path: Path, signer: SoftwareSigner, handle: KeyHandle, team: bytes
) -> None:
    _, store, exchange = _device(tmp_path / "a.db", tmp_path / "missing", signer, handle, team)
    assert exchange.import_new() == 0
    store.close()


def test_exports_the_logs_of_keys_that_sign_here(
    tmp_path: Path,
    signer: SoftwareSigner,
    handle: KeyHandle,
    other_handle: KeyHandle,
    team: bytes,
) -> None:
    folder = tmp_path / "shared"
    key = SoftwareAuthenticator()
    store_a = SqliteStore(tmp_path / "a.db")
    verifier = EntryVerifier(team)
    log_a = LocalLog(store_a, signer, handle, team, verifier)
    sync_a = DirectoryExchange(
        folder,
        store_a,
        Ingestor(store_a, verifier),
        log_a.author,
        signed_here=lambda: [key.public_key],
    )
    _, store_b, sync_b = _device(tmp_path / "b.db", folder, signer, other_handle, team)
    device = RosterDevice(key.public_key, Trust.SECURITY_KEY, "yubikey")
    roster = Roster(1, None, "Acme", ("gef",), (Member("gef", (), ("*",), (device,)),))
    draft = log_a.draft("_team", Kind.ROSTER, roster.encode(), author=key.public_key)
    entry = log_a.commit(draft.with_assertion(key.sign(draft.signing_input)))

    assert sync_a.export() == 1
    assert sync_a.import_new() == 0
    assert sync_b.sync() == 1
    assert store_b.log(key.public_key) == [entry]
    store_a.close()
    store_b.close()


def test_entries_deferred_by_the_parking_cap_are_imported_later(
    tmp_path: Path,
    signer: SoftwareSigner,
    handle: KeyHandle,
    other_handle: KeyHandle,
    team: bytes,
    message: Callable[[str], bytes],
) -> None:
    folder = tmp_path / "shared"
    log_a, store_a, sync_a = _device(tmp_path / "a.db", folder, signer, handle, team)
    entries = [log_a.append("#backend", Kind.MESSAGE, message(text)) for text in "abc"]
    sync_a.export()
    first = next((folder / log_a.author.hex()).glob("0000000001-*"))
    held_back = first.read_bytes()
    first.unlink()

    store_b = SqliteStore(tmp_path / "b.db")
    verifier = EntryVerifier(team)
    ingestor = Ingestor(store_b, verifier, max_parked_per_author=1)
    sync_b = DirectoryExchange(folder, store_b, ingestor, signer.public_key(other_handle))
    assert sync_b.import_new() == 0
    assert store_b.all_parked() == [entries[1]]

    first.write_bytes(held_back)
    assert sync_b.import_new() == 3
    assert store_b.log(log_a.author) == entries
    store_a.close()
    store_b.close()
