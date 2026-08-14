from dlamp.utils.data_type import DataType


def test_data_type_attributes():
    # Test for TK (Temperature)
    assert DataType.TK.short_name == "TK"
    assert DataType.TK.nc_key == "tk_p"
    assert "temperature" in DataType.TK.description.lower()

    # Test for PH (Geopotential Height)
    assert DataType.PH.short_name == "PH"
    assert DataType.PH.nc_key == "z_p"
    assert "geopotential height" in DataType.PH.description.lower()

    # Test for Lat (Latitude)
    assert DataType.Lat.short_name == "Lat"
    assert DataType.Lat.nc_key == "XLAT"
    assert "latitude" in DataType.Lat.description.lower()
