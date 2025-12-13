# PyDataShred - AWS Lambda Deployment Summary

## 📋 What's Included

I've created a complete AWS Lambda deployment toolkit for your PyDataShred wheel file:

### **Files Created:**

1. **[LAMBDA_QUICKSTART.md](LAMBDA_QUICKSTART.md)** ⭐ **START HERE**
   - Step-by-step deployment guide
   - Copy-paste commands
   - Troubleshooting tips

2. **[deploy_to_lambda.py](deploy_to_lambda.py)**
   - Automated Python deployment script
   - Creates Lambda Layers automatically
   - Publishes to AWS Lambda

3. **[LAMBDA_DEPLOYMENT_GUIDE.md](LAMBDA_DEPLOYMENT_GUIDE.md)**
   - Detailed documentation
   - 4 different deployment options
   - Architecture explanations

4. **[deploy-to-lambda.sh](deploy-to-lambda.sh)**
   - Bash script wrapper (optional)

---

## 🚀 Quick Start (5 Minutes)

### **1. Install AWS CLI**
```bash
# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# macOS
brew install awscliv2
```

### **2. Configure AWS**
```bash
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Format (json)
```

### **3. Create IAM Role**
```bash
# Create role (copy the ARN output!)
aws iam create-role \
  --role-name lambda-execution-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach policy
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### **4. Deploy Wheel to Lambda**

**Option A (Recommended - Python):**
```bash
cd /home/susi/repo/PyDataShred
python scripts/deploy_to_lambda.py \
  dist/pydatashred-1.0-py3-none-any.whl \
  --region us-east-1 \
  --action layer
```

**Option B (Bash):**
```bash
bash scripts/deploy-to-lambda.sh \
  dist/pydatashred-1.0-py3-none-any.whl \
  us-east-1
```

### **5. Create Lambda Function**

```bash
# Get IDs
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
LAYER_ARN="arn:aws:lambda:us-east-1:$ACCOUNT_ID:layer:pydatashred-layer:1"
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/lambda-execution-role"

# Create function (paste as function.zip)
aws lambda create-function \
  --function-name pydatashred-handler \
  --runtime python3.11 \
  --role "$ROLE_ARN" \
  --handler lambda_function.lambda_handler \
  --layers "$LAYER_ARN" \
  --timeout 60 \
  --memory-size 256
```

### **6. Test**
```bash
aws lambda invoke \
  --function-name pydatashred-handler \
  --payload '{}' \
  response.json && cat response.json
```

---

## 📊 Deployment Methods Comparison

| Method | Ease | Speed | Cost | Size Limit | Recommended |
|--------|------|-------|------|-----------|------------|
| **Lambda Layer** | ⭐⭐⭐ | Fast | Free tier | 50MB | ✅ YES |
| **Function ZIP** | ⭐⭐⭐⭐ | Very Fast | Free tier | 50MB | For small |
| **Container** | ⭐⭐ | Slow | Varies | Unlimited | For large |
| **S3 + Direct** | ⭐⭐ | Medium | Low | 50MB | With S3 |

---

## ✅ Features Included

- ✅ Automated layer creation
- ✅ Layer publishing to AWS Lambda
- ✅ Function creation with layers
- ✅ Function testing
- ✅ Error handling
- ✅ Logging & monitoring
- ✅ Multiple runtime support

---

## 📁 Directory Structure

```
scripts/
├── deploy_to_lambda.py              # Main deployment script
├── deploy-to-lambda.sh              # Bash wrapper
├── LAMBDA_QUICKSTART.md             # Quick start guide ⭐
├── LAMBDA_DEPLOYMENT_GUIDE.md       # Detailed guide
├── LAMBDA_DEPLOYMENT_SUMMARY.md     # This file
├── dynamodb_client.py               # DynamoDB query tool (bonus)
├── dynamodb_datagrip_setup.md       # DataGrip setup (bonus)
├── upload_to_databricks.py          # Databricks upload
└── upload_to_databricks_rest.py     # Databricks REST API
```

---

## 🔑 Key Concepts

### **Lambda Layer**
- Shareable package library
- Used by multiple Lambda functions
- Faster to update than functions
- Perfect for dependencies

### **Lambda Function**
- Your code that runs in Lambda
- Can use multiple layers
- Triggered by events (API, S3, Schedule, etc.)
- Runs in managed AWS environment

### **IAM Role**
- Permissions for Lambda
- Controls what Lambda can access
- Created once, reusable

---

## 📊 Architecture

```
Your Wheel File (pydatashred-1.0-py3-none-any.whl)
    ↓
Lambda Layer Package (ZIP)
    ↓
AWS Lambda Service
    ├─ pydatashred-layer (v1)
    └─ pydatashred-handler (function)
        ├ CloudWatch Logs
        ├ API Gateway (optional trigger)
        └ DynamoDB / S3 / RDS (optional)
```

---

## 🎯 Next Steps

1. **Follow [LAMBDA_QUICKSTART.md](LAMBDA_QUICKSTART.md)** - Step by step guide
2. **Deploy the layer** - Using deploy_to_lambda.py
3. **Create a function** - Attach the layer
4. **Test the function** - Invoke with test payload
5. **Add triggers** - API Gateway, EventBridge, etc.
6. **Monitor logs** - CloudWatch

---

## 🐛 Troubleshooting

### **Problem: Module not found**
```
ModuleNotFoundError: No module named 'datashredpy'
```
**Solution:** Verify layer is attached to function
```bash
aws lambda get-function-configuration --function-name pydatashred-handler
```

### **Problem: Permission denied**
**Solution:** Check IAM role
```bash
aws iam get-role --role-name lambda-execution-role
```

### **Problem: File too large**
**Solution:** Use Container Image approach (see LAMBDA_DEPLOYMENT_GUIDE.md)

---

## 📚 Related Documents

- **[LAMBDA_QUICKSTART.md](LAMBDA_QUICKSTART.md)** - Quick reference (5 min)
- **[LAMBDA_DEPLOYMENT_GUIDE.md](LAMBDA_DEPLOYMENT_GUIDE.md)** - Complete guide (30 min)
- **[dynamodb_client.py](dynamodb_client.py)** - Query DynamoDB from Lambda
- **[upload_to_databricks.py](upload_to_databricks.py)** - For Databricks deployment

---

## 🔗 AWS Resources

- [AWS Lambda Docs](https://docs.aws.amazon.com/lambda/)
- [Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-package.html)
- [Python Runtime](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html)
- [IAM Roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)

---

## 💡 Tips

✅ Start with **Lambda Layer** - it's the cleanest approach  
✅ Use **CloudWatch Logs** to debug issues  
✅ Keep functions **small and focused**  
✅ Use **Lambda Layers** for shared dependencies  
✅ Test locally before deploying  

---

**Ready to deploy?** → See **[LAMBDA_QUICKSTART.md](LAMBDA_QUICKSTART.md)**
