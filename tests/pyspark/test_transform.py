import sys
sys.path.append('/workspaces/PyDataShred/')
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from datashredpy.helper.transform import ETL

@pytest.fixture(scope="module")
def spark():
    """Create a Spark session for all tests"""
    return SparkSession.builder \
        .appName("test_scd2") \
        .master("local[*]") \
        .getOrCreate()

@pytest.fixture(scope="function")
def sample_source_df(spark):
    """Create a sample source DataFrame"""
    data = [
        (1, "John", "NY", 50000),
        (2, "Jane", "CA", 60000)
    ]
    return spark.createDataFrame(data, ["id", "name", "state", "salary"])

@pytest.fixture(scope="function")
def sample_target_df(spark):
    """Create a sample target DataFrame with SCD2 columns"""
    data = [
        (1, "John", "NJ", 45000, "2023-01-01", None, "current"),
        (3, "Bob", "TX", 55000, "2023-01-01", None, "current")
    ]
    return spark.createDataFrame(
        data, 
        ["id", "name", "state", "salary", "start_date", "end_date", "etl_flag"]
    )

def test_initial_load(spark, sample_source_df):
    """Test SCD2 implementation with empty target"""
    empty_target = spark.createDataFrame([], sample_source_df.schema)
    etl = ETL(sample_source_df, empty_target, "id")
    result = etl.apply_scd2()
    
    # Verify result
    assert result.count() == 2
    assert all(row.etl_flag == "current" for row in result.collect())
    assert all(row.end_date is None for row in result.collect())

def test_scd2_with_changes(spark, sample_source_df, sample_target_df):
    """Test SCD2 implementation with existing target data"""
    etl = ETL(sample_source_df, sample_target_df, "id")
    result = etl.apply_scd2()
    
    # Verify total count (2 source + 2 target = 4 records)
    assert result.count() == 4
    
    # Check expired records
    expired_records = result.filter(col("etl_flag") == "expired")
    assert expired_records.count() == 1  # One record should be expired (ID 1)
    
    # Check current records
    current_records = result.filter(col("etl_flag") == "current")
    assert current_records.count() == 3  # Three records should be current

def test_composite_key(spark):
    """Test SCD2 implementation with composite key"""
    # Create source with composite key
    source_data = [
        (1, "A", "John", 50000),
        (1, "B", "Jane", 60000)
    ]
    source_df = spark.createDataFrame(source_data, ["id", "dept", "name", "salary"])
    
    # Create target with composite key
    target_data = [
        (1, "A", "John", 45000, "2023-01-01", None, "current"),
        (1, "B", "Jane", 55000, "2023-01-01", None, "current")
    ]
    target_df = spark.createDataFrame(
        target_data, 
        ["id", "dept", "name", "salary", "start_date", "end_date", "etl_flag"]
    )
    
    etl = ETL(source_df, target_df, ["id", "dept"])
    result = etl.apply_scd2()
    
    # Verify composite key handling
    assert result.count() == 4  # Should have 4 records (2 expired + 2 current)

def test_no_changes(spark, sample_source_df):
    """Test SCD2 implementation when no changes exist"""
    # Create target with identical data
    target_data = [
        (1, "John", "NY", 50000, "2023-01-01", None, "current"),
        (2, "Jane", "CA", 60000, "2023-01-01", None, "current")
    ]
    target_df = spark.createDataFrame(
        target_data, 
        ["id", "name", "state", "salary", "start_date", "end_date", "etl_flag"]
    )
    
    etl = ETL(sample_source_df, target_df, "id")
    result = etl.apply_scd2()
    
    # Verify no changes
    assert result.count() == 2  # Should maintain only original records
    assert all(row.etl_flag == "current" for row in result.collect())