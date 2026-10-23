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
- [ ] All unit + functional tests pass on the exact release tree.
- [ ] Sanitizer runs (ASan/UBSan) clean on the test suite and a node soak.

## Gate 2 — Independent review
- [ ] A reviewer who did not write the changes reads the full production
      diff (it is deliberately tiny: 3 files) and signs off in writing.
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

**Current status: Gate 1 is open (powLimit). All other gates unstarted.**
Recommendation on present evidence: keep Treeneesu a local/test network.
