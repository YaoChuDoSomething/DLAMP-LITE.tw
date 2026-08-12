# DLAMP 標準佈局遷移 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 將 DLAMP 真實碼從散落 namespace (`src.*` + 頂層 `analysis/inference/visual`) 收進標準套件 `src/dlamp/`。

**Architecture:** `git mv` 保歷史把各子樹搬進 `src/dlamp/`, 批次重寫絕對 import (`src.`→`dlamp.`, 頂層→`dlamp.*`), 內部相對 import 因深度相同維持不動。const.py 路徑改錨 repo root, 入口改薄 wrapper, docs 同步。

**Tech Stack:** Python 3.11, uv (uv_build), `src/dlamp/` 已為安裝套件 (`.pth` 錨 `src/`), ruff/mypy/radon (Makefile `check`/`test`)

## Global Constraints

- Python `>=3.11,<3.12`
- 套件名稱恆為 `dlamp`, 實體在 `src/dlamp/` (pyproject 已設, `uv_build` 自動偵測)
- `.pth` 已把 `src/` 加入 sys.path, 故 `import dlamp` 與 `python -m dlamp.<script>` 皆可用
- 內部相對 import (`from ..const`, `from ...utils`) 一律**不動** — 深度與 `src.*` 相同, 自動指向 `dlamp.*`
- 無相容層: 遷移後一律 `from dlamp...`; 舊路徑 `src.*`/頂層刪除
- 保留未提交 in-progress 檔: `src/runtime_config.py` `src/standardizer.py` (遷入保完整)
- 出口: 根 `train.py` `predict.py` 薄 wrapper, **不設 console_scripts** (維持直接執行)
- Commit message 短 imperative; AI commits 附 `Co-Authored-By: opencode (deepseek-v4-flash-free)`
- 範圍外不碰: `assets/`, `config/` 內容, `externals/`, 無關重構

---

### Task 1: 物理遷移子樹進 `src/dlamp/`

**Files:**
- Modify: (git mv) `src/{models,utils,datasets,managers,debug}` → `src/dlamp/`
- Modify: (git mv) `analysis/` `inference/` `visual/` → `src/dlamp/`
- Modify: (git mv) `src/{const,runtime_config,standardization,standardizer,export_onnx,inference_onnx,unzip_tgz,generate_const_masks}.py` → `src/dlamp/`
- Create: `src/dlamp/analysis/__init__.py`
- Delete: `src/__init__.py` (空)
- Test: `find src/dlamp -maxdepth 1 -type d`

**Interfaces:**
- Produces: 目標樹 `src/dlamp/{models,utils,datasets,managers,debug,analysis,inference,visual}` + 根 scripts, 供 Task 2-4 重寫

- [ ] **Step 1: 建目錄 + git mv 子包**

```bash
cd /wk2/yaochu/main/dlamp
git mv src/models src/dlamp/models
git mv src/utils src/dlamp/utils
git mv src/datasets src/dlamp/datasets
git mv src/managers src/dlamp/managers
git mv src/debug src/dlamp/debug
git mv analysis src/dlamp/analysis
git mv inference src/dlamp/inference
git mv visual src/dlamp/visual
```

- [ ] **Step 2: git mv 根層 py 檔 + 補 analysis __init__**

```bash
cd /wk2/yaochu/main/dlamp
git mv src/const.py src/dlamp/const.py
git mv src/runtime_config.py src/dlamp/runtime_config.py
git mv src/standardization.py src/dlamp/standardization.py
git mv src/standardizer.py src/dlamp/standardizer.py
git mv src/export_onnx.py src/dlamp/export_onnx.py
git mv src/inference_onnx.py src/dlamp/inference_onnx.py
git mv src/unzip_tgz.py src/dlamp/unzip_tgz.py
git mv src/generate_const_masks.py src/dlamp/generate_const_masks.py
touch src/dlamp/analysis/__init__.py
```

- [ ] **Step 3: 移除空 src/__init__.py**

```bash
cd /wk2/yaochu/main/dlamp
rm src/__init__.py
```

- [ ] **Step 4: 驗證樹**

