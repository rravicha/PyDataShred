# AWS Lambda Handlers - PyDataShred Examples

Collection of ready-to-use Lambda handler functions for PyDataShred.

---

## **1. Basic Handler**

```python
# lambda_function.py
import json
from datashredpy.helper.models import Client, Domain, App

def lambda_handler(event, context):
    """
    Basic Lambda handler using PyDataShred
    """
    try:
        # Parse input event
        client_id = event.get('client_id', 1)
        
        # Use PyDataShred models
        response_data = {
            'client_id': client_id,
            'message': 'PyDataShred Lambda handler working!',
            'timestamp': context.invoked_function_arn
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps(response_data)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

---

## **2. DynamoDB Handler**

```python
# lambda_function.py
import json
import boto3
from datashredpy.helper.models import Client

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('pds-job-tracker-dev')

def lambda_handler(event, context):
    """
    Query DynamoDB table from Lambda
    """
    try:
        action = event.get('action', 'scan')
        
        if action == 'scan':
            # Scan table
            response = table.scan(Limit=10)
            items = response.get('Items', [])
            
        elif action == 'get':
            # Get specific item
            job_id = event.get('job_id')
            response = table.get_item(Key={'job_id': job_id})
            items = [response.get('Item')] if 'Item' in response else []
        
        else:
            items = []
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'count': len(items),
                'items': items
            }, default=str)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

---

## **3. S3 File Processing Handler**

```python
# lambda_function.py
import json
import boto3
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Process files from S3 using PyDataShred
    """
    try:
        # Parse S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        # Download file from S3
        local_file = f'/tmp/{key.split("/")[-1]}'
        s3.download_file(bucket, key, local_file)
        
        # Determine file type
        file_ext = key.split('.')[-1].upper()
        file_type_map = {
            'CSV': FileType.CSV,
            'JSON': FileType.JSON,
            'PARQUET': FileType.PARQUET,
            'EXCEL': FileType.EXCEL,
            'TSV': FileType.TSV
        }
        
        file_type = file_type_map.get(file_ext, FileType.CSV)
        
        # Read using PyDataShred
        df = Data.read(local_file, file_type, use_pandas=True)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'File processed successfully',
                'file': key,
                'rows': len(df),
                'columns': list(df.columns)
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

---

## **4. API Gateway Handler**

```python
# lambda_function.py
import json
from datashredpy.helper.models import Client, Domain, App, Resources, Aws, S3, Bucket

