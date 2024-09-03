from datashredpy.helper.enums import FileType
from typing import Optional, List, Dict, Any
import pandas as Pandas

class Data:

    @classmethod
    def _read_csv_pandas(cls, rel_path:str, **options) ->  Pandas.DataFrame:
        return Pandas.read_csv(rel_path,**options)
    
    @classmethod
    def _read_json_pandas(cls, rel_path:str, **options) ->  Pandas.DataFrame:
        return Pandas.read_json(rel_path,**options)

    @classmethod
    def _read_xlsx_pandas(cls, rel_path:str, **options) ->  Pandas.DataFrame:
        return Pandas.read_excel(rel_path, engine='openpyxl')
    
    @classmethod
    def _read_parquet_pandas(cls, rel_path:str, **options) ->  Pandas.DataFrame:
        return Pandas.read_parquet(rel_path)

    @classmethod
    def _read_xml_pandas(cls, rel_path:str, **options) ->  Pandas.DataFrame:
         #write code to read xml file , root node is named as root
        import xml.etree.ElementTree as ET  
        tree = ET.parse(rel_path)
        root = tree.getroot()
        data = []
        for child in root:
            row = {}
            for elem in child:
                row[elem.tag] = elem.text
            data.append(row)
        df = Pandas.DataFrame(data)
        return df

    @classmethod
    def _read_delta_pandas(cls, rel_path:str, **options) ->  Pandas.DataFrame:
        return None
#
    @classmethod
    def _read_csv_spark(cls, rel_path:str, **options) ->  Pandas.DataFrame:
        return None
    
    @classmethod
    def _read_json_spark(cls, rel_path:str, **options) ->  Pandas.DataFrame:
        return None

    @classmethod
    def _read_xlsx_spark(cls, rel_path:str, **options) ->  Pandas.DataFrame:
        return None
    
    @classmethod
    def _read_parquet_spark(cls, rel_path:str, **options) ->  Pandas.DataFrame:
        return None

    @classmethod
    def _read_xml_spark(cls, rel_path:str, **options) ->  Pandas.DataFrame:
        return None
    
    @classmethod
    def read(cls, rel_path: str, file_type: FileType, use_pandas: bool = True, use_spark: Optional[bool] = False, **options):
        ''' Contains functions to read inbound using pandas and spark'''
        if use_pandas:
            if file_type==FileType.CSV:
                    return cls._read_csv_pandas(rel_path, **options)
            if file_type==FileType.TSV:
                    return cls._read_csv_pandas(rel_path, **options)
            if file_type ==FileType.JSON:
                    return cls._read_json_pandas(rel_path, **options)
            if file_type == FileType.EXCEL:
                    return cls._read_xlsx_pandas(rel_path, **options)
            if file_type == FileType.PARQUET:
                    return cls._read_parquet_pandas(rel_path, **options)
            if file_type == FileType.DELTA:
                    return cls._read_delta_pandas(rel_path, **options)
            if file_type == FileType.XML:
                    return cls._read_xml_pandas(rel_path, **options)        
        if use_spark:
              pass
