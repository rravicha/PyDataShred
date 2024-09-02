from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
# from ..PyDataShred.datashredpy.data import Data

df=Data.read("C:/Users/497523/Downloads/MT cars.parquet",FileType.PARQUET)
print(df)
