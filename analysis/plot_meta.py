# analysis/plot_meta.py
"""Metadata and configurations for generating weather analysis plots.

This module provides dictionary-based configurations that define the content,
layout, and properties of each panel in the analysis figures, separating
the plot design from the plotting logic.
"""
from typing import Any, Dict, List

from src.utils import Level

# A list of dictionaries, where each dictionary defines one plot panel.
# This structure makes it easy to add, remove, or reorder plots.
ANALYSIS_PLOT_CONFIGS: List[Dict[str, Any]] = [
    {
        "title": "500hPa Wind & Height",
        "unit": "m s-1",
        "level": Level.Hpa500,
        "plot_func_key": "wind_speed",
        "cmap": "Spectral_r",
        "vmin": 0,
        "vmax": 60,
    },
    {
        "title": "500hPa Vorticity & Height",
        "unit": "1e-6 s-1",
        "level": Level.Hpa500,
        "plot_func_key": "vorticity",
        "cmap": "YlOrBr",
        "vmin": 0,
        "vmax": 200,
    },
    {
        "title": "850hPa Wind & Height",
        "unit": "m s-1",
        "level": Level.Hpa850,
        "plot_func_key": "wind_speed",
        "cmap": "Spectral_r",
        "vmin": 0,
        "vmax": 60,
    },
    {
        "title": "850hPa Vorticity & Height",
        "unit": "1e-6 s-1",
        "level": Level.Hpa850,
        "plot_func_key": "vorticity",
        "cmap": "YlOrBr",
        "vmin": 0,
        "vmax": 200,
    },
    {
        "title": "925hPa Temp & 10m Wind",
        "unit": "K",
        "level": Level.Hpa925,
        "plot_func_key": "temperature",
        "cmap": "coolwarm",
        "vmin": 270,
        "vmax": 310,
    },
    {
        "title": "925hPa Qw & 10m Wind",
        "unit": "g kg-1",
        "level": Level.Hpa925,
        "plot_func_key": "hydrometeors_mixing_ratio",
        "cmap": "GnBu_r",
        "vmin": 0,
        "vmax": 4,
    },
]
