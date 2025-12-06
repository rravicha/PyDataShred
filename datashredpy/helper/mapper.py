import sys
import os
import uuid
from typing import Any
import yaml

if os.uname().nodename == 'zebronics':
    sys.path.append('/home/susi/workspace/github/PyDataShred')
else:
    sys.path.append('/workspaces/PyDataShred')


from datashredpy.helper.models import Domain, App, Resources, Aws, S3, Rds, Bucket, Client
import json
from dataclasses import dataclass





# meta_data = Client(
#     client_id=1,
#     client_name='client1',
#     domain=Domain(
#         domain_id=1,
#         domain_name='reference',
#         app=App(
#             app_id=1,
#             app_name='oem',
#             resources=Resources(
#                 source=Aws(
#                     url='console.aws.amazon.com',
#                     region='us-east-1',
#                     s3=S3(
#                         bucket=Bucket(
#                             name='datashred-client1',
#                             prefix='raw/reference/oem',
#                             file_name='employee.csv'
#                         )
#                     )
#                 ),
#                 target=Aws(
#                     url='console.aws.amazon.com',
#                     region='us-west-2',
#                     rds=Rds(
#                         database='client1-reference',
#                         schema='oem',
#                         tablename='employee'
#                     )
#                 )
#             )
#         )
#     )
# )
# meta_data = Client(
#     client_id=1,
#     client_name='client1',
#     domain=Domain(
#         domain_id=1,
#         domain_name='reference',
#         app=App(
#             app_id=1,
#             app_name='oem',
#             resources=Resources(
#                 source=Aws(
#                     url='console.aws.amazon.com',
#                     region='us-east-1',
#                     s3=S3(
#                         bucket=Bucket(
#                             name='datashred-client1',
#                             prefix='raw/reference/oem',
#                             file_name='employee.csv'
#                         )
#                     )
#                 ),
#                 target=Aws(
#                     url='console.aws.amazon.com',
#                     region='us-west-2',
#                     rds=Rds(
#                         database='client1-reference',
#                         schema='oem',
#                         tablename='employee'
#                     )
#                 )
#             )
#         )
#     )
# )
# print(meta_data)
# meta_data_json = json.dumps(meta_data, default=lambda o: o.__dict__, indent=4)
# print(meta_data_json)

# import yaml
# print(dir(yaml))
# yaml_string = yaml.dump(meta_data_json, default_flow_style=False)

# print(yaml_string)
