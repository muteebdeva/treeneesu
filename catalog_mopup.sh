#!/bin/bash
# Mop-up: suites never entered because their batch wedged on an earlier suite.
cd ~/workspace/treeneesu/bitcoin-core || exit 1
OUT=~/workspace/treeneesu/logs/patch2a-catalog
SUITES="logging_tests mempool_tests mempool_fee_estimator_tests merkle_tests merkleblock_tests miner_tests miniminer_tests miniscript_tests minisketch_tests multisig_tests net_tests netbase_tests node_init_tests node_warnings_tests orphanage_tests pcp_tests peerman_tests pmt_tests pool_tests pow_tests prevector_tests private_broadcast_tests spend_tests wallet_crypto_tests wallet_rpc_tests wallet_tests wallet_transaction_tests walletdb_tests walletload_tests"
> "$OUT/mopup_summary.txt"
for s in $SUITES; do
  log="$OUT/mopup_$s.log"
  timeout -s KILL 180 ./build/bin/test_bitcoin --run_test="$s" --log_level=test_suite --report_level=detailed > "$log" 2>&1
  ec=$?
  echo "suite $s exit=$ec" >> "$OUT/mopup_summary.txt"
  sed 's/\x1b\[[0-9;]*m//g' "$log" | grep -E "error: in" | sed 's/.*error: in //' | tr -d '"' | cut -d/ -f1 | sort | uniq -c | sed 's/^/    FAILS /' >> "$OUT/mopup_summary.txt"
  sed 's/\x1b\[[0-9;]*m//g' "$log" | grep -E "fatal error" | sed 's/^/    ABORT /' >> "$OUT/mopup_summary.txt"
done
echo "MOPUP_DONE $(date -Iseconds)" >> "$OUT/mopup_summary.txt"
