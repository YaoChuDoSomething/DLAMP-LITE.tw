# 13 MyPy strict typing debt (~812 errors)

Type: tech-debt
Status: needs-triage
Blocked by: none

## Context

`make check` originally gated on `ruff` + `mypy` + `radon`. The ruff gate was
cleared (commit `fefce24`), but `mypy` under `[tool.mypy] strict = true` reports
~812 errors across 63 files — almost all **pre-existing debt at HEAD** (baseline
was 839). My ruff/refactor work did not add this: measured work-tree is 812 vs
839 baseline. Strict mypy is a separate, much larger debt class than the 135
ruff errors, and sits outside the ruff-fix scope.

## Decision

Per user direction, mypy is **deferred**. To keep `make all` green it was moved
out of the blocking `check` target into a dedicated non-blocking target:

- `make check` → `ruff check` + `radon cc` (passing)
- `make typecheck` → `uv run mypy src/dlamp` (non-blocking, ~812 errors)

## Current error breakdown (mypy 2.3.0, strict, `mypy src/dlamp`)

By error code:

| code           | count |
| -------------- | ----- |
| type-arg       | 240   |
| no-untyped-def | 170   |
| arg-type       | 80    |
| no-untyped-call| 77    |
| attr-defined   | 76    |
| assignment     | 44    |
| no-any-return  | 34    |
| has-type       | 18    |
| union-attr     | 11    |
| operator       | 10    |
| index          | 9     |
| var-annotated  | 8     |
| name-defined   | 6     |
| misc           | 6     |
| no-redef       | 4     |
| call-overload  | 4     |
| override       | 3     |
| call-arg       | 3     |
| type-var       | 2     |
| return-value   | 2     |
| list-item      | 2     |
| valid-type     | 1     |
| untyped-decorator | 1  |
| comparison-overlap | 1 |

By top-level subpackage (errors within `src/dlamp/`):

| subpackage | count |
| ---------- | ----- |
| models     | 273   |
| visual     | 165   |
| analysis   | 108   |
| data       | 64    |
| utils      | 56    |
| inference  | 39    |
| managers   | 34    |
| debug      | 21    |
| datasets   | 5     |
| workflows  | 2     |
| misc top-level | ~45 (train.py, standardizer, runtime_config, entrypoints, etc.) |

## Proposed remediation strategy (incremental, per-module)

Work from smallest/most-contained to largest, verifying `make typecheck` count
drops each step. Candidate order:

1. **Low-hanging typing fixes** (knock out tens quickly):
   - `type-arg` (240): add type args to `ndarray[...]`, `dict[...]`, `DataLoader[...]`, `list[...]`; largely mechanical.
   - `no-untyped-def` (170): add `-> None` / return annotations; mostly mechanical.
   - `no-any-return` (34) / `attr-defined` (76) on `self.cfg[...]` — annotate config dicts (e.g. `DictConfig`/TypedDict) once to kill many per-file.
2. **New/most-changed modules first** (they represent the active surface): `train.py`, `standardizer.py`, `runtime_config.py`, `workflows/*`, `generate_const_masks.py`, `export_onnx.py`, `inference_onnx.py`.
3. Then the big legacy cores where untyped interop dominates: `models/` (273, incl. heavy torch generics), `visual/` (165, mostly `ndarray` type-args), `analysis/` (108), `data/`, `utils/`, `inference/`, `managers/`, `debug/`.
4. Consider easing the transition: a `# mypy: no_ignore_lib`-style per-file granularity or a temporary `[tool.mypy]` section listing an allow-list of files to type-check, so `make typecheck` can incrementally include modules instead of going from 812→0 in one shot.

When complete: move `mypy src/dlamp` back into the `make check` target (restore
pre-`fefce24` behavior) and delete this issue.

## Exit criteria

- `make typecheck` exits 0 with `[tool.mypy] strict = true` intact.
- `make check` includes mypy again and remains green.
- No `# type: ignore` / `Any` scattering added as a mask; fixes are real annotations.