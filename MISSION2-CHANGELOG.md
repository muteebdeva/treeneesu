# Mission 2 — Change Record (defect/fixture repairs after Patch 2a)

All changes are in the working tree of branch `treeneesu` (HEAD = Patch 1,
`5790ce2`). Nothing is committed or pushed. Production code is untouched in
Mission 2 — every change below is in test files or test data, because every
confirmed failure traced to test fixtures that encode Bitcoin's identity or
parameters, not to defects in Treeneesu's production code. (One genuine
*design* defect was found — in the powLimit parameter choice, not in code —
and is awaiting the owner's decision; see the last section.)

## Method guarantees (per mission rules)
- No test was deleted, skipped, or weakened. Fixture *values* were
  re-encoded or recomputed; assertions are unchanged in strength.
- Every re-encoding is payload-preserving: only chain-identity bytes
  (base58 prefixes, ext-key version bytes, bech32 HRP, address prefixes)
  changed; the underlying keys/hashes/scripts are byte-identical, verified
  by checksum-validated decoding in the transform tooling.
- BIP324 vectors were regenerated with an independent Python implementation
  that first reproduced the original Bitcoin vectors byte-for-byte (control).

## Batch A — identity fixtures (Bitcoin encodings → Treeneesu encodings)
Transform tool: `transform_identity.py` (prefix maps 0→65, 5→22, 128→193;
ext-key 0488B21E→02FE6D4F, 0488ADE4→02FE6D47; bech32 HRP bc→tnsu).
- `src/test/bloom_tests.cpp` — 1 address re-encoded. Also fixed the bip32
  abort cascade that made this suite appear to "hang".
- `src/test/key_tests.cpp` — secret/address strings re-encoded.
- `src/test/data/key_io_valid.json` — 18 main-chain entries re-encoded
  (test/signet/regtest entries untouched).
- `src/test/bip328_tests.cpp` — 3 strings re-encoded.
- `src/test/script_standard_tests.cpp`, `src/test/data/bip341_wallet_vectors.json`
  — addresses re-encoded to `tnsu1…` bech32 (matched code output exactly).
- `src/test/util_tests.cpp` — 4 strings.
- `src/wallet/test/psbt_wallet_tests.cpp` — 1 string.
- `src/wallet/test/walletload_tests.cpp` — 1 xpub + descriptor checksum.
- `src/test/rpc_tests.cpp` — 1 P2SH address + 2 escaped WIF secrets.
- `src/test/bip32_tests.cpp` — 34 xprv/xpub strings in vectors test1–test4
  re-encoded (payloads byte-identical; test5 untouched). Root cause of the
  full-suite hang: Bitcoin-prefixed ext keys decode as *invalid* under
  Treeneesu prefixes, hitting `assert(keydata)` → abort → intermittent
  deadlock in the shared test process. Record: PHASE3-PATCH2A-GATE-FAILURE.md.
- `src/test/descriptor_tests.cpp` — the deep one:
  * `CountXpubs`/`CountUniqueXpubs` helpers counted the literal substring
    "xpub"; rewrote them semantically (decode candidate tokens with
    `DecodeExtPubKey`) so Treeneesu `xpub`-renamed keys are counted.
  * All descriptor strings re-encoded; BIP380 checksums recomputed with a
    Python implementation transcribed from descriptor.cpp (control-verified).
  * Stored compat-descriptor hashes recomputed via a C++ oracle linked
    against the production library; oracle output matched test-computed
    values before any slot was patched.
  * One `addr()` infer expectation (17P7ge…) re-encoded to the
    payload-identical Treeneesu address (TGMKgh…), independently produced
    by both the transform tool and the code under test.
- `src/test/net_peer_connection_tests.cpp` — expected debug-log strings used
  Bitcoin's default port 8333; updated to Treeneesu's 29333 (the abort was
  DebugLogHelper failing to find the expected line).
- `net_peer_eviction_tests` — **no change**: passes standalone; its catalog
  failure was cross-suite contamination in a shared batch process.
- `scriptpubkeyman_tests` — **no change**: same contamination explanation.