def lambda_handler(event, context):
    """
    Handle API Gateway requests
    """
    try:
        # Parse request
        http_method = event.get('httpMethod')
        path = event.get('path')
        body = json.loads(event.get('body', '{}'))
        
        # Route handling
        if path == '/client' and http_method == 'GET':
            # Get all clients (mock)
            clients = [
                {'client_id': 1, 'client_name': 'Client A'},
                {'client_id': 2, 'client_name': 'Client B'}
            ]
            status_code = 200
            response = clients
        
        elif path == '/client' and http_method == 'POST':
            # Create new client
            client_id = body.get('client_id')
            client_name = body.get('client_name')
            
            status_code = 201
            response = {
                'message': 'Client created',
                'client_id': client_id,
                'client_name': client_name
            }
        
        else:
            status_code = 404
            response = {'error': 'Not found'}
        
        return {
            'statusCode': status_code,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
```

---

## **5. EventBridge Scheduled Handler**

```python
# lambda_function.py
import json
from datetime import datetime
from datashredpy.helper.models import Client

def lambda_handler(event, context):
    """
    Scheduled task using EventBridge
    Example: Run daily data pipeline
    """
    try:
        execution_time = datetime.now().isoformat()
        
        # Your scheduled task logic here
        result = {
            'execution_time': execution_time,
            'status': 'success',
            'processed_records': 1000,
            'message': 'Daily pipeline completed'
        }
        
        # Log to CloudWatch
        print(f"Pipeline execution: {json.dumps(result)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

---

## **6. Data Pipeline Handler**

```python
# lambda_function.py
import json
import boto3
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Complete ETL pipeline using PyDataShred
    """
    try:
        # Configuration
        source_bucket = event.get('source_bucket')
        source_key = event.get('source_key')
        table_name = event.get('table_name', 'pds-job-tracker-dev')
        
        # Step 1: Read from S3
        local_file = f'/tmp/{source_key.split("/")[-1]}'
        s3.download_file(source_bucket, source_key, local_file)
        print(f"✓ Downloaded {source_key} from {source_bucket}")
        
        # Step 2: Parse with PyDataShred
        file_type = FileType.CSV if source_key.endswith('.csv') else FileType.JSON
        df = Data.read(local_file, file_type, use_pandas=True)
        print(f"✓ Parsed {len(df)} records")
        
        # Step 3: Transform
        df_transformed = df.dropna().drop_duplicates()
        print(f"✓ Transformed to {len(df_transformed)} records")
        
        # Step 4: Write to DynamoDB
        table = dynamodb.Table(table_name)
        for _, row in df_transformed.iterrows():
            table.put_item(Item=row.to_dict())
        print(f"✓ Loaded {len(df_transformed)} records to DynamoDB")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Pipeline successful',
                'source': source_key,
                'records_processed': len(df_transformed),
                'target': table_name
            })
        }
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

---

## **7. Error Handler with Logging**

```python
# lambda_function.py
import json
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Handler with comprehensive error logging
    """
    request_id = context.request_id
    
    try:
        logger.info(f"Request ID: {request_id}")
        logger.info(f"Event: {json.dumps(event)}")
        
        # Your business logic
        result = process_event(event)
        
        logger.info(f"Execution successful for {request_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(result),
            'headers': {'X-Request-ID': request_id}
        }
    
    except ValueError as e:
        logger.error(f"Validation error in {request_id}: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Bad request',
                'message': str(e),
                'request_id': request_id
            })
        }
    
    except Exception as e:
        logger.error(f"Unexpected error in {request_id}: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'request_id': request_id,
                'timestamp': datetime.now().isoformat()
            })
        }

def process_event(event):
    """Your business logic here"""
    return {'message': 'Processed successfully'}
```

---

## **8. Multi-Handler Module**

```python
# lambda_handlers.py
import json

class ClientHandler:
    """Handler for client operations"""
    
    @staticmethod
    def get_clients():
        return [
            {'id': 1, 'name': 'Client A'},
            {'id': 2, 'name': 'Client B'}
        ]
    
    @staticmethod
    def get_client(client_id):
        clients = ClientHandler.get_clients()
        return next((c for c in clients if c['id'] == client_id), None)

class DataHandler:
    """Handler for data operations"""
    
    @staticmethod
    def read_file(bucket, key):
        # Your S3 read logic
        return {'bucket': bucket, 'key': key}
    
    @staticmethod
    def process_data(data):
        # Your processing logic
        return data

def lambda_handler(event, context):
    """Route to appropriate handler"""
    try:
        action = event.get('action')
        
        if action == 'get_clients':
            result = ClientHandler.get_clients()
        elif action == 'get_client':
            client_id = event.get('client_id')
            result = ClientHandler.get_client(client_id)
        elif action == 'read_file':
            bucket = event.get('bucket')
            key = event.get('key')
            result = DataHandler.read_file(bucket, key)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Unknown action: {action}'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

---

## **How to Use These Handlers**

### **1. Copy the handler code**
```bash
# Choose a handler from above
# Copy the code to a new file
cat > lambda_function.py << 'EOF'
# Paste handler code here
EOF
```

### **2. Create deployment package**
```bash
# With layer (already has PyDataShred)
zip function.zip lambda_function.py

# Without layer (include dependencies)
pip install -r requirements.txt -t .
zip -r function.zip .
```

### **3. Update Lambda function**
```bash
aws lambda update-function-code \
  --function-name pydatashred-handler \
  --zip-file fileb://function.zip
```

### **4. Test**
```bash
# Example payload for different handlers
aws lambda invoke \
  --function-name pydatashred-handler \
  --payload '{"client_id": 1}' \
  response.json && cat response.json
```

---

## **Testing Locally**

```python
# test_handlers.py
import json
from lambda_function import lambda_handler

# Mock context
class MockContext:
    request_id = 'test-request-id'
    invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789:function:test'

# Test
event = {'client_id': 1}
context = MockContext()
response = lambda_handler(event, context)
print(json.dumps(json.loads(response['body']), indent=2))
```

---

## **Troubleshooting**

| Issue | Solution |
|-------|----------|
| `Import error` | Ensure layer is attached |
| `Timeout` | Increase timeout setting |
| `No logs` | Check CloudWatch Log Group |
| `Access denied` | Verify IAM role permissions |

---

**More examples?** Check AWS Lambda documentation or ask in the PyDataShred discussions!
