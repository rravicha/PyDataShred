'''
To run this app via command line | uvicorn app:app --port 8888
'''
# Core Packages
import sys
import json
from typing import Optional
import requests
# External Packages
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse
# Custom Built Packages
from datashredpy.api.models import Client
from datashredpy.api.routes import Register
# Instantiation
sys.path.append('/workspaces/PyDataShred/')
app = FastAPI()

# Routes
@app.get("/register")
def register_metadata(json_data):
    client_dict = Register.metadata(json_data)
    return Client(**client_dict)