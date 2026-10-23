# Treeneesu

An independent proof-of-work cryptocurrency built by modifying Bitcoin Core
v32.0 — own genesis block, network magic, ports, address formats, and
monetary policy (42M TNSU cap, 50 TNSU subsidy, 150-second block spacing).
A learning project: the coins have no monetary value, and the deliberately
low mining difficulty means the chain offers no meaningful attack
resistance. This repository holds the project's documentation and records;
the source tree lives in the development workspace (Bitcoin Core fork,
branch `treeneesu`, commits `5790ce2` + `eca8485`).

## Status (2026-10-23)
- Phases 1–3 complete through Patch 2a; full completion mission (audit →
  repairs → verification → docs → release candidate) executed.
- Unit suite: **151/152 suites pass**. Two-node main-chain demo: **passed**
  (109 real-PoW blocks, cross-node sync, confirmed payment, restart
  recovery). Functional subset incl. BIP324 v2 transport: **passed**.
- **One blocking known defect:** powLimit `0x1e0fffff` violates the
  difficulty-retarget overflow invariant — the chain would miscompute
  difficulty at block 8064. Fix (smaller powLimit + genesis regrind) awaits
  the owner's decision. See `BLOCKERS.md`.
- Release candidate notes are a **draft** (`RELEASE-NOTES-v0.1.0-rc1.md`);
  nothing is tagged or published as a release.

## Map of this repo
- `PHASE1-*.md`, `PHASE2-DESIGN.md`, `PHASE3-*.md` — build/design/patch logs
- `genesis/GENESIS-VERIFICATION.md` — genesis grinding + verification record
- `MISSION1-AUDIT.md` — the 152-suite audit and failure classification
- `MISSION2-CHANGELOG.md` — every repair, with rationale and method
- `MISSION4-5-AUDIT-SECURITY.md` — implementation audit + security self-review
- `docs/` — README, architecture, beginner's guide, glossary, verified
  command reference, troubleshooting, runbook, launch checklist
- `TEST-SUMMARY.json` — machine-readable verification results
- `BLOCKERS.md` — what still blocks a release, and whose decision unblocks it
- `TESTNET-PLAN.md`, `MAINNET-READINESS-GATES.md` — plans/gates (not executed)
- `twonode-demo.sh` — the self-checking two-node demo script

MIT-licensed (derived from Bitcoin Core; upstream notices preserved).
