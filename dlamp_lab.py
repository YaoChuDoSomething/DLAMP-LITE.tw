import os
from datetime import datetime
import numpy as np
import torch
from earth2studio.data import GFS
from earth2studio.models.px import SFNO
from earth2studio.io import XarrayBackend

# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load SFNO model
print("Loading SFNO model...")
package = SFNO.load_default_package()
model = SFNO.load_model(package).to(device)
print("SFNO model loaded.")
print(f"SFNO input variables: {model.input_variables()}")

# Set up forecast parameters
init_time = datetime(2022, 9, 11, 0, 0, 0)
num_steps = 8  # 48 hours forecast with 6-hour timestep
time_step = np.timedelta64(6, "h")

# Fetch initial conditions from GFS
print(f"Fetching initial conditions for {init_time} from GFS...")
data_source = GFS()
x = data_source.fetch(
    time=init_time,
    variable=model.input_variables(),
    )
x = x.to(device)
print("Initial conditions fetched.\n")

# Initialize IO backend
io = XarrayBackend()

# Save initial condition
io(init_time, model.output_variables(), x)

# Run prognostic loop
print("Starting 48-hour forecast...")
for i in range(num_steps):
    current_time = init_time + i * time_step
    
    # Model forward pass
    x = model(x, current_time)
    
    # Save output
    output_time = current_time + time_step
    io(output_time, model.output_variables(), x)
    print(f"Forecast step {i+1}/{num_steps} complete for time {output_time}")

print("\nForecast finished.")

# Retrieve and inspect the forecast data
forecast_data = io.to_xarray()
print("\nForecast data:\n", forecast_data)
