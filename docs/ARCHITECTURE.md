# Treeneesu architecture — what differs from Bitcoin Core and where

Treeneesu is a *parameter and identity fork*: the consensus engine, networking,
mempool, wallet, and cryptography are unmodified Bitcoin Core v32.0. All
Treeneesu-specific production changes are confined to three files, which makes
the diff small enough to audit by hand.

## Production changes

### Patch 1 — identity (committed, `5790ce2`)
| File | Change |
|---|---|
| `src/common/args.cpp` | Default data dir `.bitcoin` → `.treeneesu`; config file `bitcoin.conf` → `treeneesu.conf` (incl. Windows/macOS app-support names) |
| `src/clientversion.cpp` | User-agent name `Satoshi` → `Treeneesu` |

### Patch 2a — main-chain parameters (uncommitted)
| File | Change |
|---|---|
| `src/kernel/chainparams.cpp` (`CMainParams`) | Genesis block (ground from the design timestamp, nonce 535382); magic `a7 3e 5c 91`; P2P port 29333; halving 420,000; powLimit bits `0x1e0fffff` (**see known defect**); spacing 150 s; retarget 8,064 blocks; DNS + fixed seeds deleted; base58 prefixes 65/22/193; ext-key bytes `02FE6D4F`/`02FE6D47`; bech32 HRP `tnsu`; BIP34/65/66/CSV heights 1, segwit height 0, BIP34 hash = Treeneesu genesis; Bitcoin's script-flag exceptions and assumeutxo snapshots deleted; defaultAssumeValid zeroed; nMinimumChainWork = genesis work |
| `src/consensus/amount.h` | `MAX_MONEY` 21,000,000 → 42,000,000 coins |
| `src/chainparamsbase.cpp` | Main RPC port 8332 → 29332 |

### Test-side changes (Mission 2)
Production behavior was correct; Bitcoin's own test fixtures encode Bitcoin's
identity and parameters, so the fixtures were adapted — never weakened. Full
record: `../MISSION2-CHANGELOG.md`. Areas: address/key/descriptor encodings,
BIP324 vectors (magic-dependent), money-cap vectors, miner block table,
activation-height assumptions in the miner fixture, the functional test
harness's config filename (`bitcoin.conf` → `treeneesu.conf`).

## How the pieces fit (beginner view)

- **Chain params** (`kernel/chainparams.cpp`) are the chain's constitution:
  genesis, difficulty, ports, address prefixes. Every node reads the same
  file, which is what makes separate computers agree they are on "Treeneesu".
- **Consensus** (`src/consensus/`, `src/validation.cpp`) checks blocks and
  transactions against those params: proof-of-work, subsidy schedule,
  `MAX_MONEY`.
- **P2P** (`src/net*.cpp`, `src/net_processing.cpp`) moves blocks and
  transactions between nodes, using the network magic to recognize its own
  chain's messages, and BIP324 encrypted transport by default.
- **Wallet** (`src/wallet/`) derives keys from the ext-key prefixes and
  builds addresses from the base58/bech32 parameters — which is why changing
  prefixes changes every address string but no private key.

## Not yet done (by design freeze / pending decisions)
- Regtest replacement (Patch 2b) and removal of testnet/testnet4/signet
  parameter sets (Patch 2c) — frozen scope, needs owner approval.
- Binary/banners rebrand (`bitcoind` → `treeneesud` etc.) — cosmetic, deferred.
- powLimit fix — consensus change, awaiting owner decision (see BLOCKERS.md).
