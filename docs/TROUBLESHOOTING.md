# Troubleshooting — real failures from this project and their causes

## Test suite "hangs" forever
**Cause (here):** not a hang — a test aborted on `assert(keydata)` (invalid
key after prefix change) and the crash path intermittently deadlocked in the
shared test process. **Diagnose:** run the single suite under `gdb -batch
-ex run -ex bt`. Suites that abort also poison later suites in the same
process; always re-check a "failing" suite standalone before classifying it.

## `generatetoaddress` returns fewer blocks than requested, no error
The `maxtries` argument is one budget shared by all blocks in the call.
Expected tries per block ≈ 2^256 / target (≈ 1M at Treeneesu's starting
difficulty). Raise the budget (e.g. 2,000,000,000) — and note values above
2^31 may be rejected by the RPC argument parser.

## Second node won't sync past the first few blocks
Check both nodes agree on genesis (`getblockhash 0`) and that the follower
was started with `-connect=<peer>` (Treeneesu has no seed nodes by design).
Also confirm the leader actually mined the blocks — see the maxtries entry
above; a silent short batch looks exactly like a sync failure.

## `sendtoaddress` → "Fee estimation failed. Fallbackfee is disabled"
A fresh chain has no fee history. Start local/demo nodes with
`-fallbackfee=0.001` (never needed on a mature network).

## Functional tests: "Unable to connect to bitcoind… missing_credentials"
The harness writes node config into `treeneesu.conf`. If nodes start on the
wrong chain (cookie not where the harness looks), the config file isn't
being read — check the filename the daemon expects vs the one the harness
writes, and check the `[regtest]` section landed in the right file.

## Wallet balance is empty right after a node restart
RPC-created wallets are not auto-loaded on restart in this version. Run
`loadwallet <name>` before `getbalance`.

## Build takes ~37 minutes / tests use both cores
Expected on a 2-core VM with `-O2`. Keep `-g0` (no debug symbols) to reduce
memory pressure; build only the targets you need for iteration
(`--target test_bitcoin` covers most test work).