```bash
cd /wk2/yaochu/main/dlamp
find src/dlamp -maxdepth 1 -type d | sort
# 期望: src/dlamp/analysis  src/dlamp/datasets  src/dlamp/debug
#       src/dlamp/inference  src/dlamp/managers  src/dlamp/models
#       src/dlamp/utils  src/dlamp/visual
```

- [ ] **Step 5: Commit**

```bash
cd /wk2/yaochu/main/dlamp
git add -A
git commit -m "Move DLAMP code into src/dlamp package

Co-Authored-By: opencode (deepseek-v4-flash-free)"
```

---

### Task 2: 重寫絕對 `from src.` → `dlamp.`

**Files:**
- Modify: `train.py:8-10`
- Modify: `src/dlamp/export_onnx.py`
- Modify: `src/dlamp/inference_onnx.py`
- Modify: `src/dlamp/unzip_tgz.py`
- Modify: `src/dlamp/models/architectures/pangu_model_test.py`
- Modify: `src/dlamp/utils/__init__.py` (註解, cosmetic)
- Test: `grep -rn "from src\.\|import src\." --include=*.py . | grep -v .venv`

**Interfaces:**
- Consumes: Task 1 遷移後路徑
- Produces: 所有 `dlamp.x` import 正確, 供 Task 3 收尾頂層

- [ ] **Step 1: 改 `train.py` import**

```python
from dlamp.managers import DataManager
from dlamp.models import get_builder
from dlamp.utils import DataCompose
```

- [ ] **Step 2: 改 `src/dlamp/export_onnx.py`**

```python
from dlamp.managers import DataManager
from dlamp.models import PanguLightningModule, get_builder
from dlamp.utils import DataCompose
```

- [ ] **Step 3: 改 `src/dlamp/inference_onnx.py`**

```python
from dlamp.managers import DataManager
from dlamp.standardization import destandardization
from dlamp.utils import DataCompose
```

- [ ] **Step 4: 改 `src/dlamp/unzip_tgz.py`**

```python
from dlamp.const import DATA_PATH
```

- [ ] **Step 5: 改 `src/dlamp/models/architectures/pangu_model_test.py`**

```python
from dlamp.models import PanguModel
```

- [ ] **Step 6: 改 `src/dlamp/utils/__init__.py` 註解**

```python
# only for usage of `from dlamp.utils import *`
```

- [ ] **Step 7: 掃描確認無 `from src.` 殘留**

```bash
cd /wk2/yaochu/main/dlamp
grep -rn "from src\.\|import src\." --include=*.py . | grep -v .venv
# 期望: 無輸出
```

- [ ] **Step 8: Commit**

```bash
cd /wk2/yaochu/main/dlamp
git add -A
git commit -m "Rewrite src.* imports to dlamp namespace

Co-Authored-By: opencode (deepseek-v4-flash-free)"
```

---

### Task 3: 重寫頂層跨模組 import → `dlamp.`

**Files:**
- Modify: `predict.py`
- Modify: `src/dlamp/analysis/forecast_saver.py`
- Modify: `src/dlamp/analysis/plotter.py`
- Modify: `src/dlamp/models/builders/glide_builder.py`
- Test: `grep -rn "from analysis\.\|from inference\.\|from visual\." --include=*.py . | grep -v .venv`

**Interfaces:**
- Consumes: Task 1 遷移路徑, Task 2 `dlamp` 套件
- Produces: 頂層跨模組全改 `dlamp.*`, 移入檔不再引舊頂層

- [ ] **Step 1: 改 `predict.py`**

```python
from dlamp.analysis.data_manager import AnalysisDataManager
from dlamp.analysis.forecast_saver import ForecastSaver
from dlamp.analysis.plotter import WeatherPlotter
from dlamp.analysis.prediction import PredictionRunner
```

- [ ] **Step 2: 改 `src/dlamp/analysis/forecast_saver.py`**

```python
from dlamp.analysis.data_manager import AnalysisDataManager
from dlamp.analysis.netcdf_meta import GLOBAL_ATTRIBUTES, VARIABLE_ATTRIBUTES
```

