# PyDataShred CI/CD & Deployment Guide

## Overview

This guide explains how to:
1. **Build** wheel (.whl) files using GitHub Actions
2. **Deploy** to AWS S3 for distribution
3. **Deploy** to Databricks
4. **Deploy** to AWS Lambda/Glue

---

## 📋 Prerequisites

### GitHub Setup
- Repository must be public or have GitHub Actions enabled
- GitHub runner with Ubuntu (included by default)

### AWS Setup (Optional but Recommended)
For automatic AWS S3 uploads, configure GitHub→AWS integration:

```bash
# 1. Create IAM Role in AWS
# Trust Policy allows GitHub Actions to assume role

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT-ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR-ORG/PyDataShred:*"
        }
      }
    }
  ]
}

# 2. Attach S3 and Lambda permissions
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket",
        "arn:aws:s3:::your-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:PublishLayerVersion",
        "lambda:UpdateFunctionConfiguration"
      ],
      "Resource": "*"
    }
  ]
}
```

### Add GitHub Secrets
1. Go to: **Settings → Secrets and variables → Actions**
2. Add these secrets:

```
AWS_ROLE_TO_ASSUME=arn:aws:iam::ACCOUNT:role/GitHubActionsRole
AWS_REGION=us-east-1
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-personal-access-token
```

---

## 🔨 Build Process

### How It Works

**File**: `.github/workflows/build-wheel.yml`

**Triggers**:
- Push to `main`, `master`, or `develop` branches
- Tags starting with `v` (e.g., `v2.0.0`)
- Pull requests
- Manual workflow dispatch

**Steps**:
1. ✅ Checkout code
2. ✅ Install Python (3.8, 3.9, 3.10, 3.11, 3.12)
3. ✅ Install build dependencies
4. ✅ Build wheel (.whl file)
5. ✅ Build source distribution (.tar.gz)
6. ✅ Test wheel installation
7. ✅ Validate code
8. ✅ Create GitHub Release (if tagged)

### Build Output

Wheels are created for each Python version:
```
dist/
├── pydatashred-2.0.0-py3-none-any.whl
├── pydatashred-2.0.0-py38-none-any.whl
├── pydatashred-2.0.0-py39-none-any.whl
├── pydatashred-2.0.0-py310-none-any.whl
├── pydatashred-2.0.0-py311-none-any.whl
├── pydatashred-2.0.0-py312-none-any.whl
└── pydatashred-2.0.0.tar.gz
```

### Manual Trigger

```bash
# Push to trigger build
git push origin develop

# Or push a tag to trigger release
git tag v2.0.0
git push origin v2.0.0
```

---

## 📤 Publishing to AWS S3

### How It Works

**File**: `.github/workflows/publish-s3.yml`

**Triggers**:
- Automatically after successful build
- Manual workflow dispatch with custom S3 path

**What It Does**:
1. Downloads wheel artifacts from build workflow
2. Configures AWS credentials via OIDC
3. Uploads wheels to S3
4. Makes wheels available for download

### Configuration

#### Option 1: Using AWS OIDC (Recommended)

```bash
# 1. In AWS, create OIDC provider
# Provider URL: https://token.actions.githubusercontent.com
# Audience: sts.amazonaws.com

# 2. Add role ARN to GitHub secret
AWS_ROLE_TO_ASSUME=arn:aws:iam::123456789:role/GitHubActionsRole

# 3. Workflow automatically uses it
```

#### Option 2: Using Access Keys

```bash
# Add to GitHub secrets:
AWS_ACCESS_KEY_ID=your-key-id
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
```

### Usage

#### Automatic S3 Upload

```bash
# After build completes, workflow auto-uploads to:
# s3://your-bucket/pydatashred/

# Check artifacts via AWS CLI
aws s3 ls s3://your-bucket/pydatashred/
```

#### Manual S3 Path

```bash
# Trigger workflow with custom S3 path
gh workflow run publish-s3.yml \
  -f s3-path="s3://my-custom-bucket/libs/"
```

#### Without AWS Setup

Wheels remain available as GitHub Actions artifacts:
- Go to **Actions → Latest Build → Artifacts**
- Download directly

---

## 🧱 Databricks Deployment

### How It Works

**File**: `.github/workflows/deploy-databricks.yml`

