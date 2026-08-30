# AI/ML Training Workflow Research Report

This report synthesizes the standard workflows and essential components for professional AI/ML training projects, based on primary documentation from PyTorch, TensorFlow, JAX, and TFX.

## 1. End-to-End Training Workflow

The professional ML lifecycle is a transition from raw data to a deployable artifact, often managed as a directed acyclic graph (DAG) of components.

### High-Level Sequence

`Data Ingestion` $\rightarrow$ `Preprocessing/Transform` $\rightarrow$ `Model Definition` $\rightarrow$ `Training Loop` $\rightarrow$ `Evaluation` $\rightarrow$ `Validation/Blessing` $\rightarrow$ `Deployment (Push)`.

---

## 2. Critical Components

### A. Data Pipeline (ETL & Loading)

The goal is to keep the GPU saturated by decoupling data loading from computation.

- **PyTorch**: Uses `Dataset` for indexing and `DataLoader` for batching, shuffling, and multi-process loading (`num_workers`).
- **TensorFlow**: Uses `tf.data.Dataset` for building complex input pipelines (e.g., `.map()`, `.batch()`, `.prefetch()`).
- **JAX**: Often leverages `tf.data` for sharding data across processes in distributed environments.
- **TFX**: Uses `ExampleGen` for ingestion and `Transform` for consistent feature engineering across training and serving.

### B. Model Architecture & Definition

- **PyTorch**: Defined via `nn.Module` subclasses.
- **TensorFlow**: Defined via Keras Functional/Sequential API or custom layers.
- **JAX**: Typically uses **Flax** or **Haiku** for model definition, separating the model's parameters from its logic (pure functions).

### C. The Training Loop

The core iterative process of parameter optimization.

- **Standard Step**: `Forward Pass` $\rightarrow$ `Loss Computation` $\rightarrow$ `Backward Pass (Autograd)` $\rightarrow$ `Optimizer Step`.
- **Optimizers**: Standard choices include `SGD` and `AdamW` (implemented in `torch.optim` or `optax` for JAX).
- **Loss Functions**: Task-specific (e.g., `CrossEntropyLoss` for classification, `MSELoss` for regression).
- **Acceleration**: JAX uses `jax.jit` for XLA compilation; PyTorch uses `torch.compile` (2.0+).

### D. Evaluation & Validation

- **Metrics**: Beyond loss, projects track `Accuracy`, `F1-Score`, `mAP`, etc.
- **TFX Evaluator**: Uses **TFMA (TensorFlow Model Analysis)** to perform sliced evaluation, ensuring the model performs well across different demographic or feature slices.
- **Blessing**: A "Model Blessing" is a formal artifact produced by the Evaluator that allows a model to be pushed to production.

### E. Experiment Tracking & Versioning

- **Tools**: `Weights & Biases (W&B)`, `MLflow`, `TensorBoard`.
- **Tracking**: Logging hyperparameters, training loss curves, and model checkpoints.
- **Tuner**: TFX provides a `Tuner` component to automate hyperparameter search and pass the best config to the `Trainer`.

### F. Infrastructure & Distributed Training

- **DDP (Distributed Data Parallel)**: The standard for multi-GPU training; replicates the model and averages gradients.
- **FSDP (Fully Sharded Data Parallel)**: Shards model parameters, gradients, and optimizer states to save memory for massive models.
- **TFX Pusher**: Automates the deployment of the blessed model to a serving infrastructure.

---

## Primary Sources

- **PyTorch**: [Data Loading Docs](https://pytorch.org/docs/stable/data.html), [DDP Notes](https://pytorch.org/docs/source/notes/ddp.md)
- **TensorFlow**: [tf.data Guide](https://www.tensorflow.org/guide/data), [TFX Guide](https://www.tensorflow.org/tfx)
- **JAX**: [JAX Distributed Loading](https://github.com/jax-ml/jax/blob/main/docs/distributed_data_loading.md)
- **TFX**: [TFX Pipeline Components](https://github.com/tensorflow/tfx/blob/master/docs/guide/index.md)
