"""Tests for Data reading functionality across multiple file formats."""
import os

import pandas as pd
import pytest

from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType

DATA_DIR = "tests_data/HATCHBACK"


def test_read_csv_pandas():
    """Test reading CSV files with pandas."""
    filepath = f'{DATA_DIR}/emp.csv'
    if not os.path.exists(filepath):
        pytest.skip(f"Test file {filepath} not found")
    
    df = Data.read(filepath, file_type=FileType.CSV, use_pandas=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_read_json_pandas():
    """Test reading JSON files with pandas."""
    filepath = f'{DATA_DIR}/emp.json'
    if not os.path.exists(filepath):
        pytest.skip(f"Test file {filepath} not found")
    
    df = Data.read(filepath, file_type=FileType.JSON, use_pandas=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_read_xlsx_pandas():
    """Test reading Excel files with pandas."""
    filepath = f'{DATA_DIR}/emp.xlsx'
    if not os.path.exists(filepath):
        pytest.skip(f"Test file {filepath} not found")
    
    df = Data.read(filepath, file_type=FileType.EXCEL, use_pandas=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_read_xml_pandas():
    """Test reading XML files with pandas."""
    filepath = f'{DATA_DIR}/emp.xml'
    if not os.path.exists(filepath):
        pytest.skip(f"Test file {filepath} not found")
    
    df = Data.read(filepath, file_type=FileType.XML, use_pandas=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_read_tsv_pandas():
    """Test reading TSV files with pandas."""
    filepath = f'{DATA_DIR}/emp.tsv'
    if not os.path.exists(filepath):
        pytest.skip(f"Test file {filepath} not found")
    
    df = Data.read(filepath, file_type=FileType.TSV, use_pandas=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


if __name__ == '__main__':
    pytest.main([__file__])
