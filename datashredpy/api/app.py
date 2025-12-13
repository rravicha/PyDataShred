"""FastAPI application for metadata registration and client management.

To run via command line: uvicorn app:app --port 8888
"""
import json
import logging
from typing import Optional

import requests

from datashredpy.api.models import Client
from datashredpy.api.routes import Register

logger = logging.getLogger(__name__)

METADATA_JSON='''
{
    "client_id": 1,
    "client_name": "Client A",
    "platform": "aws",
    "domain": {
        "domain_id": 1,
        "domain_name": "example.com",
        "app": {
            "app_id": 1,
            "app_name": "MyApp",
            "resources": {
                "source": {
                    "bucket": {
                        "name": "my-bucket",
                        "prefix": "data/",
                        "file_name": "file.csv"
                    }
                },
                "target": {
                    "database": {
                        "database": "my_db",
                        "schema": "public",
                        "tablename": "my_table"
                    }
                }
            }
        }
    }
}
'''
import json
from dataclasses import dataclass


def instantiate_client_from_json(json_data: str) -> Client:
    """Instantiate Client from JSON string.
    
    Args:
        json_data: JSON string containing client configuration
        
    Returns:
        Client: Parsed client object
    """
    client_dict = json.loads(json_data)
    return Client(**client_dict)


if __name__ == "__main__":
    client_dict = json.loads(METADATA_JSON)
    client = Client(**client_dict)
    logger.info(f"Created client: {client.client_name}")

    from datashredpy.helper.data import Data
    from datashredpy.helper.enums import FileType, DbType
    # Example of reading data with Data class
    # df = Data.read('tests_data/HATCHBACK/emp.csv', FileType.CSV, use_pandas=True)


