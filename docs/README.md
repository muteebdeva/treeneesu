# Treeneesu

Treeneesu is an independent proof-of-work cryptocurrency built by modifying
Bitcoin Core v32.0. It has its own genesis block, network magic, ports,
address formats, and monetary policy (42 million TNSU cap, 50 TNSU block
subsidy, 150-second target block spacing).

**Status: release candidate in preparation — NOT ready for any public
network or real value.** One known consensus defect (the powLimit/retarget
issue, see `BLOCKERS.md` in the project root) must be fixed and approved
before any network others rely on. Treeneesu is a learning project: it has
no monetary value, and its deliberately low mining difficulty means its
chain can be rewritten cheaply by anyone. Never use it to store value.

## Quick facts (verified against the running code)

| Parameter | Value |
|---|---|
| Ticker | TNSU |
| Genesis hash | `000008c949ab6dfa087901003f3f05804bd550bb9a094fc57ecec54994c015b6` |
| Genesis message | "Treeneesu 23/Oct/2026 - a learning chain with no monetary value" |
| Network magic | `a7 3e 5c 91` |
| P2P / RPC ports (main) | 29333 / 29332 |
| Address formats | base58 `T…` (P2PKH, prefix 65), prefix 22 (P2SH), bech32 `tnsu1…` |
| Max supply | 41,999,999.9538 TNSU issued (42,000,000 cap) |
| Subsidy / halving | 50 TNSU / every 420,000 blocks |
| Target spacing | 150 seconds (retarget every 8,064 blocks) |
| Data directory | `~/.treeneesu` (config: `treeneesu.conf`) |
| User agent | `/Treeneesu:32.0.0/` |

## Build (verified on Ubuntu 24.04, this project's machine)

```bash
sudo apt install build-essential cmake libboost-dev libsqlite3-dev
cmake -B build -DBUILD_GUI=OFF -DENABLE_IPC=OFF \
      -DCMAKE_CXX_FLAGS_RELWITHDEBINFO="-O2 -g0"
cmake --build build -j 2 --target bitcoind bitcoin-cli test_bitcoin
```

## Verify

```bash
./build/bin/test_bitcoin            # full unit suite (see TEST-SUMMARY.json)
bash ../twonode-demo.sh             # two-node main-chain demo, real PoW
```

More documentation:
- `ARCHITECTURE.md` — what was changed vs Bitcoin Core, and where
- `BEGINNER-GUIDE.md` — a learning guide explaining every bug found and fixed
- `COMMANDS.md` — verified command reference
- `GLOSSARY.md`, `TROUBLESHOOTING.md`, `RUNBOOK.md`,
  `SECURITY-AND-LAUNCH-CHECKLIST.md`

Upstream copyright and license notices are preserved throughout the tree
(Bitcoin Core is MIT-licensed; Treeneesu inherits that license for the
derived code).
