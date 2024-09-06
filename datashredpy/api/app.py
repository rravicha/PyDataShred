from pyspark.sql import SparkSession
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse
from typing import Optional
import sys
sys.path.append('/workspaces/PyDataShred/')
import requests
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
import requests
app = FastAPI()

# Initialize Spark session
spark = SparkSession.builder.appName("FastAPI_PySpark").getOrCreate()

# @app.get("/")
# def read_root():
#     df = Data.read('/tests_data/MT cars.parquet', FileType.PARQUET)
    # print(str(requests.url))
    # df.show()
    # return HTMLResponse(content=df.toPandas().to_html())
    # return df
    # return {"Pydatashred get": "Welcome to the FastAPI PySpark app!"}

@app.get("/read-file")
def read_files(file_path: Optional[str] = Query(None, description="Path to the file")):
    
    '''
    You can call this endpoint like this: http://127.0.0.1:8000/read-file?file_path=path/to/your/file.txt.


    '''
    if file_path:
        return FileResponse(file_path)
    return {"error": "File path not provided"}
# @app.get("/read-file")
# def read_file(file_path: str):
#     df = spark.read.csv(file_path, header=True, inferSchema=True)
#     data = df.collect()
#     return {"data": [row.asDict() for row in data]}
# @app.post("/write-file")
# def write_file(file_path: str, data: list):
#     df = spark.createDataFrame(data)
#     df.write.csv(file_path, header=True)
#     return {"message": "File written successfully"}
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
import pandas as pd

app = FastAPI()
@app.get("/")
def read_root():
    print('shoot-'*10)
    return {"Hello": "World1"}
@app.get("/read-file", response_class=HTMLResponse)
def read_file(request: Request):
    # Read the stored CSV file
    # df = pd.read_csv('emp.csv')
    df = Data.read('emp.csv', FileType.CSV, use_pandas=True)

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

@app.get("/download-file")
def download_file():
    return FileResponse('emp.csv', media_type='text/csv', filename='emp.csv')
