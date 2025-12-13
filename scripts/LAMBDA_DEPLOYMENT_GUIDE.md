# Deploy PyDataShred Wheel to AWS Lambda - Complete Guide

## Overview
Deploy your `pydatashred-1.0-py3-none-any.whl` to AWS Lambda with step-by-step instructions.

---

## **Option 1: Lambda Layer (Recommended)**

Lambda Layers are ideal for Python packages. Your wheel will be available to all Lambda functions.

### **Step 1: Prepare the Layer Package**

```bash
# Create directory structure
mkdir -p python/lib/python3.11/site-packages
cd python/lib/python3.11/site-packages

# Extract the wheel file
wheel unpack /path/to/pydatashred-1.0-py3-none-any.whl
# Or using unzip
unzip /path/to/pydatashred-1.0-py3-none-any.whl

cd ../../../../

# Create ZIP file for Lambda Layer
zip -r ../pydatashred-layer.zip .
```

### **Step 2: Upload to S3**

```bash
# Upload the layer ZIP to S3
aws s3 cp pydatashred-layer.zip s3://your-bucket/lambda-layers/

# Or create a bucket first
aws s3 mb s3://pydatashred-lambda-layers
aws s3 cp pydatashred-layer.zip s3://pydatashred-lambda-layers/
```

### **Step 3: Create Lambda Layer**

**Via AWS Console:**
1. Go to **Lambda → Layers → Create layer**
2. **Name:** `pydatashred-layer`
3. **Upload:** Choose ZIP file from S3
4. **Compatible runtimes:** Python 3.11 (or your version)
5. Click **Create**

**Via AWS CLI:**
```bash
aws lambda publish-layer-version \
  --layer-name pydatashred-layer \
  --zip-file fileb://pydatashred-layer.zip \
  --compatible-runtimes python3.11 python3.12 \
  --region us-east-1
```

### **Step 4: Use in Lambda Function**

**Create a test Lambda function:**

```python
# lambda_function.py
import json
from datashredpy.helper.models import Client, Domain, App, Resources, Aws, S3, Bucket

def lambda_handler(event, context):
    try:
        # Use the imported package
        metadata = {
            "client_id": 1,
            "client_name": "TestClient",
            "domain": {
                "domain_id": 1,
                "domain_name": "test",
                "app": {
                    "app_id": 1,
                    "app_name": "testapp",
                    "resources": {
                        "source": "S3",
                        "target": "RDS"
                    }
                }
            }
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'PyDataShred imported successfully!', 'data': metadata})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

**Attach Layer to Lambda:**
1. Go to **Lambda → Functions → Your Function**
2. Scroll to **Layers**
3. Click **Add a layer**
4. Select **Custom layers → pydatashred-layer**
5. Click **Add**

---

## **Option 2: Direct Package Upload (Simpler)**

For smaller packages or single functions.

### **Step 1: Create Deployment Package**

```bash
# Create working directory
mkdir lambda-deployment
cd lambda-deployment

# Copy wheel file
cp /path/to/pydatashred-1.0-py3-none-any.whl .

# Create lambda_function.py
cat > lambda_function.py << 'EOF'
import json
import sys

# Add wheel to path
sys.path.insert(0, 'pydatashred-1.0-py3-none-any.whl')

from datashredpy.helper.models import Client

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('PyDataShred loaded successfully!')
    }
EOF

# Create ZIP file
zip -r pydatashred-lambda.zip lambda_function.py pydatashred-1.0-py3-none-any.whl
```

### **Step 2: Upload to Lambda**

**Via AWS CLI:**
```bash
aws lambda create-function \
  --function-name pydatashred-handler \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://pydatashred-lambda.zip \
  --timeout 60 \
  --memory-size 256 \
  --region us-east-1
```

**Via AWS Console:**
1. **Lambda → Create function**
2. **Function name:** `pydatashred-handler`
3. **Runtime:** Python 3.11
4. **Upload:** ZIP file
5. **Handler:** `lambda_function.lambda_handler`

---

## **Option 3: Container Image (For Large Packages)**

Best for packages > 50MB.

### **Step 1: Create Dockerfile**

```dockerfile
FROM public.ecr.aws/lambda/python:3.11

# Copy wheel file
COPY pydatashred-1.0-py3-none-any.whl ${LAMBDA_TASK_ROOT}/

# Install wheel
RUN pip install ${LAMBDA_TASK_ROOT}/pydatashred-1.0-py3-none-any.whl

# Copy handler
COPY lambda_function.py ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD [ "lambda_function.lambda_handler" ]
```

### **Step 2: Build and Push Image**

```bash
# Build image
docker build -t pydatashred-lambda:latest .

# Create ECR repository
aws ecr create-repository --repository-name pydatashred-lambda --region us-east-1

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag pydatashred-lambda:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/pydatashred-lambda:latest

# Push to ECR
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/pydatashred-lambda:latest
```

### **Step 3: Deploy to Lambda**

```bash
aws lambda create-function \
  --function-name pydatashred-container \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-role \
  --code ImageUri=ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/pydatashred-lambda:latest \
  --package-type Image \
  --timeout 60 \
  --memory-size 256 \
  --region us-east-1
```

---

## **Option 4: Automated Deployment (Recommended)**

Use the Python script provided.

---

## **Quick Comparison**

| Method | Pros | Cons | Size Limit |
|--------|------|------|-----------|
| **Lambda Layer** ⭐ | Reusable, clean | Slower startup | 50MB |
| **Direct ZIP** | Simple, fast | Limited reuse | 50MB |
| **Container Image** | Unlimited size | More complex | Unlimited |
| **Script (Auto)** | One-command deploy | Requires setup | 50MB |

---

## **Prerequisites**

```bash
# Install AWS CLI v2
# macOS:
brew install awscliv2

# Linux:
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows:
# Download MSI from https://aws.amazon.com/cli/

# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)
```

---

## **IAM Role Requirements**

Your Lambda execution role needs:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

Create role:
```bash
# Create trust policy
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name lambda-execution-role \
  --assume-role-policy-document file://trust-policy.json

# Attach policy
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

---

## **Testing Your Lambda**

### **Via AWS CLI:**
```bash
aws lambda invoke \
  --function-name pydatashred-handler \
  --payload '{"test": "data"}' \
  --region us-east-1 \
  response.json

cat response.json
```

### **Via AWS Console:**
1. **Lambda → Functions → Your Function**
2. Click **Test**
3. Create test event
4. Click **Invoke**

---

## **Troubleshooting**

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'datashredpy'` | Verify wheel is in layer ZIP in correct path |
| `File size too large` | Use Container Image option or split into Lambda Layers |
| `Permission denied` | Check IAM role has required permissions |
| `Timeout` | Increase timeout in Lambda configuration |

---

## **Next Steps**

1. Choose an option above (Option 1 recommended)
2. Run the steps in order
3. Test with test payload
4. Create CloudWatch alarms for monitoring

See `deploy_to_lambda.py` for automated deployment!
