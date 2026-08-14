# DLAMP Output Variable Registry

Statues: Proposed (build prerequisite for Q8 `DataPipelineConfig`)

Purpose: define the physical quantities the model is *likely* to emit, decoupled
from any ERA5/WRF file convention. Every variable is described with CF-Conventions
NetCDF metadata (or an extended definition where CF has no exact match).

## Column reference

| Column         | Meaning                                                       |
| -------------- | ------------------------------------------------------------- |
| enum           | Machine member name for code dispatch                         |
| shortname      | Canonical short symbol used in `nc_key` pattern               |
| standard_name  | CF-Conventions `standard_name` (or extended form, prefixed `cf:`) |
| description    | CF `long_name` descriptive text                               |
| units          | CF `units` (UDUNITS), `-` when dimensionless/flag               |
| nc_key         | NetCDF output variable name (naming scheme below)             |

## nc_key naming scheme

Patterns (level-stamped fields reuse the same `shortname`, level varies):

| Kind                                   | Pattern                            | Example |
| -------------------------------------- | ---------------------------------- | ------- |
| 1D latitude coordinate (strictly inc.) | `lat`                              | `lat`   |
| 1D longitude coordinate (strictly inc.)| `lon`                              | `lon`   |
| 2D lat meshgrid                        | `XLAT`                             | `XLAT`  |
| 2D lon meshgrid                        | `XLON`                             | `XLON`  |
| Pressure-coordinate 2D field           | `{shortname}_{pressure_in_hPa}`    | `TK_850`|
| AGL-coordinate 2D field                | `{shortname}_{height_in_m}m`       | `T_2m`  |
| Other horizontal-layer field           | `{shortname}`                      | `RAINNC`|

Coordinate notes:
- `lat`/`lon` MUST be 1-D, strictly monotonic in a single direction.
- `XLAT`/`XLON` are 2-D meshgrid projections of `lat`/`lon`.

## Pressure-level fields (3-D: lat × lon × level)

| enum | shortname | standard_name               | description            | units    | nc_key pattern |
| ---- | --------- | --------------------------- | ---------------------- | -------- | -------------- |
| TK   | TK        | `air_temperature`           | Temperature            | `K`      | `TK_{hPa}`     |
| Z    | Z         | `geopotential_height`       | Geopotential height    | `m`      | `Z_{hPa}`      |
| UM   | UM        | `eastward_wind`             | U-wind component       | `m s-1`  | `UM_{hPa}`     |
| VM   | VM        | `northward_wind`            | V-wind component       | `m s-1`  | `VM_{hPa}`     |
| WA   | WA        | `upward_air_velocity`       | W-wind (vertical) comp.| `m s-1`  | `WA_{hPa}`     |
| RH   | RH        | `relative_humidity`         | Relative humidity      | `%`      | `RH_{hPa}`     |
| Qv   | Qv        | `water_vapor_mixing_ratio`  | Water-vapor mixing ratio | `kg kg-1` | `Qv_{hPa}`  |
| Qc   | Qc        | `cloud_water_mixing_ratio`  | Cloud-water mix ratio  | `kg kg-1`| `Qc_{hPa}`     |
| Qi   | Qi        | `cf:cloud_ice_mixing_ratio` | Cloud-ice mix ratio   | `kg kg-1`| `Qi_{hPa}`     |
| Qr   | Qr        | `cf:rain_water_mixing_ratio`| Rain-water mix ratio  | `kg kg-1`| `Qr_{hPa}`     |
| Qs   | Qs        | `cf:snow_mixing_ratio`      | Snow mix ratio         | `kg kg-1`| `Qs_{hPa}`     |
| Qg   | Qg        | `cf:graupel_mixing_ratio`   | Graupel mix ratio      | `kg kg-1`| `Qg_{hPa}`     |

> Qt (total hydrometeors mixing ratio) is a **model input**, not an output. It
> MUST be read directly from the source data, never derived from other variables.
> Any conversion/diagnostic that computes a needed field from other physics lives
> in a data plugin under `src/dlamp/data/` (see that module's docs), kept out of
> the output registry.

## AGL fields (height above ground level)

| enum | shortname | standard_name        | description        | units   | nc_key       |
| ---- | --------- | -------------------- | ------------------ | ------- | ------------ |
| T2m  | T         | `air_temperature`    | Air temperature    | `K`     | `T_2m`       |
| Td2m | Td        | `dew_point_temperature` | Dew-point temperature | `K`  | `Td_2m`   |
| U10m | U         | `eastward_wind`      | U-wind component   | `m s-1` | `U_10m`      |
| V10m | V         | `northward_wind`     | V-wind component   | `m s-1` | `V_10m`      |

## Other horizontal-layer fields (single level)

| enum    | shortname | standard_name                       | description                         | units      | nc_key |
| ------- | --------- | ----------------------------------- | ----------------------------------- | ---------- | ------ |
| SLP     | SLP       | `air_pressure_at_sea_level`         | Sea-level pressure                  | `Pa`       | SLP    |
| PSFC    | PSFC      | `surface_air_pressure`              | Surface pressure                    | `Pa`       | PSFC   |
| SST     | SST       | `sea_surface_temperature`           | Sea-surface temperature             | `K`        | SST    |
| PW      | PW        | `atmosphere_mass_content_of_water_vapor` | Precipitable-water column     | `kg m-2`   | PW     |
| PBLH    | PBLH      | `atmosphere_boundary_layer_thickness` | Planetary boundary-layer height    | `m`        | PBLH   |
| RAINNC  | RAINNC    | `precipitation_amount`              | Accumulated precipitation           | `kg m-2`   | RAINNC |
| SWDOWN  | SWDOWN    | `surface_downwelling_shortwave_flux_in_air` | Downward shortwave flux    | `W m-2`    | SWDOWN |
| OLR     | OLR       | `toa_outgoing_longwave_flux`        | Outgoing longwave radiation         | `W m-2`    | OLR    |
| HGT     | HGT       | `surface_altitude`                  | Terrain height                      | `m`        | HGT    |
| MASKLAND| MASKLAND  | `cf:land_binary_mask`               | Land-sea mask (bool: true land, false sea) | `1`    | LANDMASK |
| dBZ     | REFL      | `radar_reflectivity`                | Max column radar reflectivity | `dBZ`      | REFL   |

## Coordinates

| enum | shortname | standard_name | description            | units        | nc_key |
| ---- | --------- | ------------- | ---------------------- | ------------ | ------ |
| Lat  | lat       | `latitude`    | Latitude (1-D, inc.)   | `degrees_north` | lat  |
| Lon  | lon       | `longitude`   | Longitude (1-D, inc.)  | `degrees_east` | lon  |
| XLAT | XLAT      | `latitude`    | Latitude meshgrid (2-D)| `degrees_north` | XLAT  |
| XLON | XLON      | `longitude`   | Longitude meshgrid (2-D)| `degrees_east` | XLON  |

## Notes / open questions

- `cf:` prefix marks extended definitions not in the canonical CF standard.
- Qt (total hydrometeors) is retained as a genuine model output.
- dBZ is a single-layer field: the maximum reflectivity evaluated across the
  vertical column (`MAX_REFL` in WRF terms); `nc_key` = `REFL`, not per-level.