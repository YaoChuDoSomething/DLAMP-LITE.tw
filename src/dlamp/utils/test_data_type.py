from dlamp.utils.data_type import DataType


def test_data_type_attributes():
    # Test for TK (Temperature)
    assert DataType.TK.short_name == "TK"
    assert DataType.TK.nc_key == "TK"
    assert DataType.TK.units == "K"
    assert DataType.TK.standard_name == "air_temperature"
    assert "temperature" in DataType.TK.description.lower()

    # Test for Z (Geopotential Height)
    assert DataType.Z.short_name == "Z"
    assert DataType.Z.nc_key == "Z"
    assert "geopotential height" in DataType.Z.description.lower()

    # Test for Lat (Latitude, 1-D coordinate)
    assert DataType.Lat.short_name == "lat"
    assert DataType.Lat.nc_key == "lat"
    assert "latitude" in DataType.Lat.description.lower()

    # Test for XLAT (Latitude meshgrid, 2-D)
    assert DataType.XLAT.short_name == "XLAT"
    assert DataType.XLAT.nc_key == "XLAT"

    # Test for Qt (model input, read directly)
    assert DataType.Qt.nc_key == "Qt"
