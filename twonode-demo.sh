#!/bin/bash
# Treeneesu two-node local network demo (main chain, real proof-of-work).
# Node1 mines; node2 connects only to node1; verifies sync, tx propagation,
# balances, genesis identity, and restart/recovery.
set -u
BIN=~/workspace/treeneesu/bitcoin-core/build/bin
D1=/tmp/tnsu-node1; D2=/tmp/tnsu-node2
GENESIS=000008c949ab6dfa087901003f3f05804bd550bb9a094fc57ecec54994c015b6
rm -rf $D1 $D2; mkdir -p $D1 $D2
C1="$BIN/bitcoin-cli -datadir=$D1 -rpcport=29332"
C2="$BIN/bitcoin-cli -datadir=$D2 -rpcport=29432"
fail() { echo "DEMO FAIL: $1"; $C1 stop 2>/dev/null; $C2 stop 2>/dev/null; exit 1; }
wait_count() { # cli, expected count, timeout secs
  for i in $(seq 1 "$3"); do [ "$($1 getblockcount 2>/dev/null)" = "$2" ] && return 0; sleep 1; done; return 1
}

$BIN/bitcoind -datadir=$D1 -port=29333 -rpcport=29332 -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 || fail "node1 start"
$BIN/bitcoind -datadir=$D2 -port=29433 -rpcport=29432 -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 -connect=127.0.0.1:29333 || fail "node2 start"
for i in $(seq 1 30); do $C1 getblockchaininfo >/dev/null 2>&1 && $C2 getblockchaininfo >/dev/null 2>&1 && break; sleep 1; done

echo "== genesis identity =="
G1=$($C1 getblockhash 0); G2=$($C2 getblockhash 0)
echo "node1 genesis: $G1"; echo "node2 genesis: $G2"
[ "$G1" = "$GENESIS" ] && [ "$G2" = "$GENESIS" ] || fail "genesis mismatch"

echo "== peer connection =="
$C2 getconnectioncount | grep -q 1 || fail "node2 not connected to node1"
$C1 createwallet miner >/dev/null && $C2 createwallet watcher >/dev/null || fail "wallet create"
A1=$($C1 getnewaddress); A2=$($C2 getnewaddress)
echo "node1 addr: $A1"; echo "node2 addr: $A2"
case "$A1" in tnsub1*|tnsu1*|T*) ;; *) echo "(legacy/segwit address form: $A1)";; esac

echo "== mine 3 blocks on node1 (real PoW, target bits 0x1e0fffff) =="
t0=$(date +%s)
$C1 generatetoaddress 3 "$A1" 2000000000 >/dev/null || fail "generatetoaddress"
t1=$(date +%s); echo "mined in $((t1-t0))s"
sleep 2
B1=$($C1 getblockcount); B2=$($C2 getblockcount)
echo "blocks: node1=$B1 node2=$B2"
[ "$B1" = 3 ] && [ "$B2" = 3 ] || fail "sync mismatch"
H1=$($C1 getblockhash 3); H2=$($C2 getblockhash 3)
[ "$H1" = "$H2" ] || fail "tip hash mismatch"
echo "tip hash match: $H1"
BAL1=$($C1 getbalance); echo "node1 balance after 3 blocks (coinbases immature): $BAL1"

echo "== mine 105 more so coinbases mature, then send 25 TNSU node1 -> node2 =="
$C1 generatetoaddress 105 "$A1" 2000000000 >/dev/null || fail "maturation mining"
wait_count "$C2" 108 30 || fail "node2 did not sync to 108"
TXID=$($C1 sendtoaddress "$A2" 25) || fail "sendtoaddress"
echo "txid: $TXID"
PROP=0
for i in $(seq 1 20); do $C2 getrawtransaction $TXID >/dev/null 2>&1 && { PROP=1; break; }; sleep 1; done
[ "$PROP" = 1 ] || fail "tx did not propagate to node2 mempool"
echo "tx visible on node2 (mempool)"
$C1 generatetoaddress 1 "$A1" 2000000000 >/dev/null || fail "confirm mining"
wait_count "$C2" 109 30 || fail "node2 did not sync to 109"
CONF=$($C2 gettransaction $TXID | python3 -c "import json,sys; print(json.load(sys.stdin)['confirmations'])")
BAL2=$($C2 getbalance)
echo "node2 confirmations: $CONF, node2 balance: $BAL2"
[ "$CONF" -ge 1 ] || fail "tx not confirmed on node2"

echo "== restart node2: recovery check =="
$C2 stop; sleep 3
$BIN/bitcoind -datadir=$D2 -port=29433 -rpcport=29432 -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 -connect=127.0.0.1:29333 || fail "node2 restart"
for i in $(seq 1 30); do $C2 getblockchaininfo >/dev/null 2>&1 && break; sleep 1; done
sleep 2
$C2 loadwallet watcher >/dev/null || fail "reload wallet after restart"
RB2=$($C2 getblockcount); RBAL=$($C2 getbalance); RG=$($C2 getblockhash 0)
echo "after restart: blocks=$RB2 balance=$RBAL genesis=$RG"
[ "$RB2" = 109 ] && [ "$RG" = "$GENESIS" ] || fail "recovery mismatch"
[ "$RBAL" = "25.00000000" ] || fail "balance did not survive restart: $RBAL"

$C1 stop; $C2 stop; sleep 2
echo "DEMO RESULT: ALL CHECKS PASSED"
