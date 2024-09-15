import sys
sys.path.append('/workspaces/PyDataShred/')

from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
# pytest fixtures
def test_read_snowpark():
    snowpark_options = {
                        "account": "VU33144",
                        "user": "RRAVICHA",
                        "password": "Susi@786",
                        "role": 'ACCOUNTADMIN',
                        "warehouse": "COMPUTE_WH",
                        "database": "MISC",
                        "schema": "DEFAULT"
                        }   
                        
    df = Data.read('titanic', FileType.SNOWFLAKE, snowpark_options=snowpark_options)
    df.show(999)

if __name__=='__main__':
    test_read_parquet()
    # input()
