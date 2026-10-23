# Treeneesu — Private Testnet Operator Guide

How to run a small **private** Treeneesu network for development and testing:
multiple nodes, real proof-of-work mining, wallet transfers, and wallet
backup/recovery. This is a learning/test network only — it has **no monetary
value**, no public peers, and no DNS/fixed seeds exist for Treeneesu. Nodes
only ever connect where you tell them to (`-connect` / `-addnode`).

Reference values for every Treeneesu chain (main parameters):

| Item | Value |
|---|---|
| Genesis hash | `00000091bddca562e9b5a2c98b31e5e5c831ffc015c6fd8853ef18d6df22dfee` |
| P2P port / RPC port | 29333 / 29332 |
| Address prefix (bech32) | `tnsu1…` |
| Block subsidy | 50 TNSU, halving every 420,000 blocks |
| Max supply | 42,000,000 TNSU (actual total issuance 41,999,999.9538) |
| Data directory | `~/.treeneesu` (config file `treeneesu.conf`) |

## 1. Prerequisites

- A build of the node software (`build-final/bin/bitcoind` and
  `build-final/bin/bitcoin-cli` in this repository, or any build of the same
  source). The binary names are unchanged from upstream Bitcoin Core.
- Each node needs its **own data directory** and its **own P2P/RPC ports**.
- Mining at the current difficulty (~2²³ expected hashes per block) is fast on
  any modern CPU, but a fresh wallet needs `-fallbackfee=0.001` to send
  transactions before it holds mature coins.

## 2. Single-machine exercise (what `testnet-run.sh` does)

Three nodes on loopback IPs 127.0.0.1 / 127.0.0.2 / 127.0.0.3, data
directories `/tmp/tnsu-net-a|b|c`, P2P ports 29333/29433/29533, RPC ports
29332/29432/29532. Run it end-to-end with:

```bash
bash testnet-run.sh
```

It performs, in order:

1. **Start + mesh.** A starts standalone; B and C `-connect` to A (C also to
   B). Each node should report `getconnectioncount` = 2.
2. **Genesis agreement.** All three nodes must return the genesis hash above
   for `getblockhash 0`. A mismatch means a node was built from different
   parameters — stop and rebuild; do not try to "fix" it with extra peers.
3. **Mine + sync.** A creates wallet `alpha`, B creates `beta`.
   `generatetoaddress 105 <addr> 2000000000` mines 105 blocks on A (the last
   argument is a *whole-batch* hash budget — smaller values can abort the
   batch part-way). B and C must reach height 105 with the **same**
   `getbestblockhash`.
4. **Transfer.** A sends 10 TNSU to B's address; one more block confirms it;
   B's `getbalance` must read exactly `10.00000000`.
5. **Backup + restore.** `backupwallet` on B, stop B, copy the backup to
   `wallets/restored/wallet.dat`, restart B, `loadwallet restored` — the
   restored wallet must show the same 10.00000000 balance and still contain
   the transfer in `gettransaction`.
6. **Restart persistence.** Stop all three nodes, restart them, and confirm
   all recover at height 106 with equal tips.

Expected final line: `TESTNET RESULT: ALL CHECKS PASSED`.

### Environment limit (verified on the development VM)

Linux network namespaces would be the stronger isolation
(`ip netns add …`), but on this VM the command fails with
`setns: Operation not permitted`, so the exercise uses loopback-IP
separation instead. The node behaviour under test (handshake, sync,
validation, wallet) is identical; only the network isolation is weaker.

## 3. Multi-machine variant

The same commands work across machines — change only the bind/connect
addresses and open the P2P port between the machines:

On machine 1 (192.0.2.10):

```bash
bitcoind -datadir=~/tnsu-node1 -bind=0.0.0.0 -port=29333 -rpcport=29332 \
  -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 \
  -rpcbind=127.0.0.1 -rpcallowip=127.0.0.1
```

On machine 2:

```bash
bitcoind -datadir=~/tnsu-node2 -bind=0.0.0.0 -port=29333 -rpcport=29332 \
  -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 \
  -rpcbind=127.0.0.1 -rpcallowip=127.0.0.1 -connect=192.0.2.10:29333
```

Keep RPC bound to localhost (as above) unless you set
`rpcauth` — the cookie/RPC on a LAN without authentication lets anyone on
the network spend the wallet. Verify both nodes agree on
`getblockhash 0` before mining anything.

## 4. Operating the network by hand

```bash
CLI="bitcoin-cli -datadir=/tmp/tnsu-net-a -rpcport=29332"
$CLI getblockchaininfo            # height, tip, difficulty
$CLI getconnectioncount           # peers
$CLI -rpcwallet=alpha getbalance  # wallet balance
$CLI generatetoaddress 1 $($CLI -rpcwallet=alpha getnewaddress) 2000000000
$CLI -rpcwallet=alpha sendtoaddress <tnsu1…address> 5
$CLI stop
```

After a restart, wallets are **not** auto-loaded in this exercise setup —
run `loadwallet <name>` before using `-rpcwallet=<name>` commands.

## 5. Backup and recovery rules

- `backupwallet <path>` makes a consistent copy of one wallet while the
  node runs. Do it **after** any important address generation.
- A backup restores balance *and* transaction history as of the backup
  moment. Coins received **after** the backup still appear (they are found
  by rescanning the chain), but labels/address-book entries added later do
  not.
- Test your restore before you need it: copy the backup into
  `wallets/<name>/wallet.dat` in a stopped node's data directory, start the
  node, `loadwallet <name>`, and compare `getbalance` with the source node.
- Never share or publish a `wallet.dat` from any chain you care about — it
  contains private keys. Testnet wallets in this guide hold worthless test
  coins, and that is the only reason handling them casually here is safe.

## 6. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `getconnectioncount` = 0 | Peer not listening yet, wrong `-connect` address/port, or the peer rejected the handshake (different genesis/params). Check both nodes' `debug.log`. |
| Nodes stuck at different heights | One node is on a different chain (params mismatch) — compare `getblockhash 0`. |
| `generatetoaddress` stops early | The last argument is a total hash budget for the whole batch; use `2000000000`. |
| Send fails with a fee error | Fresh wallet with immature/no coins: start with `-fallbackfee=0.001` and mine ≥100 blocks to your address first (coinbase matures after 100 blocks). |
| `-rpcwallet` says wallet not found after restart | `loadwallet <name>` first. |
| Port already in use | Another node (or a leftover process) holds it — each node needs unique `-port`/`-rpcport` per machine. |

## 7. Scope

This guide stands up a **private** test network between your own machines.
It is not a public testnet launch: there are no seed nodes, no faucet, and
no uptime commitment, and §7 of the project brief (launch gates) remains
closed. A proposed *public* test-chain parameter set is documented
separately in `TESTNET-PLAN.md` as a plan only.
