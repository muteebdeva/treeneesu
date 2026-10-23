# Phase 3 — Patch 1: datadir, config file, user-agent (NON-CONSENSUS)
Branch: `treeneesu` (from v32.0 tag 465dde27) · Commit: **5790ce2** · Date: 2026-10-23

## Diff summary (2 files, +10/−10)
- `src/common/args.cpp`: `BITCOIN_CONF_FILENAME` value `bitcoin.conf` → `treeneesu.conf`
  (constant name kept, minimal diff); `GetDefaultDataDir()`: `.bitcoin` → `.treeneesu`,
  `Bitcoin` → `Treeneesu` (Windows legacy + new, macOS path), comments updated.
- `src/clientversion.cpp`: `UA_NAME("Satoshi")` → `UA_NAME("Treeneesu")`.

## Verification (all real, logged)
- Incremental rebuild: 22 s, REBUILD_EXIT:0 (`logs/phase3-patch1-build.log`).
- Unit tests: full suite re-run — **827/827 cases passed** (826 clean + 1 with
  warnings, 0 failed), 26,664,922/26,664,922 assertions, TEST_EXIT:0, 1m40s
  (`logs/phase3-patch1-unittests.log`). Identical pass profile to the Phase 1
  baseline. (Assertion total differs slightly from baseline — normal run-to-run
  variance in timed/randomized suites; failure count is what matters: 0.)
  Operator note: the first invocation in this step exited 200 instantly because
  I passed an invalid Boost flag (`--report_level=summary`); not a code failure.
  Re-run used the exact Phase 1 invocation.
- Live check (sandboxed HOME=/tmp/treeneesu-fakehome, -regtest):
  - `getnetworkinfo` → **subversion "/Treeneesu:32.0.0/"** ✅
  - Created **~/.treeneesu**; `.bitcoin` was NOT created ✅
  - debug.log: `Config file: …/.treeneesu/treeneesu.conf (not found, skipping)` ✅
  - Node stopped cleanly; no bitcoind process left.
- Known remaining branding: startup banner still prints "Bitcoin Core version
  v32.0.0" (package-name string) — belongs to the later binary/package-rename
  patch, deliberately out of Patch 1 scope.

## Risk
None to consensus or network validity. Behaviour change is limited to data
location, config filename, and peer-visible user-agent name.
