# PyDataShred CI/CD & Wheel Distribution Setup

## 🎯 Overview

This repository is now configured with **production-ready CI/CD pipelines** to:

✅ **Build** wheel (.whl) files for all Python versions (3.8-3.12)  
✅ **Test** wheel installation and imports  
✅ **Publish** to AWS S3 for distribution  
✅ **Deploy** to Databricks, AWS Lambda, and AWS Glue  
✅ **Release** automatically on GitHub  

**Zero external tools** - All using native GitHub Actions!

---

## 📦 What's New

### Files Added

```
.github/workflows/
├── build-wheel.yml              ← Main build pipeline
├── publish-s3.yml               ← AWS S3 publishing
├── deploy-databricks.yml        ← Databricks deployment
└── deploy-lambda-glue.yml       ← AWS Lambda/Glue deployment

scripts/
├── deploy-to-s3.sh             ← Manual S3 deployment
├── deploy-to-databricks.sh     ← Manual Databricks deployment
└── deploy-to-lambda.sh         ← Manual Lambda layer deployment

CI_CD_DEPLOYMENT_GUIDE.md        ← Complete guide
CI_CD_QUICK_REFERENCE.md         ← Quick commands
pyproject.toml                   ← Updated with dependencies
```

### Updated Files

- **pyproject.toml** - Proper build configuration with:
  - setuptools-scm for auto versioning
  - Optional dependencies (pyspark, pandas, aws, all)
  - Metadata and classifiers
  - Build system configuration

---

## 🚀 Quick Start (5 Minutes)

### 1. Verify Setup

```bash
# Check workflows exist
ls -la .github/workflows/

# Check scripts exist
ls -la scripts/
```

### 2. Push to Trigger Build

```bash
# Make a change
echo "# Build test" >> README.md

# Commit and push
git add README.md
git commit -m "Trigger build"
git push origin main
```

### 3. Monitor Build

```bash
# View workflow runs
gh run list --workflow=build-wheel.yml

# Or go to: GitHub → Actions tab
```

### 4. Download Wheel

```bash
# Download from workflow
gh run download -n python-3-10-wheel

# Or download from GitHub Release page (if tagged)
```

---

## 📋 Workflows Explained

### 1. Build Wheel (`.github/workflows/build-wheel.yml`)

**Triggers:** Push to main/develop, tags, PRs, manual  
**What it does:**
- Builds wheels for Python 3.8, 3.9, 3.10, 3.11, 3.12
- Tests wheel installation
- Validates code syntax
- Creates GitHub Release (if tagged)

**Output:** `python-{version}-wheel` artifacts

**Manual trigger:**
```bash
gh workflow run build-wheel.yml
```

---

### 2. Publish to S3 (`.github/workflows/publish-s3.yml`)

**Triggers:** After build completes, manual with custom path  
**What it does:**
- Downloads wheel artifacts
- Configures AWS credentials via OIDC (no keys!)
- Uploads to S3
- Shows status

**Requires:** `AWS_ROLE_TO_ASSUME` secret (optional, gracefully degrades)

**Manual trigger with custom path:**
```bash
gh workflow run publish-s3.yml \
  -f s3-path="s3://my-bucket/libs/"
```

---

### 3. Deploy Databricks (`.github/workflows/deploy-databricks.yml`)

**Triggers:** After S3 publish, manual  
**What it does:**
- Generates Databricks deployment guide
- Shows 5 deployment options
- Creates deployment instructions

**Output:** DATABRICKS_DEPLOYMENT.md

---

### 4. Deploy Lambda/Glue (`.github/workflows/deploy-lambda-glue.yml`)

**Triggers:** After S3 publish, manual  
**What it does:**
- Creates Lambda layer structure
- Generates AWS Lambda deployment guide
- Optionally publishes to AWS Lambda (if credentials available)

**Output:** 
- `pydatashred-lambda-layer.zip`
- AWS_LAMBDA_DEPLOYMENT.md

---

## 🔐 AWS Setup (Optional but Recommended)

### Using OIDC (No Credentials - Recommended!)

```bash
# 1. In AWS Console:
# - Go to IAM → Identity providers → Add provider
# - Provider URL: https://token.actions.githubusercontent.com
# - Audience: sts.amazonaws.com

# 2. Create IAM role (use CloudFormation template below):

# 3. Add GitHub secret:
gh secret set AWS_ROLE_TO_ASSUME \
  --body "arn:aws:iam::ACCOUNT-ID:role/GitHubActionsRole"
```

### CloudFormation Template

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'GitHub Actions OIDC Role for PyDataShred'

