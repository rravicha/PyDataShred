"""Alternative FastAPI application for data file serving (legacy).

This module provides alternative API endpoints for file reading and serving.
"""
import logging
from typing import Optional

import pandas as pd
from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, HTMLResponse

from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
def read_root() -> dict:
    """Root endpoint returning welcome message.
    
    Returns:
        dict: Welcome message
    """
    logger.info("Root endpoint accessed")
    return {"Hello": "World - PyDataShred API"}


def get_html_content(current_url: str, html_content: str) -> str:
    """Generate HTML page with content and navigation.
    
    Args:
        current_url: Current request URL
        html_content: HTML content to embed
        
    Returns:
        str: Generated HTML page
    """
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
def read_file(request: Request) -> HTMLResponse:
    """Read CSV file and return as HTML table.
    
    Args:
        request: FastAPI request object
        
    Returns:
        HTMLResponse: HTML page with data table
    """
    filepath = 'tests_data/HATCHBACK/emp.csv'
    df = Data.read(filepath, file_type=FileType.CSV, use_pandas=True)
    html_table = df.to_html(index=False)
    return HTMLResponse(content=get_html_content(str(request.url), html_table))


@app.get("/download")
def download_file() -> FileResponse:
    """Download CSV file.
    
    Returns:
        FileResponse: CSV file for download
    """
    return FileResponse(
        'tests_data/HATCHBACK/emp.csv',
        media_type='text/csv',
        filename='emp.csv'
    )
    