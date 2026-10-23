# Defect → Regression-Test Map

Every defect or audit finding in Treeneesu's history, and the test or
check that now guards against its return. "Guard" means: if the defect
were reintroduced, the named check would fail. Checks that would *not*
catch a reintroduction are not listed as guards — gaps are stated.

| # | Defect / finding | Guard (test or check) | Where it runs |
|---|---|---|---|
| D-1 | **powLimit overflow defect** (original bits 0x1e0fffff violated `powLimit < 2^256/(4·timespan)`; would have broken the first retarget) | `pow_tests/ChainParams_MAIN_sanity` — this exact case caught the defect pre-launch. Expectations were recomputed with an independent Python difficulty model (control-verified against all upstream values) when the fix landed. | Full unit suite; both sanitizer runs |
| D-2 | Same defect, live behaviour | Retarget soak (`retarget-test/submit_and_assert.sh`): 8,070 blocks validated by two fresh daemons; bits asserted at 8063/8064/8070. | Manual/release-gate run (Gate B) |
| D-3 | miner_tests fixture nonces ground for a superseded genesis (stale test data after the D-1 fix) | `miner_tests` itself, after nonce re-grounding with the test's own construction (110/110). Any future genesis change fails this suite loudly instead of silently. | Full unit suite |
| D-4 | 21 Mission-2 test failures (identity-encoded fixtures, BIP324 vectors, descriptor checksums written for Bitcoin parameters) | The repaired suites themselves (`key_io_tests`, `bip324_tests`, `descriptor_tests`, …), repaired payload-preservingly and catalogued in MISSION2-CHANGELOG.md. | Full unit suite; sanitizer subsets |
| D-5 | **F-05 chain-class contamination** (binary could join Bitcoin testnet/testnet4/signet via live seeds + Bitcoin magic) | Code-level: seeds deleted, magic/ports separated (source commit 2ecd619). Test-level: `pow_tests` ChainParams sanity for all classes still passes (parameter consistency), functional subset passes with the framework's updated MAGIC_BYTES. **Gap, stated:** no unit test asserts "vSeeds is empty for all classes" — a future edit could re-add a seed without failing a test. Recommended follow-up: add such an assertion to a chainparams test. | Full unit suite; functional subset |
| D-6 | Supply-rule drift (subsidy/halving/MAX_MONEY inconsistent with the published schedule) | `validation_tests` (contains the total-issuance constant) + the independent Python supply model in AUDIT-REPORT.md addendum 2. Any constant change breaks one against the other. | Full unit suite; audit procedure |
| D-7 | min-chain-work tool bug (`getblockhash` non-JSON response crashed the derivation script) | Found by the tool's own live test (2026-10-23); fixed with a raw-response mode; output verified by hand (18 × 0x800040 = 0x9000480). **Gap:** the tool has no automated test; its guard is the documented live procedure in RELEASE-PROCESS.md §3. | Release procedure |
| D-8 | Genesis divergence (source constants vs. what the daemon computes) | Three-way check: genesis asserts in `chainparams.cpp` (compile/startup), `genesis/GENESIS-VERIFICATION.md` recomputation, and the CI workflow's genesis smoke step comparing `getblockhash 0` to the published hash. | Every build; CI |
| D-9 | F-01 (difficulty trivially low) | **Not a regression-testable defect** — it is a design property. Its guard is documentary: THREAT-MODEL.md §5 + F01-POW-ANALYSIS.md must be cited by any future parameter change; a change to `powLimit` in the production diff without a successor-chain review is a process failure, not a test failure. | Review process |
| D-10 | F-06 (unregistered key prefixes / HRP) | `key_io_tests` + `descriptor_tests` encode/decode Treeneesu prefixes and reject foreign ones; the registration status is guarded by F06-PREFIX-DECISION.md (documentation state, not code). | Full unit suite |

## Standing rule illustrated by D-1/D-3

Both times Treeneesu's parameters changed (initial design, then the
powLimit fix), *tests* caught what review did not, and the fixes were
verified by re-deriving expectations independently rather than copying
the code's own outputs. Any future parameter change must follow the
same pattern: independent model first, test expectations second, code
third — in that order.
