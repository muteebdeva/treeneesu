#!/usr/bin/env python3
"""Regenerate BIP32 test vectors for Treeneesu extended-key prefixes.

Transforms ONLY the strings inside TestVector test1..test4 blocks of
src/test/bip32_tests.cpp. Method: Base58Check-decode each upstream
xpub (0488B21E) / xprv (0488ADE4) string, keep the 74 payload bytes after
the version byte-identical, swap in Treeneesu version bytes
(EXT_PUBLIC 02FE6D4F / EXT_SECRET 02FE6D47), re-encode.
TEST5 block is deliberately excluded: its strings must keep FAILING to
decode, and some strings appear in both test1 and TEST5, so replacement
is span-aware, never global.
Control: re-encoding with the ORIGINAL version must reproduce the
original string exactly, or the script aborts.
"""
import hashlib, re, sys

SRC = "/home/hatch/workspace/treeneesu/bitcoin-core/src/test/bip32_tests.cpp"
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
OLD_PUB, OLD_SEC = bytes.fromhex("0488B21E"), bytes.fromhex("0488ADE4")
NEW_PUB, NEW_SEC = bytes.fromhex("02FE6D4F"), bytes.fromhex("02FE6D47")

def b58check_decode(s):
    n = 0
    for c in s:
        n = n * 58 + B58.index(c)
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    pad = len(s) - len(s.lstrip("1"))
    raw = b"\x00" * pad + raw
    payload, ck = raw[:-4], raw[-4:]
    assert hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4] == ck, f"bad checksum {s}"
    return payload

def b58check_encode(payload):
    ck = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    raw = payload + ck
    n = int.from_bytes(raw, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = B58[r] + out
    pad = len(raw) - len(raw.lstrip(b"\x00"))
    return "1" * pad + out

text = open(SRC).read()

# testN blocks run from 'TestVector testN =' to the next declaration;
# TEST5's start terminates test4's block. (Vectors are built by chained
# operator() calls, not brace initialisers.)
markers = []
for name in ["test1", "test2", "test3", "test4"]:
    m = re.search(r"TestVector " + name + r" =", text)
    assert m, name
    markers.append(m.start())
m5 = re.search(r"const std::vector<std::string> TEST5", text)
assert m5
markers.append(m5.start())
spans = [(markers[i], markers[i + 1]) for i in range(4)]
for n, (a, b) in zip(["test1", "test2", "test3", "test4"], spans):
    print(f"{n}: block chars {a}..{b}")

def in_span(pos):
    return any(a <= pos <= b for a, b in spans)

mapping, changed, skipped = {}, 0, 0
def repl(m):
    global changed, skipped
    s = m.group(1)
    if not in_span(m.start()):
        skipped += 1
        return m.group(0)
    payload = b58check_decode(s)
    assert len(payload) == 78, (s, len(payload))
    ver, body = payload[:4], payload[4:]
    assert b58check_encode(payload) == s, f"control failed {s}"
    if ver == OLD_PUB: new = b58check_encode(NEW_PUB + body)
    elif ver == OLD_SEC: new = b58check_encode(NEW_SEC + body)
    else: raise AssertionError(f"unexpected version {ver.hex()} in {s}")
    # verify: new decodes to Treeneesu version + identical body
    p2 = b58check_decode(new)
    assert p2[4:] == body and p2[:4] in (NEW_PUB, NEW_SEC)
    assert new != s
    mapping[s] = new
    changed += 1
    return '"' + new + '"'

new_text = re.sub(r'"(xpub[1-9A-HJ-NP-Za-km-z]+|xprv[1-9A-HJ-NP-Za-km-z]+)"', repl, text)
print(f"transformed occurrences: {changed}, skipped (outside test1-4, e.g. TEST5): {skipped}, unique: {len(mapping)}")
open(SRC, "w").write(new_text)
for old, new in sorted(mapping.items()):
    print(f"{old} -> {new}")
print("WROTE", SRC)
