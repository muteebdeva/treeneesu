#!/bin/bash
# Treeneesu retarget-grind supervisor.
# Keeps grind_chain alive across crashes: every 45 s, if the chain file
# is incomplete and no grinder is running, resume the grind. When the
# chain reaches 8070 blocks, run the assertion phase exactly once and
# exit. Uses flock so duplicate supervisors cannot coexist.
set -u
cd ~/workspace/treeneesu/retarget-test
exec 9>.supervise.lock
flock -n 9 || exit 0
GENESIS=00000091bddca562e9b5a2c98b31e5e5c831ffc015c6fd8853ef18d6df22dfee
while true; do
  N=$(wc -l < blocks.txt 2>/dev/null || echo 0)
  if [ "$N" -ge 8070 ]; then
    if [ ! -f .assert_done ]; then
      bash submit_and_assert.sh > ../logs/retarget-assert-v2.log 2>&1
      echo "RETARGET_EXIT:$?" >> ../logs/retarget-assert-v2.log
      touch .assert_done
    fi
    exit 0
  fi
  if ! pgrep -x grind_chain >/dev/null; then
    ./grind_chain $GENESIS 1792713600 5 0x1e01ffff 0x1d7fffc0 8064 8070 blocks.txt 5000000000 >> grind-v2.log 2>&1 &
  fi
  sleep 45
done
