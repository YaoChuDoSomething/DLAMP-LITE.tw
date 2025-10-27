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
from src.const import DATA_PATH, FIGURE_PATH, MODEL_CODE
from src.utils import DataCompose, DataGenerator, read_cwa_ncfile, DataType, Level
from visual import *


@hydra.main(version_base=None, config_path="config", config_name="predict")
def main(cfg: DictConfig, ) -> None:
    OmegaConf.set_struct(cfg, True)
    
    #EXP_CODE = "FANAPI"
    #cfg.data.start_time = "2010-09-18 18:00"
    #cfg.data.end_time = "2010-09-20 00:00"

    EXP_CODE = "MUIFA"
    cfg.data.start_time = "2022-09-11 00:00"
    cfg.data.end_time = "2022-09-11 03:00"

    case_end = datetime.strptime(cfg.data.end_time, cfg.data.format)
    case_start = datetime.strptime(cfg.data.start_time, cfg.data.format)
    case_duration = case_end - case_start
    cfg.plot.figure_columns = int(case_duration.total_seconds() // 3600) + 1
    
    eval_cases = [case_start]
    eval_cases.sort()

    print("cfg = ", cfg)
    
    # Inference [begin] ========================================================
    if cfg.inference.infer_type == "ckpt":
        infer_machine: InferenceBase = getattr(
            importlib.import_module("inference"), "BatchInferenceCkpt"
        )
        save_name = cfg.inference.best_ckpt.split("/")[-1].split("-")[0]
    elif cfg.inference.infer_type == "onnx":
        infer_machine: InferenceBase = getattr(
            importlib.import_module("inference"), "BatchInferenceOnnx"
        )
        save_name = cfg.inference.onnx_path.split("/")[-1].split(".")[0]
    infer_machine = infer_machine(cfg, eval_cases)
    infer_machine.infer(bdy_swap_method=cfg.inference.bdy_swap_method)
    
    print(dir(infer_machine))
    
    out_sfc = infer_machine.output_surface
    out_sfc[0, :, 0, :, :, 0:7]
    out_upp = infer_machine.output_upper
    
    print(np.shape(out_upp))
    print(np.shape(out_sfc))

    var_upp = ["PH", "TK", "UM", "VM", "WA", "Qv", "Qt"]
    PRES_LEV = [50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 850, 925, 1000]
    var_sfc = ["T2", "U10", "V10", "Q2", "SST", "PSFC", "SWDOWN", "OLR"]

    for t in range(np.size(out_upp, 1)):
        for var in range(np.size(out_upp, 5)):
            for lev in range(np.size(out_upp, 2)):
                print(str(var_upp[var])+"@Hpa"+str(PRES_LEV[lev])+" = ", np.mean(out_upp[0, t, lev, :, :, var].ravel()))
        for var in range(len(var_sfc)):
            print(str(var_sfc[var])+" = ", np.mean(out_sfc[0, t, 0, :, :, var].ravel()))

    # Inference [end] ==========================================================
    
    # Extract the lat/lon 
    data_gnrt: DataGenerator = infer_machine.data_manager.data_gnrt
    dc_lat, dc_lon = DataCompose.from_config({"Lat": ["NoRule"], "Lon": ["NoRule"]})
    lat = data_gnrt.yield_data(case_start, dc_lat)
    lon = data_gnrt.yield_data(case_start, dc_lon)

    # Save to NumPy NdArray
    np.save(f"./{EXP_CODE}_M{MODEL_CODE}_lat_{case_start.strftime('%Y%m%d_%H%M')}.npy", lat)
    np.save(f"./{EXP_CODE}_M{MODEL_CODE}_lon_{case_start.strftime('%Y%m%d_%H%M')}.npy", lon)
    np.save(f"./{EXP_CODE}_M{MODEL_CODE}_out_upp_{case_start.strftime('%Y%m%d_%H%M')}.npy", out_upp)
    np.save(f"./{EXP_CODE}_M{MODEL_CODE}_out_sfc_{case_start.strftime('%Y%m%d_%H%M')}.npy", out_sfc)

    var_dict = cfg.data.train_data
    data_list = DataCompose.from_config(var_dict)

    surface_data_composes = []
    upper_data_composes = []
    for dc_obj in data_list:
        if dc_obj.level.is_surface():
            print("[sfc] dc_obj = ", dc_obj)
            surface_data_composes.append(dc_obj)
        else:
            print("[upp] dc_obj = ", dc_obj)
            upper_data_composes.append(dc_obj)

    inp_sfc = data_gnrt.yield_data(case_start, surface_data_composes)
    inp_upp = data_gnrt.yield_data(case_start, upper_data_composes)

    data_itv = timedelta(**cfg.data.time_interval)
    output_itv = timedelta(**cfg.inference.output_itv)
    showcase_length = cfg.plot.figure_columns
    pressure_lv: list[Level] = DataCompose.get_all_levels(
        data_list, only_upper=True
    )
    upper_vars: list[DataType] = DataCompose.get_all_vars(
        data_list, only_upper=True
    )
    surface_vars: list[DataType] = DataCompose.get_all_vars(
        data_list, only_surface=True
    )

    # Plotting [begin] =========================================================
    def plot_data_array(data_array, data_type_name, levels, variables_list, lat, lon, output_dir, case_start_dt, output_itv):
        batch_size, time_steps, num_levels, lat_dim, lon_dim, num_vars = data_array.shape
        
        for t_idx in trange(time_steps, desc=f"Plotting {data_type_name} fields"):
            current_time = case_start_dt + t_idx * output_itv
            fig, axes = plt.subplots(num_levels, num_vars, figsize=(num_vars * 6, num_levels * 5))
            
            if num_levels == 1 and num_vars == 1: # Handle single subplot case
                axes = np.array([[axes]])
            elif num_levels == 1: # Handle single row case
                axes = np.expand_dims(axes, axis=0)
            elif num_vars == 1: # Handle single column case
                axes = np.expand_dims(axes, axis=1)

            fig.suptitle(f'{data_type_name} Prediction at {current_time.strftime("%Y-%m-%d %H:%M")}', fontsize=16)

            for l_idx in range(num_levels):
                for v_idx in range(num_vars):
                    ax = axes[l_idx, v_idx]
                    
                    # Extract 2D slice for plotting
                    # data_array shape: [batch, time, lev, lat, lon, var]
                    plot_field = data_array[0, t_idx, l_idx, :, :, v_idx] 
                    
                    # Determine appropriate colormap and normalization
                    # For now, use a simple viridis, but could be customized per variable
                    im = ax.imshow(plot_field, cmap='viridis', origin='lower',
                                   extent=[lon.min(), lon.max(), lat.min(), lat.max()])
                    
                    level_name = levels[l_idx].value if levels else "Surface"
                    
                    # Handle both DataType enum and string for variable names
                    var_name_obj = variables_list[v_idx]
                    var_name = var_name_obj.value if isinstance(var_name_obj, DataType) else str(var_name_obj)

                    ax.set_title(f'Level: {level_name}, Var: {var_name}')
                    ax.set_xlabel('Longitude')
                    ax.set_ylabel('Latitude')
                    fig.colorbar(im, ax=ax, orientation='vertical', shrink=0.8)
            
            plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to prevent suptitle overlap
            plot_filename = output_dir / f'{data_type_name}_{current_time.strftime("%Y%m%d_%H%M")}.png'
            plt.savefig(plot_filename)
            plt.close(fig)

    output_plot_dir = Path("./output/plots")
    output_plot_dir.mkdir(parents=True, exist_ok=True)

    # Plot output_upper_boundary_swapped
    plot_data_array(out_upp, "output_upper", pressure_lv, upper_vars, lat, lon, output_plot_dir, case_start, output_itv)

    # Create a new list of surface variables for boundary swapped data to account for time features
    time_feature_vars = ["TimeFeature1", "TimeFeature2", "TimeFeature3", "TimeFeature4"] # Using strings for time features
    surface_vars_bdy_swapped = surface_vars + time_feature_vars

    # Plot output_surface_boundary_swapped
    #plot_data_array(out_sfc, "output_surface", [Level("Surface")], surface_vars, lat, lon, output_plot_dir, case_start, output_itv)
    plot_data_array(out_sfc, "output_surface", [Level("Surface")], surface_vars_bdy_swapped, lat, lon, output_plot_dir, case_start, output_itv)
    # Plotting [end] ===========================================================
    

if __name__ == "__main__":
    main()

