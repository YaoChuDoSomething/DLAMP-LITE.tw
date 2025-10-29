# %%
"""
Running Deterministic Inference
===============================

Basic deterministic inference workflow.

This example will demonstrate how to run a simple inference workflow to generate a
basic determinstic forecast using one of the built in models of Earth-2 Inference
Studio.

In this example you will learn:

- How to instantiate a built in prognostic model
- Creating a data source and IO object
- Running a simple built in workflow
- Post-processing results
"""

# %%
#
# - Prognostic Model: Use the built in FourCastNet Model :py:class:`earth2studio.models.px.SFNO`.
# - Datasource: Pull data from the GFS data api :py:class:`earth2studio.data.GFS`.
# - IO Backend: Let's save the outputs into a Zarr store :py:class:`earth2studio.io.NetCDF4Backend`.

# %%    # built-in / package / inner-module
import os
from collections import OrderedDict
from datetime import datetime

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import torch
from dotenv import load_dotenv
from loguru import logger
from tqdm import tqdm

from earth2studio.data import GFS, fetch_data
from earth2studio.io import NetCDF4Backend
from earth2studio.models.px import SFNO
from earth2studio.utils.coords import CoordSystem, map_coords, split_coords
from earth2studio.utils.time import to_time_array

os.makedirs("outputs", exist_ok=True)
load_dotenv()  # TODO: make common example prep function

# Load the default model package which downloads the check point from NGC
package = SFNO.load_default_package()
model = SFNO.load_model(package)

# Create the data source
data = GFS()

# Create the IO handler, store in memory
io = NetCDF4Backend(file_name="outputs/sfno_oneway.nc", backend_kwargs={"mode": "w"})

# %%
# Execute the Workflow
# --------------------
# With all components initialized, running the workflow is a single line of Python code.
# Workflow will return the provided IO object back to the user, which can be used to
# then post process. Some have additional APIs that can be handy for post-processing or
# saving to file. Check the API docs for more information.
#
# For the forecast we will predict for two days (these will get executed as a batch) for
# 20 forecast steps which is 5 days.

# %%
nsteps = 8
init_time_str = "2022-09-11 00:00"
timefmt = "%Y-%m-%d %H:%M"
init_time = [datetime.strptime(init_time_str, timefmt)]

# io = run.deterministic(init_time, nsteps, model, data, io) is not allowed to use it.
# breakdown the `run.deterministic` as below:

logger.remove()
logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)


logger.info("Running simple workflow!")
# Load model onto the device
device = None
device = (
    device
    if device is not None
    else torch.device("cuda" if torch.cuda.is_available() else "cpu")
)
logger.info(f"Inference device: {device}")
model = model.to(device)

output_coords = OrderedDict({})
    
    # Fetch data from data source and load onto device
SFNO_ic = model.input_coords()
time = to_time_array(init_time)

if hasattr(model, "interp_method"):
    interp_to = SFNO_ic
    interp_method = model.interp_method
else:
    interp_to = None
    interp_method = "nearest"

x, coords = fetch_data(
    source=data,
    time=time,
    variable=SFNO_ic["variable"],
    lead_time=SFNO_ic["lead_time"],
    device=device,
    interp_to=interp_to,
    interp_method=interp_method,
)

logger.success(f"Fetched data from {data.__class__.__name__}")

print("x, coords = ", np.shape(x), coords)

# Set up IO backend
total_coords = model.output_coords(model.input_coords()).copy()

print("total_coords = ", total_coords)
for key, value in model.output_coords(
    model.input_coords()
).items():  # Scrub batch dims
    if value.shape == (0,):
        del total_coords[key]
total_coords["time"] = time
total_coords["lead_time"] = np.asarray(
    [
        model.output_coords(model.input_coords())["lead_time"] * i
        for i in range(nsteps + 1)
    ]
).flatten()
total_coords.move_to_end("lead_time", last=False)
total_coords.move_to_end("time", last=False)

for key, value in total_coords.items():
    total_coords[key] = output_coords.get(key, value)
var_names = total_coords.pop("variable")
io.add_array(total_coords, var_names)

print("input coords = ", model.input_coords())

# Map lat and lon if needed
x, coords = map_coords(x, coords, model.input_coords())


# Create SFNO iterator =================================
model = model.create_iterator(x, coords)

logger.info("Inference starting!")
with tqdm(total=nsteps + 1, desc="Running inference", position=1) as pbar:
    for step, (x, coords) in enumerate(model):
        # Subselect domain/variables as indicated in output_coords
        x, coords = map_coords(x, coords, output_coords)
        io.write(*split_coords(x, coords))
        pbar.update(1)
        if step == nsteps:
            break

logger.success("Inference complete")



#print(io.root.tree())

# %%
# Post Processing
# ---------------
# The last step is to post process our results. Cartopy is a great library for plotting
# fields on projections of a sphere. Here we will just plot the temperature at 2 meters
# (t2m) 1 day into the forecast.
#
# Notice that the NetCDF4Backend IO function has additional APIs to interact with the stored data.

# %%
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

forecast = "2024-01-01"
variable = "t2m"
for step in range(nsteps):
    #step = 4  # lead time = 24 hrs

    plt.close("all")
    # Create a Robinson projection
    projection = ccrs.Robinson()

    # Create a figure and axes with the specified projection
    fig, ax = plt.subplots(subplot_kw={"projection": projection}, figsize=(10, 6))

    # Plot the field using pcolormesh
    im = ax.pcolormesh(
        io["lon"][:],
        io["lat"][:],
        io[variable][0, step],
        transform=ccrs.PlateCarree(),
        cmap="Spectral_r",
    )

    # Set title
    ax.set_title(f"{forecast} - Lead time: {6*step}hrs")

    # Add coastlines and gridlines
    ax.coastlines()
    ax.gridlines()
    plt.savefig(f"outputs/t2m_f{step:03d}H.jpg")