## Batch B — parameter fixtures
- `src/test/validation_tests.cpp` — subsidy_limit_test expected total
  2099999997690000 → **4199999995380000** (Treeneesu's designed exact
  issuance under D3: 50 TNSU, 420k halving, 42M cap), with comment.
- `pow_tests` — **OPEN, blocked on owner decision** (see below).

## Batch C — money-range fixtures
- `src/test/data/tx_invalid.json` — exactly 2 entries (surgical 2-line diff):
  BADTX entries whose output totals were Bitcoin's cap + ε
  (2,100,000,000,000,001 and 2,100,000,000,000,256 sats) are valid under
  Treeneesu's 42M cap; raised to 4,200,000,000,000,001 and
  4,200,000,000,000,256 sats, preserving the cap+ε test intent.

## Batch D — BIP324 vectors (network-magic-dependent)
- `src/test/bip324_tests.cpp` — 28 lines: for all 7 packet vectors, the
  magic-dependent outputs (session ID, both garbage terminators, ciphertext
  / ciphertext suffix) regenerated for Treeneesu magic a7 3e 5c 91.
  Generator: `bip324_py.py` + `bip324_driver.py` (independent implementation:
  EllSwift decode, tagged-hash ECDH, HKDF, FSChaCha20, FSChaCha20Poly1305).
  Control run against Bitcoin magic reproduced every stored field
  byte-for-byte, including rekey-crossing packets (idx 673/1024) and ~100 KB
  payloads. Inputs (keys, contents, aad) unchanged.

## Investigations (from M1 audit)
- `src/test/miner_tests.cpp` — three-part fixture repair:
  1. BLOCKINFO's 110 precomputed nonces were PoW solutions for blocks on
     Bitcoin's genesis at Bitcoin's nBits — meaningless on Treeneesu.
     Re-ground all 110 nonces using the test's own block construction
     (instrumented run), then installed as constants; test structure intact.
  2. Template coinbases carry witness data because Treeneesu activates
     segwit at height 0 (D8); the test strips the witness commitment but not
     the witness itself → "unexpected-witness". Added witness clearing next
     to the existing commitment-stripping line.
  3. The suite's scenarios assume Bitcoin mainnet's buried activation
     heights (segwit 481824, CSV 419328, CLTV 388381, DERSIG 363725,
     BIP34 227931 — all inactive at the tested heights ~110–300). Pinned the
     fixture chain to those heights via `-testactivationheight` (the same
     mechanism upstream uses, e.g. txvalidationcache_tests), so miner logic
     is tested under upstream's activation conditions. After (1)–(3) the
     entire suite passes, including all four sub-scenarios.
- `src/test/denialofservice_tests.cpp` — stale_tip_peer_management: the
  fake-clock advance `3*spacing + 1s` (451s at Treeneesu's 150s spacing) no
  longer exceeds net_processing's 10-minute STALE_CHECK_INTERVAL, so the
  stale-tip re-check never ran. Delta now `3*spacing + 11min`, with comment.
  Production code unchanged and correct.

## OPEN — genuine design defect requiring owner decision (powLimit)
`pow_tests` failures exposed a real defect in design parameter D4:
Treeneesu's powLimit (bits 0x1e0fffff, target ≈ 2^236) violates the retarget
overflow invariant powLimit < 2^256 / (4 × nPowTargetTimespan) ≈ 2^233.8.
At the first retarget (block 8064), `CalculateNextWorkRequired` multiplies
the target by the elapsed timespan in 256-bit arithmetic and overflows even
for on-schedule blocks. Options presented to the owner (2026-10-23):
(1) bits 0x1e01ffff (~8.4M hashes/block, invariant satisfied) — recommended;
(2) bits 0x1d3fffff (~67M hashes/block, more margin);
(3) keep and document (not recommended).
Any change requires a genesis regrind (new nonce/hash, BIP34Hash and
nMinimumChainWork updates, GENESIS-VERIFICATION refresh). pow_tests'
historical-height expectations will be recomputed with an independent
Python difficulty model (control-checked against Bitcoin's expected values)
after the decision.
