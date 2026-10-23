#!/usr/bin/env python3
"""Parse TestBIP324PacketVector calls from bip324_tests.cpp, run them through
the independent Python BIP324 implementation with a given network magic, and
either verify against the stored outputs (control) or emit regenerated calls.
"""
import re, sys
sys.path.insert(0, '/home/hatch/workspace/treeneesu')
from bip324_py import BIP324Cipher

CPP = '/home/hatch/workspace/treeneesu/bitcoin-core/src/test/bip324_tests.cpp'

def parse_vectors(path=CPP):
    text = open(path).read()
    vecs = []
    for m in re.finditer(r'TestBIP324PacketVector\((.*?)\);', text, re.S):
        args = [a.strip() for a in m.group(1).split(',')]
        args = [a for a in args if a != '']
        if not args[0].isdigit():
            continue  # the function declaration, not a call
        assert len(args) == 14, (len(args), args[:3])
        q = lambda s: s.strip('"')
        vecs.append(dict(
            idx=int(args[0]), priv=q(args[1]), ell_ours=q(args[2]), ell_theirs=q(args[3]),
            initiating=args[4] == 'true', contents=q(args[5]), multiply=int(args[6]),
            aad=q(args[7]), ignore=args[8] == 'true', send_gt=q(args[9]), recv_gt=q(args[10]),
            session=q(args[11]), ciphertext=q(args[12]), endswith=q(args[13]),
            span=(m.start(), m.end())))
    return vecs

def run_vector(v, magic):
    c = BIP324Cipher(bytes.fromhex(v['priv']), bytes.fromhex(v['ell_ours']), magic)
    c.initialize(bytes.fromhex(v['ell_theirs']), v['initiating'])
    for _ in range(v['idx']):
        c.encrypt(b'', b'', True)
    contents = bytes.fromhex(v['contents']) * v['multiply']
    ct = c.encrypt(contents, bytes.fromhex(v['aad']), v['ignore'])
    return c, ct

def fmt_call(v, c, ct):
    ct_full = ct.hex()
    if v['ciphertext']:
        ct_field, end_field = ct_full, ''
    else:
        ct_field, end_field = '', ct_full[-len(v['endswith']):] if v['endswith'] else ''
    args = [str(v['idx']), '"%s"' % v['priv'], '"%s"' % v['ell_ours'], '"%s"' % v['ell_theirs'],
            'true' if v['initiating'] else 'false', '"%s"' % v['contents'], str(v['multiply']),
            '"%s"' % v['aad'], 'true' if v['ignore'] else 'false',
            '"%s"' % c.send_gt.hex(), '"%s"' % c.recv_gt.hex(), '"%s"' % c.session_id.hex(),
            '"%s"' % ct_field, '"%s"' % end_field]
    return "TestBIP324PacketVector(\n        " + ",\n        ".join(args) + ");"

if __name__ == '__main__':
    mode = sys.argv[1]
    magic = bytes.fromhex(sys.argv[2])
    vecs = parse_vectors()
    print(f"{len(vecs)} vectors", file=sys.stderr)
    if mode == 'verify':
        bad = 0
        for i, v in enumerate(vecs):
            c, ct = run_vector(v, magic)
            checks = [
                ('session', c.session_id.hex(), v['session']),
                ('send_gt', c.send_gt.hex(), v['send_gt']),
                ('recv_gt', c.recv_gt.hex(), v['recv_gt']),
            ]
            if v['ciphertext']:
                checks.append(('ciphertext', ct.hex(), v['ciphertext']))
            else:
                checks.append(('endswith', ct.hex()[-len(v['endswith']):] if v['endswith'] else '', v['endswith']))
            for name, got, want in checks:
                if got != want:
                    bad += 1
                    print(f"vector {i+1} idx={v['idx']} MISMATCH {name}:\n  got  {got[:64]}\n  want {want[:64]}")
        print("CONTROL RESULT:", "ALL MATCH" if bad == 0 else f"{bad} mismatches")
    elif mode == 'generate':
        text = open(CPP).read()
        out = []
        last = 0
        for v in vecs:
            c, ct = run_vector(v, magic)
            out.append(text[last:v['span'][0]])
            out.append(fmt_call(v, c, ct))
            last = v['span'][1]
        out.append(text[last:])
        open('/tmp/bip324_regenerated.cpp', 'w').write(''.join(out))
        print("wrote /tmp/bip324_regenerated.cpp")
