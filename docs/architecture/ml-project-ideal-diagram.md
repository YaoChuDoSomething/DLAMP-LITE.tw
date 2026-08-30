# ML-Weather Prediction System Architecture Diagram

## Machine Learning Weather Prediction (MLWP) 系統架構

這是一套針對您提供的 **MLWP (Machine Learning Weather Prediction) 系統架構** 所設計的 Mermaid 圖表集合。

為了全面展示這個 AI/ML 專案，我為您繪製了四種不同視角的圖表：**元件圖 (Component Diagram)**、**類別圖 (Class Diagram)**、**資料流程圖 (Data Flow Diagram, DFD)** 以及 **系統架構圖 (Architecture Diagram)**。

---

### 1. 元件圖 (Component Diagram)

**目的**：展示系統的模組化結構，以及各個子系統（Pipeline）如何被組織在不同的分層（Layers）中。
**設計**：使用帶有子圖 (subgraph) 的流程圖來呈現分層架構，並加入自訂樣式以區分不同層級。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#e1f5fe', 'edgeLabelBackground':'#ffffff'}}}%%
graph TB
    %% 定義樣式
    classDef layerStyle fill:#f8f9fa,stroke:#ced4da,stroke-width:2px,rx:10,ry:10;
    classDef compStyle fill:#ffffff,stroke:#4dabf7,stroke-width:2px,color:#333;
    
    subgraph Layer1 [1. Data Preparation Layer]
        DPP[Data Production Pipeline<br/>Ingest GRIB/NC]:::compStyle
        DMP[Data Model Pipeline<br/>Standardize xr.DataArray]:::compStyle
        VSP[Variable Synthesis Pipeline<br/>Derive Physical Quantities]:::compStyle
        SFP[Statistical Feature Pipeline<br/>Climatology & Z-score]:::compStyle
    end

    subgraph Layer2 [2. Modeling and Core Layer]
        PMP[Physical Model Pipeline<br/>Baseline NWP]:::compStyle
        PCP[Physical Constraint Pipeline<br/>Mass/Thermo Penalties]:::compStyle
        MTP[Model Training Pipeline<br/>AI Forward/Backprop]:::compStyle
        MIP[Model Inference Pipeline<br/>Autoregressive Rollout]:::compStyle
    end

    subgraph Layer3 [3. Validation and Archival Layer]
        DVP[Data Validation Pipeline<br/>RMSE, ACC Metrics]:::compStyle
        DAP[Data Archival Pipeline<br/>Zarr/NetCDF Chunking]:::compStyle
    end

    subgraph Layer4 [4. Analysis and Visualization Layer]
        DAnP[Data Analysis Pipeline<br/>Spectral/CDO/MetPy]:::compStyle
        Plot2D[2D Plotting Pipeline<br/>Surface/Contours]:::compStyle
        PlotProf[Profile Plotting Pipeline<br/>Skew-T/Cross-sections]:::compStyle
        Plot3D[3D Plotting Pipeline<br/>Volumetric Isosurfaces]:::compStyle
    end

    %% 元件之間的依賴關係
    Layer1 --> Layer2
    Layer2 --> Layer3
    Layer3 --> Layer4

    class Layer1,Layer2,Layer3,Layer4 layerStyle;
```

---

### 2. 類別圖 (Class Diagram)

**目的**：以物件導向 (OOP) 的視角，展示各個 Pipeline 的內部方法（Functions）與職責，以及它們之間的關聯性。
**設計**：將括號內的描述轉換為類別的方法 (Methods) 與屬性 (Attributes)。

```mermaid
classDiagram
    %% Data Preparation Layer
    class DataProductionPipeline {
        +String sourceFormat
        +ingestRawFiles(source: String) Data
    }
    class DataModelPipeline {
        +standardizeToDataArray(data: Data) xr_DataArray
        +applyCFConventions()
    }
    class VariableSynthesisPipeline {
        +deriveWindSpeed(u, v) Tensor
        +deriveRelativeHumidity(t, q) Tensor
    }
    class StatisticalFeaturePipeline {
        +calculateClimatology()
        +applyZScoreNormalization() Tensor
    }

    %% Modeling and Core Layer
    class PhysicalModelPipeline {
        +generateBaselineNWP()
        +getBackgroundFields()
    }
    class PhysicalConstraintPipeline {
        +calcMassConservationLoss() float
        +calcThermodynamicLoss() float
    }
    class ModelTrainingPipeline {
        +forwardPass()
        +backpropagation()
        +saveCheckpoint()
    }
    class ModelInferencePipeline {
        +autoregressiveRollout(steps: int)
        +generateEnsemble(members: int)
    }

    %% Validation and Archival Layer
    class DataValidationPipeline {
        +calculateRMSE(pred, truth) float
        +calculateACC(pred, truth) float
    }
    class DataArchivalPipeline {
        +chunkData()
        +saveToZarr(path: String)
        +saveToNetCDF(path: String)
    }

    %% Analysis and Visualization Layer
    class DataAnalysisPipeline {
        +spectralAnalysis()
        +runMetPyDiagnostics()
    }
    class VisualizationPipelines {
        <<Interface>>
        +plot2DSurfaceMaps()
        +plotProfileSkewT()
        +plot3DVolumetric()
    }

    %% 關係定義
    DataProductionPipeline --> DataModelPipeline : feeds
    DataModelPipeline --> VariableSynthesisPipeline : formats
    VariableSynthesisPipeline --> StatisticalFeaturePipeline : enhances
    
    StatisticalFeaturePipeline --> ModelTrainingPipeline : training data
    StatisticalFeaturePipeline --> ModelInferencePipeline : initial states
    
    PhysicalModelPipeline --> ModelTrainingPipeline : background
    PhysicalConstraintPipeline --* ModelTrainingPipeline : loss function
    
    ModelTrainingPipeline --> DataValidationPipeline : validates
    ModelInferencePipeline --> DataArchivalPipeline : outputs
    
    DataArchivalPipeline --> DataAnalysisPipeline : reads
    DataAnalysisPipeline --> VisualizationPipelines : renders