Parameters:
  GitHubOrg:
    Type: String
    Default: rravicha

Resources:
  GitHubActionsRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Federated: !Sub 'arn:aws:iam::${AWS::AccountId}:oidc-provider/token.actions.githubusercontent.com'
            Action: 'sts:AssumeRoleWithWebIdentity'
            Condition:
              StringEquals:
                'token.actions.githubusercontent.com:aud': 'sts.amazonaws.com'
              StringLike:
                'token.actions.githubusercontent.com:sub': 
                  - !Sub 'repo:${GitHubOrg}/PyDataShred:*'
      ManagedPolicyArns:
        - !Sub 'arn:aws:iam::${AWS::AccountId}:policy/GitHubActionsPolicy'

  GitHubActionsPolicy:
    Type: AWS::IAM::Policy
    Properties:
      PolicyName: GitHubActionsS3Lambda
      PolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Action:
              - 's3:PutObject'
              - 's3:GetObject'
              - 's3:ListBucket'
            Resource:
              - 'arn:aws:s3:::your-bucket'
              - 'arn:aws:s3:::your-bucket/*'
          - Effect: Allow
            Action:
              - 'lambda:PublishLayerVersion'
              - 'lambda:UpdateFunctionConfiguration'
            Resource: '*'
      Roles:
        - !Ref GitHubActionsRole

Outputs:
  RoleArn:
    Value: !GetAtt GitHubActionsRole.Arn
    Export:
      Name: GitHubActionsRoleArn
```

---

## 🛠️ Deployment Options

### Option 1: Automated (via GitHub Actions)

**Setup OIDC → Commit → Push → Wheels in S3**

Wheels automatically upload to S3 after build.

```bash
git push origin main
# → Builds wheel → Uploads to S3
```

### Option 2: Manual Script-Based

**Build locally → Run script → Deploy**

```bash
# Build wheel
python -m build --wheel

# Deploy to S3
./scripts/deploy-to-s3.sh "s3://my-bucket/libs/"

# Deploy to Databricks
./scripts/deploy-to-databricks.sh "dbfs:/libraries/"

# Deploy to Lambda
./scripts/deploy-to-lambda.sh "pydatashred-layer" "pydatashred-lambda-layer.zip"
```

### Option 3: GitHub Artifacts

**Download from GitHub → Manual upload**

```bash
# Download from Actions
gh run download -n python-3-10-wheel

# Then upload manually to your platform
```

---

## 📦 Databricks Deployment

### Quickest Method: S3 + Notebook

```bash
# 1. Push to trigger build
git push origin main

# 2. S3 auto-uploads (if configured)
# Or manually:
aws s3 cp dist/*.whl s3://bucket/libs/

# 3. In Databricks notebook:
%pip install s3://bucket/libs/pydatashred-2.0.0-py3-none-any.whl

# 4. Verify
from datashredpy.datamesh import DataProduct
print("✓ Ready")
```

### Using DBFS

```bash
# Upload via CLI
databricks fs cp dist/*.whl dbfs:/libraries/

# In cluster: Libraries → Install from DBFS
# dbfs:/libraries/pydatashred-2.0.0-py3-none-any.whl
```

---

## ⚡ AWS Lambda Deployment

### Quick Deploy

```bash
# 1. Build locally
python -m build --wheel

# 2. Create layer structure
mkdir -p lambda-layer/python/lib/python3.10/site-packages
cd lambda-layer/python/lib/python3.10/site-packages
unzip ../../../../../../dist/pydatashred-*.whl
cd ../../../../../../
zip -r ../pydatashred-lambda-layer.zip .

# 3. Publish layer
aws lambda publish-layer-version \
  --layer-name pydatashred \
  --zip-file fileb://pydatashred-lambda-layer.zip \
  --compatible-runtimes python3.10 python3.11 python3.12

# 4. Add to function
aws lambda update-function-configuration \
  --function-name my-function \
  --layers arn:aws:lambda:region:account:layer:pydatashred:1
```

---

## 🔧 AWS Glue Deployment

### Simplest: S3 Reference

```bash
# Upload wheel to S3
aws s3 cp dist/*.whl s3://bucket/libs/

# In Glue job configuration:
# Extra Python libraries: s3://bucket/libs/pydatashred-2.0.0-py3-none-any.whl
```

---

## 📝 Version Management

### Automatic Versioning (via git tags)

```bash
# Version comes from git tag
git tag v2.1.0
git push origin v2.1.0

# Wheel built as: pydatashred-2.1.0-py3-none-any.whl
```

### Manual Versioning

```toml
# In pyproject.toml
[project]
version = "2.1.0"
```

---

## ✅ Verification Checklist

### Local Build

```bash
# 1. Check pyproject.toml
cat pyproject.toml

# 2. Install build tools
pip install build setuptools wheel setuptools-scm

# 3. Build locally
python -m build --wheel

# 4. Verify wheel
ls -lh dist/*.whl
unzip -l dist/*.whl | head

# 5. Test installation
pip install dist/*.whl
python -c "from datashredpy.datamesh import DataProduct; print('✓')"
```

### GitHub Workflows

```bash
# 1. Check workflows syntax
gh workflow list

# 2. View workflow file
cat .github/workflows/build-wheel.yml

# 3. Trigger manually
gh workflow run build-wheel.yml

# 4. Monitor
gh run list --workflow=build-wheel.yml

# 5. Download artifacts
gh run download -n python-3-10-wheel
```

---

## 🔍 Troubleshooting

### Build Fails

```bash
# Check workflow logs
gh run list --workflow=build-wheel.yml
gh run view RUN_ID --log

# Test locally
python -m py_compile datashredpy/**/*.py
python -m build --wheel
```

### S3 Upload Fails

```bash
# Check AWS credentials
aws sts get-caller-identity

