# Treeneesu

**Treeneesu is an independent proof-of-work blockchain derived from Bitcoin
Core v32.0.** It has its own genesis block, consensus parameters, network
magic, ports, address formats, and chain identity. It is a development and
learning network: **its coins are experimental, have no monetary value, and
are not traded anywhere.** A passing test suite does not make any
cryptocurrency safe for real funds — see `MAINNET-READINESS-GATES.md` before
even thinking about value.

**Status (2026-10-23):** local network fully working. Full unit suite
**152/152 suites pass**; two-node demo (sync, wallet payment, invalid-block
rejection, restart recovery) passes end-to-end. No public network exists.

## Network parameters (Treeneesu "main")

| Parameter | Value |
|---|---|
| Genesis hash | `00000091bddca562e9b5a2c98b31e5e5c831ffc015c6fd8853ef18d6df22dfee` |
| Genesis message | `Treeneesu 23/Oct/2026 - a learning chain with no monetary value` |
| Network magic | `a7 3e 5c 91` |
| P2P port / RPC port | 29333 / 29332 |
| Address prefixes | pubkey 65 (`T…`), script 22, WIF 193; bech32 HRP `tnsu` |
| Extended keys | xpub `02FE6D4F`, xprv `02FE6D47` (unregistered — import with care) |
| Block subsidy / halving | 50 TNSU / every 420,000 blocks; max supply 42,000,000 TNSU |
| Block spacing / retarget | 150 s / every 8,064 blocks (14 days), Bitcoin algorithm |
| powLimit | bits `0x1e01ffff` (≈2²³ hashes per block at easiest difficulty) |
| Seed nodes | **none** — connect peers manually with `-addnode`/`-connect` |
| Data dir / config | `~/.treeneesu` / `treeneesu.conf`; user agent `/Treeneesu:32.0.0/` |

Deliberate deviations from Bitcoin are listed in `PHASE2-DESIGN.md` and
`MISSION4-5-AUDIT-SECURITY.md`. The chain is trivially rewritable by one CPU
by design (low difficulty); never present it as secure.

## Build (Ubuntu 24.04, ₹0)

```sh
sudo apt-get install -y build-essential cmake libboost-dev libsqlite3-dev
cd bitcoin-core
cmake -B build -DBUILD_GUI=OFF -DENABLE_IPC=OFF \
      -DCMAKE_CXX_FLAGS_RELWITHDEBINFO="-O2 -g0"
cmake --build build -j 2 --target bitcoind bitcoin-cli test_bitcoin
```

Binaries land in `build/bin/` and are still named `bitcoind` / `bitcoin-cli`
/ `test_bitcoin` (cosmetic rename deferred — BLOCKERS.md B6). The version
banner still prints "Bitcoin Core version v32.0.0"; the running node's
identity is Treeneesu's (check `getnetworkinfo`: subversion
`/Treeneesu:32.0.0/`).

## Run a node, mine, and pay (all commands verified against the built binaries)

```sh
# start a node (creates ~/.treeneesu)
./build/bin/bitcoind -daemon -fallbackfee=0.001
CLI="./build/bin/bitcoin-cli"

$CLI getblockhash 0            # → the genesis hash above
$CLI createwallet miner
ADDR=$($CLI getnewaddress)     # → tnsu1… / T…
$CLI generatetoaddress 3 "$ADDR" 2000000000   # mine 3 blocks (real PoW)
$CLI getbalance                # coinbases mature after 100 blocks
$CLI sendtoaddress <address> 25
$CLI getblockcount
$CLI stop
```

Two-node sync, transaction propagation, invalid-block rejection, and
restart recovery are demonstrated end-to-end by `./twonode-demo.sh`
(recorded run: `logs/twonode-demo-final.log` — ALL CHECKS PASSED).

## Tests

```sh
./build/bin/test_bitcoin        # 152 suites; expected: all pass
                                # (script_assets_tests self-skips with a
                                #  warning when DIR_UNIT_TEST_DATA is unset)
python3 test/functional/test_runner.py feature_help rpc_net wallet_basic \
        p2p_v2_transport feature_segwit rpc_blockchain
```

Full evidence: `TEST-SUMMARY.json`, `logs/final-fullrun/full2.log`,
`logs/asan-subset.log` (AddressSanitizer subset: 12/12 suites, zero reports),
`AUDIT-REPORT.md` (independent genesis verification).

## Repository layout

- `bitcoin-core/` — the source tree (upstream v32.0 + 4 Treeneesu commits;
  exact history in `history/treeneesu-commits.bundle`, verifiable against
  the public upstream: `git bundle verify`)
- `docs/` — beginner guide, architecture, commands, runbook, troubleshooting
- `genesis/` — genesis construction + verification records
- `*.md` at root — design, audit, changelog, security review, testnet plan,
  mainnet gates, blockers, final report

## License

Upstream code is under the MIT license (see `bitcoin-core/COPYING`); all
upstream copyright notices are preserved. Treeneesu changes are offered
under the same terms.
