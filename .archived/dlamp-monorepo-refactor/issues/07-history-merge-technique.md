# 07 Decide history-preserving merge technique

Type: research
Status: resolved
Blocked by:

## Question

Decide which technique merges the two git histories into the brand-new monorepo while preserving both:

- Research: `git-filter-repo` (per-repo rewrite + union merge), `git subtree`/`git subtree add`, and graft/submodule approaches — trade-offs for two `dev`-branched repos of roughly this size (DLAMP.tw with LFS assets, DLAMP.data with binary test fixtures).
- Note the LFS wrinkle: `assets/**/*.npy` and `export/*.onnx` are LFS-tracked in DLAMP.tw — how the chosen technique carries (or re-attaches) LFS pointers and the `.gitattributes`.
- Deliver a recommendation with concrete commands, or a decision that execution sessions will follow. Do NOT execute the merge — this ticket only decides.

Output: research summary + approved merge recipe, linked as an asset in the resolution comment.

## Answer

Decision + recipe: `assets/07-history-merge-technique.md`. Full cited research: `/tmp/opencode/git-merge-research.md`.

**Chosen: `git-filter-repo --to-subdirectory-filter` per repo, then union-merge into a fresh repo with `git merge --allow-unrelated-histories`.** DLAMP.tw → `src/dlamp/`, dlamp.data → `src/dlamp/data/`. Only technique satisfying all requirements: both histories real commits in the monorepo DAG, per-subdir prefix in every historical commit, fully clone-transferable (no grafts/replace refs/submodules), LFS a non-issue (paths-only rewrite; pointers byte-identical; no `git lfs migrate`; just `git lfs install` + `git lfs push --all`).

Rejected: `git subtree add` (no historical path-prefix, slow on large repos), `git replace --graft`/grafts (local-only, not transferable on clone, deprecated), submodules (histories stay outside the monorepo DAG).

Verified env: git 2.43.0, git-lfs 3.4.1, **git-filter-repo not installed yet** (install at execution). 11 LFS files in DLAMP.tw; `export/*.onnx` rule present but `export/` empty. `externals/dlamp-data` is untracked (not a gitlink) — no special handling. Two unrelated roots → both merges need the flag; no path overlap. Recipe count check: 53 + 55 + 2 merges.

Escalation to ticket 08: all hashes change and old repos get archived — "archived" semantics are ticket 08's job.
