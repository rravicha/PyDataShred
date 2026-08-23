import sys
import os

# Get absolute path to project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
# pytest fixtures
def test_read_snowpark():
    snowpark_options = {
                        "account": "MS76173",
                        "user": "RRAVICHA",
                        "password": "code$Mesh12345",
                        "role": 'ACCOUNTADMIN',
                        "warehouse": "COMPUTE_WH",
                        "database": "MISC",
                        "schema": "DEFAULT"
                        }   
                        
    df = Data.read('titanic', FileType.SNOWFLAKE, snowpark_options=snowpark_options)
    df.show(999)

if __name__=='__main__':
    test_read_snowpark()
    # input()