- [ ] **Step 3: 改 `src/dlamp/analysis/plotter.py`**

```python
from dlamp.analysis.data_manager import AnalysisDataManager
from dlamp.analysis.plot_meta import ANALYSIS_PLOT_CONFIGS
```

- [ ] **Step 4: 改 `src/dlamp/models/builders/glide_builder.py`**

```python
from dlamp.inference.infer_utils import init_ort_instance, load_pangu_model
```

- [ ] **Step 5: 掃描確認無舊頂層 import 殘留**

```bash
cd /wk2/yaochu/main/dlamp
grep -rn "from analysis\.\|from inference\.\|from visual\." --include=*.py . | grep -v .venv
# 預期: 只允許 `from dlamp.analysis.` / `from dlamp.inference.` 行
grep -rn "from dlamp.analysis\.\|from dlamp.inference\.\|from dlamp.visual\." --include=*.py . | grep -v .venv
# 期望: 列出上述已改行
```

- [ ] **Step 6: Commit**

```bash
cd /wk2/yaochu/main/dlamp
git add -A
git commit -m "Rewrite top-level cross imports to dlamp

Co-Authored-By: opencode (deepseek-v4-flash-free)"
```

---

### Task 4: 刪除 toy 樣板 + 舊頂層空殼 + stale test

**Files:**
- Delete: `src/dlamp/{model.py,lightning_module.py,datamodule.py,train.py,config/}`
- Delete: `tests/test_dlamp.py`
- Delete: (根) `analysis/` `inference/` `visual/` 已 git mv, 若留空勿複製
- Test: `ls src/dlamp; find src -maxdepth 1`

**Interfaces:**
- Consumes: Task 1 已遷走舊頂層
- Produces: 乾淨 `src/dlamp/` 無 toy, 供 Task 5 路徑錨定

- [ ] **Step 1: 刪 toy 樣板**

```bash
cd /wk2/yaochu/main/dlamp
git rm src/dlamp/model.py src/dlamp/lightning_module.py src/dlamp/datamodule.py src/dlamp/train.py
git rm -r src/dlamp/config
```

- [ ] **Step 2: 刪 toy 測試**

```bash
cd /wk2/yaochu/main/dlamp
git rm tests/test_dlamp.py
```

- [ ] **Step 3: 確認舊頂層移空**

```bash
cd /wk2/yaochu/main/dlamp
ls analysis inference visual 2>&1   # 期望: No such file or directory
```

- [ ] **Step 4: Commit**

```bash
cd /wk2/yaochu/main/dlamp
git commit -m "Remove toy scaffold and its tests

Co-Authored-By: opencode (deepseek-v4-flash-free)"
```

---

### Task 5: const.py 錨定 repo root + Hydra config_path

**Files:**
- Modify: `src/dlamp/const.py`
- Modify: `train.py`, `predict.py` (hydra `config_path`)
- Test: `python -c "from dlamp import const; print(const.REPO_ROOT); print(const.CHECKPOINT_DIR)"`

**Interfaces:**
- Consumes: Task 1 遷移 (const 在 `src/dlamp/`)
- Produces: `REPO_ROOT` 常數, 供依賴 const 路徑的模組; repo root 算出 `config/` 供 Hydra

- [ ] **Step 1: const.py 加 REPO_ROOT 並改路徑常數**

於 `src/dlamp/const.py` 頂部 (datetime/os 之後) 增加:

```python
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parent.parent.parent
```

將常數改為錨定錨定 (逐條):

```python
STANDARDIZATION_PATH = str(REPO_ROOT / "assets" / "standardization" / f"z_score_3h_{MODEL_CODE}.json")
DATA_CONFIG_PATH = str(REPO_ROOT / "config" / "data" / f"rwrf_{MODEL_CODE}.yaml")
BLACKLIST_PATH = str(REPO_ROOT / "assets" / "blacklist_rwrf_3h.txt")
CHECKPOINT_DIR = str(REPO_ROOT / "checkpoints")
LAND_SEA_MASK_PATH = str(REPO_ROOT / "assets" / "constant_masks" / "land_sea_mask_4km.npy")
TOPOGRAPHY_MASK_PATH = str(REPO_ROOT / "assets" / "constant_masks" / "topography_mask_4km.npy")
COUNTY_SHP_PATH = str(REPO_ROOT / "assets" / "town_shp" / "COUNTY_MOI_1090820.shp")
FIGURE_PATH = str(REPO_ROOT / "gallery")
```
註: env var 讀取 (`MODEL_CODE` 等) 與 `EVAL_CASES`/colorbar 維持不動。

