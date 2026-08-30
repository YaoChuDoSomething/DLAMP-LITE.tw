# DLAMP Codebase Architecture & Domain Model Analysis

針對 **DLAMP (Deep Learning Atmospheric Model / Prediction)** 專案，結合 `/codebase-onboarding` 與 `/domain-modeling` 規範，對訓練、推論、核心模型、資料特徵與資料流分類模組進行完整的架構剖析與領域建模。

---

## 1. 系統架構與管線分析 (Architecture Pipelines)

```text
                              DLAMP Pipeline Architecture
                              
 [ ERA5 / RWRF NetCDF Data ] 
             │
             ▼
  ┌──────────────────────┐
  │ Feature Engineering  │ ── (Standardization z-score, Constant Masks, Time Features)
  └──────────────────────┘
             │
             ▼
  ┌──────────────────────┐
  │  Data Manager & PyTorch│
  │     DataLoaders      │
  └──────────────────────┘
             │
             ├─────────────────────────────────────────┐
             ▼                                         ▼
  ┌──────────────────────┐                  ┌──────────────────────┐
  │ Training Pipeline    │                  │ Inference Pipeline   │
  │ (train.py)           │                  │ (predict.py)         │
  └──────────────────────┘                  └──────────────────────┘
             │                                         │
             ├───────────────┐                         ├───────────────┐
             ▼               ▼                         ▼               ▼
     ┌───────────────┐ ┌───────────┐           ┌───────────────┐ ┌───────────┐
     │  Pangu Model  │ │  Glide    │           │ ONNX Engine   │ │ Checkpoint│
     │  (3D AutoEnc) │ │ (Diffusion│           │ (ONNX Runtime)│ │  Engine   │
     └───────────────┘ └───────────┘           └───────────────┘ └───────────┘
                                                       │
                                                       ▼
                                            ┌─────────────────────┐
                                            │ NetCDF Export &     │
                                            │ WeatherPlotter (12P)│
                                            └─────────────────────┘
```

---

### 1.1 訓練工作流程管線 (Training Pipeline)

