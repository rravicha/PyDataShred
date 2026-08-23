"""Data models for AWS infrastructure and client configuration."""
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

@dataclass
class Bucket:
    name: str
    prefix: str
    file_name: str

@dataclass
class S3:
    bucket: Bucket
@dataclass
class Rds:
    database: str
    schema: str
    tablename: str
@dataclass
class Dynamodb:
    table_name: str
    region: str
    key_schema: List[Dict[str, str]] = None
    attribute_definitions: List[Dict[str, str]] = None

@dataclass
class Aws:
    url: str
    region: str
    s3: S3 = None
    rds: Rds = None
    dynamodb: Dynamodb = None

@dataclass
class Nas:
    host: str
    path: str
    file_name: str

@dataclass
class Resources:
    source: Any
    target : Any

@dataclass
class App:
    app_id: int
    app_name: str
    resources: Resources

@dataclass
class Domain:
    """Business domain configuration."""

    domain_id: int
    domain_name: str
    app: App


@dataclass
class Client:
    """Client configuration containing domain and application metadata."""

    client_id: int
    client_name: str
    domain: Domain