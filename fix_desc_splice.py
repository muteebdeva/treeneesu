#!/usr/bin/env python3
"""Splice a correctly rebuilt '// Checksums' block into descriptor_tests.cpp
from git HEAD, and repair 'computed checksum' quotes in CheckUnparsable lines
elsewhere in the file. Valid Check lines get recomputed checksums and an
oracle-verified compat hash. Unparsable lines keep their deliberately wrong
provided checksums; only the quoted computed values are updated.
"""
import re, subprocess, sys

CD = '/home/hatch/workspace/treeneesu/bitcoin-core'
tsrc = open('/home/hatch/workspace/treeneesu/transform_identity.py').read().split('path = sys.argv')[0]
tg = {}; exec(tsrc, tg)
xform_b58, xform_bech32 = tg['xform_b58'], tg['xform_bech32']
csrc = open('/home/hatch/workspace/treeneesu/fix_desc_checksums.py').read().split('path = sys.argv')[0]
cg = {}; exec(csrc, cg)
ck = cg['descriptor_checksum']

def transform_text(text):
    def sub_b58(m):
        s = m.group(0); n = xform_b58(s.strip('"'))
        return '"' + n + '"' if n else s
    text = re.sub(r'"[1-9A-HJ-NP-Za-km-z]{26,120}"', sub_b58, text)
    def sub_tok(m):
        return xform_b58(m.group(0)) or m.group(0)
    text = re.sub(r'(?:xpub|xprv)[1-9A-HJ-NP-Za-km-z]{107}', sub_tok, text)
    text = re.sub(r'(?<![1-9A-HJ-NP-Za-km-z])[5KL][1-9A-HJ-NP-Za-km-z]{50,51}(?![1-9A-HJ-NP-Za-km-z])', sub_tok, text)
    def sub_b32(m):
        return xform_bech32(m.group(0)) or m.group(0)
    return re.sub(r'bc1[ac-hj-np-z02-9]{11,110}', sub_b32, text)

def oracle_hash(desc):
    out = subprocess.run(['/tmp/oracle', desc], capture_output=True, text=True).stdout
    m = re.search(r'HASH ([a-f0-9]{64})', out)
    assert m, out
    return m.group(1)

def fix_valid_line(line):
    def fix(m):
        return f'"{m.group(1)}#{ck(m.group(1))}"'
    line = re.sub(r'"([^"#]{8,})#([a-z0-9]{8})"', fix, line)
    if 'op_compat_desc_hash' in line:
        first = re.search(r'"([^"#]{8,})#[a-z0-9]{8}"', line)
        if first is None:
            first = re.search(r'"([^"]{8,})"', line)
        h = oracle_hash(first.group(1))
        line = re.sub(r'op_compat_desc_hash=\*/uint256\{"[a-f0-9]{64}"\}', 'op_compat_desc_hash=*/uint256{"' + h + '"}', line)
    return line

def fix_unparsable_line(line):
    # bodies of input descriptors (with checksums) in order
    bodies = [m.group(1) for m in re.finditer(r'"([^"#]{8,})#([a-z0-9]{8})"', line)]
    idx = [0]
    def rep(m):
        body = bodies[min(idx[0], len(bodies) - 1)] if bodies else ''
        idx[0] += 1
        return m.group(1) + ck(body) + m.group(2)
    return re.sub(r"(does not match computed checksum ')[a-z0-9]{8}(')", rep, line)

head = subprocess.run(['git', '-C', CD, 'show', 'HEAD:src/test/descriptor_tests.cpp'], capture_output=True, text=True).stdout.split('\n')
path = CD + '/src/test/descriptor_tests.cpp'
cur = open(path).read().split('\n')

def find(lines, marker, start=0):
    return next(i for i in range(start, len(lines)) if marker in lines[i])

hs = find(head, '// Checksums'); he = find(head, '// Addr and raw tests', hs)
cs = find(cur, '// Checksums'); ce = find(cur, '// Addr and raw tests', cs)
block = []
for hline in head[hs:he]:
    t = transform_text(hline)
    stripped = t.lstrip()
    if stripped.startswith('Check('):
        t = fix_valid_line(t)
    elif stripped.startswith('CheckUnparsable') and 'computed checksum' in t:
        t = fix_unparsable_line(t)
    block.append(t)
cur[cs:ce] = block
print(f"spliced checksums block: {len(block)} lines")

# repair computed-checksum quotes in unparsable lines across the whole file
fixed = 0
for hline in head:
    if 'CheckUnparsable' not in hline or 'computed checksum' not in hline:
        continue
    t = fix_unparsable_line(transform_text(hline))
    bodies = [m.group(1) for m in re.finditer(r'"([^"#]{8,})#([a-z0-9]{8})"', t)]
    if not bodies:
        continue
    key = bodies[0][:45]
    for i, cline in enumerate(cur):
        if key in cline and 'CheckUnparsable' in cline:
            if cline != t:
                cur[i] = t; fixed += 1
            break
print("unparsable lines repaired:", fixed)
open(path, 'w').write('\n'.join(cur))
