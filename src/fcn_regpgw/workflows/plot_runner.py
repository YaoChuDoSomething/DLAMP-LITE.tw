"""Plotting and visualization workflow runner for FCN-RegPGW.

Orchestrates batch generation of meteorological contour charts from forecast
output directories and optional compilation into video animations.
"""

import re
from pathlib import Path

import numpy as np

from fcn_regpgw.config import PlotConfig
from fcn_regpgw.utils.file_util import ensure_dir
from fcn_regpgw.utils.logging_util import get_logger
from fcn_regpgw.visual.animation import AnimationExporter
from fcn_regpgw.visual.coastlines import CoastlineProvider
from fcn_regpgw.visual.plotter import WeatherPlotter

logger = get_logger(__name__)


class PlotRunner:
    """Workflow runner for batch meteorological plotting and animation rendering."""

    def __init__(self, config: PlotConfig | None = None) -> None:
        """Initialize PlotRunner.

        Args:
            config (Optional[PlotConfig]): Plotting and export configuration.
        """
        self.config = config or PlotConfig()
        coast_provider = (
            CoastlineProvider(self.config.coast_csv_path)
            if self.config.coast_csv_path
            else None
        )
        self.plotter = WeatherPlotter(coastline_provider=coast_provider)

    def run(
        self,
        var_type: str = "wsp850",
    ) -> list[Path]:
        """Execute batch plotting on forecast state files in data directory.

        Args:
            var_type (str): Target field to plot ('wsp850' or 'precip').

        Returns:
            List[Path]: List of generated plot figure image paths.

        Raises:
            FileNotFoundError: If input data directory has no forecast files.
        """
        in_dir = Path(self.config.data_dir)
        out_dir = ensure_dir(self.config.output_dir)

        prefix = "output_precip_" if var_type == "precip" else "output_weather_"
        files = sorted(in_dir.glob(f"{prefix}*.npy"))

        if not files:
            logger.warning(
                "No forecast files found matching pattern '%s*.npy' in %s",
                prefix,
                in_dir,
            )
            return []

        logger.info(
            "Found %d forecast files for batch plotting in %s",
            len(files),
            in_dir,
        )
        generated_plots: list[Path] = []

        for f in files:
            # Extract lead hour
            match = re.search(r"(\d+)h", f.name)
            lead_hour = int(match.group(1)) if match else 0

            data = np.load(f)
            out_png = out_dir / f"{f.stem}.png"

            if var_type == "precip":
                self.plotter.plot_precipitation(
                    precip_data=data,
                    lead_hour=lead_hour,
                    output_file=out_png,
                )
            else:
                self.plotter.plot_wind_speed_850(
                    weather_data=data,
                    lead_hour=lead_hour,
                    output_file=out_png,
                )
            generated_plots.append(out_png)

        # Video export if requested
        if self.config.export_mp4 and generated_plots:
            AnimationExporter.export_video(
                image_paths=generated_plots,
                output_video_path=self.config.mp4_path,
                fps=self.config.fps,
            )

        return generated_plots
