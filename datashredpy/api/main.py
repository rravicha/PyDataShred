"""FastAPI application for client metadata registration.

Run with: uvicorn main:app --port 8888
"""
import json
import logging
from typing import Optional

import requests
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse

from datashredpy.api.models import Client
from datashredpy.api.routes import Register

logger = logging.getLogger(__name__)