# Check IAM permissions
aws s3 ls s3://your-bucket/

# Verify role has permissions
aws iam get-role --role-name GitHubActionsRole
```

### Databricks Install Fails

```python
# Check version compatibility
import sys
print(f"Python {sys.version}")

# Verify wheel is compatible
# Wheel name must match Python version (py310, py311, etc.)
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **CI_CD_DEPLOYMENT_GUIDE.md** | Complete guide (60+ pages) |
| **CI_CD_QUICK_REFERENCE.md** | Quick commands and checklists |
| **DATABRICKS_DEPLOYMENT.md** | Auto-generated by workflow |
| **AWS_LAMBDA_DEPLOYMENT.md** | Auto-generated by workflow |
| **.github/workflows/*.yml** | Workflow definitions |
| **scripts/deploy-*.sh** | Manual deployment scripts |

---

## 🎯 Common Tasks

### Build and Release

```bash
# Update version
sed -i 's/version = "2.0.0"/version = "2.1.0"/' pyproject.toml

# Commit and tag
git add pyproject.toml
git commit -m "Release v2.1.0"
git tag v2.1.0
git push origin main --tags

# GitHub Actions automatically:
# ✓ Builds wheels
# ✓ Creates release
# ✓ Uploads to S3
# ✓ Generates deployment guides
```

### Deploy to All Platforms

```bash
# Automatic (after push):
# 1. Wheels build
# 2. S3 uploads (if OIDC configured)
# 3. Lambda layer generated
# 4. Deployment guides created

# Manual:
./scripts/deploy-to-s3.sh "s3://bucket/"
./scripts/deploy-to-databricks.sh "dbfs:/libraries/"
./scripts/deploy-to-lambda.sh "layer-name" "zip-file"
```

---

## 🎓 Next Steps

1. **Verify Setup**
   ```bash
   # Check all files present
   ls -la .github/workflows/
   ls -la scripts/
   cat pyproject.toml
   ```

2. **Test Build**
   ```bash
   # Push to trigger
   git push origin main
   
   # Check GitHub → Actions
   ```

3. **Configure AWS (Optional)**
   ```bash
   # Follow AWS OIDC setup above
   # Or skip for now - workflows gracefully degrade
   ```

4. **First Release**
   ```bash
   git tag v2.0.0
   git push origin v2.0.0
   # → Release auto-created with wheels
   ```

5. **Deploy Anywhere**
   ```bash
   # Databricks, Lambda, Glue, etc.
   # Choose from 5 deployment options
   ```

---

## 🆘 Quick Help

```bash
# View build status
gh run list --workflow=build-wheel.yml

# Download latest artifacts
gh run download -n python-3-10-wheel

# View full logs
gh run view RUN_ID --log

# List secrets
gh secret list

# Trigger build manually
gh workflow run build-wheel.yml
```

---

## 📞 Support

For issues:
1. Check GitHub Actions logs
2. Review workflow YAML
3. Verify secrets configured
4. Test locally: `python -m build --wheel`
5. Check AWS IAM permissions

---

## 📄 License

Apache 2.0 - See LICENSE file

---

**Happy building! 🚀**

For detailed information, see:
- [CI_CD_DEPLOYMENT_GUIDE.md](CI_CD_DEPLOYMENT_GUIDE.md) - Complete reference
- [CI_CD_QUICK_REFERENCE.md](CI_CD_QUICK_REFERENCE.md) - Quick commands

