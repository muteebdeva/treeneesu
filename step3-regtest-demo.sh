#!/usr/bin/env bash
# Treeneesu Phase 1 Step 3 — regtest demo (upstream Bitcoin Core v32.0, UNMODIFIED)
# Local-only regression-test chain. Coins are worthless test coins.
# What it does: start node -> create wallet -> mine 101 blocks (coinbase matures
# after 100) -> check balance -> send 10 test BTC to a second address -> mine 1
# block -> verify the payment arrived confirmed -> stop the node cleanly.
set -u
BIN="$HOME/workspace/treeneesu/bitcoin-core/build/bin"
DATA=/tmp/treeneesu-regtest-demo
CLI="$BIN/bitcoin-cli -regtest -datadir=$DATA"

rm -rf "$DATA"; mkdir -p "$DATA"

echo "== 1. Start regtest node (background daemon, local only) =="
"$BIN/bitcoind" -regtest -datadir="$DATA" -daemon -fallbackfee=0.0002
for i in $(seq 1 30); do $CLI getblockchaininfo >/dev/null 2>&1 && break; sleep 1; done

echo "== 2. Chain info at start =="
$CLI getblockchaininfo | grep -E '"chain"|"blocks"|"headers"'

echo "== 3. Create wallet 'demo' and a receiving address =="
$CLI createwallet demo
ADDR=$($CLI -rpcwallet=demo getnewaddress)
echo "miner address: $ADDR"

echo "== 4. Mine 101 blocks to that address (50 test BTC each, spendable after 100 confirmations) =="
$CLI -rpcwallet=demo generatetoaddress 101 "$ADDR" | tail -2
$CLI getblockchaininfo | grep -E '"blocks"'
echo "balance after mining:"; $CLI -rpcwallet=demo getbalances | grep -A2 '"mine"'

echo "== 5. Send 10 test BTC to a fresh address in the same wallet =="
ADDR2=$($CLI -rpcwallet=demo getnewaddress)
TXID=$($CLI -rpcwallet=demo sendtoaddress "$ADDR2" 10)
echo "recipient address: $ADDR2"
echo "txid: $TXID"
echo "confirmations before mining (expect 0):"
$CLI -rpcwallet=demo gettransaction "$TXID" | grep -E '"confirmations"|"amount"'

echo "== 6. Mine 1 block to confirm it =="
$CLI -rpcwallet=demo generatetoaddress 1 "$ADDR" >/dev/null
echo "confirmations after mining (expect 1):"
$CLI -rpcwallet=demo gettransaction "$TXID" | grep -E '"confirmations"|"amount"'
$CLI getblockchaininfo | grep -E '"blocks"'

echo "== 7. Stop node cleanly =="
$CLI stop
sleep 2
echo "DEMO_DONE"
