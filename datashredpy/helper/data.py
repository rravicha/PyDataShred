from datashredpy.helper.enums import FileType
from typing import Optional, List, Dict, Any
import pandas as Pandas

class Data:
    '''
    This is primary wrapper class contains logic for reading and writing files/db/api
    This class is designed to be used as a singleton
    '''
    def __init__(self):
        pass
    @classmethod
    def _read_csv(cls, rel_path:str, file_type: FileType, **options) ->  Pandas.DataFrame:
        return Pandas.read_csv(rel_path,**options) if file_type else None

    @classmethod
    def read(cls, rel_path: str, file_type: FileType, use_pandas: bool = True,
             use_spark: Optional[bool] = True, **options):
        if file_type==FileType.CSV:
            if use_pandas:
                return cls._read_csv(rel_path, file_type, **options)
            
    @classmethod
    def _read_xlsx(cls,rel_path:str, file_type: FileType, **options) ->  Pandas.DataFrame:
        return Pandas.read_excel(rel_path, engine='openpyxl')

    @classmethod
    def read(cls, rel_path: str, file_type: FileType, use_pandas: bool = True, use_spark: Optional[bool] = True, **options):
        if file_type==FileType.XLSX:
            if use_pandas:
                return cls._read_xlsx(rel_path, file_type, **options)
    

