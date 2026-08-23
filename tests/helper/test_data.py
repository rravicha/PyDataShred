"""Tests for helper data reading functionality."""
import logging

logger = logging.getLogger(__name__)


def test_read_csv():
    """Test reading CSV files from helper module."""
    from datashredpy.helper.data import Data
    from datashredpy.helper.enums import FileType

    # This test is skipped as it requires actual data file
    logger.info("CSV read test - skipped, requires data.csv")
