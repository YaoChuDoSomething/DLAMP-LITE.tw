# AI-ML Development Workflow Specification

This document defines the standard end-to-end pipeline for AI-ML development within this project, ensuring production-readiness, reproducibility, and maintainability.

## 1. High-Level Pipeline Sequence

The development flow follows a strict sequential order to prevent "model-first" pitfalls and ensure data integrity.

`Data Pipeline` $\rightarrow$ `Model Design` $\rightarrow$ `Training` $\rightarrow$ `Evaluation` $\rightarrow$ `Deployment`

---

## 2. Detailed Phase Specifications

### Phase 1: Data Pipeline
**Goal**: Transform raw data into ML-ready features with guaranteed quality.
- **Ingestion**: Define data sources, versioning (DVC/LakeFS), and loading mechanisms.
- **Preprocessing**: Cleaning, normalization, handling missing values, and augmentation.
- **Validation**: Implement "Data Contracts" (Great Expectations/TFDV) to detect schema drift and anomalies.
- **Feature Engineering**: Feature extraction, embedding generation, and storage in a Feature Store (Feast/Tecton).
- **Deliverables**: 
    - Validated dataset versions.
    - Feature engineering scripts and documentation.
    - Data quality reports.

### Phase 2: Model Design
**Goal**: Define the mathematical and structural blueprint of the model.
- **Architecture Selection**: Research and select model families (e.g., Transformer, CNN, MLP) based on the task.
- **Interface Definition**: Define strict input/output shapes, types, and constraints (e.g., tensor dimensions).
- **Constraint Analysis**: Analyze latency, memory, and compute budgets for the target environment.
- **Loss Function & Metrics**: Define the objective function and success metrics (Technical vs. Business).
- **Deliverables**: 
    - Model specification document.
    - Interface contracts (Type hints/Schemas).
    - Baseline complexity analysis.

### Phase 3: Training
**Goal**: Optimize model parameters to maximize performance on the training set.
- **Infrastructure Setup**: Configure distributed training (DDP, FSDP, DeepSpeed) and hardware acceleration.
- **Execution**: Implement training loops, mixed precision, and gradient checkpointing.
- **Hyperparameter Optimization (HPO)**: Systematic search (Optuna/Ray Tune) for optimal learning rates, batch sizes, etc.
- **Experiment Tracking**: Log every run, artifact, and metric (MLflow/W&B).
- **Deliverables**: 
    - Trained model checkpoints.
    - HPO logs and reports.
    - Training curves and convergence analysis.

### Phase 4: Evaluation
**Goal**: Rigorously verify model performance on unseen data.
- **Offline Evaluation**: Cross-validation, holdout sets, and temporal validation.
- **Online Evaluation**: A/B testing, shadow deployments, and champion-challenger setups.
- **Robustness & Bias**: Adversarial testing, slice-based analysis, and fairness audits.
- **Error Analysis**: Qualitative review of failure cases to inform the next iteration.
- **Deliverables**: 
    - Evaluation report (Precision, Recall, F1, AUC, etc.).
    - Bias/Fairness audit.
    - Error analysis report.

### Phase 5: Deployment
**Goal**: Transition the model from a research artifact to a production service.
- **Serving Architecture**: Design the inference API (FastAPI/gRPC) and orchestration (Kubernetes/BentoML).
- **Optimization**: Quantization (INT8/FP16), pruning, and distillation for latency/throughput.
- **Interoperability**: Export to universal formats (ONNX/TensorRT).
- **Monitoring**: Implement drift detection (data/model) and performance alerting (Prometheus/Grafana).
- **Deliverables**: 
    - Optimized model artifact.
    - Serving infrastructure code (IaC).
    - Monitoring dashboard and alerting rules.

---

## 3. Local Cutting & Refactor Strategy

To align the current codebase with this workflow, we apply a **Local Cutting** strategy: isolating components into a "Deep Module" structure where behavior is hidden behind a small, stable interface.

### Refactoring Targets

| Current Component | Workflow Phase | Action | Target Architecture |
|---|---|---|---|
| `src/dlamp/data/` | Data Pipeline | Decouple preprocessing from registry. Separate "Ingestion" from "Transformation". | `dlamp.data.ingestion` $\rightarrow$ `dlamp.data.preproc` $\rightarrow$ `dlamp.data.registry` |
| `src/dlamp/models/` | Model Design | Extract architecture definitions from LightningModules. Separate "Shape" from "Training Logic". | `dlamp.models.architectures` $\rightarrow$ `dlamp.models.lightning_modules` |
| `src/dlamp/workflows/` | Training/Exec | Standardize training entrypoints. Implement unified experiment tracking. | `dlamp.workflows.train` $\rightarrow$ `dlamp.workflows.eval` $\rightarrow$ `dlamp.workflows.execute` |
| `src/dlamp/inference/` | Deployment | Isolate ONNX/PyTorch engines. Create a unified `InferenceEngine` interface. | `dlamp.inference.engine` $\rightarrow$ `dlamp.inference.serving` |

### Refactoring Mechanism
1. **Interface Lock**: Define the target interface in a `.py` file (e.g., `interface.py`).
2. **Adapter Implementation**: Create an adapter to bridge existing code to the new interface.
3. **Surgical Patch**: Replace existing calls with the new interface calls.
4. **Verification**: Run existing tests to ensure zero regression.
