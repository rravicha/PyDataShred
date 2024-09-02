def test_read_csv():
    from datashredpy.helper.data import Data
    df = Data.read("data.csv", FileType.CSV)
    assert df.count() > 0