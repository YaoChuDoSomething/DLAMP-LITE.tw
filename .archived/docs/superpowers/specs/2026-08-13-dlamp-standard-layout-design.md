# DLAMP 標準 Python 專案佈局 (src/dlamp/) 設計

日期: 2026-08-13
狀態: 已批准 (brainstorming 三節通過)

## 1. 動機與目標

DLAMP 真實碼目前散落於:
- `src/` 頂層 namespace (`src.models`、`src.utils` 等), 靠 `.pth` 把 `src/` 塞進 sys.path, 從 repo root 執行
- 頂層 `analysis/` `inference/` `visual/` 獨立 namespace
- `src/dlamp/` 已作為套件安裝 (uv), 但內容是**無關 toy MLP 樣板**

目標: 將全部真實碼收進標準套件 `src/dlamp/` 下, 使 `import dlamp` 即為真實包。這符合 handoff docs (`docs/dlamp_session_handoff.md`、`docs/architecture-init.md`) 既定遷移方向。

## 2. 範圍內

- 遷移 `src/{models,utils,datasets,managers,debug}` 及頂層 `analysis/` `inference/` `visual/` 進 `src/dlamp/`
- 遷移 scripts: `src/export_onnx.py` `src/inference_onnx.py` `src/unzip_tgz.py` `src/generate_const_masks.py` → `src/dlamp/`
- 保留未提交 in-progress 重構檔: `src/runtime_config.py` `src/standardizer.py` (遷入保完整)
- 改 import 命名空間、改入口、修路徑錨定、同步 docs

## 3. 範圍外 (不碰)

- `assets/` `config/` (date yaml) 內容不重排 — 執行期數據
- `externals/` 第三方子模組
- 不做無關重構

## 4. 目標套件樹

```
src/dlamp/
  __init__.py  py.typed
  const.py              # 改錨 repo root
  runtime_config.py     # 遷入保留
  standardization.py  standardizer.py
  models/
    __init__.py  model_utils.py
    architectures/  builders/  callbacks/
    diffusion_process/  lightning_modules/  loss_fn/
  utils/
    __init__.py  data_compose.py data_generator.py data_type.py file_util.py time_util.py
  datasets/  custom_dataset.py
  managers/  data_manager.py datetime_manager.py
  debug/  boundary_plots.py
  analysis/  data_manager.py forecast_saver.py netcdf_meta.py plot_meta.py plotter.py prediction.py video_creator.py
  inference/  batch_inference_{ckpt,onnx}.py infer_utils.py inference_base.py
  visual/  tw_background.py viz_*.py        # 明確置入套件
  export_onnx.py  inference_onnx.py  unzip_tgz.py  generate_const_masks.py

刪除:
  src/models src/managers src/datasets src/utils src/debug src/__init__.py   (遷走後)
  /analysis /inference /visual
  src/dlamp/{model,lightning_module,datamodule,train,config/}   (toy 樣板)
  tests/test_dlamp.py   (toy 測試)

根保留:
  train.py  predict.py   # 薄 wrapper: from dlamp.<module> import main; main()
```

## 5. 遷移執行方式

**採用 approach A: `git mv` + 一次 import 重寫。**
- `git mv` 保歷史
- 批次 rewrite (`sed`/python 腳本):
  - 絕對 `from src.` / `import src.` → `dlamp.`
  - 頂層 `from analysis.` `from inference.` `from visual.` → `dlamp.analysis.` 等 (遷入的檔案內)
  - 內部相對 import (`from ..const` `from ...utils`) → **不動**, 因 `src.x` 與 `dlamp.x` 深度相同, 自動指向 `dlamp.const` 等
- scripts 遷入後以 `python -m dlamp.export_onnx` 等直接執行

## 6. 入口策略

- 根 `train.py` `predict.py` 變薄 wrapper, `from dlamp.<module> import main; main()`
- **不設 console_scripts** (依使用者決定: 維持直接執行)
- `@hydra.main(config_path=...)` 由 repo root 算出絕對路徑, `chdir:False` 維持

## 7. 路徑錨定

```python
REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # src/dlamp/const.py → repo root
```
- 由 `REPO_ROOT` 拼 `assets/` `config/` `checkpoints/` `gallery/` `export/` 絕對路徑, 不再依 CWD
- env vars (`DLAMP_EXP_CODE` 等) 與 `EVAL_CASES` 維持
- `runtime_config.py` `standardizer.py` 若用 CWD 相對, 一併改錨

## 8. 測試 sweep

- `tests/` 引舊路徑 (`src.models`, 頂層, 或 toy `dlamp.datamodule`) 全改 `dlamp.*`/`dlamp.models.*`
- 刪 `tests/test_dlamp.py` (toy)
- 套件內 `*_test.py` (unittest) 引 `src.models` → `dlamp.models`
- 收尾驗證: import sweep + `make check` (ruff/mypy) + `make test`

## 9. 工具微調

- `mypy_path="src"`、pytest `pythonpath=["src"]` → 維持 (套件在 `src/dlamp`, `src` 上層即可; `.pth` 已錨 `src`)

## 10. docs 同步

- 更新 `AGENTS.md`: import 範例 `from src...` → `from dlamp...`; 入口表 `python src/export_onnx.py` → `python -m dlamp.export_onnx`; 路徑說明錨 repo root
- 檢查 `GEMINI.md` 有無路徑/import 範例需同步