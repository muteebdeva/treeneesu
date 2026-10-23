# Remaining blockers — Treeneesu release candidate

Updated 2026-10-23. Nothing on this list is hidden in the release notes;
the RC must not ship past a blocker without the noted approval.

## B1. powLimit consensus defect — OWNER DECISION REQUIRED
powLimit bits `0x1e0fffff` (target ≈ 2^236) violates the retarget overflow
invariant (must be < ≈2^233.8); the difficulty retarget at block 8064 would
miscompute. Options presented 2026-10-23: (1) `0x1e01ffff` — recommended;
(2) `0x1d3fffff`; (3) keep and document (not recommended).
**Unblocks:** genesis regrind, BIP34Hash/nMinimumChainWork update,
pow_tests recomputation, clean rebuild, RC.
**Severity:** fatal for any chain that must live past block 8064.

## B2. Patch 2b / 2c scope — OWNER APPROVAL REQUIRED
Regtest is still Bitcoin's; testnet/testnet4/signet parameter sets still
exist with Bitcoin seeds. Mission scope froze 2b/2c. A fully independent
release should replace regtest with Treeneesu parameters and delete or
replace the other chains.

## B3. Clean-checkout rebuild — pending B1
From-scratch clone→build→test verification of the exact RC tree. Deferred
so it is done once, on the final parameters.

## B4. AddressSanitizer run — in progress
ASan build underway (logs/asan-build.log); subset run + short two-node
session under ASan still to be executed and recorded.

## B5. Commit / tag / push — OWNER APPROVAL REQUIRED (standing rule)
Status update 2026-10-23: on the owner's one-word instruction "Push", the
source changes were committed locally (branch `treeneesu`, commit
`eca8485`, on top of Patch 1 `5790ce2`) and the documentation package
(26 files) was published to the private repo `muteebdeva/treeneesu` via the
GitHub API. No tag, no release, and no source-tree push were made (the
source repo's only remote is upstream bitcoin/bitcoin). Any further
commit/push requires fresh explicit approval. Note: the BLOCKERS.md copy
on GitHub predates this status update and still says "uncommitted" —
refresh it on the next approved push.

## B6. Cosmetic rebrand remainder — optional, non-blocking
Binary names (`bitcoind`, `bitcoin-cli`), the startup banner, and Qt GUI
strings still say Bitcoin. No functional impact; deferred by design.

## B7. Public testnet / mainnet — HUMAN APPROVAL GATE
See TESTNET-PLAN.md and MAINNET-READINESS-GATES.md. No public network, no
seed infrastructure, no spending, no announcements without the gate.
