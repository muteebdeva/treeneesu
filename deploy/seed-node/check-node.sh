#!/bin/bash
# Seed-node health check: prints one status line; exit 0 = healthy.
# Checks: daemon answers, peers > 0, tip not stalled (>30 min old).
# Sends nothing anywhere — wire stdout/exit code into your own alerting.
set -u
CLI=${TNSU_CLI:-"bitcoin-cli -datadir=/var/lib/treeneesu -rpcport=29332"}
INFO=$($CLI getblockchaininfo 2>/dev/null) || { echo "UNHEALTHY: daemon not answering"; exit 1; }
PEERS=$($CLI getconnectioncount 2>/dev/null || echo 0)
TIP_TIME=$(echo "$INFO" | python3 -c "import json,sys; print(json.load(sys.stdin)['mediantime'])" 2>/dev/null || echo 0)
NOW=$(date +%s)
AGE=$(( NOW - TIP_TIME ))
HEIGHT=$(echo "$INFO" | python3 -c "import json,sys; print(json.load(sys.stdin)['blocks'])" 2>/dev/null || echo "?")
if [ "$PEERS" -eq 0 ]; then echo "UNHEALTHY: 0 peers at height $HEIGHT"; exit 1; fi
if [ "$AGE" -gt 1800 ]; then echo "UNHEALTHY: tip stalled ${AGE}s at height $HEIGHT (peers $PEERS)"; exit 1; fi
echo "OK: height $HEIGHT peers $PEERS tip_age ${AGE}s"
