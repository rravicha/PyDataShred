
import os

from datashredpy.cloud.aws import dynamodb;os.system('cls')
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
    domain_id: int
    domain_name: str
    app: App

@dataclass
class Client:
    client_id: int
    client_name: str
    domain: Domain

# Example usage
class Movies:
    """Encapsulates an Amazon DynamoDB table of movie data.

    Example data structure for a movie record in this table:
        {
            "year": 1999,
            "title": "For Love of the Game",
            "info": {
                "directors": ["Sam Raimi"],
                "release_date": "1999-09-15T00:00:00Z",
                "rating": 6.3,
                "plot": "A washed up pitcher flashes through his career.",
                "rank": 4987,
                "running_time_secs": 8220,
                "actors": [
                    "Kevin Costner",
                    "Kelly Preston",
                    "John C. Reilly"
                ]
            }
        }
    """

    def __init__(self, dyn_resource):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        # The table variable is set during the scenario in the call to
        # 'exists' if the table exists. Otherwise, it is set by 'create_table'.
        self.table = None


    def get_movie(self, title, year):
        """
        Gets movie data from the table for a specific movie.

        :param title: The title of the movie.
        :param year: The release year of the movie.
        :return: The data about the requested movie.
        """
        try:
            response = self.table.get_item(Key={"year": year, "title": title})
        except ClientError as err:
            logger.error(
                "Couldn't get movie %s from table %s. Here's why: %s: %s",
                title,
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response["Item"]


    def create_table(self, table_name, key_schema, attribute_definitions):
        """
        Creates a DynamoDB table.

        :param table_name: The name of the table to create.
        :param key_schema: The key schema for the table.
        :param attribute_definitions: The attribute definitions for the table.
        :return: The newly created table.
        """
        table = self.dyn_resource.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attributejson.dumps(attribute_definitions),
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5,
            },
        )
        # Wait until the table exists.
        table.meta.client.get_waiter("table_exists").wait(TableName=table_name)
        return table