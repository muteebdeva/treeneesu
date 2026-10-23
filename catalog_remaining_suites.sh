#!/bin/bash
# Catalog-only run: enumerate failures in suites the full run never reached
# (it wedged in bloom_tests). NO fixes are made by this script.
cd ~/workspace/treeneesu/bitcoin-core || exit 1
OUT=~/workspace/treeneesu/logs/patch2a-catalog
mkdir -p "$OUT"
./build/bin/test_bitcoin --list_content=HRF 2>&1 | grep -E "^[A-Za-z]" | sed 's/\*$//' > "$OUT/all_suites.txt"
# suites already fully run in gate run #2 (19 completed + bloom wedged)
DONE="addrman_tests allocator_tests amount_tests argsman_tests arith_uint256_tests banman_tests base32_tests base58_tests base64_tests baseindex_tests bech32_tests bip32_tests bip324_tests blockchain_tests blockencodings_tests blockfilter_index_tests blockfilter_tests blockmanager_tests blockpolicyestimator_tests bloom_tests"
> "$OUT/summary.txt"
mapfile -t SUITES < <(grep -vxF -f <(tr ' ' '\n' <<< "$DONE") "$OUT/all_suites.txt")
echo "remaining suites: ${#SUITES[@]}" >> "$OUT/summary.txt"
B=0
for ((i=0; i<${#SUITES[@]}; i+=15)); do
  B=$((B+1))
  batch=("${SUITES[@]:i:15}")
  filter=$(IFS=:; echo "${batch[*]}")
  log="$OUT/batch_$B.log"
  timeout -s KILL 240 ./build/bin/test_bitcoin --run_test="$filter" --log_level=test_suite --report_level=detailed > "$log" 2>&1
  ec=$?
  echo "batch $B exit=$ec suites=${batch[*]}" >> "$OUT/summary.txt"
  sed 's/\x1b\[[0-9;]*m//g' "$log" | grep -E "error: in" | sed 's/.*error: in //' | tr -d '"' | cut -d/ -f1 | sort | uniq -c | sort -rn | sed 's/^/    FAILS /' >> "$OUT/summary.txt"
  sed 's/\x1b\[[0-9;]*m//g' "$log" | grep -E "fatal error" | sed 's/^/    ABORT /' >> "$OUT/summary.txt"
  sed 's/\x1b\[[0-9;]*m//g' "$log" | grep -E "Entering test suite" | awk -F'"' '{print $2}' | while read -r s; do
    grep -q "Leaving test suite \"$s\"" <(sed 's/\x1b\[[0-9;]*m//g' "$log") || echo "    INCOMPLETE_SUITE $s" >> "$OUT/summary.txt"
  done
done
echo "CATALOG_DONE $(date -Iseconds)" >> "$OUT/summary.txt"
