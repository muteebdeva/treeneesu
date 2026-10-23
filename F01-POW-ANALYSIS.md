# F-01 — Proof-of-Work Security: Full Analysis & Successor-Chain Proposal

Companion to THREAT-MODEL.md §5. This document records the analysis
the audit's F-01 demanded, the options considered, and the decision.
No consensus parameter of the existing chain was changed as a result —
deliberately, for the reasons in §3.

## 1. Where the configuration lives

- `src/kernel/chainparams.cpp` (CMainParams): `powLimit =
  0x000001ffff00…00` (bits 0x1e01ffff), `nPowTargetTimespan = 14 days`,
  `nPowTargetSpacing = 150 s`, retarget period 8,064 blocks,
  `fPowAllowMinDifficultyBlocks = false`, `fPowNoRetargeting = false`.
- The retarget algorithm itself is upstream `src/pow.cpp`, unmodified.
- Consequence: expected hashes per block ≈ 2²³; difficulty (Bitcoin's
  scale) = 0.0019531, confirmed live from `getblockchaininfo` during
  the audit.

## 2. Attack cost table (measured hardware class: this VM, SHA-NI CPU)

| Attack | Work required | Wall-clock on 1 core (~5 MH/s) |
|---|---|---|
| Forge 1 block | ~2²³ hashes | ~2 s |
| Rewrite 6 confirmations | ~2^25.6 | ~10 s |
| Rewrite 1 day (576 blocks) | ~2^32.2 | ~15 min |
| Rewrite from genesis to exceed `nMinimumChainWork` | 1 block | ~2 s |

With even one GPU (≥500 MH/s) every row drops by ~100×. There is no
honest-hashpower base to compare against: outside demonstrations, the
chain's hashrate is zero, so an attacker's share q ≈ 1 and the
whitepaper success probability (q/p)^z ≈ 1 at any depth z
(THREAT-MODEL.md §5.3).

## 3. Options considered

**Option 1 — Raise difficulty in place (change powLimit, keep
genesis).** Impossible as stated: the genesis block's own bits must be
≤ powLimit and its hash must satisfy its target. A harder powLimit
invalidates the existing genesis; a "kept" genesis with a harder
limit is rejected by the node's own sanity checks (`pow_tests`
ChainParams sanity exists precisely to catch such inconsistencies).

**Option 2 — New genesis at higher difficulty, same parameters
otherwise (a new chain).** Technically straightforward (grind a new
genesis, update asserts/fixtures, re-run the whole verification
programme — the project has done this exact dance once, for the
powLimit fix, commit 35f49eb). Measured cost of the grind itself,
by target bits (at ~5 MH/s single-core):
- bits 0x1d00ffff (Bitcoin's genesis difficulty, ~2³²): ~15 min.
- bits 0x1c0fffff (~2³⁶): ~4 hours.
- bits 0x1b0fffff (~2⁴⁰): ~2.5 days.
But the result **is not more secure in any way that matters**: with no
independent miners, the sole miner and the attacker are the same
person with the same laptop. Worse, chain *startup* breaks: if the
initial difficulty is set for a hashrate that doesn't exist, blocks
arrive slower than 150 s and the retarget needs whole 8,064-block
periods (each slower than the last one's target window in wall time)
to ease down by at most 4× per period — a chain can be stillborn.
This is the failure mode the audit brief itself warns about.

**Option 3 — Keep the chain as an experimental chain; define the
successor-chain preconditions (CHOSEN).** The current difficulty is
correct *for the chain's documented purpose* (fast, cheap blocks for
protocol experimentation, full retarget dynamics at the boundary).
Security for value is declared out of scope in the threat model, the
README, and the audit — consistently, not as an excuse.
A value-bearing successor requires, as *preconditions before its
genesis is ground*: (a) committed independent mining hashpower from
≥3 operators exceeding a stated threshold for ≥30 days on a rehearsal
chain; (b) genesis difficulty set from that measured hashpower so the
150 s interval holds at launch; (c) `nMinimumChainWork` policy per
THREAT-MODEL.md §6; (d) bootstrap infrastructure (deploy/ package);
(e) a fresh audit. Estimated engineering cost once preconditions
exist: days, because Options 2's procedure is already rehearsed and
documented by this project (genesis grinding tooling in `genesis/`,
parameter-fix playbook in git history).

## 4. Tests added/kept for difficulty behaviour

- `pow_tests` (upstream suite, Treeneesu-repaired expectations)
  covers: retarget at the limit, both clamp directions, the
  8,064-boundary arithmetic, and ChainParams sanity for every chain
  class. These are the regression tests for the original powLimit
  defect (F-12) — the defect was *found* by the sanity case.
- The live boundary behaviour is covered by the F-02 soak
  (`retarget-test/`), whose assertion phase validates every block —
  including the retargeted bits at 8,064 — through real consensus code
  on two fresh nodes.
- Adversarial-timestamp behaviour (future-time limits, median-time-
  past) is upstream code, unmodified, covered by upstream
  `validation_tests`/`miner_tests`; no Treeneesu-specific change means
  no Treeneesu-specific test is owed there. Inventing one would test
  Bitcoin, not Treeneesu.

## 5. Bottom line

F-01 is a true and permanent property of this chain's design point.
The engineering response is honesty plus a rehearsed exit path
(Option 3), not a cosmetic constant change that would destroy the
chain's verified evidence base while purchasing zero security.
Any future claim that a Treeneesu-family chain is production-secure
must be evaluated against §3 Option 3's preconditions — all of them,
with evidence.
