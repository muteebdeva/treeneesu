#!/usr/bin/env python3
"""Iterative descriptor_tests repair driven by the test log itself.
Usage: fix_desc_iterate.py <test_log>
1. For every 'CompatDescriptorHash() H does not match for priv P' in the log:
   oracle-verify H against P, then replace the stored uint256 near P's
   Check call (same line or within the next 6 lines) with H.
2. For every 'Provided checksum 'P' does not match computed checksum 'C''
   EXPECTED-value mismatch: in the current file, find the input descriptor
   string carrying '#P' nearest the expected message and set the quoted
   computed value to the BIP380 checksum of that string's body (verified
   against the log's ACTUAL computed value where the log shows it).
"""
import re, subprocess, sys

CD = '/home/hatch/workspace/treeneesu/bitcoin-core'
path = CD + '/src/test/descriptor_tests.cpp'
csrc = open('/home/hatch/workspace/treeneesu/fix_desc_checksums.py').read().split('path = sys.argv')[0]
cg = {}; exec(csrc, cg)
ck = cg['descriptor_checksum']

log = re.sub(r'\x1b\[[0-9;]*m', '', open(sys.argv[1]).read())
text = open(path).read()
lines = text.split('\n')

def oracle(desc):
    out = subprocess.run(['/tmp/oracle', desc], capture_output=True, text=True).stdout
    m = re.search(r'HASH ([a-f0-9]{64})', out)
    return m.group(1) if m else None

# --- 1. compat hashes ---
pairs = set(re.findall(r'CompatDescriptorHash\(\) ([a-f0-9]{64}) does not match for priv (.+?)(?:"|\n)', log))
fixed = 0
for h, priv in pairs:
    priv = priv.strip()
    if oracle(priv.split('#')[0]) != h:
        print("ORACLE DISAGREES for", priv[:50]); continue
    key = priv[:45]
    for i, line in enumerate(lines):
        if key in line:
            for j in range(i, min(i + 7, len(lines))):
                if 'op_compat_desc_hash' in lines[j]:
                    lines[j], c = re.subn(r'op_compat_desc_hash=\*/uint256\{"[a-f0-9]{64}"\}', 'op_compat_desc_hash=*/uint256{"' + h + '"}', lines[j])
                    fixed += c
                    break
            break
print("compat hashes fixed:", fixed)

# --- 2. expected computed-checksum quotes ---
text = '\n'.join(lines)
# actual pairs from log: [Provided 'P' does not match computed 'A' != Provided 'P' does not match computed 'E']
actual = {}
for m in re.finditer(r"\[Provided checksum '([a-z0-9]{8})' does not match computed checksum '([a-z0-9]{8})' != Provided checksum '[a-z0-9]{8}' does not match computed checksum '([a-z0-9]{8})'\]", log):
    actual[m.group(1)] = m.group(2)
n = 0
for provided, act in actual.items():
    # find input strings carrying #provided; compute ck over body; require == actual
    cands = [m.group(1) for m in re.finditer(r'"([^"#]{8,})#' + provided + r'"', text)]
    good = [b for b in cands if ck(b) == act]
    if not good:
        print(f"no body verifies for provided {provided} (actual {act}); candidates {len(cands)}")
        continue
    # replace the expected quote following that provided mention
    pat = re.compile(r"(Provided checksum '" + provided + r"' does not match computed checksum ')[a-z0-9]{8}(')")
    text, c = pat.subn(lambda mm: mm.group(1) + act + mm.group(2), text)
    n += c
print("expected computed quotes fixed:", n)
open(path, 'w').write(text)
