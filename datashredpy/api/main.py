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
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse
# Custom Built Packages
from datashredpy.api.models import Client
from datashredpy.api.routes import Register

client_dict = Register.metadata(json_data)