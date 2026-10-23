#!/usr/bin/env python3
"""Recompute BIP380 descriptor checksums in a file for descriptors whose
body changed (identity re-encoding). Control: every checksummed descriptor
whose body did NOT change must reproduce its existing checksum; the script
aborts if any control fails. Only descriptors containing a Treeneesu-encoded
ext key (ds3... token) or a changed WIF get new checksums.
"""
import re, sys

INPUT_CHARSET = "0123456789()[],'/*abcdefgh@:$%{}IJKLMNOPQRSTUVWXYZ&+-.;<=>?!^_|~ijklmnopqrstuvwxyzABCDEFGH`#\"\\ "
CHECKSUM_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
GEN = [0xf5dee51989, 0xa9fdca3312, 0x1bab10e32d, 0x3706b1677a, 0x644d626ffd]

def polymod(c, val):
    c0 = c >> 35
    c = ((c & 0x7ffffffff) << 5) ^ val
    for i in range(5):
        if (c0 >> i) & 1:
            c ^= GEN[i]
    return c

def descriptor_checksum(desc):
    c = 1; cls = 0; clscount = 0
    for ch in desc:
        pos = INPUT_CHARSET.index(ch)
        c = polymod(c, pos & 31)
        cls = cls * 3 + (pos >> 5)
        clscount += 1
        if clscount == 3:
            c = polymod(c, cls); cls = 0; clscount = 0
    if clscount:
        c = polymod(c, cls)
    for _ in range(8):
        c = polymod(c, 0)
    c ^= 1
    return "".join(CHECKSUM_CHARSET[(c >> (5 * (7 - j))) & 31] for j in range(8))

path = sys.argv[1]
text = open(path).read()
# find descriptor-like strings ending in #xxxxxxxx inside quotes
pat = re.compile(r'"([^"#]{8,})#([a-z0-9]{8})"')
changed, control_ok, control_fail = 0, 0, 0
def repl(m):
    global changed, control_ok, control_fail
    body, old_ck = m.group(1), m.group(2)
    new_ck = descriptor_checksum(body)
    if new_ck == old_ck:
        control_ok += 1
        return m.group(0)
    # body changed or checksum wrong: only rewrite if body contains a
    # re-encoded (Treeneesu) key token, otherwise it's a control failure
    if "ds3" in body:
        changed += 1
        print(f"checksum {old_ck} -> {new_ck} for {body[:60]}...")
        return f'"{body}#{new_ck}"'
    control_fail += 1
    print(f"CONTROL FAILURE: stored {old_ck}, computed {new_ck}, body {body[:80]}")
    return m.group(0)
text = pat.sub(repl, text)
print(f"controls ok={control_ok} controls FAILED={control_fail} rewritten={changed}")
if control_fail:
    sys.exit("aborting: checksum implementation disagrees with unchanged descriptors")
open(path, "w").write(text)
print("WROTE", path)
