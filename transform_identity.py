#!/usr/bin/env python3
"""Re-encode Bitcoin MAINNET identity strings as Treeneesu strings, payload-preserving.

Handles:
 - Base58Check 1-byte prefixes: P2PKH 0->65, P2SH 5->22, WIF 128->193
 - Base58Check ext keys: xpub 0488B21E->02FE6D4F, xprv 0488ADE4->02FE6D47
 - Bech32/bech32m HRP: bc->tnsu (witness version + program bytes unchanged)
Testnet/regtest strings never match the maps and are left untouched.
Every transformation asserts: payload after the version/HRP is byte-identical,
and a same-identity re-encode control reproduces the input exactly.
Usage: transform_identity.py <file> [--bech32]  (prints a mapping table)
"""
import hashlib, re, sys

B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BYTE_MAP = {0: 65, 5: 22, 128: 193}
EXT_MAP = {bytes.fromhex("0488B21E"): bytes.fromhex("02FE6D4F"),
           bytes.fromhex("0488ADE4"): bytes.fromhex("02FE6D47")}

def b58d(s):
    n = 0
    for c in s: n = n * 58 + B58.index(c)
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    raw = b"\x00" * (len(s) - len(s.lstrip("1"))) + raw
    p, ck = raw[:-4], raw[-4:]
    assert hashlib.sha256(hashlib.sha256(p).digest()).digest()[:4] == ck
    return p

def b58e(p):
    ck = hashlib.sha256(hashlib.sha256(p).digest()).digest()[:4]
    raw = p + ck
    n = int.from_bytes(raw, "big"); out = ""
    while n: n, r = divmod(n, 58); out = B58[r] + out
    return "1" * (len(raw) - len(raw.lstrip(b"\x00"))) + out

def xform_b58(s):
    try: p = b58d(s)
    except Exception: return None
    if len(p) == 78 and p[:4] in EXT_MAP:
        q = EXT_MAP[p[:4]] + p[4:]
    elif len(p) in (21, 33, 34) and p[0] in BYTE_MAP:
        q = bytes([BYTE_MAP[p[0]]]) + p[1:]
    else:
        return None
    assert b58e(p) == s
    n = b58e(q)
    assert b58d(n)[4:] == p[4:] or b58d(n)[1:] == p[1:]
    return n

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
def bech32_polymod(values):
    chk = 1; GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    for v in values:
        b = chk >> 25; chk = (chk & 0x1ffffff) << 5 ^ v
        for i in range(5):
            if (b >> i) & 1: chk ^= GEN[i]
    return chk
def hrp_expand(hrp): return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]
def bech32_decode(s):
    s = s.lower()
    pos = s.rfind("1"); hrp, data = s[:pos], [CHARSET.index(c) for c in s[pos + 1:]]
    const = bech32_polymod(hrp_expand(hrp) + data)
    assert const in (1, 0x2bc830a3), "bad bech32 checksum"
    return hrp, data[:-6], (1 if const == 1 else 0x2bc830a3)
def bech32_encode(hrp, data, const):
    pm = bech32_polymod(hrp_expand(hrp) + data + [0] * 6) ^ const
    cs = [(pm >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + "1" + "".join(CHARSET[d] for d in data + cs)
def xform_bech32(s):
    try: hrp, data, const = bech32_decode(s)
    except Exception: return None
    if hrp != "bc": return None
    assert bech32_encode(hrp, data, const) == s.lower()
    return bech32_encode("tnsu", data, const)

path = sys.argv[1]
do_bech = "--bech32" in sys.argv
text = open(path).read()
mapping = {}
def sub_b58(m):
    s = m.group(0); n = xform_b58(s.strip('"'))
    if n is None: return s
    mapping[s.strip('"')] = n
    return '"' + n + '"' if s.startswith('"') else n
text = re.sub(r'"[1-9A-HJ-NP-Za-km-z]{26,120}"', sub_b58, text)
if do_bech:
    def sub_b32(m):
        s = m.group(0); n = xform_bech32(s)
        if n is None: return s
        mapping[s] = n; return n
    text = re.sub(r'bc1[ac-hj-np-z02-9]{11,110}', sub_b32, text)
if "--substrings" in sys.argv:
    def sub_tok(m):
        s = m.group(0); n = xform_b58(s)
        if n is None: return s
        mapping[s] = n; return n
    text = re.sub(r'(?:xpub|xprv)[1-9A-HJ-NP-Za-km-z]{107}', sub_tok, text)
    text = re.sub(r'(?<![1-9A-HJ-NP-Za-km-z])[5KL][1-9A-HJ-NP-Za-km-z]{50,51}(?![1-9A-HJ-NP-Za-km-z])', sub_tok, text)
open(path, "w").write(text)
for k, v in sorted(mapping.items()): print(f"{k} -> {v}")
print(f"TOTAL {len(mapping)} substitutions in {path}")
