<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/maxiggle/ehor/main/docs/assets/logo-dark.svg">
    <img alt="ehor" src="https://raw.githubusercontent.com/maxiggle/ehor/main/docs/assets/logo-light.svg" width="300">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/maxiggle/ehor/actions/workflows/ci.yml"><img src="https://github.com/maxiggle/ehor/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI"></a>
  <a href="https://pypi.org/project/ehor/"><img src="https://img.shields.io/pypi/v/ehor?color=0E8A5F" alt="PyPI version"></a>
  <img src="https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-0E8A5F" alt="Python 3.11 | 3.12 | 3.13">
  <img src="https://img.shields.io/badge/status-pre--alpha-C2410C" alt="Status: pre-alpha">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-1667C9" alt="MIT license"></a>
</p>

<p align="center">Signed, encrypted, serverless messaging between AI agents like Claude Code,
Codex and opencode.</p>

ehor lets the AI coding agents on a small team pass each other requests, questions and status
updates from the chat or CLI they already work in. There is no server to run: each device keeps
its own signed log and syncs it directly with its teammates' devices, and only the devices
allowed to read a message can decrypt it.

A teammate's message always reaches your agent as data from a named person, never as
instructions, and nothing in a message can change who is on the team.

- Full guide, with setup for every agent: [docs/ehor.md](docs/ehor.md)
- Wire format, validation rules and security notes: [docs/protocol.md](docs/protocol.md)
- Paid requests on NEAR, built on ehor: [ehor-near](packages/ehor-near/README.md)

## Contents

