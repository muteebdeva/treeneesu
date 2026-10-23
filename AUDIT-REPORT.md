# Treeneesu — Independent Audit Report (2026-10-23, completion mission §2)

## Git history verification (local clone `bitcoin-core/`, branch `treeneesu`)

| Commit | Subject | Verified |
|---|---|---|
| `465dde2` | Merge bitcoin/bitcoin#36508: [32.0] Finalize (upstream v32.0 base) | ✔ `git log` |
| `5790ce2` | Patch 1 — data directory, config file, user-agent identity | ✔ exists |
| `eca8485` | Patch 2a (main chain parameters) + Mission 2 test repairs | ✔ exists |
| `35f49eb` | Fix D4 powLimit overflow defect (Option A) | ✔ exists, HEAD |

Total diff vs upstream: 26 files (5 production, 21 test/framework).

**Push status (honest distinction):** the local clone's commits live in
`bitcoin-core/.git`. The GitHub repository receives (a) the complete working
tree as a single import commit via the Git Data API, and (b) a `git bundle`
of the Treeneesu commit chain (see `history/`) so the exact commit hashes
above remain independently verifiable against the public upstream base.
A raw `git push` is not possible through the available GitHub connector
(it exposes the REST API only, no git transport credentials).

## Genesis three-way verification

Parameters read from source (`src/kernel/chainparams.cpp`, CMainParams):

- pszTimestamp: `Treeneesu 23/Oct/2026 - a learning chain with no monetary value`
- Pubkey (from source): `048439b61821b6aa…0a478` (130 hex chars)
- nTime 1792713600, nBits 0x1e01ffff, nNonce 26434925, reward 50 TNSU

Independent Python recomputation (genesis/grind_genesis.py, control-verified
against Bitcoin's genesis construction):

- Merkle root: `9b242aa5c3f7c5478b6285a1f073f202994dc41dd58bcea70680102b6a2096cf` ✔ = source assert
- Serialized header (80 B): `01000000 0000…0000 cf96206a2b108006a7ce8bd51dc44d9902f273f0a185628b47c5f7c3a52a249b 80a3da6a ffff011e 6d5d9301`
- Block hash: `00000091bddca562e9b5a2c98b31e5e5c831ffc015c6fd8853ef18d6df22dfee` ✔ = reported value
- Target: `000001ffff0000…0000`; hash ≤ target ✔

Compiled-daemon check (clean build, 2026-10-23): `getblockhash 0` returned
the identical hash; daemon startup runs the in-code asserts on
hashGenesisBlock and hashMerkleRoot. **All three agree: source, independent
recomputation, compiled binary.**

Note on method: chainparams.cpp contains three 130-hex pubkey-like strings
(Bitcoin's genesis pubkey for the retained upstream chain classes, Treeneesu's,
and signet material). An extraction that grabs the wrong one produces a wrong
merkle root — the audit used the key the CMainParams constructor actually
passes, and the merkle assert confirms the choice.
