# Beginner's learning guide — how Treeneesu was built, and what each bug taught

This guide explains, in plain language, the important ideas behind the
project and every significant problem that appeared along the way. If you
understand these, you understand most of how a Bitcoin-like chain works.

## The big picture

A cryptocurrency node is a program that (1) keeps a copy of the ledger
(blockchain), (2) checks new blocks against fixed rules, and (3) gossips
with other nodes running the *same* rules. To make a new coin from Bitcoin
Core you mostly change the **rule sheet** (chain parameters) — the engine
stays the same. The rule sheet lives in `src/kernel/chainparams.cpp`.

## Lesson 1 — A genesis block is ground, not written

Every chain starts from a hardcoded first block. To create one you put your
message, timestamp, and reward into a block header and then vary the *nonce*
until the block's hash is small enough (proof-of-work "grinding"). We
verified our grinding program by first reproducing Bitcoin's own genesis
block exactly — always test your tool on a known answer before trusting it
on an unknown one. Treeneesu's genesis: nonce 535382, hash `000008c9…015b6`.

## Lesson 2 — Test fixtures are not the product

After changing the parameters, dozens of Bitcoin's tests failed. Almost
none were real bugs: the tests contained Bitcoin addresses, Bitcoin keys,
and Bitcoin amounts as *expected answers*. Changing the chain's address
prefix (like changing a country's phone code) makes every expected string
wrong while the underlying data is identical. The fix is to re-encode the
same data under the new identity — verifying the payload bytes never change.

The most dramatic example: the full test suite appeared to **hang**. Under a
debugger, the truth came out: a test key encoded for Bitcoin is *invalid*
under Treeneesu's prefixes, the code hit an `assert`, the process aborted —
and the crash handler itself intermittently deadlocked, making an instant
failure look like a hang. Lesson: when a test "hangs", get a stack trace
before believing it.

## Lesson 3 — Some "fixtures" are really the old chain's history

The miner test contains 110 precomputed block nonces — proof-of-work
solutions for blocks built on **Bitcoin's** genesis. On Treeneesu they are
meaningless numbers. We re-ground all 110 with the test's own block
construction. Similarly, the BIP324 encrypted-transport test vectors depend
on the network magic (it's mixed into the key derivation), so we wrote an
independent Python implementation of BIP324 — and only trusted it after it
reproduced Bitcoin's vectors *byte-for-byte* (a "control run").

## Lesson 4 — Defaults hide assumptions

Several tests failed for invisible reasons:
- Expected log text mentioned port **8333** (Bitcoin's). Ours is 29333.
- A denial-of-service test advanced a fake clock by `3 × block spacing + 1s`
  — enough for Bitcoin (1801 s) but not for Treeneesu (451 s), because the
  code re-checks stale tips only every **10 minutes**. The production code
  was right; the test's arithmetic assumed Bitcoin's spacing.
- The miner tests assumed Bitcoin's feature-activation heights (segwit,
  CSV… activate hundreds of thousands of blocks in). Treeneesu activates
  everything at the start, so the fixture pins the old heights *for the
  test chain only*, using the built-in `-testactivationheight` switch.

## Lesson 5 — The one real bug: difficulty arithmetic can overflow

`pow_tests` caught a genuine design mistake. Every 8,064 blocks the network
recalculates difficulty: *new target = old target × (actual time / target
time)*, computed in 256-bit integers. Treeneesu's chosen easiest target
(≈2^236) is so large that multiplying it by the time ratio (up to ≈2^22)
**overflows 256 bits** — the first retarget would produce garbage. A target
must stay below ≈2^233.8 for this chain's retarget period. The fix (a
smaller powLimit + a fresh genesis) changes consensus, so it waits for the
project owner's explicit decision. Moral: parameters interact; the test
suite is what catches it *before* a live network does.

## Lesson 6 — Tools have budgets and names have consequences

- `generatetoaddress`'s `maxtries` is a budget shared by the *whole batch*,
  not per block: at ~1M expected tries per block, a 1M budget mines about
  one block, no error shown. Read return values, not just exit codes.
- Renaming the config file (`bitcoin.conf` → `treeneesu.conf`) silently
  broke Bitcoin's functional test harness, which writes its settings into
  `bitcoin.conf` and then couldn't find its nodes' RPC cookie. A rename is
  never "just cosmetic" until you've searched for every place the old name
  is written or read.

## What "verified" means here

Every claim in this project is backed by something repeatable: a test run
with a saved log, a demo script (`twonode-demo.sh`) that mines real blocks
between two nodes and checks balances to the satoshi, or an
independent-implementation control run. If a number in these docs has no
log behind it, treat it as unverified and ask.
