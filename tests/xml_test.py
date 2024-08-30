import sys
 
sys.path.append('/workspaces/PyDataShred')
 
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
 
 
df=Data.read('/workspaces/PyDataShred/tests_data/XML_data.xml',FileType.XML)
print(df)