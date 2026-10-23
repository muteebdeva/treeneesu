# TREENEESU — Phase 1, Step 3: Unit Tests + Regtest Demo — Log
Date: 2026-10-23 (Asia/Kolkata) · Approved by Muteeb via options widget 13:53 IST
Result: ✅ UNIT TESTS PASSED · ✅ REGTEST DEMO SUCCEEDED (evidence below)

## 1. Unit tests — full upstream suite, unmodified binary
Command:
```
./build/bin/test_bitcoin --log_level=test_suite --report_level=detailed
```
Result (13:53:38 → 13:55:19 IST, 1m41s, TEST_EXIT:0):
- Running **827 test cases**
- **826 passed clean, 1 passed with warnings, 0 failed**
- **26,782,108 assertions out of 26,782,108 passed** (1 failed *warning*, not a failure)
- Full output: logs/step3-unittests.log

## 2. Regtest demo — script: step3-regtest-demo.sh (kept in this folder)
Run 13:55:40 → 13:55:44 IST, DEMO_SCRIPT_EXIT:0. Full output: logs/step3-regtest.log.
- Node started with `-regtest -datadir=/tmp/treeneesu-regtest-demo` (local only).
  getblockchaininfo: chain="regtest", blocks=0.
- Wallet "demo" created. Miner address: bcrt1qn7xknjha86kwqr49jxp5d2fmstwhwllzrx3nqk
  (note the `bcrt` prefix — regtest addresses are visibly NOT mainnet `bc1`).
- `generatetoaddress 101` → blocks=101. Trusted balance **50.00000000** — exactly
  right: of 101 coinbase rewards (50 each), only the first is mature (100-confirmation
  coinbase maturity rule), the other 100 are still immature.
- Sent **10 test BTC** → recipient bcrt1qhfrm92tfx6g264s3ca5qnej7wmqra7j0jpxkgk,
  txid f8387fd7f2483b15a321922fdae8f127e07635c9b64e084e71d82622106f56b4.
  Confirmations: **0** before mining. (gettransaction top-level amount shows 0.00
  because sender and recipient are the same wallet — details show -10.00 / +10.00.)
- Mined 1 block → blocks=102, transaction confirmations: **1**. ✅
- `bitcoin-cli stop` → "Bitcoin Core stopping"; verified afterwards:
  no bitcoind process running. Demo datadir left in /tmp for inspection.

## Phase 1 verdict
All five Phase 1 items from the commission are now DONE with recorded evidence:
1. ✅ Repository inspected (Step 1)
2. ✅ Architecture + chain-parameter files identified (Step 1)
3. ✅ Built from the repo's documented commands, pinned at v32.0 (Step 2)
4. ✅ Existing automated tests run — 827/827 unit cases passed (Step 3)
5. ✅ Regtest node launched, blocks generated, test transaction confirmed (Step 3)

This baseline is UPSTREAM Bitcoin Core v32.0, unmodified (git status clean).
Nothing about it is Treeneesu yet — that is Phase 2 (design) and Phase 3 (code).

## Not done / not claimed
- Functional (Python) test suite: not run (294 scripts; impractical to run all on
  this 2-core VM — can run a selected subset in Phase 3 for changed areas).
- GitHub repo muteebdeva/treeneesu: not updated with Step 2/3 logs yet (his OK needed).
