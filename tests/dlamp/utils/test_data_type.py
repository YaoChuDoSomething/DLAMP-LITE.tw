from dlamp.utils.data_type import DataType


def test_data_type_attributes():
    # Test for TK (Temperature)
    assert DataType.TK.short_name == "TK"
    assert DataType.TK.nc_key == "tk_p"
    assert DataType.TK.units == "K"
    assert DataType.TK.standard_name == "air_temperature"
    assert "temperature" in DataType.TK.description.lower()

    # Test for PH (Geopotential Height)
    assert DataType.PH.short_name == "PH"
    assert DataType.PH.nc_key == "z_p"
    assert "geopotential height" in DataType.PH.description.lower()

    # Test for Lat (Latitude, 1-D coordinate)
    assert DataType.Lat.short_name == "Lat"
    assert DataType.Lat.nc_key == "XLAT"
    assert "latitude" in DataType.Lat.description.lower()

    # Test for MASK (land-sea mask)
    assert DataType.MASK.short_name == "MASK"
    assert DataType.MASK.nc_key == "LANDMASK"

    # Test for Qt (model input, read directly)
    assert DataType.Qt.nc_key == "QTOTAL_p"