**Steps**:
1. Builds wheel file
2. Generates deployment guide
3. Shows 5 options for deployment

### Option 1: Using S3 (Recommended)

```bash
# Upload to S3 first
aws s3 cp dist/pydatashred-2.0.0-py3-none-any.whl \
  s3://your-bucket/libraries/

# In Databricks notebook
%pip install s3://your-bucket/libraries/pydatashred-2.0.0-py3-none-any.whl

# Verify
from datashredpy.datamesh import DataProduct
print("✓ Installed")
```

### Option 2: Using Databricks CLI

```bash
# Configure CLI
databricks configure --token

# Upload to DBFS
databricks fs cp dist/pydatashred-2.0.0-py3-none-any.whl \
  dbfs:/mnt/libraries/pydatashred/

# Add to cluster config
# Libraries → Install from DBFS → dbfs:/mnt/libraries/pydatashred/
```

### Option 3: Direct Upload in UI

```
1. Go to Cluster Configuration
2. Click Libraries tab
3. Click "Install new"
4. Select "Upload"
5. Choose dist/pydatashred-*.whl
6. Click Install
```

### Option 4: Python API

```python
import requests
import os

# In Databricks
token = dbutils.notebook.run("/path/to/get_token")
host = "https://your-workspace.cloud.databricks.com"

# Upload wheel
with open('/Workspace/pydatashred.whl', 'rb') as f:
    requests.put(
        f'{host}/api/2.0/dbfs/put',
        headers={'Authorization': f'Bearer {token}'},
        data=f.read(),
        params={'path': 'dbfs:/libraries/pydatashred.whl'}
    )
```

### Option 5: Direct in Notebook

```python
# In Databricks notebook
%pip install https://github.com/rravicha/PyDataShred/releases/download/v2.0.0/pydatashred-2.0.0-py3-none-any.whl

# Import
from datashredpy.datamesh import DataProduct
```

---

## ⚡ AWS Lambda Deployment

### How It Works

**File**: `.github/workflows/deploy-lambda-glue.yml`

**Creates**:
- Lambda layer zip file (compatible with Python 3.10, 3.11, 3.12)
- Publication script
- Deployment guide

### Deploy to Lambda

```bash
# 1. Download pydatashred-lambda-layer.zip from artifacts

# 2. Publish layer to AWS
aws lambda publish-layer-version \
  --layer-name pydatashred-layer \
  --zip-file fileb://pydatashred-lambda-layer.zip \
  --compatible-runtimes python3.10 python3.11 python3.12

# 3. Get layer ARN from output
# arn:aws:lambda:us-east-1:123456789:layer:pydatashred-layer:1

# 4. Add to Lambda function
aws lambda update-function-configuration \
  --function-name my-function \
  --layers arn:aws:lambda:us-east-1:123456789:layer:pydatashred-layer:1

# 5. Use in code
# from datashredpy.datamesh import DataProduct
```

### Lambda Function Example

```python
import json
from datashredpy.datamesh import DataProduct, DataProductContract

def lambda_handler(event, context):
    """Process data with PyDataShred"""
    
    try:
        # Your data processing
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Success',
                'datamesh': 'Available'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

---

## 🔧 AWS Glue Deployment

### Option 1: S3 Wheel Reference

```bash
# Upload wheel to S3
aws s3 cp dist/pydatashred-2.0.0-py3-none-any.whl \
  s3://your-bucket/libraries/

# In Glue job:
# Go to Job Details → Advanced Properties
# Python libraries: s3://your-bucket/libraries/pydatashred-2.0.0-py3-none-any.whl
```

### Option 2: Direct Installation

```python
import sys
import subprocess

# Install at runtime
subprocess.check_call([
    sys.executable, "-m", "pip", "install",
    "s3://your-bucket/libraries/pydatashred-2.0.0-py3-none-any.whl"
])

# Import
from datashredpy.datamesh import DataProduct
```

### Glue Job Example

```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# PyDataShred available as library
from datashredpy.datamesh import DataProduct, DataProductContract

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Your Glue job code here
# Use DataProduct for data governance

job.commit()
```

---

## 🔄 Complete Workflow

### Scenario: Release Version 2.1.0

```bash
# 1. Update version in pyproject.toml
# version = "2.1.0"

