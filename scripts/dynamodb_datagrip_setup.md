# DynamoDB DataGrip Setup Guide

## Important Note
**DynamoDB does NOT have a standard JDBC driver** because it's a NoSQL database, not a relational database. DataGrip is primarily designed for SQL databases.

---

## Option 1: Simba DynamoDB JDBC Driver (Paid - Official)

### Overview
- **Vendor**: Simba Technologies
- **Cost**: Commercial (paid license required)
- **Support**: Official support from Simba

### Steps to Install

1. **Download the driver**
   - Visit: https://www.simba.com/products/DynamoDB/doc/JDBC_InstallGuide/
   - Request evaluation license or purchase

2. **Add to DataGrip**
   - In DataGrip: **File → Settings → Database Drivers**
   - Click **+** to add new driver
   - **Name**: DynamoDB (Simba)
   - **Driver Files**: Add the JAR files from Simba package
   - **Driver Class**: `com.simba.dynamodb.jdbc.Driver`
   - **Connection URL**: `jdbc:dynamodb://us-east-1`

3. **Create Connection**
   - **Database → New → Data Source → DynamoDB**
   - Configure AWS credentials in DataGrip

---

## Option 2: Use AWS SDK (Recommended - Free Alternative)

Since DataGrip has limitations with DynamoDB, use Python scripts instead:

### Setup AWS SDK
```bash
pip install boto3 botocore
```

### Python Script to Query DynamoDB
```python
import boto3
from boto3.dynamodb.conditions import Key

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('pds-job-tracker-dev')

# Scan all items
response = table.scan()
for item in response['Items']:
    print(item)

# Query specific item
response = table.query(
    KeyConditionExpression=Key('job_id').eq('job-123')
)
print(response['Items'])
```

---

## Option 3: DBeaver Community (Free Alternative to DataGrip)

DBeaver has better NoSQL support:

1. **Download**: https://dbeaver.io/download/
2. **Install DynamoDB Driver**:
   - Extensions → Find Extensions
   - Search: "DynamoDB"
   - Install AWS DynamoDB extension

3. **Create Connection**:
   - **Database → New Database Connection**
   - Select **Amazon DynamoDB**
   - Configure AWS credentials
   - Test connection

---

## Option 4: Attunity DynamoDB Driver (Alternative)

### Features
- JDBC-based
- Works with some SQL clients
- Limited SQL support (converts to DynamoDB API calls)

### Installation
```bash
# Download from Attunity or Maven Central
# Maven dependency:
<dependency>
    <groupId>com.attunity</groupId>
    <artifactId>dynamodb-jdbc</artifactId>
    <version>latest</version>
</dependency>
```

---

## Option 5: AWS DataExchange DynamoDB Driver

Some third-party JDBC drivers available on AWS DataExchange:
- Visit: https://aws.amazon.com/dataexchange/
- Search: DynamoDB JDBC Driver
- Review available options

---

## Configuration Examples

### DataGrip Connection URL Format
```
# Generic format (if driver supports it)
jdbc:dynamodb://[host]:[port];AccessKey=[key];SecretKey=[secret];Region=[region]

# Example
jdbc:dynamodb://dynamodb.us-east-1.amazonaws.com:443;AccessKey=AKXXXXX;SecretKey=xxxxx;Region=us-east-1
```

### Environment Variables (for AWS CLI)
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

---

## Recommended Setup

### Best Practice: Use Python with DataGrip

1. **Keep DataGrip** for SQL databases (RDS, PostgreSQL, etc.)
2. **Use Python scripts** for DynamoDB queries
3. **Store scripts** in your project for reusability

### Create Python Data Source in DataGrip

```python
# scripts/query_dynamodb.py
import boto3
import json
from boto3.dynamodb.conditions import Key

def query_jobs(table_name='pds-job-tracker-dev', region='us-east-1'):
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    response = table.scan()
    return response['Items']

def get_job(job_id, table_name='pds-job-tracker-dev', region='us-east-1'):
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    response = table.get_item(Key={'job_id': job_id})
    return response.get('Item')

if __name__ == '__main__':
    jobs = query_jobs()
    print(json.dumps(jobs, indent=2, default=str))
```

---

## Summary Table

| Option | Cost | DataGrip Support | Ease | Recommendation |
|--------|------|-----------------|------|---|
| Simba Driver | Paid | Yes | Medium | For production with budget |
| AWS SDK | Free | No | Easy | ⭐ Best for development |
| DBeaver | Free | Yes | Easy | Better for NoSQL |
| Attunity | Varies | Maybe | Hard | Legacy option |
| Python Scripts | Free | No | Easy | ⭐ Recommended |

---

## Quick Start - Python Approach

```bash
# 1. Install boto3
pip install boto3

# 2. Configure AWS
aws configure  # or set environment variables

# 3. Run query
python scripts/query_dynamodb.py
```

---

## Links
- DynamoDB JDBC: https://www.simba.com/products/DynamoDB/
- DBeaver: https://dbeaver.io/
- Boto3 Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html
- AWS SDK: https://docs.aws.amazon.com/dynamodb/latest/developerguide/
