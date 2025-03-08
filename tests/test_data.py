import pytest
import pandas as pd
import sys
sys.path.append('/workspaces/PyDataShred')
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType, DbType, ApiType

def test_read_csv_pandas():
    df = Data.read('tests_data/emp.csv', file_type=FileType.CSV, use_pandas=True)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['Emp_id', 'Emp_name', 'salary']
    assert df.shape == (4, 3)
    assert df.loc[0, 'Emp_id'] == 1
    assert df.loc[1, 'Emp_name'] == 'Aditya'

def test_read_json_pandas():
    df = Data.read('tests_data/emp.json', file_type=FileType.JSON, use_pandas=True)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['Emp_id', 'Emp_name', 'salary']
    assert df.shape == (4, 3)
    assert df.loc[0, 'Emp_id'] == 1
    assert df.loc[1, 'Emp_name'] == 'Aditya'

def test_read_xlsx_pandas():
    df = Data.read('tests_data/emp.xlsx', file_type=FileType.EXCEL, use_pandas=True)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['Emp_id', 'Emp_name', 'salary']
    assert df.shape == (4, 3)
    assert df.loc[0, 'Emp_id'] == 1
    assert df.loc[1, 'Emp_name'] == 'Aditya'

def test_read_parquet_pandas():
    df = Data.read('tests_data/emp.parquet', file_type=FileType.PARQUET, use_pandas=True)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['Emp_id', 'Emp_name', 'salary']
    assert df.shape == (4, 3)
    assert df.loc[0, 'Emp_id'] == 1
    assert df.loc[1, 'Emp_name'] == 'Aditya'

def test_read_xml_pandas():
    df = Data.read('tests_data/emp.xml', file_type=FileType.XML, use_pandas=True)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['Emp_id', 'Emp_name', 'salary']
    assert df.shape == (4, 3)
    assert df.loc[0, 'Emp_id'] == 1
    assert df.loc[1, 'Emp_name'] == 'Aditya'

def test_read_api():
    data = Data.read('https://api.example.com/data', api_type=ApiType.DEFAULT_API)
    assert isinstance(data, list)
    assert isinstance(data[0], dict)

def test_read_sqlite():
    rows = Data.read('emp', db_type=DbType.SQLITE)
    assert isinstance(rows, list)
    assert len(rows) > 0
    assert isinstance(rows[0], tuple)

if __name__ == '__main__':
    pytest.main()