- [ ] **Step 2: `train.py` Hydra config_path 錨 repo root**

`@hydra.main` decorator 內 `config_path` 改為絕對:

```python
from pathlib import Path
_HYDRA_CONFIG_DIR = str(Path(__file__).resolve().parent / "config")

@hydra.main(version_base=None, config_path=_HYDRA_CONFIG_DIR, config_name="train_pangu")
```
(實際 decorator 行依現有 `config_name` 調整; 只改 `config_path`。)

- [ ] **Step 3: `predict.py` Hydra config_path 錨 repo root**

```python
from pathlib import Path
_HYDRA_CONFIG_DIR = str(Path(__file__).resolve().parent / "config")

@hydra.main(version_base=None, config_path=_HYDRA_CONFIG_DIR, config_name="predict")
```

- [ ] **Step 4: 驗證路徑常數**

```bash
cd /wk2/yaochu/main/dlamp
uv run python -c "from dlamp import const; print(const.REPO_ROOT); print(const.CHECKPOINT_DIR); print(const.DATA_CONFIG_PATH)"
# 期望: repo root 絕對路徑, checkpoints 目錄, config/data/rwrf_<code>.yaml
```

- [ ] **Step 5: Commit**

```bash
cd /wk2/yaochu/main/dlamp
git add -A
git commit -m "Anchor const paths to repo root

Co-Authored-By: opencode (deepseek-v4-flash-free)"
```

---

### Task 6: 收尾驗證 (ruff/mypy_const/import sweep)

**Files:**
- Test: 全部
- Modify: 若有遭 lint 失敗之 import — 原地修

**Interfaces:**
- Consumes: Task 1-5 全部
- Produces: 通過 `make check` + import sweep 之乾淨狀態

- [ ] **Step 1: import 全模組 sweep**

```bash
cd /wk2/yaochu/main/dlamp
uv run python -c "
import importlib
for m in ['dlamp','dlamp.const','dlamp.utils','dlamp.managers','dlamp.datasets',
          'dlamp.analysis','dlamp.inference','dlamp.visual',
          'dlamp.models','dlamp.models.architectures','dlamp.models.builders',
          'dlamp.standardizer','dlamp.runtime_config']:
    importlib.import_module(m)
    print('OK', m)
"
```
(若某模組含重依賴需資源, 標註已驗證即適用; 重大 import 錯誤需修。)

- [ ] **Step 2: ruff / mypy / radon**

```bash
cd /wk2/yaochu/main/dlamp
uv run ruff check src/dlamp
uv run mypy src/dlamp
uv run radon cc src/dlamp -a -s
# 期望: 無 error。pre-existing warning 記錄不動。
```

- [ ] **Step 3: 跑真實架構 unittest**

```bash
cd /wk2/yaochu/main/dlamp
UV="uv run"
$UV python -m dlamp.models.architectures.glide_unet_test
$UV python -m dlamp.models.architectures.unet_test
# 期望: 各別運行, 無 import 錯誤 (AGENTS: stale 測試可能自身有邏輯失敗, 只驗 import 正確)
```

- [ ] **Step 4: 確認舊 namespace 全清**

```bash
cd /wk2/yaochu/main/dlamp
grep -rln "from src\.\|import src\.\|from analysis\.\|from inference\.\|from visual\." --include=*.py . | grep -v .venv
# 期望: 無輸出
```

- [ ] **Step 5: Commit**

```bash
cd /wk2/yaochu/main/dlamp
git add -A
git commit -m "Verify migration with linters and import sweep

Co-Authored-By: opencode (deepseek-v4-flash-free)"
```

---

