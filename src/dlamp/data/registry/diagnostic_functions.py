import numpy as np
import xarray as xr


def _create_dataarray(
    data: np.ndarray,
    ds: xr.Dataset,
    var_name: str,
    long_name: str,
    units: str,
) -> xr.DataArray:
    """Build an xarray DataArray with standard coordinates and metadata."""

    # setup default coords
    coords = {"Time": ds["Time"]}
    # coords["pres_bottom_top"] = {}
    dims = ["Time"]

    if var_name == "pres_levels":
        dims.append("pres_bottom_top")
        coords["pres_bottom_top"] = ds["pres_bottom_top"]

    elif var_name in ["XLONG_C", "XLAT_C"]:
        dims += ["corner_south_north", "corner_west_east"]
        coords["corner_south_north"] = ("corner_south_north", np.linspace(-450, 450, 451))
        coords["corner_west_east"] = ("corner_west_east", np.linspace(-450, 450, 451))

    elif data.ndim == 3:
        dims += ["pres_bottom_top", "south_north", "west_east"]
        coords.update(
            {
                "pres_bottom_top": ds["pres_bottom_top"],
                "south_north": ds["south_north"],
                "west_east": ds["west_east"],
            }
        )

    elif data.ndim == 2:
        dims += ["south_north", "west_east"]
        coords.update(
            {
                "south_north": ds["south_north"],
                "west_east": ds["west_east"],
            }
        )

    return xr.DataArray(
        np.expand_dims(data, axis=0).astype(np.float32),
        coords=coords,
        dims=dims,
        name=var_name,
        attrs={
            "long_name": long_name,
            "units": units,
            # "dtype": str(data.dtype),
        },
    )


def sat_vapor_pressure_water(T):  # T in Celsius
    return 6.112 * np.exp((17.67 * T) / (T + 243.5))  # hPa