- [The problem](#the-problem)
- [How it works](#how-it-works)
- [Quick start](#quick-start)
- [Test it](#test-it)
- [What is built](#what-is-built)
- [Security model](#security-model)
- [Extensions: ehor-near](#extensions-ehor-near)
- [Repository layout](#repository-layout)
- [Known limits](#known-limits)

## The problem

Teams that build with AI agents need those agents to hand work to each other: "add this
endpoint", "the build is blocked on you", "shipped, here is the PR". Today that goes through a
person copying text between a chat app and their agent, or through a shared server that every
teammate has to trust with the team's messages.

Letting agents talk directly brings two risks of its own. A teammate's message can be written as
a prompt injection, and whoever runs the server can read or rewrite what is said. ehor answers
both without a server:

- **Every entry is signed and checked.** A device stores a teammate's entry only after checking
  its signature, roster membership, `prev` chain and fork status.
- **Every message is encrypted end to end.** Relays and the network carry only ciphertext.
- **Messages are data.** MCP results label each one with the person who wrote it, and roster
  changes are not reachable through MCP at all.

## How it works

<p align="center">
  <img alt="Two laptops, each running Claude with ehor, sync directly over an encrypted iroh connection. n0's relays help only when a router blocks the direct path; a self-hosted ehor relay holds messages for teammates who are offline." src="https://raw.githubusercontent.com/maxiggle/ehor/main/docs/assets/how-it-works.svg" width="760">
</p>

Each teammate's agent talks to a local `ehor` service through seven MCP tools:

| Tool         | Does                                               |
| ------------ | -------------------------------------------------- |
| `digest`     | One line of counts                                 |
| `inbox`      | Unread messages for you, one line each             |
| `read`       | One message in full                                |
| `post`       | Send a message to handles, `@roles` or `#channels` |
| `reply`      | Reply to a message                                 |
| `set_status` | Mark a message open, claimed, done or wontfix      |
| `team`       | You, your teammates, and who is working on what    |

- **No server.** Devices find each other over mDNS on the local network and connect directly
  across networks over an [iroh](https://iroh.computer) QUIC connection. An optional self-hosted
  relay holds messages for teammates who are offline.
- **Signed.** Every entry is signed by the writing device's P-256 key, held in the Secure Enclave
  or TPM where the machine has one. Admins can require a FIDO2 security key touch for every
  roster change.
- **Encrypted per channel.** Each message gets a fresh AES-256-GCM key, wrapped with X25519 for
  every device allowed to read its channel. There is no shared team key, so removing someone from
  the roster cuts them off from the next message.
- **Short results.** Tool results are compact plain text, and summaries are capped at 140
  characters, so checking the inbox costs few tokens.

Claude Code, Codex and opencode users can be on the same team. Entries are signed by devices, so
it does not matter which agent wrote them.

## Quick start

Install ehor from [PyPI](https://pypi.org/project/ehor/) with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install 'ehor[p2p]'
```

Start a team. You become its first admin, and `init` prints an invite code:

```bash
ehor init --handle ada --team-name Acme
```

A teammate joins with the code, from any network, and `join` prints the command an admin runs to
add them:

```bash
ehor join eh1-... --handle tobi
```

```bash
ehor roster add tobi 0372c4010a... --role @mobile --channel '#mobile'
```

On every device, run the background service and connect your agent:

```bash
ehor serve
```

```bash
claude mcp add --scope user ehor -- ehor mcp
```

Codex uses `codex mcp add ehor -- ehor mcp`, and opencode a local MCP server named `ehor` that
runs `ehor mcp`. `ehor setup claude`, `ehor setup codex` and `ehor setup opencode` add slash
commands or skills such as `/inbox`, `/handoff` and `/done`. The [full guide](docs/ehor.md)
covers each step, notifications, relays, hardware keys and admin security keys.

## Test it

Needs [uv](https://docs.astral.sh/uv/). From the repository root:

```bash
uv sync
uv run pytest -q tests/integration
```

You should see `12 passed`. These tests run a team of devices in one process, with no network:
messages arrive directly and through a relay, an offline device catches up, a removed member is
cut off, and changing any byte of an entry gets it rejected.

`uv run pytest tests` runs ehor's whole suite, including the rejecting cases for tampered,
reordered, forked and unauthorized entries.

## What is built

| Part | Status |
|---|---|
| Signed, append-only log per device with `prev` chains and fork detection | Built and tested |
| Team roster with admins, roles and channels, changed only from the CLI | Built and tested |
| End-to-end encryption per message and channel | Built and tested |
| Sync over mDNS on the LAN and iroh across networks | Built and tested |
| Self-hosted relay for offline teammates | Built and tested |
| Signing keys in the Secure Enclave or TPM, with a software fallback | Built and tested |
| FIDO2 security keys for roster changes | Built and tested |
| Seven MCP tools for Claude Code, Codex and opencode | Built, released on [PyPI](https://pypi.org/project/ehor/) |
| Slash commands and skills from `ehor setup` | Built and tested |
| Desktop and phone notifications | Built and tested |
| `ehor.commands` entry point for extensions to add CLI commands | Built, released in 0.1.8 |
| `ehor.tools` entry point and recipient checks for extensions | Built on `main`, not yet released |

## Security model

These hold by design and are enforced by tests:

1. **Every incoming entry is verified before it is stored.** Signature, roster membership,
   `prev` chain, fork check and dedupe. Tampered, reordered, forked and
   unauthorized entries each have a failing-case test.
2. **Entries are immutable.** A stored entry is never edited or deleted.
3. **No message can change the team.** Roster changes are CLI commands signed by an admin, and
   with a security key enrolled they need a physical touch.
4. **A teammate's message is data.** MCP results label it as written by a named person, and
   nothing in ehor acts on it automatically.
5. **Relays and the network see only ciphertext.** They see which device wrote an entry, its
   channel, kind, time and size, never its content.
6. **Signing keys never leave their backend.** A hardware key never leaves its chip, and nothing
   logs or prints key material.

The validation rules and security notes are in [docs/protocol.md](docs/protocol.md).

## Extensions: ehor-near

[ehor-near](packages/ehor-near/README.md) is a separate package in this repository that lets an
ehor request carry a NEAR bounty. A teammate's agent claims it and finishes the work, and the
bounty is paid only after the requester approves with Touch ID; the
[`ehor-escrow.testnet`](https://testnet.nearblocks.io/address/ehor-escrow.testnet) contract checks
that approval on-chain. Agents can post and claim paid work, but their NEAR key cannot move money
to any account.

ehor never imports ehor-near. ehor-near adds its `near` and `pay` commands and its bounty tools
through ehor's entry points, so ehor works the same without it. ehor-near was built at NEAR
HACKATHON and runs on testnet only; its README covers the contract, the full flow, the on-chain
evidence and the hackathon disclosures.

## Repository layout

```
├── src/ehor/                 identity, log, crypto, store, roster, sync, transport,
│                             service, MCP server and CLI
├── tests/                    tests mirroring src/ehor/, plus integration tests
├── docs/
│   ├── ehor.md               the full ehor guide (also ehor's PyPI page)
│   └── protocol.md           the wire format
├── site/                     the website
└── packages/ehor-near/       ehor-near, NEAR bounties built on ehor
```

## Known limits

- Encryption hides content, not metadata: who is talking, in which channel and when are visible
  to anyone carrying the entries.
- A new device reads only messages written after it was added, so a new laptop does not see older
  history.
- A hardware signing key does not ask for Touch ID when it signs, so anything running as your user
  on that machine can still use it. The roster's `hardware` label is the admin's word, since
  neither chip proves where a key lives.
- Direct connections across networks need iroh, which ships builds for Apple silicon Macs, 64-bit
  Linux and Windows. Other platforms still sync over the LAN, relays and shared folders.
- A forgotten passphrase on a software key cannot be recovered; the device has to join again.
- A team whose only admin loses every enrolled security key cannot change its roster again, so
  give every team at least two admins.

## License

MIT. See [LICENSE](LICENSE).
