from __future__ import annotations

from enum import Enum


class DataType(Enum):
    def __new__(cls, short_name: str, description: str, nc_key: str):
        obj = object.__new__(cls)
        obj._value_ = (short_name, description, nc_key)
        return obj

    @property
    def short_name(self):
        return self.value[0]

    @property
    def description(self):
        return self.value[1]

    @property
    def nc_key(self):
        return self.value[2]

    # var_name = (short_name, description, nc_key)
    PH = ("PH", "Geopotential Height", "z_p")
    P = ("P", "Pressure Level", "pres_levels")
    TK = ("TK", "Temperature", "tk_p")
    UM = ("UM", "U-wind", "umet_p")
    VM = ("VM", "V-wind", "vmet_p")
    WA = ("WA", "W-wind", "wa_p")
    Qv = ("Qv", "Water Vapor Mixing Ratio", "QVAPOR_p")
    Qr = ("Qr", "Rain Water Mixing Ratio", "QRAIN_p")
    Qs = ("Qs", "Snow Mixing Ratio", "QSNOW_p")
    Qg = ("Qg", "Graupel Mixing Ratio", "QGRAUP_p")
    Qc = ("Qc", "Cloud Water Mixing Ratio", "QCLOUD_p")
    Qi = ("Qi", "Ice Mixing Ratio", "QICE_p")
    Qt = ("Qt", "Total Hydrometeors Mixing Ratio", "QTOTAL_p")
    RH = ("RH", "Relative Humidity", "rh")
    Td = ("Td", "Dew Point Temperature", "td")
    SLP = ("SLP", "Sea Level Pressure", "slp")
    SST = ("SST", "SST", "SST")
    PSFC = ("PSFC", "Surface Pressure", "PSFC")
    PW = ("PW", "Precipitable Water", "pw")
    PBLH = ("PBLH", "PBL Height", "PBLH")
    RAINNC = ("RAINNC", "Accumulated Precipitation", "RAINNC")
    SWDOWN = ("SWDOWN", "Downward Shortwave Flux", "SWDOWN")
    OLR = ("OLR", "Outgoing Longwave Radiation", "OLR")
    Lat = ("Lat", "Latitude", "XLAT")
    Lon = ("Lon", "Longitude", "XLONG")
    MASK = ("MASK", "Land-Sea Mask", "LANDMASK")
    HGT = ("HGT", "Terrain Height", "HGT")
    Radar = ("Radar", "Maximum Radar Reflectivity", "MAX_REFL")
    dBZ = ("dBZ", "Radar Reflectivity", "REFL_p")


class Level(Enum):
    def __new__(cls, description: str, code: str, nc_key: str):
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
