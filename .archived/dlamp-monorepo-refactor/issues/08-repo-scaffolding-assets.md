# 08 Decide monorepo scaffolding and asset migration

Type: grilling
Status: resolved
Blocked by: 07

## Question

Decide the concrete scaffolding of the new monorepo (execution sessions build it):

- Repo identity: name/URL (proposed `YaoChuDoSomething/DLAMP`) and local path (proposed `/wk2/yaochu/main/dlamp-monorepo`); confirm or amend.
- Init method per ticket 07's recipe (merged history start), branch strategy (`dev`? `main`?).
- Asset migration: LFS assets from DLAMP.tw (`assets/**/*.npy`, `export/*.onnx`) and dlamp-data test fixtures (`test/fixtures/*.nc`) — copy as-is, re-point LFS, or regenerate via `generate_fixtures.py`; where each lands per ticket 03's tree.
- Archiving the old repos: what "archived" means for DLAMP.tw and DLAMP.data (private/read-only? `archived` tag? README pointer to the monorepo?).
- Repo conventions to carry: `GEMINI.md` style rules, `AGENTS.md`, `.pre-commit-config.yaml`, `Makefile` — which move over, which get rewritten for the new layout.

Grill one decision at a time; the answer records the scaffolding checklist.

## Answer

Grilled Q1–Q5 with the user, all confirmed. Scaffolding checklist:

**1. Repo identity** — `YaoChuDoSomething/DLAMP` @ `/wk2/yaochu/main/dlamp-monorepo`. (Couldn't verify name availability on GitHub — no `gh` here; verify before the execution session; if `DLAMP` collides use a suffix. Per user, ignore `github/dlamp`/`worktree` copies.)

**2. Init + branch** — per ticket 07 recipe, but pin the default branch explicitly: `git init -b main` (so both `--allow-unrelated-histories` merges land on `main` deterministically, avoiding the `init.defaultBranch` variable). Single working branch **`main`**; no `dev`.

**3. Assets** — 11 LFS files, all under `assets/`; `export/` holds only `.gitkeep` (no onnx blobs tracked; keep the `export/*.onnx` LFS rule in the relocated `.gitattributes` anyway). DLAMP.tw assets land at `src/dlamp/assets/**` — **provisional pending ticket 03's tree**. No copy/re-point/regenerate needed: ticket 07's paths-only rewrite keeps LFS pointers, then `git lfs install` + `git lfs push --all`. Canonical dlamp-data has **no fixtures / no `generate_fixtures.py`** to migrate — record "nothing to migrate"; any future fixture generation belongs to ticket 09's testing spec.

**4. Archiving** — GitHub Archive toggle + README banner pointing to the monorepo, on **both** `DLAMP.tw` and `dlamp.data`. No privacy change (stay public), no deletion. History stays browsable.

**5. Conventions** — carry **`GEMINI.md`** and **`.pre-commit-config.yaml`** verbatim (repo-agnostic; `check-added-large-files` is fine since LFS pointers are small). Rewrite **`AGENTS.md`** (entrypoints→`[project.scripts]`, data components, testing-spec pointer, drop nested-repo note) and **`Makefile`** (keep `install/test/check/clean` structure; update paths + `test`/`check` scopes for the merged package set once 03's tree is final). **`pyproject.toml`** (incl. `>=3.11,<3.12` pin and overlapping deps with dlamp-data) → deferred to ticket 06.