### Task 7: docs 同步 (AGENTS.md)

**Files:**
- Modify: `AGENTS.md`
- Modify: `GEMINI.md` (若有 import/路徑範例)
- Test: `grep -n "src/models\|src/utils\|src/managers\|analysis\.\|inference\.\|visual\.\|from src\|import src" AGENTS.md GEMINI.md`

- [ ] **Step 1: AGENTS.md Package Manager 段更新 import 描述**

`from src...` → `from dlamp...`; `from analysis.../inference...` → `from dlamp.analysis...` 等; 保留「run from repo root」但改 `python -m dlamp.<script>`。

- [ ] **Step 2: AGENTS.md Entrypoints 表更新**

| 欄: Command | 更新 |
|---|---|
| `python src/export_onnx.py` | `python -m dlamp.export_onnx` |
| `python train.py` / `python predict.py` | 不變 (薄 wrapper) |

- [ ] **Step 3: AGENTS.md 路徑段更新**

`config/data/rwrf_<code>.yaml` 與 `assets/standardization/...` 改為錨 repo root 說明。

- [ ] **Step 4: 檢查 GEMINI.md**

若含 `src/` import 或路徑範例, 同步 `dlamp`.

- [ ] **Step 5: Commit**

```bash
cd /wk2/yaochu/main/dlamp
git add AGENTS.md GEMINI.md
git commit -m "Update agent docs for dlamp namespace

Co-Authored-By: opencode (deepseek-v4-flash-free)"
```

---

### Task 8: 全量回歸 + 收尾

**Files:**
- Test: 全 repo 邏輯路徑
- Modify: 視遺漏修正

- [ ] **Step 1: 完整 import + Makefile smoke**

```bash
cd /wk2/yaochu/main/dlamp
uv run make check
uv run python -c "import dlamp, dlamp.analysis, dlamp.inference, dlamp.visual, dlamp.models, dlamp.utils"
# 期望: check 通過 (除前存在之 stale 測試/警告)
```

- [ ] **Step 2: 逐路徑 grep 確認達標 (spec §4/§8)**

```bash
cd /wk2/yaochu/main/dlamp
ls src/dlamp           # 含 const, utils, models, datasets, managers, debug, analysis, inference, visual, scripts
ls -d analysis inference visual 2>&1   # 不存在
ls src/dlamp/model.py tests/test_dlamp.py 2>&1   # 不存在
```

- [ ] **Step 3: Commit 任何收尾變更**

```bash
cd /wk2/yaochu/main/dlamp
git add -A && git commit -m "Finalize DLAMP standard layout migration

Co-Authored-By: opencode (deepseek-v4-flash-free)"
```

---

## Self-Review

**Spec 覆蓋:**
- §4 套件樹 → Task 1 (遷移) + Task 4 (刪 toy/舊殼)
- §5 approach A (git mv + rewrite) → Task 1-3
- §6 入口 (薄 wrapper, 直接執行, 無 console_scripts) → Task 1 保根 wrapper + Task 2/3 改其 import; 無 console_scripts (確認無新增)
- §7 路徑錨定 → Task 5
- §8 tests sweep → Task 4 (刪 toy test) + Task 6 (unittest 驗) ; 已注意 tests/ 其餘 stale 屬前存在, 範圍外
- §9 工具 → 未改 mypy_path/pythonpath (維持 `src`), 符合
- §10 docs → Task 7

**Placeholder 掃描:** 全 task 含明確 file/step/code/命令, 無 TBD/TODO。

**Type/名稱一致性:** `dlamp` 恆為包名; `dlamp.analysis`/`dlamp.inference`/`dlamp.visual` 為子包 (均補/保留 `__init__.py`); 函式名未變, 僅命名空間前綴改。

**注意事項註記:** `tests/` 內 `dlamp.downloader`/`dlamp.diagnostics`/`dlamp.regridder` 及 flat `dlamp.models.*` (非 `architectures/`) 為**前存在 stale 測試**, 引用真實碼不存在之模組, 屬既有損壞, 超出本重構正確性範圍 (AGENTS.md 已載明), 本計劃不修, 僅確保不自傷。