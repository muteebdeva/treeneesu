# Patch 2a — TEST GATE FAILURE REPORT (2026-10-23, interim)
Per Muteeb's order: gate failed → sequence stopped, nothing committed, 2b/2c not started.

## Build: PASSED
BUILD_START 14:16:16 → BUILD_END 14:47:37 IST = **31m 21s**, BUILD_EXIT:0, 0 error lines.
(Near-full rebuild: consensus/amount.h is included across the codebase.)

## Unit tests: FAILED TO COMPLETE (hung) — gate NOT passed
- Full-suite run started 14:47:44. Log stopped advancing inside
  `bip32_tests/bip32_max_depth` (src/test/bip32_tests.cpp:228).
- After ~29 min: process alive but 1 s total CPU, single thread in
  futex_do_wait (userspace lock wait) — a hang, not slow computation. Run killed.
- Isolated re-run (`--run_test=bip32_tests`, 30 s timeout): reproduced.
  * 68 failed checks, ALL of the form EncodeExtKey/DecodeExtKey/EncodeExtPubKey/
    DecodeExtPubKey == upstream vector — the test vectors are Bitcoin
    `xprv`/`xpub` strings; Treeneesu's extended-key prefixes (02FE6D4F/02FE6D47)
    make encode/decode differ and decode of the old strings fail.
  * A SIGABRT was also reported around bip32_has_hardened_derivation in the
    isolated run, and the suite then hung in/after bip32_max_depth. Precise
    abort/hang mechanism NOT yet pinned down — not guessed at here. Leading
    fact: both hanging cases start from DecodeExtKey() of a now-invalid
    upstream string, i.e. they execute on invalid-key objects, a path that
    disappears once vectors are valid Treeneesu encodings.
- Positive evidence from the same run: every suite before bip32 (addrman …
  bech32) constructed CMainParams repeatedly — the Treeneesu genesis asserts
  in the C++ code PASS (otherwise fixture creation would abort everywhere).

## Remediation path (within Patch 2a's approved plan: "fixtures get Treeneesu data")
1. Regenerate bip32 test vectors: decode each upstream string (Base58Check),
   keep the 78-byte payload byte-identical except the 4 version bytes, re-encode
   with Treeneesu prefixes. Same seeds, same derivation paths, same checks —
   coverage preserved exactly. TEST5 ("must fail to decode" strings) stays
   untouched: still invalid under Treeneesu prefixes.
2. Rebuild test_bitcoin only, re-run FULL gate under a 10-minute timeout guard
   (process fix: a hang becomes a bounded, reported failure).
3. Enumerate any further fixture failures (key_io, descriptors, wallet…) and
   fix the same documented way. Document every modification in the 2a commit.
4. If the hang persists with valid vectors, stop again and debug it as its
   own bug — it will not be papered over.
