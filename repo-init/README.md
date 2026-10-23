# Treeneesu

**Development and testing only.** Treeneesu is an experimental, independent
cryptocurrency being developed from the open-source Bitcoin Core codebase.
It has **no real monetary value**, no public network, no mainnet launch,
and no token sale. Do not use it with real funds.

## Status (2026-10-23)

- **Phase 1 — Baseline:** in progress
  - Step 1 (inspect upstream repository): ✅ done — see
    [PHASE1-STEP1-INSPECTION.md](PHASE1-STEP1-INSPECTION.md)
  - Step 2 (install dependencies, build Bitcoin Core, run tests,
    regtest demo): ⏳ not started — no build or test result is claimed yet
- **Phase 2 — Design:** not started. No consensus changes will be made
  before a written design is reviewed and approved.
- **Phase 3 — Implementation:** not started. The Bitcoin Core source code
  will be added to this repository in this phase, on a dedicated
  Treeneesu branch, with upstream history and license notices preserved.
- **Phase 4 — Independence verification:** not started.

This repository currently contains documentation only, by design.

## Upstream baseline

- Project: Bitcoin Core — https://github.com/bitcoin/bitcoin
- Baseline inspected: `master` @ `152a55397e451fed9c10041bddf01aa6839847d5`
  (version 32.99.0-dev, 2026-10-22). Pinning to the v32.0 release tag is
  under consideration before the build step.
- License: MIT — Copyright (c) 2009–2026 The Bitcoin Core developers.
  Upstream copyright and license notices will be preserved in all derived
  code. This project is not affiliated with Bitcoin Core or its developers.

## Working rules

1. One manageable step at a time; every build/test claim backed by an
   actual recorded command and result.
2. Before any consensus-critical change: explain the risk and show the
   proposed diff first.
3. Small, reviewable patches; automated tests for every
   consensus-critical change.
4. Local/private test networks only (regtest-style). Test coins must
   never be mistakable for real Bitcoin.
5. ₹0 budget — free and open-source tools only. No paid services,
   no private keys or seed phrases in this repository, ever.
