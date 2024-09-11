from pyspark.sql import SparkSession
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse
from typing import Optional
import sys
sys.path.append('/workspaces/PyDataShred/')
import requests
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
import pandas as pd

app = FastAPI()
@app.get("/")
def read_root():
    print('shoot-'*10)
    return {"Hello": "World1"}

def get_html_content(current_url, html_content):
    return f"""
    <html>
        <body>
            <h2>Current URL: {current_url}</h2>
            {html_content}  
            <a href="/download">Download File</a>
        </body>
    </html>
    """
@app.get("/read", response_class=HTMLResponse)
def read_file(request: Request):

    df = Data.read('tests_data/emp.csv', FileType.CSV, use_pandas=True)
    html_table = df.to_html(index=False)
    return HTMLResponse(content=get_html_content(str(request.url), html_table))

@app.get("/read1", response_class=HTMLResponse)
def read_file1(request: Request):
    df = Data.read('tests_data/emp.csv', FileType.CSV, use_pandas=False)
    html_table = df.to_html(index=False)
    current_url = str(request.url)
    html_content = f"""
    <html>
        <body>
            <h2>Current URL: {current_url}</h2>
            {html_table}
            <a href="/download">Download File</a>
        </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/download")
def download_file():
    return FileResponse('tests_data/emp.csv', media_type='text/csv', filename='emp.csv')
