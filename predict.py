import importlib
from datetime import datetime, timedelta
from pathlib import Path

import hydra
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from omegaconf import DictConfig, OmegaConf
from tqdm import tqdm, trange

from inference import InferenceBase
from src.const import EXP_CODE, NPY_DB, DATA_PATH, FIGURE_PATH
from src.utils import DataCompose, DataGenerator, read_cwa_ncfile
from visual import *
import os

@hydra.main(version_base=None, config_path="config", config_name="predict")
def main(cfg: DictConfig) -> None:
    OmegaConf.set_struct(cfg, True)
    start_t = datetime.strptime(cfg.data.start_time, cfg.data.format)
    eval_cases = [start_t]
    print('=>', cfg.data.start_time, start_t, eval_cases)
    eval_cases.sort()
    print("==================================================")
    print(cfg)
    print("==================================================")
    os.makedirs(FIGURE_PATH, exist_ok=True)
    # Inference
    if cfg.inference.infer_type == "ckpt":
        infer_machine: InferenceBase = getattr(
            importlib.import_module("inference"), "BatchInferenceCkpt"
        )
    elif cfg.inference.infer_type == "onnx":
        infer_machine: InferenceBase = getattr(
            importlib.import_module("inference"), "BatchInferenceOnnx"
        )
    infer_machine = infer_machine(cfg, eval_cases)
    infer_machine.infer(bdy_swap_method=cfg.inference.bdy_swap_method)

    data_gnrt: DataGenerator = infer_machine.data_manager.data_gnrt
    dc_lat, dc_lon = DataCompose.from_config({"Lat": ["NoRule"], "Lon": ["NoRule"]})
    start_t = datetime.strptime(cfg.data.start_time, cfg.data.format)
    lat = data_gnrt.yield_data(start_t, dc_lat)
    lon = data_gnrt.yield_data(start_t, dc_lon)

    for eval_case in tqdm(eval_cases, desc="Dump_Data"):
        t_list, i_list = [], []
        for i in range(infer_machine.showcase_length):
            curr_time = eval_case + infer_machine.output_itv * i

            t_list.append(curr_time.strftime("%Y-%m-%d %HZ"))
            i_list.append(
                f"Init: {eval_case.strftime('%Y-%m-%d %HZ')} Fcst: +{i:02d}H"
            )
            out_sfc = infer_machine.output_surface
            out_upp = infer_machine.output_upper
            inp_sfc = infer_machine.input_surface
            inp_upp = infer_machine.input_upper
            tgt_sfc = infer_machine.target_surface
            tgt_upp = infer_machine.target_upper
            print(out_upp.size, out_upp.shape, out_upp.ndim)

    start_str = start_t.strftime('%Y%m%d_%H%M')
    np.save(f"{NPY_DB}/{EXP_CODES}_I{start_str}_out_surface.npy",out_sfc)
    np.save(f"{NPY_DB}/{EXP_CODES}_I{start_str}_out_upper.npy", out_upp)
    np.save(f"{NPY_DB}/{EXP_CODES}_I{start_str}_inp_surface.npy", inp_sfc)
    np.save(f"{NPY_DB}/{EXP_CODES}_I{start_str}_inp_upper.npy", inp_upp)
    np.save(f"{NPY_DB}/{EXP_CODES}_I{start_str}_tgt_surface.npy", tgt_sfc)
    np.save(f"{NPY_DB}/{EXP_CODES}_I{start_str}_tgt_upper.npy", tgt_upp)
    ### variables rank
    np.save(f"{NPY_DB}/{EXP_CODES}_I{start_str}_upper_vars.npy", infer_machine.upper_vars)
    np.save(f"{NPY_DB}/{EXP_CODES}_I{start_str}_surface_vars.npy", infer_machine.surface_vars)
    ### dimension
    np.save(f"{NPY_DB}/{EXP_CODES}_I{start_str}_geolon.npy" , lon )
    np.save(f"{NPY_DB}/{EXP_CODES}_I{start_str}_geolat.npy" , lat )
    np.save(f"{NPY_DB}/{EXP_CODES}_I{start_str}_pres_levels.npy", infer_machine.pressure_lv)

if __name__ == "__main__":
    main()
