"""Data models for client, domain, and infrastructure configuration."""
import uuid
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class SnowflakeAuthentication:
    """Snowflake database authentication credentials."""

    account: str
    user: str
    password: str
    role: str


@dataclass
class Snowflake:
    """Snowflake database configuration."""

    connection_str: SnowflakeAuthentication
    warehouse: str
    database: str
    schema: str
    query: str


@dataclass
class Bucket:
    """S3 bucket configuration."""

    name: str
    prefix: str
    file_name: str


@dataclass
class S3:
    """S3 resource configuration."""

    bucket: Bucket


@dataclass
class Rds:
    """AWS RDS configuration."""

    database: str
    schema: str
    tablename: str


@dataclass
class Dynamodb:
    """AWS DynamoDB configuration."""

    table_name: str
    region: str
    key_schema: Optional[List[Dict[str, str]]] = None
    attribute_definitions: Optional[List[Dict[str, str]]] = None


@dataclass
class Aws:
    """AWS infrastructure configuration."""

    url: str
    region: str
    s3: Optional[S3] = None
    rds: Optional[Rds] = None
    dynamodb: Optional[Dynamodb] = None


@dataclass
class Nas:
    """Network Attached Storage configuration."""

    host: str
    path: str
    file_name: str


@dataclass
class Resources:
    """Data resources configuration (source and target)."""

    source: Any
    target: Any


@dataclass
class App:
    """Application configuration."""

    app_id: int
    app_name: str
    resources: Resources


@dataclass
class Domain:
    """Business domain configuration."""

    domain_name: str
    domain_id: str = field(default_factory=lambda: str(uuid.uuid1()))
    app: Optional[App] = None


@dataclass
class Client:
    """Client configuration containing domain and application metadata."""

    client_id: int
    client_name: str
    domain: Domain