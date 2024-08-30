import sys

sys.path.append('/workspaces/PyDataShred')

from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType



df=Data.read('/workspaces/PyDataShred/tests_data/F.xlsx',FileType.XLSX)
print(df)
