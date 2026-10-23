# F-06 — Extended-Key Prefixes & Bech32 HRP: Investigation and Decision

**Status: dispositioned (keep + register), 2026-10-23.**

## Current values (src/kernel/chainparams.cpp, CMainParams)

| Item | Value | Human-readable form |
|---|---|---|
| EXT_PUBLIC_KEY | `0x02FE6D4F` | extended keys begin "tnsu…" family prefix (base58) |
| EXT_SECRET_KEY | `0x02FE6D47` | — |
| bech32 HRP | `tnsu` | addresses `tnsu1…` |
| base58 PUBKEY / SCRIPT / SECRET | 65 / 22 / 193 | "T…" / — / — |

## What was checked

- The SLIP-0132 registry ("Registered HD version bytes for BIP-0032",
  SatoshiLabs) is the authoritative allocation list for extended-key
  version bytes. Its published allocations in the 0x02xxxxxx range
  (per the Electrum project's version-bytes reference and SLIP-0132
  summaries) are: `0x0295b43f`/`0x0295b005` (Ypub/Yprv),
  `0x02aa7ed3`/`0x02aa7a99` (Zpub/Zprv), `0x024289ef`/`0x024285b5`
  (Upub/Uprv, testnet), `0x02575483`/`0x02575048` (Vpub/Vprv, testnet).
- Treeneesu's `0x02FE6D4F` / `0x02FE6D47` match **none** of the
  documented allocations surveyed. No collision was found.
- Limit of this check, stated honestly: the survey covered the
  published reference tables, not an exhaustive machine diff of the
  registry file, and neither value is *registered*. "No collision
  found" is not "registered and guaranteed unique".
- SLIP-0173 is the corresponding registry for bech32 HRPs; `tnsu` is
  likewise unregistered there.

## Risk assessment

- An unregistered-but-unique prefix fails safe in practice: software
  that does not know the prefix rejects the key string (checksum and
  version checks upstream are strict — `key_io_tests` and
  `descriptor_tests` exercise Treeneesu's prefixes, including
  wrong-prefix rejection, and pass).
- The realistic harm is *confusion*, not theft: if another project
  later registers or squats `0x02FE6D4F`, extended keys could be
  misinterpreted by multi-chain wallet software. The same seed phrase
  must never secure value on any chain (THREAT-MODEL.md §8.3), which
  bounds the blast radius for Treeneesu's actual (experimental) scope.

## Decision

1. **Keep the current prefixes.** Changing them now would orphan every
   wallet/address artifact produced by the verified demos and testnet,
   in exchange for no demonstrated collision.
2. **Register them.** Prepared registration entries are below; the
   submission itself (pull requests to `satoshilabs/slips`) is an
   external publication action and is the **owner's** to make.
3. Until registration is confirmed, all documentation must keep saying
   **unregistered** — as the code comments already do.

## Prepared registration entries (owner action)

SLIP-0132 table rows (coin: Treeneesu (TNSU), experimental):

```
| 0x02fe6d4f | tnsu… (public)  | BIP32 / P2PKH-or-P2SH | Treeneesu mainnet (experimental) |
| 0x02fe6d47 | tnsu… (private) | BIP32 / P2PKH-or-P2SH | Treeneesu mainnet (experimental) |
```
(Exact base58 lead strings to be computed from the reference
implementation at submission time; do not hand-derive them here.)

SLIP-0173 table row:

```
| tnsu | Treeneesu | BIP-0173 bech32 HRP for mainnet addresses (experimental network) |
```

## Tests

Existing coverage is the regression suite: `key_io_tests`,
`bip32_tests`, `descriptor_tests` (all in the 152-suite full run and
in both sanitizer subsets) encode/decode Treeneesu mainnet extended
keys and reject foreign prefixes. No new test was needed for a
documentation-and-registration disposition; if the prefixes ever
change, those suites are the ones that must be re-derived first.
