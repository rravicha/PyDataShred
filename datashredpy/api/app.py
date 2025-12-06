'''
To run this app via command line | uvicorn app:app --port 8888
'''
# Core Packages
import sys
sys.path.append('/workspaces/PyDataShred/')
import json
from typing import Optional
import requests
# External Packages
# from fastapi import FastAPI, Query
# from fastapi.responses import FileResponse, HTMLResponse
# Custom Built Packages
from datashredpy.api.models import Client
from datashredpy.api.routes import Register
# from datashredpy.cloud.aws.dynamodb import Dynamodb
# Instantiation

# app = FastAPI()

# # Routes
# @app.get("/register/client")
# def register_metadata(json_data):
#     client_dict = Register.metadata(json_data)
#     return Client(**client_dict)

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
    client_dict = json.loads(json_data)
    return Client(**client_dict)

client_dict = json.loads(METADATA_JSON)
print(Client(**client_dict))

from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType, DbType
# df = Data.read('tests_data/HATCHBACK/emp.csv', FileType.CSV,use_pandas=True)


