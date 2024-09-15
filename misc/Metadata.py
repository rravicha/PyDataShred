
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
meta_data = Domain(
    domain_id=1,
    domain_name='reference',
    app=App(
        app_id=1,
        app_name='oem',
        resources=Resources(
            source=Aws(
                url='console.aws.amazon.com',
                region='us-east-1',
                s3=S3(bucket=Bucket(name='datashred-moodys',prefix='raw/reference/oem',file_name='employee.csv'))
                ),
            target=Aws(
                url='console.aws.amazon.com',
                region='us-west-2',
                rds=Rds(database='moodys-reference', schema='oem', tablename='employee')
            )
        )
    )
)

client1 = Client(client_id=1, client_name='moodys', domain=meta_data)
print(client1)
print(dir(client1.domain))
# form a json for class client