def diag_z_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Geopotential height = geopotential / g

    """
    g = 9.80665  # Standard gravity constant

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["z"].values) / g
            nc_key = "z_p"

        case "ERA5_r":
            data = np.squeeze(ds["z_p"].values) * g
            nc_key = "z"

        case "RWRF":
            data = np.squeeze(ds["z_p"].values)
            nc_key = "z_p"

        case _:
            data = np.nan
            nc_key = "z"

    return _create_dataarray(data, ds, nc_key, "Geopotential Height", "m")


def diag_tk_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Air Temperature [K]

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["t"].values)

        case "ERA5_r":
            data = np.squeeze(ds["tk_p"].values)

        case "RWRF":
            data = np.squeeze(ds["tk_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "tk_p", "Air Temperature", "K")


def diag_umet_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    U-component of wind (Earth-rotated)

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["u"].values)
            nc_key = "umet_p"

        case "ERA5_r":
            data = np.squeeze(ds["umet_p"].values)
            nc_key = "u"

        case "RWRF":
            data = np.squeeze(ds["umet_p"].values)
            nc_key = "umet_p"

        case _:
            data = np.nan

    return _create_dataarray(data, ds, nc_key, "U-component of Wind", "m s-1")


def diag_vmet_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    V-component of wind (Earth-rotated)

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["v"].values)
            nc_key = "vmet_p"

        case "ERA5_r":
            data = np.squeeze(ds["vmet_p"].values)
            nc_key = "v"

        case "RWRF":
            data = np.squeeze(ds["vmet_p"].values)
            nc_key = "vmet_p"

        case _:
            data = np.nan

    return _create_dataarray(data, ds, nc_key, "V-component of Wind", "m s-1")


def diag_QVAPOR_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Specific humidity to water vapor mixing ratio

    """

    match source_dataset:
        case "ERA5":
            if "q" in ds:
                q = np.squeeze(ds["q"].values)
                data = q / (1 - q)
            elif "r" in ds and "t" in ds and "pres_levels" in ds:
                # Convert relative humidity to mixing ratio
                rh = np.squeeze(ds["r"].values) / 100.0  # convert to fraction
                t = np.squeeze(ds["t"].values)  # temperature in Kelvin
                p = np.squeeze(ds["pres_levels"].values) * 100  # pressure in Pa

                # Convert temperature to Celsius for vapor pressure calculation
                t_celsius = t - 273.15

                # Saturation vapor pressure (hPa)
                es = sat_vapor_pressure_water(t_celsius)

                # Actual vapor pressure (hPa)
                e = rh * es

                # Mixing ratio
                data = (0.622 * e) / (p / 100.0 - e)  # p/100.0 to convert Pa to hPa
            else:
                data = np.nan

        case "RWRF":
            data = np.squeeze(ds["QVAPOR_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "QVAPOR_p", "Water Vapor Mixing Ratio", "kg kg-1")


def diag_QRAIN_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Specific rain water content to rain water mixing ratio

    """

    match source_dataset:
        case "ERA5":
            q = np.squeeze(ds["crwc"].values)
            data = q / (1 - q)

        case "RWRF":
            data = np.squeeze(ds["QRAIN_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "QRAIN_p", "Rain Water Mixing Ratio", "kg kg-1")


def diag_QCLOUD_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Specific cloud liquid water content to cloud water mixing ratio

    """

    match source_dataset:
        case "ERA5":
            q = np.squeeze(ds["clwc"].values)
            data = q / (1 - q)

        case "RWRF":
            data = np.squeeze(ds["QCLOUD_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "QCLOUD_p", "Cloud Water Mixing Ratio", "kg kg-1")


def diag_QSNOW_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Specific snow water content to snow water mixing ratio

    """

    match source_dataset:
        case "ERA5":
            q = np.squeeze(ds["cswc"].values)
            data = q / (1 - q)

        case "RWRF":
            data = np.squeeze(ds["QSNOW_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "QSNOW_p", "Snow Water Mixing Ratio", "kg kg-1")


def diag_QICE_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Specific cloud ice content to cloud ice mixing ratio

    """

    match source_dataset:
        case "ERA5":
            q = np.squeeze(ds["ciwc"].values)
            data = q / (1 - q)

        case "RWRF":
            data = np.squeeze(ds["QICE_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "QICE_p", "Cloud Ice Mixing Ratio", "kg kg-1")


def diag_QGRAUP_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Specific graupel water content to graupel water mixing ratio

    """

    match source_dataset:
        case "ERA5":
            q = np.squeeze(ds["q"].values) * 0
            data = q / (1 - q)

        case "RWRF":
            data = np.squeeze(ds["QGRAUP_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "QGRAUP_p", "Graupel Water Mixing Ratio", "kg kg-1")


def diag_QTOTAL_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Total hydrometeors mixing ratio

    """

    match source_dataset:
        case "ERA5":
            qlist = ["clwc", "crwc", "ciwc", "cswc"]
            # Convert each specific humidity to mixing ratio first, then sum them up.
            mixing_ratios = [np.squeeze(ds[q].values) / (1 - np.squeeze(ds[q].values)) for q in qlist]
            data = sum(mixing_ratios)
            nc_key = "QTOTAL_p"

        case "RWRF":
            qlist = ["QCLOUD_p", "QRAIN_p", "QICE_p", "QSNOW_p", "QGRAUP_p"]
            data = sum(np.squeeze(ds[q].values) for q in qlist)
            nc_key = "QTOTAL_p"
        case _:
            data = np.nan

    return _create_dataarray(data, ds, nc_key, "Total Hydrometeors Mixing Ratio", "kg kg-1")


def diag_wa_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    omega [Pa s-1] to w [m s-1]

    """
    Rd = 287.058  # Dry air gas constant J/(kg K)
    g = 9.80665  # Standard gravity constant

    match source_dataset:
        case "ERA5":
            omega = np.squeeze(ds["w"].values)
            tmk = np.squeeze(ds["t"].values)
            plev = np.squeeze(ds["pres_levels"].values * 100)  # pressure in Pa

            if "q" in ds:
                q = np.squeeze(ds["q"].values)
                qvp = q / (1 - q)
            elif "r" in ds and "t" in ds and "pres_levels" in ds:
                # Convert relative humidity to mixing ratio
                rh = np.squeeze(ds["r"].values) / 100.0  # convert to fraction
                t_celsius = tmk - 273.15  # temperature in Celsius

                # Saturation vapor pressure (hPa)
                es = sat_vapor_pressure_water(t_celsius)

                # Actual vapor pressure (hPa)
                e = rh * es

                # Mixing ratio
                qvp = (0.622 * e) / (plev / 100.0 - e)  # plev/100.0 to convert Pa to hPa
            else:
                qvp = np.zeros_like(tmk)  # Default to 0 if no humidity data

            t_virt = tmk * (1 + 0.61 * qvp)

            prs = np.zeros(np.shape(tmk))
            for pl in range(len(plev)):
                prs[pl] = plev[pl]

            data = -1 * omega * Rd * t_virt / prs / g

        case "RWRF":
            data = np.squeeze(ds["wa_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "wa_p", "Vertical Velocity", "m s-1")


def diag_T2(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Air Temperature at 2 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["2t"].values)

        case "RWRF":
            data = np.squeeze(ds["T2"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "T2", "2m Temperature", "K")


def diag_Q2(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    water vapor mixing ratio at 2 m height above surface

    """

    match source_dataset:
        case "ERA5":
            td2 = np.squeeze(ds["2d"].values)
            sp = np.squeeze(ds["sp"].values)
            e = sat_vapor_pressure_water(td2 - 273.15) * 100  # [Pa]
            data = (0.622 * e) / (sp - e)

        case "RWRF":
            data = np.squeeze(ds["Q2"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "Q2", "2m Mixing Ratio", "kg kg-1")


def diag_rh2(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    relative humidity at 2 m height above surface

    """

    match source_dataset:
        case "ERA5":
            td2 = np.squeeze(ds["2d"].values)
            t2 = np.squeeze(ds["2t"].values)
            e = sat_vapor_pressure_water(td2 - 273.15) * 100  # [Pa]
            esat = sat_vapor_pressure_water(t2 - 273.15) * 100  # [Pa]
            data = e / esat * 100

        case "RWRF":
            data = np.squeeze(ds["rh2"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "rh2", "2m Relative Humidity", "%")


def diag_td2(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    dew-point temperature at 2 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["2d"].values)

        case "RWRF":
            data = np.squeeze(ds["td2"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "td2", "2m Dew Point Temperature", "K")


def diag_umet10(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    U-wind at 10 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["10u"].values)

        case "RWRF":
            data = np.squeeze(ds["umet10"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "umet10", "10m U-component of Wind", "m s-1")


def diag_vmet10(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    V-wind at 10 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["10v"].values)

        case "RWRF":
            data = np.squeeze(ds["vmet10"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "vmet10", "10m V-component of Wind", "m s-1")


def diag_umet100(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    U-wind at 100 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["100u"].values)
            nc_key = "umet100"

        case "ERA5_r":
            data = np.squeeze(ds["umet100"].values)
            nc_key = "u100m"

        case "RWRF":
            data = np.squeeze(ds["umet100"].values)
            nc_key = "umet100"

        case _:
            data = np.nan
            nc_key = "umet100"

    return _create_dataarray(data, ds, nc_key, "100m U-component of Wind", "m s-1")


def diag_vmet100(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    V-wind at 100 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["100v"].values)
            nc_key = "vmet100"

        case "ERA5_r":
            data = np.squeeze(ds["vmet100"].values)
            nc_key = "v100m"

        case "RWRF":
            data = np.squeeze(ds["vmet100"].values)
            nc_key = "vmet100"

        case _:
            data = np.nan
            nc_key = "vmet100"

    return _create_dataarray(data, ds, nc_key, "100m V-component of Wind", "m s-1")


def diag_slp(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    sea-level pressure at surface [hPa]

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["msl"].values) / 100.0

        case "ERA5_r":
            data = np.squeeze(ds["slp"].values) * 100.0

        case "RWRF":
            data = np.squeeze(ds["slp"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "slp", "Sea Level Pressure", "hPa")


def diag_SST(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    sea surface temperature

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["sst"].values)
            nc_key = "SST"
            # sst[np.isnan(sst)] = np.nanmean(sst.ravel())
            # data = sst

        case "ERA5_r":
            data = np.squeeze(ds["SST"].values)
            nc_key = "sst"

        case "RWRF":
            data = np.squeeze(ds["SST"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, nc_key, "Sea Surface Temperature", "K")


def diag_PSFC(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    surface pressure [Pa]

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["sp"].values)
            nc_key = "PSFC"

        case "ERA5_r":
            data = np.squeeze(ds["PSFC"].values)
            nc_key = "sp"

        case "RWRF":
            data = np.squeeze(ds["PSFC"].values)
            nc_key = "PSFC"

        case _:
            data = np.nan

    return _create_dataarray(data, ds, nc_key, "Surface Pressure", "Pa")


def diag_pw(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    dew-point temperature at 2 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["tcwv"].values)
            nc_key = "pw"

        case "ERA5_r":
            data = np.squeeze(ds["pw"].values)
            nc_key = "tcwv"

        case "RWRF":
            data = np.squeeze(ds["pw"].values)
            nc_key = "pw"

        case _:
            data = np.nan

    return _create_dataarray(data, ds, nc_key, "Precipitable Water", "kg m-2")


def diag_PBLH(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    dew-point temperature at 2 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["blh"].values)

        case "RWRF":
            data = np.squeeze(ds["PBLH"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "PBLH", "Planetary Boundary Layer Height", "m")


def diag_RAINNC(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Total Precipitation

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["tp"].values)

        case "RWRF":
            data = np.squeeze(ds["RAINNC"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "RAINNC", "Total Precipitation", "m")


def diag_SWDOWN(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Downward shortwave radiation at surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["ssrd"].values) / 3600

        case "RWRF":
            data = np.squeeze(ds["SWDOWN"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "SWDOWN", "Surface Shortwave Downward Radiation", "W m-2")


def diag_OLR(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Outward longwave radiation at TOA

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["ttr"].values) / 3600

        case "RWRF":
            data = np.squeeze(ds["OLR"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "OLR", "Outgoing Longwave Radiation", "W m-2")


def _calc_dbz(
    prs: np.ndarray,
    tmk: np.ndarray,
    qvp: np.ndarray,
    qra: np.ndarray,
    qsn: np.ndarray,
    qgr: np.ndarray,
    qcl: np.ndarray | None = None,
    qci: np.ndarray | None = None,
    *,
    sn0: int = 0,
    ivarint: int = 1,
    iliqskin: int = 1,
) -> np.ndarray:
    """Compute equivalent radar reflectivity factor (dBZ).

    Vectorized port of the RIP ``CALCDBZ`` Fortran routine
    (``wrf_user_dbz.f``, Stoelinga 2005), as wrapped by NCL ``wrf_dbz``,
    extended to optionally include cloud water (``qcl``) and cloud ice
    (``qci``) mixing ratios.

    Args:
        prs: Pressure (Pa), shape (..., ny, nx).
        tmk: Air temperature (K).
        qvp: Water-vapor mixing ratio (kg kg-1).
        qra: Rain-water mixing ratio (kg kg-1).
        qsn: Snow mixing ratio (kg kg-1).
        qgr: Graupel mixing ratio (kg kg-1).
        qcl: Cloud-water mixing ratio (kg kg-1), optional.
        qci: Cloud-ice mixing ratio (kg kg-1), optional.
        sn0: If 0, rain is converted to snow below freezing.
        ivarint: If 1, use Thompson (2004) variable intercept parameters.
        iliqskin: If 1, use liquid-skin (wet) snow/graupel factor above freezing.

    Returns:
        Equivalent radar reflectivity factor (dBZ) of same shape as ``prs``.
    """
    pi = np.pi
    gamma_seven = 720.0
    rho_r = 1000.0
    rho_s = 100.0
    rho_g = 400.0
    alpha = 0.224
    rhowat = 1000.0
    celkel = 273.15
    r1 = 1.0e-15
    rd = 287.04
    rn0_r = 8.0e6
    rn0_s = 2.0e7
    rn0_g = 4.0e6
    ron_min = 8.0e6

    qvp = np.maximum(qvp, 0.0)
    qra = np.maximum(qra, 0.0)
    qsn = np.maximum(qsn, 0.0)
    qgr = np.maximum(qgr, 0.0)

    if sn0 == 0:
        frozen = tmk < celkel
        qsn = np.where(frozen, qra, qsn)
        qra = np.where(frozen, 0.0, qra)

    virtual_t = tmk * (0.622 + qvp) / (0.622 * (1.0 + qvp))
    rho_air = prs / (rd * virtual_t)

    factor_r = gamma_seven * 1e18 * (1.0 / (pi * rho_r)) ** 1.75
    factor_s = gamma_seven * 1e18 * (1.0 / (pi * rho_s)) ** 1.75 * (rho_s / rhowat) ** 2 * alpha
    factor_g = gamma_seven * 1e18 * (1.0 / (pi * rho_g)) ** 1.75 * (rho_g / rhowat) ** 2 * alpha

    if iliqskin == 1:
        wet = tmk > celkel
        factorb_s = np.where(wet, factor_s / alpha, factor_s)
        factorb_g = np.where(wet, factor_g / alpha, factor_g)
    else:
        factorb_s = factor_s
        factorb_g = factor_g

    if ivarint == 1:
        temp_c = np.minimum(-0.001, tmk - celkel)
        sonv = np.minimum(2.0e8, 2.0e6 * np.exp(-0.12 * temp_c))

        gon = 5.0e7
        with np.errstate(divide="ignore", invalid="ignore"):
            gonv = np.where(
                qgr > r1,
                np.maximum(
                    np.minimum(
                        2.38 * (pi * rho_g / (rho_air * qgr)) ** 0.92,
                        gon,
                    ),
                    1.0e4,
                ),
                gon,
            )

        ron2 = 1.0e10
        ron_qr0 = 1.0e-4
        ron_delqr0 = 0.25 * ron_qr0
        ron_const1r = (ron2 - ron_min) * 0.5
        ron_const2r = (ron2 + ron_min) * 0.5
        ronv = np.where(
            qra > r1,
            ron_const1r * np.tanh((ron_qr0 - qra) / ron_delqr0) + ron_const2r,
            ron2,
        )
    else:
        sonv = np.full_like(qsn, rn0_s)
        gonv = np.full_like(qgr, rn0_g)
        ronv = np.full_like(qra, rn0_r)

    z_e = (
        factor_r * (rho_air * qra) ** 1.75 / ronv**0.75
        + factorb_s * (rho_air * qsn) ** 1.75 / sonv**0.75
        + factorb_g * (rho_air * qgr) ** 1.75 / gonv**0.75
    )

    if qcl is not None:
        qcl = np.maximum(qcl, 0.0)
        n0_c = 1.0e8
        factor_c = gamma_seven * 1e18 * (1.0 / (pi * rhowat)) ** 1.75
        z_e = z_e + factor_c * (rho_air * qcl) ** 1.75 / n0_c**0.75

    if qci is not None:
        qci = np.maximum(qci, 0.0)
        n0_i = 1.0e6
        rho_i = 890.0
        factor_i = gamma_seven * 1e18 * (1.0 / (pi * rho_i)) ** 1.75 * (rho_i / rhowat) ** 2 * alpha
        z_e = z_e + factor_i * (rho_air * qci) ** 1.75 / n0_i**0.75

    z_e = np.maximum(z_e, 0.001)
    return 10.0 * np.log10(z_e)


def _load_refl_inputs(source_dataset: str, ds: xr.Dataset) -> tuple[np.ndarray, ...]:
    """Load CALCDBZ input fields for a source dataset.

    Returns a tuple of (tmk, qvp, qra, qsn, qgr, qcl, qci, prs) arrays.
    Missing optional hydrometeors (graupel, cloud water, cloud ice)
    degrade to zeros or ``None`` as appropriate.
    """
    if source_dataset == "ERA5":
        tmk = np.squeeze(ds["t"].values)
        qvp = np.squeeze(ds["q"].values) / (1 - np.squeeze(ds["q"].values))
        qra = np.squeeze(ds["crwc"].values / (1 - ds["crwc"].values))
        qsn = np.squeeze(ds["cswc"].values / (1 - ds["cswc"].values))
        qgr = np.zeros(np.shape(tmk))
        qcl = np.squeeze(ds["clwc"].values / (1 - ds["clwc"].values)) if "clwc" in ds else None
        qci = np.squeeze(ds["ciwc"].values / (1 - ds["ciwc"].values)) if "ciwc" in ds else None
    elif source_dataset == "RWRF":
        tmk = np.squeeze(ds["tk_p"].values)
        qvp = np.squeeze(ds["QVAPOR_p"].values)
        qra = np.squeeze(ds["QRAIN_p"].values)
        qsn = np.squeeze(ds["QSNOW_p"].values)
        qgr = np.squeeze(ds["QGRAUP_p"].values) if "QGRAUP_p" in ds else np.zeros(np.shape(tmk))
        qcl = np.squeeze(ds["QCLOUD_p"].values) if "QCLOUD_p" in ds else None
        qci = np.squeeze(ds["QICE_p"].values) if "QICE_p" in ds else None
    else:
        template = ds["t" if "t" in ds else "tk_p"].values
        nan_array = np.full(np.shape(np.squeeze(template)), np.nan)
        return (nan_array,) * 8

    prs = np.zeros(np.shape(tmk))
    plev = np.squeeze(ds["pres_levels"].values)
    for pl in range(len(plev)):
        prs[pl, :, :] = plev[pl] * 100
    return tmk, qvp, qra, qsn, qgr, qcl, qci, prs


def diag_REFL(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Emulated Radar Reflectivity

    Five-hydrometeor (Qc, Qi, Qr, Qs, Qg) equivalent reflectivity factor.

    """

    tmk, qvp, qra, qsn, qgr, qcl, qci, prs = _load_refl_inputs(source_dataset, ds)
    if np.isnan(tmk).all():
        return _create_dataarray(tmk, ds, "REFL", "Emulated Radar Reflectivity", "dBZ")

    data = _calc_dbz(
        prs,
        tmk,
        qvp,
        qra,
        qsn,
        qgr,
        qcl=qcl,
        qci=qci,
        sn0=0,
        ivarint=1,
        iliqskin=1,
    )

    return _create_dataarray(data, ds, "REFL", "Emulated Radar Reflectivity", "dBZ")


def diag_MAX_REFL(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Emulated Column Maximum Radar Reflectivity
    """
    REFL = diag_REFL(source_dataset, ds)
    # The dimensions of REFL.values are (Time, pres_bottom_top, south_north, west_east)
    # We take the maximum over the pressure level axis (axis=1)
    _, nl, ny, nx = np.shape(REFL.values)

    data = np.max(np.reshape(REFL.values, (nl, ny, nx)), axis=0)

    return _create_dataarray(data, ds, "MAX_REFL", "Emulated Column Maximum Radar Reflectivity", "dBZ")
