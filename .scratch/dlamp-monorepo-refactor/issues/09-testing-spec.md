# 09 Decide testing specification content

Type: grilling
Status: resolved
Blocked by: 03

## Question

Decide what the monorepo's **testing specification** (`docs/testing/testing-specification.md`) contains:

- `tests/` layout: mirror `src/dlamp/` structure (and `src/dlamp/data/`)? Single top-level `tests/` with per-module subdirs? Where dlamp-data's existing `test/` files move.
- Test naming and structure conventions (pytest style, `test_*.py`, fixture/module naming); how the stale DLAMP.tw tests (e.g. crashing `pangu_model_test.py`) are handled by the policy.
- Fixtures convention: where fixtures live, `generate_fixtures.py` reuse, env-driven fixture paths (ticket 05).
- Documentation conventions for test code: Google-style docstrings per `GEMINI.md`, what each test module's doc header must state.
- Coverage targets and how coverage is measured (`pytest --cov`), and the documented way to run the suite (Makefile/pyproject commands).
- A documented baseline inventory of existing tests (from tickets 01/02) that the spec accounts for.

Grill one decision at a time; the answer records the spec outline, which the design doc embeds and ticket 11 elaborates per module.

## Answer

Grilled Q1–Q6, all confirmed by user. Testing-spec outline (`docs/testing/testing-specification.md`):

**Q1 — tests/ layout:** single top-level `tests/`, mirroring the package: `tests/dlamp/` ↔ `src/dlamp/`, `tests/dlamp/data/` ↔ `src/dlamp/data/`. `testpaths=["tests"]`, `pythonpath=["src"]` (existing scaffolding pyproject). dlamp-data has **no tests to migrate** (02); `tests/test_dlamp.py` deleted (tests removed starter).

**Q2 — Naming + stale policy:** `<module>_test.py` suffix (consistent with surviving legacy files); `Test<Module>` classes, `test_*` methods, conftest at `tests/dlamp/conftest.py` + `tests/dlamp/data/conftest.py`. Migrate 3 architecture tests (`unet`, `glide_unet`, `earth_3d_specifics`) → `tests/dlamp/models/` (fix in 11); **delete** `pangu_model_test.py` (import-crash + superseded by ONNX workflow); delete `tests/test_dlamp.py`.

**Q3 — Fixtures:** single `tests/fixtures/`; small fixtures committed, large (NC/NPY, e.g. 4.9MB `target.nc`) referenced via env-driven paths (`DLAMP_DATA_PATH`) not committed. No `generate_fixtures.py` re-implementation (doesn't exist canonically) — session-scoped conftest fixtures instead. `dlamp.const` path constants (05-Q4) feed fixtures directly. Real-data tests use `@pytest.mark.integration` (default-skipped, run `-m integration`); unit tests must not depend on external data.

**Q4 — Doc conventions:** Google-style docstrings per GEMINI.md on every test module + fixture. Module doc header must state: purpose, unit under test (module path), strategy (unit/integration), external deps (env/fixtures), run command.

**Q5 — Coverage + run commands:** **no global `--cov-fail-under`**; spec records baseline coverage numbers from `pytest --cov=src/dlamp --cov-report=term-missing`; per-module targets set in 11. Default run: `uv run pytest --cov=src/dlamp tests/ -m "not integration"`. Integration: `uv run pytest tests/ -m integration`. Single module: full path. Makefile `test`/`check` kept, `check` scope → `src/dlamp` (03 tree). HTML report → `htmlcov/` (gitignored).

**Q6 — Baseline inventory (spec section):**
- `tests/test_dlamp.py` → delete (tests deleted starter, 03-B)
- `src/models/architectures/unet_test.py` → `tests/dlamp/models/unet_test.py`, fix in 11
- `src/models/architectures/glide_unet_test.py` → `tests/dlamp/models/glide_unet_test.py`, fix in 11
- `src/models/architectures/earth_3d_specifics_test.py` → `tests/dlamp/models/earth_3d_specifics_test.py`, fix in 11
- `src/models/architectures/pangu_model_test.py` → delete (import-crash, superseded)
- dlamp-data: 0 tests at merge → 11 builds tests from scratch for `cds_downloader`/`dlamp_regridder`/`diagnostic_*`

Consumed by: design doc (12) embeds spec; ticket 11 per-module test plans; `updated.py` reconciliation handled in 11.