```

---

### 3. 資料流程圖 (Data Flow Diagram, DFD)

**目的**：追蹤氣象資料（如 GRIB/NC）從原始輸入，經過特徵工程、模型訓練/推論，直到最終視覺化與儲存的生命週期。
**設計**：使用由左至右 (`LR`) 的方向，並使用圓柱體圖形表示資料庫/儲存節點。

```mermaid
graph LR
    %% 節點形狀定義
    RawData[(Raw Sources\nGRIB/NC)]
    ArchivedData[(Archived Data\nZarr/NetCDF)]
    TruthData[(Analysis/Truth\nData)]
    
    %% 流程節點
    subgraph Data Prep
        Ingest(Ingestion)
        Std(Standardization\nxr.DataArray)
        Derive(Variable\nSynthesis)
        Norm(Z-score\nNormalization)
    end
    
    subgraph AI Core
        Train(AI Model\nTraining)
        Infer(Autoregressive\nInference)
        Loss(Physical\nConstraints)
    end
    
    subgraph Output & Viz
        Valid(Validation\nRMSE/ACC)
        Viz(2D/3D/Profile\nPlotting)
    end

    %% 資料流向
    RawData --> Ingest
    Ingest --> Std --> Derive --> Norm
    
    Norm -->|Train Split| Train
    Norm -->|Test/Init Split| Infer
    Loss -.->|Penalty Gradients| Train
    
    Train -->|Model Weights| Infer
    Infer -->|Predicted States| Valid
    TruthData -->|Ground Truth| Valid
    
    Infer -->|Forecast Tensors| ArchivedData
    ArchivedData --> Viz
    ArchivedData --> Analysis(Spectral Analysis)
    Analysis --> Viz
    
    %% 樣式
    classDef storage fill:#fbc02d,stroke:#f57f17,stroke-width:2px;
    class RawData,ArchivedData,TruthData storage;
```

---

### 4. 系統架構圖 (Architecture Diagram)

**目的**：提供高階的系統鳥瞰圖，適合放在專案的 README 或架構文件中。強調各個模組在整個基礎設施中的定位。
**設計**：採用區塊與顏色管理，區分「資料層」、「核心運算層」、「儲存與驗證層」及「展示層」。

```mermaid
graph TB
    classDef default fill:#fff,stroke:#333,stroke-width:1px;
    classDef tier fill:#f4f6f8,stroke:#878e95,stroke-width:2px,stroke-dasharray: 5 5;
    classDef data fill:#e8f5e9,stroke:#4caf50,stroke-width:2px;
    classDef compute fill:#fff3e0,stroke:#ff9800,stroke-width:2px;
    classDef storage fill:#e3f2fd,stroke:#2196f3,stroke-width:2px;
    classDef presentation fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px;

    subgraph T1 [Data Tier: Preparation & Feature Engineering]
        direction LR
        D1(Data Production) --> D2(Data Model)
        D2 --> D3(Variable Synthesis)
        D3 --> D4(Statistical Features)
    end
    class T1 tier;
    class D1,D2,D3,D4 data;

    subgraph T2 [Compute Tier: AI/ML & Physics Core]
        direction TB
        C1(Physical Model Baseline)
        C2(Physical Constraints Loss)
        C3(Model Training Engine)
        C4(Model Inference Engine)
        
        C1 -.-> C3
        C2 -.-> C3
        C3 ==>|Checkpoints| C4
    end
    class T2 tier;
    class C1,C2,C3,C4 compute;

    subgraph T3 [Storage & Validation Tier]
        direction LR
        S1(Data Validation: RMSE/ACC)
        S2[(Data Archival: Zarr/NetCDF)]
    end
    class T3 tier;
    class S1,S2 storage;

    subgraph T4 [Presentation Tier: Analysis & Visualization]
        direction LR
        P1(Data Analysis)
        P2(2D Surface Maps)
        P3(Profile Skew-T)
        P4(3D Volumetric)
    end
    class T4 tier;
    class P1,P2,P3,P4 presentation;

    %% 跨層連接
    T1 ===>|Preprocessed Tensors| T2
    T2 ===>|Predictions & Ensembles| T3
    T3 ===>|Chunked Datasets| T4

    %% 外部實體
    External[External Weather APIs / GRIB] --> T1
    T4 --> Users((End Users / Meteorologists))
```

### 💡 Mermaid 專家建議與最佳實踐 (Best Practices)

1. **渲染環境**：這些圖表使用了標準的 Mermaid 語法，在 GitHub, GitLab, Notion 或 Obsidian 中皆可完美渲染。
2. **樣式自訂 (Styling)**：在架構圖與元件圖中，我使用了 `classDef` 來定義顏色。這有助於在複雜的 AI 專案中，一眼區分出「資料處理 (綠)」、「模型運算 (橘)」、「儲存 (藍)」與「視覺化 (紫)」。
3. **擴充性**：如果未來您的專案加入了 MLOps (如 MLflow, Weights & Biases) 或分散式訓練 (DDP, Ray)，可以直接在 **Compute Tier (T2)** 中新增節點，架構圖依然能保持整潔。
