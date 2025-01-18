import sys
sys.path.append('/workspaces/PyDataShred')
from datashredpy.helper.models import Domain, App, Resources, Aws, S3, Rds, Bucket, Client
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
                s3=S3(bucket=Bucket(name='datashred-client1',prefix='raw/reference/oem',file_name='employee.csv'))
                ),
            target=Aws(
                url='console.aws.amazon.com',
                region='us-west-2',
                rds=Rds(database='client1-reference', schema='oem', tablename='employee')
            )
        )
    )
)

client1 = Client(client_id=1, client_name='client1', domain=meta_data)
print(client1)
print(dir(client1.domain))
# form a json for class client
