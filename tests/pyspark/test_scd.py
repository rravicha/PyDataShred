import sys
sys.path.append('/workspaces/PyDataShred/')
sys.path.append('/workspaces/PyDataShred/tests_data/HATCHBACK')

from datashredpy.helper.enums import FileType
from datashredpy.helper.data import Data
from datashredpy.helper.transform import ETL
# pytest fixtures
def test_read_parquet():
    DF1 = '/workspaces/PyDataShred/tests_data/HATCHBACK/scd/supply_v1.csv'
    DF2 = '/workspaces/PyDataShred/tests_data/HATCHBACK/scd/supply_v2.csv'
    data1 = Data.read(DF1, file_type = FileType.CSV)
    data1.show()
    data2 = Data.read(DF2, file_type = FileType.CSV)
    data2.show()

    data3= ETL.apply_scd2(source_df = data1, target_df = data2, key_columns = ['id'])
    data3.show()
if __name__=='__main__':
    test_read_parquet()
