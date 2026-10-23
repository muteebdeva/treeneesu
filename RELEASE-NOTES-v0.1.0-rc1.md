# Treeneesu v0.1.0-rc1 — release notes (DRAFT, not published)

**This is a release *candidate* prepared for owner review. It is not
published, tagged, or pushed anywhere, and the software is not ready for
public networks or any real value.**

## What Treeneesu is
An independent proof-of-work cryptocurrency derived from Bitcoin Core v32.0,
created as a learning project. Own genesis block, network magic, ports,
address formats (`tnsu1…`, `T…`), and monetary policy: 42M TNSU cap,
50 TNSU subsidy, 420,000-block halvings, 150-second target spacing,
BIP324 encrypted transport bound to the new network magic.

## What was verified for this candidate
- Full unit suite: 151 of 152 suites pass (see Known issues).
- Two-node main-chain demo: peering without seeds, 109 real-PoW blocks,
  sync, a confirmed 25 TNSU payment, exact balances, restart recovery.
- Functional tests: help, net RPC, basic wallet, segwit, blockchain RPC,
  and the BIP324 v2 transport test all pass.
- Independent-implementation verification of the BIP324 test vectors,
  descriptor checksums/hashes, and BIP32 vectors (control runs against
  Bitcoin's known-good data before trusting Treeneesu outputs).

## Known issues (must-read)
1. **powLimit defect (consensus, blocking):** the easiest-target parameter
   is too large for the retarget arithmetic; difficulty would miscompute
   at block 8064. A fix (smaller powLimit + new genesis) requires a
   parameter decision and re-verification. Do not run a persistent network
   until this is fixed. (BLOCKERS.md, B1.)
2. **Developer chains not yet replaced:** regtest is still Bitcoin's;
   testnet/testnet4/signet parameter sets still exist. Main chain is
   unaffected. (B2.)
3. **Security posture:** mining difficulty is intentionally tiny — the
   chain can be rewritten by one ordinary computer. Treeneesu demonstrates
   mechanics; it does not provide meaningful settlement security. It has
   no monetary value. Do not buy, sell, or accept TNSU as payment.
4. Cosmetic: binaries and startup banner still carry Bitcoin names.

## License
Derived from Bitcoin Core (MIT). Upstream copyright and license notices are
preserved throughout the tree.
