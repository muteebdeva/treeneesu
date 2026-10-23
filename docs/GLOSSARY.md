# Glossary

- **Block** — a batch of transactions plus a header (previous-block hash,
  merkle root, timestamp, difficulty bits, nonce) sealed by proof-of-work.
- **Genesis block** — block 0, hardcoded in the software; defines the chain.
- **Nonce** — the number varied during mining until the block hash meets the
  target.
- **Target / powLimit** — the maximum allowed block hash value; lower target
  = harder mining. `powLimit` is the easiest (largest) target, used at the
  start of a chain.
- **Difficulty retarget** — every 8,064 blocks (Treeneesu), the target is
  scaled by actual-vs-expected elapsed time to hold spacing near 150 s.
- **Halving** — every 420,000 blocks the block subsidy halves; this schedule
  is what creates the 42M cap.
- **MAX_MONEY** — the largest valid amount of TNSU in any single check
  (42,000,000 coins), enforced by `MoneyRange`.
- **Network magic** — 4 bytes at the start of every P2P message identifying
  the chain (`a7 3e 5c 91` for Treeneesu); nodes ignore foreign magic.
- **Base58Check / bech32** — address encodings. Changing their prefixes/HRP
  changes address strings without changing keys.
- **Extended key (xpub/xprv)** — a parent key string from which wallet keys
  are derived; its version bytes are chain-specific in Treeneesu.
- **BIP324** — the encrypted v2 P2P transport; its session keys are derived
  (via HKDF) from an EllSwift ECDH exchange plus the network magic.
- **Descriptor** — a string describing how a wallet derives addresses from
  keys; includes a BIP380 checksum.
- **Fixture (test)** — precomputed inputs/expected outputs inside a test;
  often chain-specific even when the code under test is not.
- **Control run** — running a new tool/implementation against known-good
  data (e.g., Bitcoin's vectors) before trusting its new outputs.
- **Regtest** — a private, instant-mining developer chain; Treeneesu's is
  still Bitcoin's until Patch 2b.
- **Eclipse attack** — isolating a node by controlling all its peers;
  relevant because Treeneesu has no seed nodes yet.
