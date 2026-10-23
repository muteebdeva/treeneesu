#!/bin/bash
# Treeneesu PRIVATE TESTNET exercise: three independent nodes on separate
# loopback IPs/datadirs (this VM cannot create network namespaces:
# "setns: Operation not permitted" — see TESTNET-GUIDE.md for the
# multi-machine variant, which uses identical commands with real IPs).
# Checks: peer mesh, genesis agreement, mining + sync, wallet transfer,
# wallet backup + restore, full restart persistence.
set -u
BIN=${TNSU_BIN:-~/workspace/treeneesu/bitcoin-core/build-final/bin}
A=/tmp/tnsu-net-a; B=/tmp/tnsu-net-b; C=/tmp/tnsu-net-c
GENESIS=00000091bddca562e9b5a2c98b31e5e5c831ffc015c6fd8853ef18d6df22dfee
rm -rf $A $B $C; mkdir -p $A $B $C
CA="$BIN/bitcoin-cli -datadir=$A -rpcport=29332"
CB="$BIN/bitcoin-cli -datadir=$B -rpcport=29432"
CC="$BIN/bitcoin-cli -datadir=$C -rpcport=29532"
fail() { echo "TESTNET FAIL: $1"; $CA stop 2>/dev/null; $CB stop 2>/dev/null; $CC stop 2>/dev/null; exit 1; }
wait_count() { for i in $(seq 1 "$3"); do [ "$($1 getblockcount 2>/dev/null)" = "$2" ] && return 0; sleep 1; done; return 1; }

$BIN/bitcoind -datadir=$A -bind=127.0.0.1 -port=29333 -rpcport=29332 -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 || fail "node A start"
$BIN/bitcoind -datadir=$B -bind=127.0.0.2 -port=29433 -rpcport=29432 -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 -connect=127.0.0.1:29333 || fail "node B start"
$BIN/bitcoind -datadir=$C -bind=127.0.0.3 -port=29533 -rpcport=29532 -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 -connect=127.0.0.1:29333 -connect=127.0.0.2:29433 || fail "node C start"
for i in $(seq 1 30); do $CA getblockchaininfo >/dev/null 2>&1 && $CB getblockchaininfo >/dev/null 2>&1 && $CC getblockchaininfo >/dev/null 2>&1 && break; sleep 1; done

echo "== genesis agreement (3 nodes) =="
for cli in "$CA" "$CB" "$CC"; do [ "$($cli getblockhash 0)" = "$GENESIS" ] || fail "genesis mismatch"; done
echo "all three nodes on Treeneesu genesis $GENESIS"
echo "peer counts: A=$($CA getconnectioncount) B=$($CB getconnectioncount) C=$($CC getconnectioncount)"

$CA createwallet alpha >/dev/null; $CB createwallet beta >/dev/null || fail "wallet create"
AA=$($CA getnewaddress); AB=$($CB getnewaddress)
echo "A addr: $AA"; echo "B addr: $AB"

echo "== mine 105 on A, all sync =="
$CA generatetoaddress 105 "$AA" 2000000000 >/dev/null || fail "mining on A"
wait_count "$CB" 105 60 || fail "B sync"; wait_count "$CC" 105 60 || fail "C sync"
[ "$($CA getbestblockhash)" = "$($CB getbestblockhash)" ] && [ "$($CB getbestblockhash)" = "$($CC getbestblockhash)" ] || fail "tip mismatch"
echo "all nodes at height 105, tips equal"

echo "== transfer 10 TNSU A -> B, confirm =="
TX=$($CA sendtoaddress "$AB" 10) || fail "send A->B"
echo "txid: $TX"
$CA generatetoaddress 1 "$AA" 2000000000 >/dev/null || fail "confirmation mining"
wait_count "$CB" 106 60 || fail "B sync to 106"; wait_count "$CC" 106 60 || fail "C sync to 106"
BAL_B=$($CB getbalance); echo "B balance: $BAL_B"
[ "$BAL_B" = "10.00000000" ] || fail "B balance wrong: $BAL_B"

echo "== wallet backup + restore on B =="
$CB backupwallet /tmp/tnsu-beta-backup.dat || fail "backupwallet"
$CB stop; sleep 3
mkdir -p $B/wallets/restored; cp /tmp/tnsu-beta-backup.dat $B/wallets/restored/wallet.dat
$BIN/bitcoind -datadir=$B -bind=127.0.0.2 -port=29433 -rpcport=29432 -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 -connect=127.0.0.1:29333 || fail "B restart for restore"
for i in $(seq 1 30); do $CB getblockchaininfo >/dev/null 2>&1 && break; sleep 1; done
$CB loadwallet restored >/dev/null || fail "load restored wallet"
RBAL=$($CB -rpcwallet=restored getbalance); echo "restored wallet balance: $RBAL"
[ "$RBAL" = "10.00000000" ] || fail "restored balance wrong: $RBAL"
$CB -rpcwallet=restored gettransaction $TX >/dev/null || fail "restored wallet lost the tx history"

echo "== restart all nodes: persistence =="
$CA stop; $CB stop; $CC stop; sleep 3
$BIN/bitcoind -datadir=$A -bind=127.0.0.1 -port=29333 -rpcport=29332 -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 || fail "A restart"
$BIN/bitcoind -datadir=$B -bind=127.0.0.2 -port=29433 -rpcport=29432 -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 -connect=127.0.0.1:29333 || fail "B restart"
$BIN/bitcoind -datadir=$C -bind=127.0.0.3 -port=29533 -rpcport=29532 -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 -connect=127.0.0.1:29333 || fail "C restart"
for i in $(seq 1 30); do [ "$($CA getblockcount 2>/dev/null)" = 106 ] && [ "$($CB getblockcount 2>/dev/null)" = 106 ] && [ "$($CC getblockcount 2>/dev/null)" = 106 ] && break; sleep 1; done
[ "$($CA getblockcount)" = 106 ] && [ "$($CB getblockcount)" = 106 ] && [ "$($CC getblockcount)" = 106 ] || fail "heights after restart"
[ "$($CA getbestblockhash)" = "$($CC getbestblockhash)" ] || fail "tips diverged after restart"
echo "all nodes recovered at height 106 with equal tips"

$CA stop; $CB stop; $CC stop; sleep 2
echo "TESTNET RESULT: ALL CHECKS PASSED"
