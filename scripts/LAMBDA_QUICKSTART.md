# AWS Lambda Deployment - Quick Start

## **Complete Steps to Deploy pydatashred to AWS Lambda**

Follow these steps in order:

---

## **Prerequisites**

### **1. Install AWS CLI**

**Linux/macOS:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**macOS (Homebrew):**
```bash
brew install awscliv2
```

**Windows:** Download from https://aws.amazon.com/cli/

### **2. Configure AWS Credentials**

```bash
aws configure
```

Enter:
- **Access Key ID**: Your AWS access key
- **Secret Access Key**: Your AWS secret key
- **Default region**: `us-east-1` (or your region)
- **Output format**: `json`

**Verify:**
```bash
aws sts get-caller-identity
```

### **3. Create IAM Role (One-time setup)**

```bash
# Create trust policy
cat > /tmp/trust-policy.json << 'EOF'
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
  --assume-role-policy-document file:///tmp/trust-policy.json

# Attach basic execution policy
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Get role ARN (save this!)
aws iam get-role --role-name lambda-execution-role --query 'Role.Arn' --output text
```

---

## **Step 1: Build Wheel File**

If you don't have the wheel yet:

```bash
cd /home/susi/repo/PyDataShred

# Build wheel
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
python setup.py bdist_wheel

# Check wheel
ls -lh dist/pydatashred*.whl
```

---

## **Step 2: Deploy to Lambda (Choose One Method)**

### **Option A: Using Python Script (Recommended)**

```bash
# Make sure you're in the repo directory
cd /home/susi/repo/PyDataShred

# Run deployment script
python scripts/deploy_to_lambda.py \
  dist/pydatashred-1.0-py3-none-any.whl \
  --region us-east-1 \
  --action layer \
  --layer-name pydatashred-layer
```

**Output:**
```
✓ Layer published successfully!
  Layer ARN: arn:aws:lambda:us-east-1:123456789:layer:pydatashred-layer:1
```

**Save the Layer ARN** - you'll need it for Lambda functions!

---

### **Option B: Using Bash Script**

```bash
cd /home/susi/repo/PyDataShred

# Make script executable
chmod +x scripts/deploy-to-lambda.sh

# Run deployment
bash scripts/deploy-to-lambda.sh \
  dist/pydatashred-1.0-py3-none-any.whl \
  us-east-1 \
  default
```

---

### **Option C: Manual AWS CLI Commands**

```bash
# Step 1: Create layer package directory
mkdir -p lambda_layer/python/lib/python3.11/site-packages
cd lambda_layer

# Step 2: Extract wheel
unzip ../dist/pydatashred-1.0-py3-none-any.whl \
  -d python/lib/python3.11/site-packages

# Step 3: Create ZIP
zip -r pydatashred-layer.zip python/

# Step 4: Publish to Lambda
aws lambda publish-layer-version \
  --layer-name pydatashred-layer \
  --zip-file fileb://pydatashred-layer.zip \
  --compatible-runtimes python3.11 python3.12 \
  --region us-east-1
```

---

## **Step 3: Create Lambda Function**

### **Option A: AWS Console (Easy)**

1. Go to **Lambda** → **Create function**
2. **Function name:** `pydatashred-handler`
3. **Runtime:** Python 3.11
4. Scroll down → **Layers** → **Add a layer**
5. **Custom layers** → Select `pydatashred-layer`
6. Click **Add**
7. Paste this code in the editor:

```python
import json
from datashredpy.helper.models import Client

def lambda_handler(event, context):
    try:
        # Your code using PyDataShred
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'PyDataShred working!',
                'event': event
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

8. Click **Deploy**

### **Option B: AWS CLI**

```bash
# Get your account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Get role ARN from previous step
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/lambda-execution-role"

# Get layer ARN from deployment
LAYER_ARN="arn:aws:lambda:us-east-1:$ACCOUNT_ID:layer:pydatashred-layer:1"

# Create function
aws lambda create-function \
  --function-name pydatashred-handler \
  --runtime python3.11 \
  --role "$ROLE_ARN" \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://scripts/lambda_function.zip \
  --layers "$LAYER_ARN" \
  --timeout 60 \
  --memory-size 256 \
  --region us-east-1
```

---

## **Step 4: Test Your Lambda Function**

### **Via AWS Console:**

1. Go to **Lambda** → **Functions** → **pydatashred-handler**
2. Click **Test**
3. Create a test event
4. Click **Invoke**

### **Via AWS CLI:**

```bash
aws lambda invoke \
  --function-name pydatashred-handler \
  --payload '{"test": "data"}' \
  --region us-east-1 \
  response.json

cat response.json
```

**Expected Output:**
```json
{
  "statusCode": 200,
  "body": "{\"message\": \"PyDataShred working!\", \"event\": {...}}"
}
```

---

## **Step 5: Monitor and Troubleshoot**

### **View Logs**

```bash
# Get recent logs
aws logs tail /aws/lambda/pydatashred-handler --follow

# Or via console:
# Lambda → Functions → pydatashred-handler → Monitor → View logs in CloudWatch
```

### **Common Errors**

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: datashredpy` | Verify layer is attached to function |
| `Permission denied` | Check IAM role has permissions |
| `Function timeout` | Increase timeout in function settings |
| `Code.ZipEntrySize` error | Use Container Image option for large packages |

---

## **Step 6: Deploy Function Code**

Once you confirm the layer works, deploy your actual function:

```bash
# Option 1: Update via console
# Lambda → Functions → pydatashred-handler → Code → Edit inline

# Option 2: Update via CLI
aws lambda update-function-code \
  --function-name pydatashred-handler \
  --zip-file fileb://your-function-code.zip \
  --region us-east-1
```

---

## **Summary Commands (Copy & Paste)**

```bash
# Set variables
WHEEL_FILE="dist/pydatashred-1.0-py3-none-any.whl"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/lambda-execution-role"

# 1. Deploy layer
python scripts/deploy_to_lambda.py "$WHEEL_FILE" --region "$REGION" --action layer

# 2. Create function (get LAYER_ARN from above)
aws lambda create-function \
  --function-name pydatashred-handler \
  --runtime python3.11 \
  --role "$ROLE_ARN" \
  --handler index.handler \
  --zip-file fileb://function.zip \
  --layers "arn:aws:lambda:$REGION:$ACCOUNT_ID:layer:pydatashred-layer:1" \
  --region "$REGION"

# 3. Test
aws lambda invoke \
  --function-name pydatashred-handler \
  --payload '{}' \
  --region "$REGION" \
  response.json && cat response.json
```

---

## **Next: Add Triggers**

Once your Lambda is working, add triggers:

- **API Gateway**: Create REST API
- **EventBridge**: Schedule execution
- **S3**: Trigger on file upload
- **SNS/SQS**: Message-based invocation

Go to: **Lambda → Functions → pydatashred-handler → Add trigger**

---

## **Resources**

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-package.html)
- [Python Runtime](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html)
- [CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/)

---

**Need Help?**
- Check CloudWatch logs: `aws logs tail /aws/lambda/pydatashred-handler --follow`
- Test locally: Use the Python script `scripts/dynamodb_client.py`
- Review guide: See `LAMBDA_DEPLOYMENT_GUIDE.md`
