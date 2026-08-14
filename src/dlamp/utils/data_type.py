from __future__ import annotations

from enum import Enum
from typing import Self, cast


class DataType(Enum):
    def __new__(
        cls,
        short_name: str,
        standard_name: str,
        description: str,
        units: str,
        nc_key: str,
    ) -> Self:
        obj = object.__new__(cls)
        obj._value_ = (short_name, standard_name, description, units, nc_key)
        return obj

    @property
    def short_name(self) -> str:
        return cast(str, self.value[0])

    @property
    def standard_name(self) -> str:
        return cast(str, self.value[1])

    @property
    def description(self) -> str:
        return cast(str, self.value[2])

    @property
    def units(self) -> str:
        return cast(str, self.value[3])

    @property
    def nc_key(self) -> str:
        return cast(str, self.value[4])

    # Coordinates
    # fmt: off
    # (short_name, standard_name, description, units, nc_key)
    Lat   = ("lat",   "latitude",  "Latitude (1-D, monotonic increasing)",  "degrees_north", "lat")
    Lon   = ("lon",   "longitude", "Longitude (1-D, monotonic increasing)", "degrees_east",  "lon")
    XLAT  = ("XLAT",  "latitude",  "Latitude meshgrid (2-D)",               "degrees_north", "XLAT")
    XLON  = ("XLON",  "longitude", "Longitude meshgrid (2-D)",              "degrees_east",  "XLON")

    # Pressure-level fields (nc_key = {shortname}_{hPa})
    TK  = ("TK",  "air_temperature",                  "Temperature",                      "K",       "TK")
    Z   = ("Z",   "geopotential_height",              "Geopotential height",              "m",       "Z")
    UM  = ("UM",  "eastward_wind",                    "U-wind component",                 "m s-1",   "UM")
    VM  = ("VM",  "northward_wind",                   "V-wind component",                 "m s-1",   "VM")
    WA  = ("WA",  "upward_air_velocity",              "W-wind (vertical) component",      "m s-1",   "WA")
    RH  = ("RH",  "relative_humidity",                "Relative humidity",                "%",       "RH")
    Qv  = ("Qv",  "water_vapor_mixing_ratio",         "Water-vapor mixing ratio",         "kg kg-1", "Qv")
    Qc  = ("Qc",  "cloud_water_mixing_ratio",         "Cloud-water mixing ratio",         "kg kg-1", "Qc")
    Qi  = ("Qi",  "cf:cloud_ice_mixing_ratio",        "Cloud-ice mixing ratio",           "kg kg-1", "Qi")
    Qr  = ("Qr",  "cf:rain_water_mixing_ratio",       "Rain-water mixing ratio",          "kg kg-1", "Qr")
    Qs  = ("Qs",  "cf:snow_mixing_ratio",             "Snow mixing ratio",                "kg kg-1", "Qs")
    Qg  = ("Qg",  "cf:graupel_mixing_ratio",          "Graupel mixing ratio",             "kg kg-1", "Qg")

    # AGL fields (nc_key = {shortname}_{height_in_m}m)
    T2m  = ("T",  "air_temperature",        "Air temperature",           "K",       "T_2m")
    Td2m = ("Td", "dew_point_temperature",  "Dew-point temperature",     "K",       "Td_2m")
    U10m = ("U",  "eastward_wind",          "U-wind component",          "m s-1",   "U_10m")
    V10m = ("V",  "northward_wind",         "V-wind component",          "m s-1",   "V_10m")

    # Other single-level horizontal fields
    SLP      = ("SLP",     "air_pressure_at_sea_level",         "Sea-level pressure",            "Pa",      "SLP")
    PSFC     = ("PSFC",    "surface_air_pressure",              "Surface pressure",              "Pa",      "PSFC")
    SST      = ("SST",     "sea_surface_temperature",           "Sea-surface temperature",       "K",       "SST")
    PW       = ("PW",      "atmosphere_mass_content_of_water_vapor", "Precipitable-water column", "kg m-2",  "PW")
    PBLH     = ("PBLH",    "atmosphere_boundary_layer_thickness", "Planetary boundary-layer height", "m",  "PBLH")
    RAINNC   = ("RAINNC",  "precipitation_amount",              "Accumulated precipitation",     "kg m-2",  "RAINNC")
    SWDOWN   = ("SWDOWN",  "surface_downwelling_shortwave_flux_in_air", "Downward shortwave flux", "W m-2",  "SWDOWN")
    OLR      = ("OLR",     "toa_outgoing_longwave_flux",        "Outgoing longwave radiation",   "W m-2",   "OLR")
    HGT      = ("HGT",     "surface_altitude",                  "Terrain height",                "m",       "HGT")
    MASKLAND = ("MASKLAND", "cf:land_binary_mask",              "Land-sea mask (bool)",          "1",       "LANDMASK")
    dBZ      = ("REFL",    "radar_reflectivity",                "Max column radar reflectivity", "dBZ",     "REFL")

    # Model input: read directly from source, never derived (no diagnostic).
    Qt = ("Qt", "cf:total_hydrometeor_mixing_ratio", "Total hydrometeor mixing ratio", "kg kg-1", "Qt")

    # Pressure coordinate (not a model output): source pressure-level array, used
    # only to map a level to its index when reading a pressure-level field.
    P = ("P", "air_pressure", "Pressure coordinate", "Pa", "pres_levels")
    # fmt: on


