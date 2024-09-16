from snowflake.snowpark import Session
from datashredpy.helper.enums import FileType, DbType
from typing import Optional
import pandas as Pandas

from datashredpy.utilities.init_spark import SparkSessionOption

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
        # write code to read xml file , root node is named as root
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
        return cls.spark.read.csv(rel_path)
    
    @classmethod
    def _read_json_spark(cls, rel_path:str, **options) ->  Pandas.DataFrame:
        return None

    @classmethod
    def _read_xlsx_spark(cls, rel_path:str, **options) ->  Pandas.DataFrame:
        return None
   
    @classmethod
    def _read_parquet_spark(cls, rel_path:str, **options):
        return cls.spark.read.parquet(rel_path)

    @classmethod
    def _read_xml_spark(cls, rel_path:str, **options) ->  Pandas.DataFrame:
        return None

    @classmethod
    def _read_snowflake(cls, table_name, **snowpark_options) ->  Pandas.DataFrame:
        return Session.builder.configs(snowpark_options).create().table(table_name)
    
    @classmethod
    def _read_sqlite(cls, table_name, **options):
        import sqlite3
        import os
        sys.path.append('/workspace/PyDataShred/tests_data/HATCHBACK/')
        conn=sqlite3.connect('storage.db')
        cur=conn.cursor()
        cur.execute("SELECT * FROM {table_name};")
        rows=cur.fetchall()
        return rows

    @classmethod
    def read(cls, rel_path: str, file_type: FileType = None, db_type: DbType=None, use_pandas: Optional[bool] = False, use_spark: Optional[bool] = True, snowpark_options: Optional[dict] = False, **options):
        ''' Contains functions to read inbound using pandas and spark'''
        if db_type:
            if db_type ==DbType.SQLITE:
                return cls._read_sqlite(rel_path, **options)
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
            if file_type==FileType.SNOWFLAKE:
                return cls._read_snowflake(rel_path, **snowpark_options)
            cls.spark = SparkSessionOption.get_spark_instance()
            if file_type==FileType.PARQUET:
                 return cls._read_parquet_spark(rel_path, **options)
            if file_type==FileType.CSV:
                return cls._read_csv_spark(rel_path, **options)
            
