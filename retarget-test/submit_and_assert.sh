#!/bin/bash
# Treeneesu RETARGET TEST — submission + assertion phase.
# Feeds the pre-ground main-parameter chain (retarget-test/blocks.txt,
# produced by grind_chain) to a fresh node and asserts the difficulty
# retarget at block 8064 matches the independent Python difficulty model:
#   blocks 1..8063    bits 0x1e01ffff (5-second synthetic spacing)
#   block  8064+      bits 0x1d7fffc0 (timespan clamped to 1/4 -> target /4)
# Also verifies a second node syncs the full 8070-block chain and that the
# tip survives a restart. Fails loudly at the first rejected block.
set -u
BIN=${TNSU_BIN:-~/workspace/treeneesu/bitcoin-core/build-final/bin}
D1=/tmp/tnsu-rt1; D2=/tmp/tnsu-rt2
BLOCKS=${1:-~/workspace/treeneesu/retarget-test/blocks.txt}
rm -rf $D1 $D2; mkdir -p $D1 $D2
C1="$BIN/bitcoin-cli -datadir=$D1 -rpcport=29332"
C2="$BIN/bitcoin-cli -datadir=$D2 -rpcport=29432"
fail() { echo "RETARGET TEST FAIL: $1"; $C1 stop 2>/dev/null; $C2 stop 2>/dev/null; exit 1; }

$BIN/bitcoind -datadir=$D1 -port=29333 -rpcport=29332 -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 || fail "node1 start"
$BIN/bitcoind -datadir=$D2 -port=29433 -rpcport=29432 -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 -connect=127.0.0.1:29333 || fail "node2 start"
for i in $(seq 1 30); do $C1 getblockchaininfo >/dev/null 2>&1 && $C2 getblockchaininfo >/dev/null 2>&1 && break; sleep 1; done
[ "$($C1 getblockhash 0)" = "00000091bddca562e9b5a2c98b31e5e5c831ffc015c6fd8853ef18d6df22dfee" ] || fail "genesis mismatch"

echo "== submitting ground chain =="
N=0
while read -r H HEX HASH; do
  R=$($C1 submitblock "$HEX" 2>&1)
  if [ -n "$R" ] && [ "$R" != "null" ]; then echo "block $H rejected: $R"; fail "submission stopped at height $H"; fi
  N=$H
  [ $((N % 1000)) = 0 ] && echo "  submitted $N"
done < "$BLOCKS"
echo "submitted $N blocks; node1 height: $($C1 getblockcount)"
[ "$($C1 getblockcount)" = "$N" ] || fail "node1 height mismatch"

bits() { $1 getblockheader "$($1 getblockhash $2)" | python3 -c "import json,sys; print(json.load(sys.stdin)['bits'])"; }
B8063=$(bits "$C1" 8063); B8064=$(bits "$C1" 8064); B8070=$(bits "$C1" 8070)
echo "bits @8063: $B8063 | @8064: $B8064 | @8070: $B8070"
[ "$B8063" = "1e01ffff" ] || fail "pre-retarget bits wrong"
[ "$B8064" = "1d7fffc0" ] || fail "retarget bits != model prediction 1d7fffc0"
[ "$B8070" = "1d7fffc0" ] || fail "post-retarget bits changed unexpectedly"
echo "RETARGET ASSERTION PASSED: 0x1e01ffff -> 0x1d7fffc0 at block 8064, stable beyond"

echo "== node2 sync =="
for i in $(seq 1 120); do [ "$($C2 getblockcount 2>/dev/null)" = "$N" ] && break; sleep 2; done
[ "$($C2 getblockcount)" = "$N" ] || fail "node2 did not sync to $N"
[ "$($C1 getbestblockhash)" = "$($C2 getbestblockhash)" ] || fail "tip mismatch"
B2_8064=$(bits "$C2" 8064); [ "$B2_8064" = "1d7fffc0" ] || fail "node2 disagrees on retarget bits"
echo "node2 synced to $N with identical tip and retarget bits"

echo "== restart node1 =="
$C1 stop; sleep 3
$BIN/bitcoind -datadir=$D1 -port=29333 -rpcport=29332 -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 || fail "node1 restart"
for i in $(seq 1 30); do [ "$($C1 getblockcount 2>/dev/null)" = "$N" ] && break; sleep 1; done
[ "$($C1 getblockcount)" = "$N" ] || fail "height lost after restart"
echo "height $N persisted after restart"

$C1 stop; $C2 stop; sleep 2
echo "RETARGET TEST RESULT: ALL CHECKS PASSED"
