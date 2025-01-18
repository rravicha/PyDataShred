
import os;os.system('cls')
from dataclasses import dataclass
from typing import List, Dict, Any

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
class Aws:
    url: str
    region: str
    s3: S3 = None
    rds: Rds = None
  
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
    domain_id: int
    domain_name: str
    app: App

@dataclass
class Client:
    client_id: int
    client_name: str
    domain: Domain

# Example usage
