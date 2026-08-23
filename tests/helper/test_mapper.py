import sys

from pydantic import NatsDsn

from datashredpy.helper.models import Domain, App, Resources, Aws, S3, Rds, Bucket, Client, Nas
import json


meta_data = Client(
    client_id=1,
    client_name='Cognizant',
    domain=Domain(
        domain_id=1,
        domain_name='Outreach',
        app=App(
            app_id=1,
            app_name='Events',
            resources=Resources(
                source=Nas(
                    host='localhost',
                    path='/data/Cognizant/Outreach/Events',
                    file_name='2025_january_events.csv'
                ),
                target=Aws(
                    url='console.aws.amazon.com',
                    region='us-east-1',
                    s3=S3(
                        bucket=Bucket(
                            name='cognizant',
                            prefix='landing/outreach/events/chennai/2025/01',
                            file_name='events.csv'
                        )
                    )
                )
            )
        )
    )
)
print(meta_data)
meta_data_json = json.dumps(meta_data, default=lambda o: o.__dict__, indent=4)
print(meta_data_json)