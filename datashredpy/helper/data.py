from datashredpy.helper.enums import FileType
from typing import Optional, List, Dict, Any
import pandas as Pandas

class Data:

    @classmethod
    def _read_csv(cls,rel_path:str, file_type: FileType, **options) ->  Pandas.DataFrame:
        return Pandas.read_csv(rel_path,**options)

    @classmethod
    def read(cls, rel_path: str, file_type: FileType, use_pandas: bool = True, use_spark: Optional[bool] = True, **options):
        if file_type==FileType.CSV:
            if use_pandas:
                return cls._read_csv(rel_path, file_type, **options)
    
    @classmethod
    def _read_json(cls,rel_path:str, file_type: FileType, **options) ->  Pandas.DataFrame:
        return Pandas.read_json(rel_path,**options)

    @classmethod
    def read(cls, rel_path: str, file_type: FileType, use_pandas: bool = True, use_spark: Optional[bool] = True, **options):
        if file_type==FileType.JSON:
            if use_pandas:
                return cls._read_json(rel_path, file_type, **options)
    

    