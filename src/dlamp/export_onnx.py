import logging
from pathlib import Path

import hydra
import torch
from omegaconf import DictConfig, OmegaConf

from dlamp.const import REPO_ROOT
from dlamp.managers import DataManager
from dlamp.models import PanguLightningModule, get_builder
from dlamp.utils import DataCompose

logger = logging.getLogger(__name__)

# torch >= 2.6 defaults torch.load(weights_only=True), which rejects plain
# dict/list/str/float containers. Our checkpoint hparams are primitive-only,
# so allow them (harmless under the pinned torch==2.4.0).
torch.serialization.add_safe_globals([dict, list, tuple, str, float, int, bool, type(None)])


@hydra.main(version_base=None, config_path=str(REPO_ROOT / "config"), config_name="predict")
def main(cfg: DictConfig) -> None:
    OmegaConf.set_struct(cfg, True)

    # prepare data
    data_list = DataCompose.from_config(cfg.data.train_data)
    data_manager = DataManager(data_list, **cfg.data, **cfg.lightning)

    # model builder
    model_builder = get_builder(cfg.model.model_name)(
        "export_onnx",
        data_list,
        image_shape=data_manager.image_shape,
        add_time_features=cfg.data.add_time_features,
        **cfg.model,
        **cfg.lightning,
    )

    # load LightningModule from checkpoint
    pl_module = PanguLightningModule.load_from_checkpoint(
        checkpoint_path=cfg.inference.best_ckpt,
        test_dataloader=None,
        backbone_model=model_builder._backbone_model(),
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pl_module = pl_module.to(device)

    # sample an input: real batch, or a zero tensor of the model's expected
    # shape when mock_input=true (no data required)
    if cfg.inference.get("mock_input", False):
        levels = len(model_builder.pressure_levels)
        upper_ch = len(model_builder.upper_vars)
        sfc_ch = len(model_builder.surface_vars) + (4 if cfg.data.add_time_features else 0)
        input_sample = (
            torch.zeros(1, levels, *cfg.data.image_shape, upper_ch, device=device),
            torch.zeros(1, 1, *cfg.data.image_shape, sfc_ch, device=device),
        )
    else:
        data_manager.setup("fit")
        inp_data, _oup_data = next(iter(data_manager.train_dataloader()))
        input_sample = (
            inp_data["upper_air"].to(device),
            inp_data["surface"].to(device),
        )

    # export onnx
    date = cfg.inference.best_ckpt.split("_")[1]  # e.g. 240831
    export_dir = Path("./export")
    export_dir.mkdir(parents=True, exist_ok=True)
    onnx_path = export_dir / f"{cfg.model.model_name}_model_{date}.onnx"
    # Single thread keeps the CPU tracing pass within a modest memory budget.
    torch.set_num_threads(1)
    with torch.no_grad():
        torch.onnx.export(
            pl_module,
            input_sample,
            str(onnx_path),
            export_params=True,
            verbose=False,
            input_names=["input_upper", "input_surface"],
            output_names=["output_upper", "output_surface"],
            dynamic_axes={
                "input_upper": {0: "batch_size"},
                "input_surface": {0: "batch_size"},
                "output_upper": {0: "batch_size"},
                "output_surface": {0: "batch_size"},
            },
            opset_version=13,
            dynamo=False,
        )
    logger.info("Exported ONNX: %s", onnx_path)


if __name__ == "__main__":
    main()
