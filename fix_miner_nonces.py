#!/usr/bin/env python3
"""Install grind4 nonces into miner_tests.cpp (which already carries the
MinerTestingSetup activation-height pinning + witness line), replacing the
temporary grinding loop with the fixed assignment again."""
import re

CD = '/home/hatch/workspace/treeneesu/bitcoin-core'
path = CD + '/src/test/miner_tests.cpp'
log = re.sub(r'\x1b\[[0-9;]*m', '', open('/tmp/grind4.log').read())
ground = re.findall(r'GROUND extranonce=(\d+) nonce=(\d+)', log)
assert len(ground) == 110, len(ground)

text = open(path).read()

# 1. remove the grinder, restore fixed assignment
grinder = """            block.hashMerkleRoot = BlockMerkleRoot(block);
            block.nNonce = 0;
            while (!CheckProofOfWork(block.GetHash(), block.nBits, Assert(m_node.chainman)->GetParams().GetConsensus())) { ++block.nNonce; }
            BOOST_TEST_MESSAGE("GROUND extranonce=" << bi.extranonce << " nonce=" << block.nNonce);"""
fixed = """            block.hashMerkleRoot = BlockMerkleRoot(block);
            block.nNonce = bi.nonce;"""
assert grinder in text
text = text.replace(grinder, fixed, 1)

# 2. replace BLOCKINFO nonces in order
it = iter(ground)
def repl(m):
    en, nonce = next(it)
    assert int(m.group(1)) == int(en), (m.group(1), en)
    return '{%s, %s}' % (m.group(1), nonce)
start = text.index('BLOCKINFO[]')
end = text.index('};', start)
region = text[start:end]
new_region, cnt = re.subn(r'\{(\d+), (\d+)\}', repl, region)
assert cnt == 110, cnt
text = text[:start] + new_region + text[end:]
open(path, 'w').write(text)
print("installed grind4 nonces; grinder removed")
