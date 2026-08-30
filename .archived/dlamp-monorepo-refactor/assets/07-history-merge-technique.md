# 07 — History-preserving merge technique (decision)

Research date: 2026-08-12. Research only — nothing was executed. Full cited research in `/tmp/opencode/git-merge-research.md`.

## Decision

**`git-filter-repo` per-repo path relocation + union merge with `git merge --allow-unrelated-histories` into a brand-new repo.**

- DLAMP.tw history rewritten into subdir `src/dlamp/`; dlamp.data history rewritten into subdir `src/dlamp/data/`; then both fetched as remotes into a fresh `git init` repo and joined by two ordinary merge commits.
- The combined DAG is two root commits joined by normal merge commits — fully clone-transferable, no grafts/replace refs/submodules.
- LFS is a non-issue: filter-repo rewrites paths only (never blob content), so pointer blobs survive byte-identical; content-addressed LFS store needs no `git lfs migrate`; run `git lfs install` + `git lfs push --all` on the monorepo.
- Alternatives rejected: `git subtree add` (no path-prefix in history, slow on large repos), `git replace --graft` / `info/grafts` (local-only, not clone-transferable, deprecated), submodules (histories stay outside the monorepo's DAG).

## Environment facts (verified)

- git **2.43.0**, git-lfs **3.4.1**; `git-filter-repo` **not installed** (install before executing).
- DLAMP.tw `.gitattributes`: `assets/demo/**`, `assets/town_shp/**`, `assets/terrain_shp/**`, `assets/constant_masks/**` → `filter=lfs diff=lfs merge=lfs -text`; `export/*.onnx` → same. **11 LFS files** currently tracked (constant_masks npy, demo gif, shp/dbf, etc.); `export/` currently empty (rule present, no blobs).
- dlamp.data: no LFS, no `.gitattributes`.
- `externals/dlamp-data` inside DLAMP.tw is **untracked** (`?? externals/`) — a working-tree nested repo, NOT a gitlink. No history handling needed; it is the same project merged in as Repo B.
- Two unrelated roots → both merges need `--allow-unrelated-histories`; no path overlap (`src/dlamp/**` vs `src/dlamp/data/**`).

## Merge recipe (execution sessions follow this)

Requirements: `git>=2.36`, `git-filter-repo` (install from https://github.com/newren/git-filter-repo).

```bash
# ---------- Phase 1: rewrite DLAMP.tw (branch dev) into src/dlamp/ ----------
git clone --no-local /wk2/yaochu/main/dlamp /tmp/merge/dlamp-tw   # fresh clone mandatory
cd /tmp/merge/dlamp-tw
git checkout dev
git filter-repo --analyze                                          # optional, read-only
git filter-repo --to-subdirectory-filter src/dlamp \
    --tag-rename '':'dlamp-'                                       # renamed to avoid tag collisions

# ---------- Phase 2: rewrite dlamp.data (branch main) into src/dlamp/data/ ----------
git clone --no-local /wk2/yaochu/main/dlamp/externals/dlamp-data /tmp/merge/dlamp-data
cd /tmp/merge/dlamp-data
git checkout main
git filter-repo --to-subdirectory-filter src/dlamp/data \
    --tag-rename '':'dlampdata-'

# ---------- Phase 3: union-merge into the brand-new monorepo ----------
git init /tmp/merge/monorepo
cd /tmp/merge/monorepo
git remote add dlamp-tw /tmp/merge/dlamp-tw
git fetch dlamp-tw
git remote add dlamp-data /tmp/merge/dlamp-data
git fetch dlamp-data
git merge --allow-unrelated-histories dlamp-tw/dev \
    -m "Merge DLAMP.tw history into monorepo"
git merge --allow-unrelated-histories dlamp-data/main \
    -m "Merge dlamp.data history into monorepo"
git remote remove dlamp-tw dlamp-data

# Verify: two roots, both histories, both tips
git log --graph --oneline --all
git rev-list --count --all          # == 53 + 55 + 2 merges

# ---------- Phase 4: LFS in the monorepo ----------
git lfs install                      # registers clean/smudge/process filters (also global)
# src/dlamp/.gitattributes preserved verbatim by filter-repo; rules still apply under src/dlamp/
git check-attr filter -- src/dlamp/assets/constant_masks/land_sea_mask_2km.npy
git remote add origin <new-monorepo-url>
git push -u origin --all --tags
git lfs push --all origin            # content-addressed; re-uploads only if remote is fresh
```

Notes:
- Fresh-clone safety check: abort on non-fresh clone; use `--no-local` for local paths rather than `--force`.
- Optional de-bloat during Phase 1 only if decided (changes history): `--invert-paths --path analysis/` or `--strip-blobs-bigger-than <size>`.
- All commit hashes change; the old DLAMP.tw / dlamp.data repos are archived (ticket 08 defines "archived").

## Trade-off table

| Technique | History preservation | Path relocation | Clone-transferable | LFS | Caveats |
|---|---|---|---|---|---|
| **filter-repo + unrelated merge** (chosen) | Full; per-subdir prefix in every commit | Yes (`--to-subdirectory-filter` = `--path-rename :<dir>/`) | Yes | Pointers untouched; store re-keys by OID | Destructive on source clones (work in fresh clones); hashes change; filter-repo not yet installed |
| **git subtree add** | Full but joined via synthetic merge; commits keep original unprefixed paths | Only at synthetic merge | Yes | Pointers intact; A's `.gitattributes` lands in subtree | Slow on large repos; its sync-upstream strength not needed here |
| **git replace --graft / grafts** | Full DAGs, union is local fiction | None (needs separate rewrite anyway) | **No** — `refs/replace/*` not in default fetch refspec; grafts not transferred | Intact | Local-only; commit-graph disabled; grafts deprecated |
| **git submodule** | Histories live in submodule repos, outside monorepo DAG | Yes (gitlinks) | Yes, but separate repos | Per-submodule | Fails "both histories in the monorepo" requirement |

## Sources (primary)

- git-filter-repo README + manpage (github.com/newren/git-filter-repo): `--to-subdirectory-filter` for "merging with another repo"; fresh-clone safety check; no `--lfs` option; LFS objects only tracked/orphaned, never rewritten.
- git-merge manpage (git-scm.com/docs/git-merge): `--allow-unrelated-histories` for "histories of two projects that started their lives independently"; TRUE MERGE definition.
- git-subtree manpage (local 2.43.0): subtrees vs submodules; `add` joins via a created commit; `split` slow on large projects.
- git-replace manpage + gitrepository-layout manpage (local): `--graft` mechanics; grafts deprecated / transfer problems.
- git-fetch manpage: default refspec has no `refs/replace/*`.
- gitattributes manpage (local): clean/smudge filter contract.
- git-lfs spec (github.com/git-lfs/git-lfs): pointer format; content-addressed `oid sha256:`; `git lfs install` filter registration.
