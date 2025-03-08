import sys
sys.path.append('.')

def test_read_csv():
    from datashredpy.helper.data import Data
    from datashredpy.helper.enums import FileType
    df = Data.read("data.csv", FileType.CSV)
    print(df)
    assert df.count() > 0

test_read_csv()