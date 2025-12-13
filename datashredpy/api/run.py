"""FastAPI application for reading and serving data files.

Run with: uvicorn run:app --port 8000
"""
import logging
from typing import Optional

import pandas as pd
from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

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


@app.get("/read", response_class=HTMLResponse)
def read_file(request: Request) -> str:
    # Read the stored CSV file
    # df = pd.read_csv('emp.csv')
    df = Data.read('tests_data/emp.csv', FileType.CSV, use_pandas=True)

    # input('hold')
    # Convert the DataFrame to HTML
    html_table = df.to_html(index=False)
    
    # Get the current URL
    current_url = str(request.url)
    
    # Create the HTML response with the current URL
    html_content = f"""
    <html>
        <body>
            <h2>Current URL: {current_url}</h2>
            {html_table}
            
        </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/download")
def download_file():
    return FileResponse('emp.csv', media_type='text/csv', filename='emp.csv')
