#!/usr/bin/env python3
"""Upload Treeneesu documentation/deliverables to the private GitHub repo
muteebdeva/treeneesu via the Contents API (secure connector gh.py)."""
import base64, json, subprocess, sys, os

GH = ['python3', '/home/hatch/workspace/custom-connectors/custom.legacy-github/bin/gh.py']
ROOT = '/home/hatch/workspace/treeneesu'
REPO = 'muteebdeva/treeneesu'

def gh(method, path, body=None):
    args = GH + [method, path]
    if body is not None:
        args.append(json.dumps(body))
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{method} {path} -> rc={r.returncode}: {r.stdout[:200]} {r.stderr[:200]}")
    return json.loads(r.stdout) if r.stdout.strip().startswith(('{', '[')) else r.stdout

# current root listing for SHAs of existing files
existing = {item['path']: item['sha'] for item in gh('GET', f'/repos/{REPO}/contents/')}

files = [
    ('REPO-README.md', 'README.md'),
    ('PHASE1-STEP2-BUILD.md', 'PHASE1-STEP2-BUILD.md'),
    ('PHASE1-STEP3-TESTS-REGTEST.md', 'PHASE1-STEP3-TESTS-REGTEST.md'),
    ('PHASE2-DESIGN.md', 'PHASE2-DESIGN.md'),
    ('PHASE3-PATCH1.md', 'PHASE3-PATCH1.md'),
    ('PHASE3-PATCH2-PLAN.md', 'PHASE3-PATCH2-PLAN.md'),
    ('PHASE3-PATCH2A-GATE-FAILURE.md', 'PHASE3-PATCH2A-GATE-FAILURE.md'),
    ('genesis/GENESIS-VERIFICATION.md', 'genesis/GENESIS-VERIFICATION.md'),
    ('MISSION1-AUDIT.md', 'MISSION1-AUDIT.md'),
    ('MISSION2-CHANGELOG.md', 'MISSION2-CHANGELOG.md'),
    ('MISSION4-5-AUDIT-SECURITY.md', 'MISSION4-5-AUDIT-SECURITY.md'),
    ('BLOCKERS.md', 'BLOCKERS.md'),
    ('TEST-SUMMARY.json', 'TEST-SUMMARY.json'),
    ('RELEASE-NOTES-v0.1.0-rc1.md', 'RELEASE-NOTES-v0.1.0-rc1.md'),
    ('TESTNET-PLAN.md', 'TESTNET-PLAN.md'),
    ('MAINNET-READINESS-GATES.md', 'MAINNET-READINESS-GATES.md'),
    ('PORTFOLIO-SUMMARY.md', 'PORTFOLIO-SUMMARY.md'),
    ('twonode-demo.sh', 'twonode-demo.sh'),
]
for name in sorted(os.listdir(ROOT + '/docs')):
    files.append((f'docs/{name}', f'docs/{name}'))

ok, fail = [], []
for local, remote in files:
    path = os.path.join(ROOT, local)
    if not os.path.exists(path):
        fail.append((remote, 'missing locally')); continue
    content = base64.b64encode(open(path, 'rb').read()).decode()
    body = {'message': f'docs: add/update {remote} (2026-10-23 mission deliverables)',
            'content': content}
    if remote in existing:
        body['sha'] = existing[remote]
    try:
        resp = gh('PUT', f'/repos/{REPO}/contents/{remote}', body)
        ok.append((remote, resp.get('commit', {}).get('sha', '?')[:8]))
        print(f"OK  {remote}  commit {ok[-1][1]}")
    except Exception as e:
        fail.append((remote, str(e)[:160]))
        print(f"FAIL {remote}: {fail[-1][1]}")
print(f"\nuploaded {len(ok)}/{len(files)}; failures: {len(fail)}")
sys.exit(1 if fail else 0)
