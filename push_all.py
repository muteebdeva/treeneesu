#!/usr/bin/env python3
"""Push the ENTIRE Treeneesu workspace to github.com/muteebdeva/treeneesu
as ONE commit, using the GitHub Git Data API through the stored connector
credential (same mechanism as bin/gh.py; the credential is never printed).

- Blobs are uploaded in parallel (6 workers) and cached locally
  (~/.cache/tnsu-push/blobs.json, keyed by path+size+mtime) so an
  interrupted run resumes instead of re-uploading.
- Excludes: .git dirs, bitcoin-core build trees, __pycache__, and the
  generated bitcoin-core/test/config.ini.
"""
import base64, json, os, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

ROOT = os.path.expanduser("~/workspace/treeneesu")
CACHE = os.path.expanduser("~/.cache/tnsu-push/blobs.json")
REPO = "muteebdeva/treeneesu"
BASE = "https://api.github.com"
EXCLUDE_DIRS = {".git", "__pycache__", "build", "build-asan", "build-final", "build-ubsan"}
EXCLUDE_FILES = {"bitcoin-core/test/config.ini"}

def api(method, path, body=None, timeout=180):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        **({"Content-Type": "application/json"} if data else {}),
    })
    add_surrogate_to_request(req, "custom.github", allowed_hosts=("api.github.com",))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return read_json_response(resp)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:400]
        raise RuntimeError(f"{method} {path} -> HTTP {e.code}: {detail}") from None

def collect():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for name in filenames + [d for d in dirnames if os.path.islink(os.path.join(dirpath, d))]:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, ROOT)
            if rel in EXCLUDE_FILES:
                continue
            out.append((rel, full))
    return sorted(out)

def upload_one(item, cache):
    rel, full = item
    if os.path.islink(full):
        content = os.readlink(full).encode()
        mode = "120000"
        key_src = f"link:{os.readlink(full)}"
        st_size, st_mtime = 0, 0
    else:
        st = os.stat(full)
        content = None
        mode = "100755" if (st.st_mode & 0o111) else "100644"
        key_src = None
        st_size, st_mtime = st.st_size, int(st.st_mtime)
    key = f"{rel}|{st_size}|{st_mtime}|{key_src or ''}"
    if key in cache:
        return rel, mode, cache[key], key, True
    if content is None:
        with open(full, "rb") as f:
            content = f.read()
    r = api("POST", f"/repos/{REPO}/git/blobs",
            {"content": base64.b64encode(content).decode(), "encoding": "base64"})
    return rel, mode, r["sha"], key, False

def main():
    dry = "--dry-run" in sys.argv
    files = collect()
    total = sum(os.path.getsize(f) for _, f in files if not os.path.islink(f))
    print(f"files: {len(files)}  bytes: {total/1e6:.1f} MB")
    biggest = sorted(((os.path.getsize(f), r) for r, f in files if not os.path.islink(f)), reverse=True)[:3]
    for size, rel in biggest:
        print(f"  largest: {size/1e6:.1f} MB  {rel}")
    if dry:
        return
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

    repo = api("GET", f"/repos/{REPO}")
    branch = repo["default_branch"]
    ref = api("GET", f"/repos/{REPO}/git/ref/heads/{branch}")
    base_commit = ref["object"]["sha"]
    base_tree = api("GET", f"/repos/{REPO}/git/commits/{base_commit}")["tree"]["sha"]
    print(f"branch {branch}: base commit {base_commit[:12]} tree {base_tree[:12]}")

    entries, done, reused = [], 0, 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        for rel, mode, sha, key, was_cached in ex.map(lambda it: upload_one(it, cache), files):
            entries.append({"path": rel, "mode": mode, "type": "blob", "sha": sha})
            cache[key] = sha
            done += 1; reused += was_cached
            if done % 250 == 0:
                print(f"  blobs {done}/{len(files)} ({reused} cached)")
                json.dump(cache, open(CACHE, "w"))
    json.dump(cache, open(CACHE, "w"))
    print(f"blobs done: {done} ({reused} from cache)")

    # A single tree POST with 3000+ nested entries fails on GitHub's side
    # (HTTP 502). Build the hierarchy bottom-up instead: one tree object
    # per directory, deepest first; tree/blob shas are content-addressed,
    # so unchanged subtrees coincide with the ones already on GitHub.
    import time
    from collections import defaultdict
    def api_retry(method, path, body=None, tries=4):
        for i in range(tries):
            try:
                return api(method, path, body)
            except RuntimeError:
                if i == tries - 1:
                    raise
                time.sleep(2 * (i + 1))
    by_dir = defaultdict(list)          # dir -> [(name, mode, sha)] files
    subdirs = defaultdict(set)          # dir -> {child dir names}
    for e in entries:
        parts = e["path"].split("/")
        d = "/".join(parts[:-1])
        by_dir[d].append((parts[-1], e["mode"], e["sha"]))
        for i in range(1, len(parts)):
            subdirs["/".join(parts[:i - 1])].add(parts[i - 1])
    tree_sha = {}
    for d in sorted(by_dir.keys() | subdirs.keys(), key=lambda s: -(len(s.split("/")) if s else 0)):
        items = [{"path": n, "mode": m, "type": "blob", "sha": s} for n, m, s in by_dir.get(d, [])]
        for child in sorted(subdirs.get(d, [])):
            cd = f"{d}/{child}" if d else child
            items.append({"path": child, "mode": "040000", "type": "tree", "sha": tree_sha[cd]})
        r = api_retry("POST", f"/repos/{REPO}/git/trees", {"tree": items})
        tree_sha[d] = r["sha"]
    tree = {"sha": tree_sha[""]}
    print(f"tree: {tree['sha'][:12]} (built from {len(tree_sha)} directory trees)")
    commit = api("POST", f"/repos/{REPO}/git/commits", {
        "message": ("Treeneesu: completion-mission final state — full suite 152/152, "
                    "demo v2 passed, ASan subset clean\n\n"
                    "Local source HEAD 03727d8 (miner_tests nonces re-ground for the "
                    "Option A genesis). Adds README.md, FINAL-REPORT.md, refreshed "
                    "TEST-SUMMARY.json/BLOCKERS.md, final test/demo/ASan/functional "
                    "logs, and the refreshed history bundle. Excluded: build trees, "
                    ".git internals, generated test/config.ini."),
        "tree": tree["sha"], "parents": [base_commit]})
    print(f"commit: {commit['sha'][:12]}")
    api("PATCH", f"/repos/{REPO}/git/refs/heads/{branch}", {"sha": commit["sha"]})
    print(f"ref updated -> https://github.com/{REPO}/tree/{branch}")

if __name__ == "__main__":
    main()
