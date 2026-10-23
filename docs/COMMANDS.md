# Verified command reference

Every command below was actually run in this project (paths assume the repo
at `~/workspace/treeneesu/bitcoin-core`). Times are for this machine
(2 cores, 7.7 GiB RAM) and will differ elsewhere.

## Build

```bash
sudo apt install build-essential cmake libboost-dev libsqlite3-dev gdb
cmake -B build -DBUILD_GUI=OFF -DENABLE_IPC=OFF \
      -DCMAKE_CXX_FLAGS_RELWITHDEBINFO="-O2 -g0"
cmake --build build -j 2 --target test_bitcoin        # ~35–60 s incremental; ~37 min from scratch (all targets)
cmake --build build -j 2 --target bitcoind bitcoin-cli
```

## Unit tests

```bash
./build/bin/test_bitcoin                                   # full suite (~4 min)
./build/bin/test_bitcoin --run_test=descriptor_tests \
    --log_level=test_suite --report_level=detailed         # one suite
./build/bin/test_bitcoin --list_content=HRF 2>&1 | head    # list suites (goes to stderr)
```
Note: `--report_level` accepts `confirm|short|detailed|no` (not `summary`).

## Run a node (Treeneesu main chain)

```bash
./build/bin/bitcoind -datadir=/tmp/tnsu-node1 -port=29333 -rpcport=29332 \
    -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001
./build/bin/bitcoin-cli -datadir=/tmp/tnsu-node1 -rpcport=29332 getblockchaininfo
./build/bin/bitcoin-cli -datadir=/tmp/tnsu-node1 -rpcport=29332 getblockhash 0
# expect: 000008c949ab6dfa087901003f3f05804bd550bb9a094fc57ecec54994c015b6
```

Connect a second node (no seeds exist by design — peer manually):

```bash
./build/bin/bitcoind -datadir=/tmp/tnsu-node2 -port=29433 -rpcport=29432 \
    -daemon -server -listen -discover=0 -dnsseed=0 -fallbackfee=0.001 \
    -connect=127.0.0.1:29333
```

## Mine and transact (local demo)

```bash
CLI="./build/bin/bitcoin-cli -datadir=/tmp/tnsu-node1 -rpcport=29332"
$CLI createwallet miner
ADDR=$($CLI getnewaddress)                    # tnsu1…
$CLI generatetoaddress 3 "$ADDR" 2000000000   # maxtries is a WHOLE-BATCH budget
$CLI generatetoaddress 105 "$ADDR" 2000000000 # ~105 more so coinbases mature (100 blocks)
$CLI sendtoaddress <other-node-address> 25
$CLI getbalance
```
The complete, self-checking version is `../twonode-demo.sh`.

## Functional tests (subset)

```bash
cp build/test/config.ini test/config.ini   # runner expects it in the source tree
python3 test/functional/test_runner.py --jobs=2 \
    feature_help.py rpc_net.py wallet_basic.py \
    p2p_v2_transport.py feature_segwit.py rpc_blockchain.py
```

## Debugging recipes used in this project

```bash
# Stack trace for an aborting test suite (container blocks gdb -p attach;
# run the test UNDER gdb instead):
gdb -batch -ex run -ex bt --args ./build/bin/test_bitcoin --run_test=<suite>
```
