"""Spark session initialization and configuration utilities."""
import logging
from typing import Dict, Optional

from pyspark.sql import SparkSession

from datashredpy.helper.enums import ConfigOptions

logger = logging.getLogger(__name__)


class SparkSessionOption:
    """Singleton and factory for Spark session management."""

    _instance = None

    @classmethod
    def get_spark_instance(
        cls,
        app_name: str = "PyDataShred",
        master: str = "local[*]",
        config_options: Optional[Dict] = None,
        snow_spark: bool = False
    ) -> SparkSession:
        """Get or create a singleton Spark instance for application-wide sharing.
        
        Args:
            app_name: Name of the Spark application
            master: Spark master URL (default: local[*])
            config_options: Dictionary of Spark configuration options
            snow_spark: If True, add Snowflake Spark connector
            
        Returns:
            SparkSession: Configured Spark session instance
        """
        if snow_spark:
            config_options = {
                "spark.jars.packages": "net.snowflake:spark-snowflake_2.12:2.9.0-spark_3.1"
            }
        
        if cls._instance is None:
            spark_builder = SparkSession.builder.appName(app_name).master(master)
            if config_options:
                for key, value in config_options.items():
                    spark_builder = spark_builder.config(key, value)
            cls._instance = spark_builder.getOrCreate()
            logger.info(f"Created Spark instance: {app_name}")
        
        return cls._instance

    @staticmethod
    def get_spark_session(
        app_name: str = "PyDataShred",
        master: str = "local[*]",
        config_options: Optional[Dict] = None
    ) -> SparkSession:
        """Create a new Spark session (non-singleton).
        
        Args:
            app_name: Name of the Spark application
            master: Spark master URL (default: local[*])
            config_options: Dictionary of Spark configuration options
            
        Returns:
            SparkSession: New Spark session instance
        """
        spark_builder = SparkSession.builder.appName(app_name).master(master)
        if config_options:
            for key, value in config_options.items():
                spark_builder = spark_builder.config(key, value)
        
        spark_session = spark_builder.getOrCreate()
        logger.info(f"Created Spark session: {app_name}")
        return spark_session
