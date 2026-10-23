#!/usr/bin/env python3
"""Rebuild every checksum-bearing line of descriptor_tests.cpp from git HEAD:
transform identity strings (same transformer as the rest of Batch A), then
- valid Check(...) lines: set each descriptor's checksum to the computed one;
- CheckUnparsable lines whose expected error quotes a computed checksum:
  keep the deliberately-wrong provided checksum, update the quoted computed
  value to the checksum of the transformed body.
All other lines are left byte-identical. Prints every line it rewrites.
"""
import re, subprocess, sys

sys.path.insert(0, '/home/hatch/workspace/treeneesu')
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
        n = xform_b58(m.group(0))
        return n if n else m.group(0)
    text = re.sub(r'(?:xpub|xprv)[1-9A-HJ-NP-Za-km-z]{107}', sub_tok, text)
    text = re.sub(r'(?<![1-9A-HJ-NP-Za-km-z])[5KL][1-9A-HJ-NP-Za-km-z]{50,51}(?![1-9A-HJ-NP-Za-km-z])', sub_tok, text)
    def sub_b32(m):
        n = xform_bech32(m.group(0))
        return n if n else m.group(0)
    text = re.sub(r'bc1[ac-hj-np-z02-9]{11,110}', sub_b32, text)
    return text

path = '/home/hatch/workspace/treeneesu/bitcoin-core/src/test/descriptor_tests.cpp'
head = subprocess.run(['git', '-C', '/home/hatch/workspace/treeneesu/bitcoin-core', 'show', 'HEAD:src/test/descriptor_tests.cpp'], capture_output=True, text=True).stdout.split('\n')
cur = open(path).read().split('\n')

def desc_strings(line):
    # quoted strings that look like descriptors carrying a checksum
    return [m for m in re.finditer(r'"([^"#]{8,})#([a-z0-9]{8})"', line)]

rewritten = 0
for hline in head:
    if not desc_strings(hline):
        continue
    tline = transform_text(hline)
    is_unparsable = tline.lstrip().startswith('CheckUnparsable')
    # fix checksums per role
    def fix(m):
        body, provided = m.group(1), m.group(2)
        computed = ck(body)
        if not is_unparsable:
            return f'"{body}#{computed}"'
        return m.group(0)  # keep deliberately wrong provided checksum
    tline2 = desc_strings_fix = re.sub(r'"([^"#]{8,})#([a-z0-9]{8})"', fix, tline)
    if is_unparsable and 'does not match computed checksum' in tline2:
        # update quoted computed values: for each input descriptor in the line,
        # its computed checksum replaces the corresponding quoted value
        bodies = [m.group(1) for m in desc_strings(tline2)]
        for body in bodies:
            tline2 = re.sub(r"(does not match computed checksum ')[a-z0-9]{8}(')", lambda mm: mm.group(1) + ck(body) + mm.group(2), tline2, count=1)
    # locate the corresponding current line: same first descriptor body prefix
    m0 = desc_strings(tline2)
    if not m0:
        continue
    key = m0[0].group(1)[:50]
    for i, cline in enumerate(cur):
        if key in cline and (('CheckUnparsable' in cline) == is_unparsable or 'Check(' in cline or 'CheckUnparsable' in cline):
            if cline != tline2:
                cur[i] = tline2
                rewritten += 1
                print(f"line {i+1} rewritten ({'unparsable' if is_unparsable else 'valid'})")
            break
open(path, 'w').write('\n'.join(cur))
print("total rewritten:", rewritten)
