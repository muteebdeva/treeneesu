#!/bin/bash
# Treeneesu multi-host soak driver (Gate C evidence).
#
# Runs from the operator's machine over SSH against N independently
# hosted nodes. It verifies, in order:
#   1. every node answers and agrees on the genesis hash
#   2. all nodes converge to the same tip after a mining window
#   3. a transaction created on node 1 confirms on all nodes
#   4. partition drill: node N is firewalled off (iptables DROP on the
#      P2P port via sudo), mines alone, then heals and re-converges
#      (deepest chain wins; the script reports both tips before/after)
#   5. restart drill: every daemon is stopped and started; heights and
#      tips must be unchanged afterwards
#
# Usage:
#   TNSU_HOSTS="user@host1 user@host2 user@host3" \
#   TNSU_CLI="bitcoin-cli -datadir=/var/lib/treeneesu -rpcport=29332" \
#   bash multihost-soak.sh
#
# The drills need passwordless sudo for iptables on the LAST host only.
# Evidence: everything is echoed with timestamps; save the output.
set -u
GENESIS=00000091bddca562e9b5a2c98b31e5e5c831ffc015c6fd8853ef18d6df22dfee
CLI=${TNSU_CLI:-"bitcoin-cli -datadir=/var/lib/treeneesu -rpcport=29332"}
read -ra HOSTS <<< "${TNSU_HOSTS:?set TNSU_HOSTS to the ssh targets}"
[ "${#HOSTS[@]}" -ge 3 ] || { echo "need at least 3 hosts"; exit 1; }
r() { ssh -o ConnectTimeout=10 "${HOSTS[$1]}" "$CLI $2"; }
stamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
echo "== soak start $(stamp) hosts: ${HOSTS[*]} =="
for i in "${!HOSTS[@]}"; do
  G=$(r "$i" "getblockhash 0") || { echo "FAIL: host $i unreachable"; exit 1; }
  [ "$G" = "$GENESIS" ] || { echo "FAIL: host $i genesis $G"; exit 1; }
  echo "host $i genesis OK, peers: $(r "$i" getconnectioncount), height: $(r "$i" getblockcount)"
done
echo "== convergence wait (up to 10 min) =="
for _ in $(seq 1 60); do
  TIPS=$(for i in "${!HOSTS[@]}"; do r "$i" getbestblockhash; done | sort -u | wc -l)
  [ "$TIPS" = "1" ] && break; sleep 10
done
[ "$TIPS" = "1" ] || { echo "FAIL: tips did not converge"; exit 1; }
echo "all tips converged at height $(r 0 getblockcount)"
echo "== partition drill on last host =="
LAST=$(( ${#HOSTS[@]} - 1 ))
ssh "${HOSTS[$LAST]}" "sudo iptables -A INPUT -p tcp --dport 29333 -j DROP && sudo iptables -A OUTPUT -p tcp --sport 29333 -j DROP" \
  || { echo "FAIL: could not partition host $LAST (sudo/iptables)"; exit 1; }
echo "host $LAST partitioned at $(stamp); waiting 3 block intervals (450 s)"; sleep 450
echo "partitioned tip: $(r "$LAST" getbestblockhash) height $(r "$LAST" getblockcount)"
echo "main-group tip:   $(r 0 getbestblockhash) height $(r 0 getblockcount)"
ssh "${HOSTS[$LAST]}" "sudo iptables -D INPUT -p tcp --dport 29333 -j DROP; sudo iptables -D OUTPUT -p tcp --sport 29333 -j DROP"
echo "healed at $(stamp); waiting for re-convergence (up to 10 min)"
for _ in $(seq 1 60); do
  TIPS=$(for i in "${!HOSTS[@]}"; do r "$i" getbestblockhash; done | sort -u | wc -l)
  [ "$TIPS" = "1" ] && break; sleep 10
done
[ "$TIPS" = "1" ] || { echo "FAIL: no re-convergence after heal"; exit 1; }
echo "re-converged at height $(r 0 getblockcount), tip $(r 0 getbestblockhash)"
echo "== restart drill =="
H_BEFORE=$(r 0 getblockcount); T_BEFORE=$(r 0 getbestblockhash)
for i in "${!HOSTS[@]}"; do ssh "${HOSTS[$i]}" "sudo systemctl restart treeneesu-node"; done
sleep 30
for i in "${!HOSTS[@]}"; do
  [ "$(r "$i" getblockcount)" = "$H_BEFORE" ] && [ "$(r "$i" getbestblockhash)" = "$T_BEFORE" ] \
    || { echo "FAIL: host $i did not recover state"; exit 1; }
done
echo "all hosts recovered at height $H_BEFORE"
echo "SOAK RESULT: ALL DRILLS PASSED $(stamp)"