# 2. Commit and push
git add pyproject.toml
git commit -m "Release v2.1.0"

# 3. Tag release
git tag v2.1.0
git push origin v2.1.0

# 4. GitHub Actions automatically:
# ✅ Builds wheels for all Python versions
# ✅ Tests installation
# ✅ Validates code
# ✅ Creates GitHub Release with wheels
# ✅ Uploads to S3 (if configured)
# ✅ Creates Lambda layer

# 5. Download artifacts:
# - From GitHub Release page
# - From GitHub Actions workflow
# - From S3 (if configured)

# 6. Deploy to your platform
# - Databricks: Upload wheel
# - Lambda: Publish layer
# - Glue: Reference S3 wheel
```

---

## 📊 Workflow Status & Monitoring

### Check Build Status

```bash
# View all workflows
gh workflow list

# View specific workflow runs
gh workflow view build-wheel.yml

# Check latest run
gh run list --workflow=build-wheel.yml -L 5

# Get run details
gh run view RUN_ID --log
```

### Download Artifacts

```bash
# List artifacts from latest run
gh run list --workflow=build-wheel.yml --limit 1 --json artifacts

# Download artifact
gh run download RUN_ID -n python-3-10-wheel
```

### View Logs

```bash
# Full logs
gh run view RUN_ID --log

# Specific job logs
gh run view RUN_ID --log-failed
```

---

## 🔐 Security Best Practices

### Secrets Management

```bash
# Never commit secrets to git
# Use GitHub Secrets instead:

# 1. Settings → Secrets and variables
# 2. Add environment-specific secrets:
#    - AWS_ROLE_TO_ASSUME
#    - DATABRICKS_TOKEN
#    - etc.

# 3. Reference in workflows: ${{ secrets.SECRET_NAME }}
```

### OIDC for AWS (No Keys!)

Benefits:
- ✅ No long-lived credentials
- ✅ Automatic token rotation
- ✅ Fine-grained permissions via roles
- ✅ Auditable access

```yaml
# In workflow:
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
    aws-region: us-east-1
```

---

## 📝 Version Management

### Automatic Versioning

Using `setuptools-scm`, version is auto-detected from:

```bash
# Option 1: Git tags
git tag v2.0.0
# Version becomes: 2.0.0

# Option 2: Fallback version
# Uses: version in pyproject.toml + git distance
```

### Manual Version Update

```toml
# In pyproject.toml
[project]
version = "2.1.0"
```

---

## 🚀 Quick Start Checklist

- [ ] GitHub repository created/configured
- [ ] `.github/workflows/*.yml` files in place
- [ ] `pyproject.toml` updated with proper config
- [ ] Push to main branch to trigger first build
- [ ] Verify artifacts in Actions tab
- [ ] (Optional) Configure AWS for S3 uploads
- [ ] (Optional) Add DATABRICKS_TOKEN secret
- [ ] Tag release: `git tag v2.0.0 && git push --tags`
- [ ] Download wheel from release/artifacts
- [ ] Deploy to Databricks/Lambda/Glue

---

## 🆘 Troubleshooting

### Build Fails

```bash
# Check syntax
python -m py_compile datashredpy/**/*.py

# Check dependencies
cat pyproject.toml  # Ensure all dependencies listed

# View GitHub Actions logs
# Actions tab → workflow run → job logs
```

### S3 Upload Fails

```bash
# Check AWS credentials
echo $AWS_ACCESS_KEY_ID

# Check S3 path
aws s3 ls s3://your-bucket/

# Check IAM permissions
# Ensure role has s3:PutObject permission
```

### Import Errors in Databricks

```python
# Check version
%pip show pydatashred

# Reinstall
%pip uninstall pydatashred
%pip install s3://bucket/pydatashred-2.0.0-py3-none-any.whl

# Check Python version compatibility
import sys
print(f"Python {sys.version}")
```

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Setuptools Build System](https://setuptools.pypa.io/)
- [Databricks Docs](https://docs.databricks.com/)
- [AWS Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/invocation-layers.html)
- [AWS Glue Docs](https://docs.aws.amazon.com/glue/)

---

## 📞 Support

For issues:
1. Check GitHub Actions logs
2. Review workflow YAML syntax
3. Verify secrets are configured
4. Check AWS IAM permissions
5. Open GitHub issue with error details

