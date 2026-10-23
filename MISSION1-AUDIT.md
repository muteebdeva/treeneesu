# Mission 1 — Complete Test Audit (Patch 2a tree, 2026-10-23)

Scope: Bitcoin Core v32.0 + Patch 1 (committed 5790ce2) + Patch 2a (uncommitted)
+ bip32 fixture regeneration (uncommitted). Method: full run (10-min cap), then
133 remaining suites in 9 batches (240 s cap each), then 29 mop-up suites
individually (180 s cap). Logs: logs/phase3-patch2a-unittests-2.log,
logs/patch2a-catalog/{batch_*,mopup_*}.log + summary.txt + mopup_summary.txt.

## Inventory result
- **152 suites total. ~125 pass completely.**
- Suites with failures/aborts: **21** (incl. bip32, already fixed and verified
  514/514). Every failure group is classified below.
- **No genuine implementation defect has been found yet.** All confirmed causes
  are (a) fixtures embedding Bitcoin mainnet identity (prefixes/HRP/magic),
  (b) fixtures encoding Bitcoin parameters (supply cap, difficulty), or
  (c) knock-on effects of (a)/(b). Three items remain under investigation
  (miner, net_peer, denialofservice) before classification.

## Classification by origin

### A. Mainnet-identity fixtures (re-encode same payloads under Treeneesu identity)
| Suite | Evidence | Fix |
|---|---|---|
| bip32_tests | FIXED: xprv/xpub version bytes; invalid key → assert(keydata) key.cpp:185 (gdb stack) → SIGABRT; abort-path deadlock = the "hang" | done (34 strings) |
| bloom_tests | DecodeSecret("5Kg1…") mainnet WIF → invalid key → GetPubKey assert → SIGABRT ×2; hang in merkle_block_1 is abort-aftermath | WIF re-encode (same key bytes); expected bloom bytes unchanged |
| key_tests | mainnet WIF strings ("5K…"/"L…") → IsValid fails ×8, SIGABRT ×2 (same assert path) | WIF re-encode |
| key_io_tests | 64 fails: mainnet entries of key_io_valid.json (addresses, WIF, ext keys, bc1) | regenerate "main" entries only; test/regtest entries unchanged |
| descriptor_tests | 4F + 2 aborts (out_of_range after failed parse): xpubs + WIF (L4rK…) in descriptor strings | re-encode ext keys/WIFs inside descriptor test data |
| bip328_tests | 3F "Synthetic xpub mismatch" (BIP352 vectors carry mainnet xpub encoding) | version-swap synthetic xpubs |
| script_standard_tests | 8F: expected bech32 strings bc1… vs produced tnsu1… (payload identical, only HRP+checksum differ — verified character-by-character in log) | update expected strings / bip341 vectors' bip350Address fields |
| util_tests | 6F message_verify: mainnet addresses 3B5f…/1Kqb… change error-code path | re-encode same payloads (prefix 22 / 65) |
| rpc_tests | rpc_rawsign aborts: throw "Invalid Bitcoin address: 3HqAe9…" (mainnet P2SH) | re-encode address (prefix 22) |
| walletload_tests | wallet_load_descriptors LOAD_FAIL: stored descriptors contain mainnet xpubs | re-encode ext keys in the test's wallet descriptor data |
| psbt_wallet_tests | psbt_updater_test SIGABRT (descriptor/ext-key family, to confirm at fix time) | re-encode fixture keys |
| scriptpubkeyman_tests | DescriptorScriptPubKeyManTests SIGABRT (same family, to confirm) | re-encode fixture keys |

### B. Bitcoin-parameter fixtures (recompute expectations from Treeneesu parameters)
| Suite | Evidence | Fix |
|---|---|---|
| validation_tests | subsidy_limit_test: expected 2099999997690000 (BTC schedule), got 4199999995380000 = Treeneesu's designed total exactly (41,999,999.9538 TNSU) — code is CORRECT, expectation is Bitcoin's | update constant to Treeneesu schedule sum |
| pow_tests | 4F: expected nBits computed for 2016-block/600 s retarget; Treeneesu is 8064/150 s. ChainParams_MAIN_sanity bound is Bitcoin's powLimit range | recompute expected nBits independently (Python difficulty model, control-checked vs Bitcoin values); adjust sanity bound to Treeneesu targ_max |
| transaction_tests | 146F, all in tx_invalid with third field "BADTX": entries whose invalidity is the 21M money-range cap. Under MAX_MONEY=42M the tx validates → test falls through to ParseScriptFlags("BADTX") → "unknown flag" + "No error". (Mechanism read from transaction_tests.cpp:56-112 + entry dump; per-entry amounts to be decoded and confirmed at fix time.) | for each confirmed money-range entry, raise the offending amount above 42M so the entry still tests money-range rejection; document each |

### C. Chain-identity protocol vectors
| Suite | Evidence | Fix |
|---|---|---|
| bip324_tests | 280F packet_test_vectors. Source comment (bip324_tests.cpp:167): "BIP324 key derivation uses network magic in the HKDF process… vectors are written for [mainnet]" | Independent Python BIP324 implementation; FIRST reproduce all Bitcoin-magic vectors exactly (control), THEN generate Treeneesu-magic vectors and update test data |

### D. Under investigation (do not classify yet)
| Suite | Evidence | Next step |
|---|---|---|
| miner_tests | CreateNewBlock_validity: submitBlock critical check failed (regtest-based fixture; 2a did not change regtest) | rerun isolated, capture failing subcase + rejection reason |
| net_peer_connection_tests / net_peer_eviction_tests | 1F + SIGABRT each | gdb stack traces per case |
| denialofservice_tests | stale_tip_peer_management: 1 check (GetTryNewOutboundPeer) | rerun ×3 isolated: flaky vs deterministic |

### E. Test-harness artifact (documented, not a product bug)
When a test case aborts via assert → SIGABRT, Boost.Test's signal handling
intermittently deadlocks the process (single thread, futex_do_wait, 0 CPU) —
observed in full-suite bip32 run (29 min), bip324→bloom run, batches 3/4/9.
Individually-run aborting cases exit cleanly with code 201. Consequence:
full-suite runs wedge at the first aborting suite; per-suite runs are the
reliable enumeration method. Once no case aborts, this artifact disappears.

## Repair order
1. Batch A: all of class A (one transformer tool, per-file logs of every substitution).
2. Batch B: class B constants/expectations (independent recomputation for pow).
3. Batch C: transaction_tests BADTX entries (per-entry confirmation first).
4. Batch D: BIP324 vectors (independent implementation + control run).
5. Investigations D to conclusion.
6. Rebuild; full unit suite (10-min cap); functional subset; two-node demo.
