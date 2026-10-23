#!/bin/bash
cd ~/workspace/treeneesu/bitcoin-core/build-ubsan
export UBSAN_OPTIONS=halt_on_error=false:print_stacktrace=1
SUITES="pow_tests miner_tests bip32_tests bip324_tests descriptor_tests key_tests key_io_tests transaction_tests validation_tests denialofservice_tests bloom_tests coins_tests"
for s in $SUITES; do
  echo "=== SUITE $s ==="
  ./bin/test_bitcoin --run_test=$s --log_level=test_suite --report_level=detailed > /tmp/ubsan-$s.log 2>&1
  echo "EXIT:$? $s"
  grep -c "runtime error" /tmp/ubsan-$s.log | sed "s/^/RUNTIME_ERRORS:$s:/"
done
echo "UBSAN_SUBSET_DONE"
