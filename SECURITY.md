# Security Policy

## Status of the software

Treeneesu is an **experimental** Bitcoin Core–derived blockchain for
learning and protocol testing. Its coins have no monetary value. It is
**not production software** (see AUDIT-PRODUCTION-READINESS.md and
THREAT-MODEL.md). Do not use it to secure anything of value.

## Reporting a vulnerability

If you find a security problem in the Treeneesu-specific changes (the
5 production files listed in PRODUCTION-DIFF.patch) or in this
repository's tooling:

1. Open a **private** report: use GitHub's "Report a vulnerability"
   (Security Advisories) on the `muteebdeva/treeneesu` repository if
   enabled; otherwise contact the repository owner through GitHub
   direct message. Do not file a public issue for an exploitable flaw.
2. Include: affected commit hash, component, reproduction steps, and
   impact as you understand it.
3. Expect an acknowledgement within 7 days. There is no bounty and no
   SLA — this is a one-maintainer learning project; reports are
   handled in the open after a fix or a 90-day window, whichever
   comes first.

Vulnerabilities in upstream Bitcoin Core itself should be reported to
the Bitcoin Core project under its own security policy; if a report
concerns both, say so and it will be coordinated upstream-first.

## Known, accepted limitations (not vulnerabilities to report)

These are documented design properties, listed so reporters do not
waste effort (reports that add *new* information about them are still
welcome):

- Proof-of-work difficulty is trivially low (~2²³ hashes/block);
  history rewriting is cheap. See THREAT-MODEL.md §5.
- `nMinimumChainWork` equals the genesis block's work pre-launch
  (THREAT-MODEL.md §6).
- Extended-key prefixes and the bech32 HRP are unregistered
  (F06-PREFIX-DECISION.md).
- Auxiliary chain classes carry inherited upstream parameters with
  Treeneesu-isolated network identity (BLOCKERS.md B2/F-05).
