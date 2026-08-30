# Model Architectures Test Plan

## 1. Scope & Target Submodules

- `dlamp.models.architectures.unet`
- `dlamp.models.architectures.glide_unet`
- `dlamp.models.architectures.earth_3d_specifics`
- `dlamp.models.builders` (`PanguBuilder`, `GlideBuilder`)
- `dlamp.models.loss_fn`

## 2. Unit Test Specifications

- `tests/dlamp/models/architectures/test_unet.py`: Migrated and standardized from `unet_test.py`. Forward pass tensor shape verification (`[B, C, H, W]`).
- `tests/dlamp/models/architectures/test_glide_unet.py`: Migrated and standardized from `glide_unet_test.py`. Timestep embedding and conditioning forward pass.
- `tests/dlamp/models/architectures/test_earth_3d_specifics.py`: Migrated and standardized from `earth_3d_specifics_test.py`. 3D Earth Transformer attention mechanisms.
- `tests/dlamp/models/builders/test_builders.py`: Test builder factory dispatch by `cfg.model.model_name`.

## 3. Integration Test Scenarios (`@pytest.mark.integration`)

- 1-epoch / 1-step forward-backward training pass on synthetic tensors with PyTorch Lightning trainer.

## 4. Regression Test Specifications (`@pytest.mark.regression`)

- Deterministic forward pass output comparison with fixed seed and fixed weights.
- Tolerance: `rtol=1e-5`, `atol=1e-6`.

## 5. Fixtures & Environment Requirements

- `torch==2.4.0` environment.
- Fixed random seed fixtures (`@pytest.fixture`).

## 6. Target Coverage & Acceptance Criteria

- Target Line Coverage: >80%
- All architecture forward passes execute without tensor dimension mismatch errors.
