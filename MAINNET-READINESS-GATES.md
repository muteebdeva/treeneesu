# Mission 8b — Mainnet-readiness gates (evaluation framework, NOT a launch plan)

Treeneesu's current main chain exists for local/development use. Moving it
(or any successor chain) toward a real public mainnet would require every
gate below. **The final gate is human: the owner's explicit approval. No
agent step in this project may cross it, and nothing here authorizes
spending, publishing, or deployment.**

## Gate 1 — Consensus correctness
- [ ] powLimit defect fixed and re-verified (clean rebuild, full suite,
      two-node demo, long-run soak past at least one retarget — i.e. a
      private chain mined beyond block 8064 with correct difficulty).
      Status 2026-10-23: defect FIXED (owner chose Option A, bits
      0x1e01ffff, genesis re-ground, three-way verified); clean rebuild,
      full suite (152/152) and two-node demo all re-run green on the
      fixed parameters. The retarget soak is IN PROGRESS: an 8,070-block
      chain is being ground with an independent tool (cross-validated
      against the Python difficulty model and the daemon) and will be
      submitted to two fresh nodes with bits asserted at heights 8063 /
      8064 / 8070 (predicted 0x1e01ffff → 0x1d7fffc0). This box stays
      unchecked until that run lands.
- [x] All unit + functional tests pass on the exact release tree.
      (152/152 unit suites, exit 0; functional subset all passed —
      TEST-SUMMARY.json.)
- [ ] Sanitizer runs (ASan/UBSan) clean on the test suite and a node soak.
      Status 2026-10-23: ASan AND UBSan both clean on the 12-suite
      repaired/key subset (zero reports, all exit 0 — logs/asan-subset.log,
      logs/ubsan-subset.log). Full-suite sanitizer runs and a sanitizer
      node soak have NOT been done; this box stays unchecked.

## Gate 2 — Independent review
- [ ] A reviewer who did not write the changes reads the full production
      diff (it is deliberately tiny: 5 files — src/kernel/chainparams.cpp,
      src/chainparamsbase.cpp, src/common/args.cpp, src/clientversion.cpp,
      src/consensus/amount.h) and signs off in writing.
- [ ] Parameter choices (difficulty, ports, prefixes) checked against
      public registries for collisions one more time.
- [ ] Honest limits documented: at Treeneesu's difficulty, the chain is
      not secure against reorg attacks; "mainnet" would still be a toy.
      If that is unacceptable, the correct decision is *don't launch*.

## Gate 3 — Network survivability
- [ ] Multiple independently operated nodes in different locations.
- [ ] Seed mechanism designed and reviewed (today there are no seeds).
- [ ] Upgrade/rollback procedure rehearsed on the test chain.

## Gate 4 — User safety
- [ ] Wallet backup/restore documentation tested by a non-developer.
- [ ] Public materials contain no investment language, no price, no
      promises; the "no monetary value / learning project" status is
      either still true and stated, or the owner has consciously re-scoped
      the project with legal advice (outside this project's competence).

## Gate 5 — Operations
- [ ] Monitoring: height/peer/log checks someone actually watches.
- [ ] Incident contact and a published halt/restart procedure.
- [ ] Release process: reproducible build instructions verified from a
      clean machine by someone else.

## Gate 6 — Human approval (hard gate)
- [ ] The owner reviews Gates 1–5 evidence and approves launch in explicit
      words. Silence, prior enthusiasm, or "keep going" do not count.

**Current status (2026-10-23, completion phase): Gate 1 is substantially
advanced — powLimit fixed and re-verified, full tests green, ASan+UBSan
clean on the key subset — but remains OPEN on the retarget soak (in
progress) and full-suite sanitizer scope. Gates 2–5 unstarted; Gate 6
(human approval) untouched.**
Recommendation on present evidence: keep Treeneesu a local/test network.
