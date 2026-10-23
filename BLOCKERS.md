# Treeneesu — Remaining Blockers and Open Items (updated 2026-10-23, completion mission)

## B1. powLimit consensus defect — ✅ CLOSED (2026-10-23)
Owner chose Option A: powLimit bits 0x1e01ffff. Implemented in commit
35f49eb with a genesis regrind (hash
00000091bddca562e9b5a2c98b31e5e5c831ffc015c6fd8853ef18d6df22dfee),
three-way verified (source / independent recomputation / compiled
daemon). pow_tests fully green; full suite 152/152.

## B2. Patch 2b / 2c scope — OWNER DECISION (unchanged)
Replacing the regtest class with a Treeneesu test chain (2b) and deleting
upstream testnet/testnet4/signet classes (2c) remain undone by design
freeze. The retained upstream chain classes still carry Bitcoin
parameters; nothing in the Treeneesu main network depends on them, but a
future public testnet should be built as 2b rather than reusing them.
Consequence to know: the binary still answers -chain=test etc. with
Bitcoin-parameter chains. This is a scope limitation, not a defect in
the Treeneesu main chain.

## B3. Clean-checkout rebuild — ✅ CLOSED (2026-10-23)
Fresh build-final tree compiled from committed source (exit 0) and ran
the full suite: 152/152 suites, exit 0 (logs/final-fullrun/full2.log).
Note: "clean checkout" here means a fresh build directory on this
machine; the build needs Boost + SQLite3 headers (see README for the
sysroot note).

## B4. Sanitizers — ✅ ASan CLOSED; UBSan OPEN (disclosed, not run)
ASan build exit 0; 12-suite repaired/key subset all exit 0 with zero
sanitizer reports (logs/asan-subset.log). UBSan was NOT run: three full
builds saturated the 2-core VM all session. Recommended before any
public-network step.

## B5. Commit / push — ✅ CLOSED for this mission (2026-10-23)
Owner authorized the push ("do fast and push all in github", "whenever
this will complete... push this all"). Local commits 5790ce2, eca8485,
35f49eb, 03727d8; GitHub main carries the full project tree (import
commit 32451353791d… plus the completion-mission delta commit); history
preserved as history/treeneesu-commits.bundle. No tag and no GitHub
Release were created — release publication remains a separate decision.

## B6. Cosmetic rebrand remainder — optional, non-blocking (unchanged)
Startup banner prints "Bitcoin Core version v32.0.0"; binaries are named
bitcoind / bitcoin-cli / test_bitcoin. The runtime identity (user agent
/Treeneesu:32.0.0/, data dir .treeneesu, config treeneesu.conf) is
Treeneesu. Renaming the banner/binaries is cosmetic and was deliberately
deferred to avoid build-system churn.

## B7. Public testnet / mainnet — HUMAN APPROVAL GATE (unchanged)
Nothing public has been launched. TESTNET-PLAN.md and
MAINNET-READINESS-GATES.md describe the path; Gate items (notably UBSan,
external review, seed infrastructure, and the 2b test chain) must close
first. Treeneesu coins have no monetary value; do not treat this
codebase as production-ready for real funds on the strength of a passing
test suite.

## B8. Environment note (new, informational)
The build VM can be replaced without warning (observed 2026-10-23
17:58), wiping system packages and /tmp. Durable state lives in the
workspace; build dependencies are mirrored in ~/workspace/sysroot.
Anyone reproducing the build elsewhere should install the documented
apt packages normally.
