URL='https://fakerestapi.azurewebsites.net/api/v1/Authors'
import sys
sys.path.append('.')
sys.path.append('/workspace/PyDataShred')
from datashredpy.helper.data import Data
from datashredpy.helper.enums import ApiType
from tests.enums import TestFilePath
from datashredpy.helper.transform import Utils
# pytest fixtures
def test_read_parquet():
    raw_api_data =  Data.read(URL, ApiType.DEFAULT_API)
    print(raw_api_data)
    df=Utils.raw_json_to_pyspark(raw_api_data)
    df.show(999)
    
# https://fakerestapi.azurewebsites.net/api/v1/Authors/1

if __name__=='__main__':
    test_read_parquet()