* **入口點**：[`train.py`](file:///wk2/yaochu/main/dlamp/train.py) (預設使用 `train_pangu` config，亦可切換 `train_diffusion`)。
* **執行流程**：
  1. **配置加載與驗證**：Hydra 加載與強類型驗證 (`OmegaConf.set_struct(cfg, True)`)。
  2. **數據組合與管理器**：[`DataCompose.from_config`](file:///wk2/yaochu/main/dlamp/src/utils/data_compose.py) 建立數據集列表，並傳入 [`DataManager`](file:///wk2/yaochu/main/dlamp/src/managers/data_manager.py) 生成 Train/Val/Test PyTorch DataLoaders。
  3. **模型構建器 dispatch**：[`get_builder(cfg.model.model_name)`](file:///wk2/yaochu/main/dlamp/src/models/builders/__init__.py) 根據名稱分發建立 `PanguBuilder` 或 `GlideBuilder`。
  4. **Trainer 與 Logger**：自動綁定 WandB Logger，設定 PyTorch Lightning Trainer 並執行 `trainer.fit()`。

---

### 1.2 推論工作流程管線 (Inference Pipeline)

* **入口點**：[`predict.py`](file:///wk2/yaochu/main/dlamp/predict.py) & [`src/export_onnx.py`](file:///wk2/yaochu/main/dlamp/src/export_onnx.py)。
* **執行流程**：
  1. **Inference Engine 選擇**：支援 `ONNX` (`export/*.onnx`) 與 `Checkpoint` (`checkpoints/*.ckpt`) 雙引擎推論。
  2. **預測執行**：[`PredictionRunner`](file:///wk2/yaochu/main/dlamp/analysis/prediction/runner.py) 依時間步逐時生成 Upper-air 與 Surface 氣象預測張量。
  3. **Data Management**：由 [`AnalysisDataManager`](file:///wk2/yaochu/main/dlamp/analysis/data_manager.py) 進行標準化反轉（De-standardization / Un-z-score）。
  4. **NetCDF 輸出與繪圖**：[`ForecastSaver`](file:///wk2/yaochu/main/dlamp/analysis/forecast_saver.py) 寫出符合 WRF 標準的 NetCDF 預測檔，並由 [`WeatherPlotter`](file:///wk2/yaochu/main/dlamp/analysis/plotter.py) 生成 12-panel 氣象場分析圖表。

---

### 1.3 核心模型模組 (Core Model Architecture)

* **架構路徑**：[`src/models/architectures/`](file:///wk2/yaochu/main/dlamp/src/models/architectures/)
* **模型模組分流**：
  * **Pangu-Weather 類神經網路** ([`pangu_model.py`](file:///wk2/yaochu/main/dlamp/src/models/architectures/pangu_model.py))：3D/2D 氣象場 Autoencoder 結構，包含 Patch Embedding、3D Swin Transformer Block 以及 Downsample / Upsample 操作。
  * **Glide / DDPM 擴散模型** ([`glide/`](file:///wk2/yaochu/main/dlamp/src/models/architectures/glide/))：用於機率性高解析度大氣場擴散生成。
  * **Loss Functions** ([`src/models/loss_fn/`](file:///wk2/yaochu/main/dlamp/src/models/loss_fn/))：自訂物理/緯度加權損失函數（Latitude-weighted MSE/MAE）。

---

### 1.4 資料特徵與處理管線 (Data & Feature Pipeline)

* **資料來源**：`DLAMP_DATA_PATH` 下之 ERA5 / OP_ERA5 逐時 NetCDF 檔案。
* **特徵組裝與處理**：
  * **Standardization** ([`src/standardization.py`](file:///wk2/yaochu/main/dlamp/src/standardization.py))：根據 `DLAMP_EXP_CODE` 加載 3小時/6小時的 `z_score_*.json` 進行動態均值與標準差標準化。
  * **Mask Generators** ([`src/generate_const_masks.py`](file:///wk2/yaochu/main/dlamp/src/generate_const_masks.py))：產生地形高度、海陸遮罩與常數氣象掩碼。
  * **Time Feature Encoders**：附加正弦/餘弦時間與季節特徵標籤。

---

### 1.5 資料流分類與模型介面

* **Upper-Air (高空大氣場)**：3D 張量 ($B, C, Z, H, W$)，包含多層位勢高度 (Z)、風速 ($U, V$)、溫度 ($T$)、相對濕度 ($Q$)。
* **Surface (地面氣象場)**：2D 張量 ($B, C, H, W$)，包含海平面氣壓 (MSL)、10m風速 ($U_{10}, V_{10}$)、2m溫度 ($T_{2m}$) 等。

---

## 2. 領域模型 (Domain Glossary in [`CONTEXT.md`](file:///wk2/yaochu/main/dlamp/CONTEXT.md))

專案已建立領域辭彙集（Ubiquitous Language），定義大氣機器學習的核心術語：

```markdown
# DLAMP Domain Glossary

### Model Code / Experiment Code (DLAMP_EXP_CODE)
The unique version tag (e.g., `20250627`, `20250729`) identifying a model checkpoint, 
its matching data configuration YAML (`rwrf_<code>.yaml`), and its exact standardization JSON.

### Upper-Air Variables
3D atmospheric fields defined across multiple pressure levels (e.g., 1000hPa to 50hPa), 
including Geopotential (Z), Temperature (T), U/V Wind components, and Specific Humidity (Q).

### Surface Variables
2D ground-level meteorological fields, including Mean Sea Level Pressure (MSL), 
10-meter U/V Wind components, and 2-meter Temperature (T2M).

### Standardization Vector (Z-Score)
The calculated per-variable mean and standard deviation mapped by lead time (e.g., 3-hour window)
used to normalize raw NetCDF physical quantities prior to neural network forward pass.
```