class Level(Enum):
    code: str
    nc_key: str

    def __new__(cls, description: str, code: str, nc_key: str) -> Self:
        obj = object.__new__(cls)
        obj._value_ = description
        obj.code = code
        obj.nc_key = nc_key
        return obj

    # level_name = (description, code, nc_key)
    Hpa50 = ("50 Hpa", "50", "50")
    Hpa100 = ("100 Hpa", "100", "100")
    Hpa150 = ("150 Hpa", "150", "150")
    Hpa200 = ("200 Hpa", "200", "200")
    Hpa250 = ("250 Hpa", "250", "250")
    Hpa300 = ("300 Hpa", "300", "300")
    Hpa350 = ("350 Hpa", "350", "350")
    Hpa400 = ("400 Hpa", "400", "400")
    Hpa450 = ("450 Hpa", "450", "450")
    Hpa500 = ("500 Hpa", "500", "500")
    Hpa550 = ("550 Hpa", "550", "550")
    Hpa600 = ("600 Hpa", "600", "600")
    Hpa650 = ("650 Hpa", "650", "650")
    Hpa700 = ("700 Hpa", "700", "700")
    Hpa750 = ("750 Hpa", "750", "750")
    Hpa800 = ("800 Hpa", "800", "800")
    Hpa850 = ("850 Hpa", "850", "850")
    Hpa900 = ("900 Hpa", "900", "900")
    Hpa925 = ("925 Hpa", "925", "925")
    Hpa950 = ("950 Hpa", "950", "950")
    Hpa975 = ("975 Hpa", "975", "975")
    Hpa1000 = ("1000 Hpa", "H00", "1000")
    LowestModelLevel = ("Lowest Model Level", "B00", "")
    Meter2 = ("2 m", "B02", "2")
    Meter10 = ("10 m", "B10", "10")
    Meter100 = ("100 m", "H10", "")
    Surface = ("Surface", "S00", "")
    SeaSurface = ("Sea Surface", "W00", "")
    TOA = ("Top Of Atmosphere", "W00", "")
    NoRule = ("NoRule", "X00", "")

    def is_surface(self) -> bool:
        return self in [
            self.LowestModelLevel,
            self.Meter2,
            self.Meter10,
            self.Meter100,
            self.Surface,
            self.SeaSurface,
            self.TOA,
            self.NoRule,
        ]
