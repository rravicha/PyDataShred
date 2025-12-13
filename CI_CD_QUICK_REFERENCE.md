# CI/CD Quick Reference

## 🚀 One-Command Setups

### Setup AWS OIDC (No Credentials!)

```bash
# 1. Create OIDC Provider in AWS Console:
# - Go to IAM → Identity providers → Add provider
# - Provider: https://token.actions.githubusercontent.com
# - Audience: sts.amazonaws.com

# 2. Get your AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 3. Create IAM role with trust policy
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG/PyDataShred:*"
        }
      }
    }
  ]
}
EOF

# 4. Create role
aws iam create-role \
  --role-name GitHubActionsRole \
  --assume-role-policy-document file://trust-policy.json

# 5. Add inline policy
cat > inline-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
        "lambda:PublishLayerVersion"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name GitHubActionsRole \
  --policy-name S3LambdaPolicy \
  --policy-document file://inline-policy.json

# 6. Add GitHub Secret (replace with your account ID)
gh secret set AWS_ROLE_TO_ASSUME --body "arn:aws:iam::${AWS_ACCOUNT_ID}:role/GitHubActionsRole"
```

### Trigger Build Manually

```bash
# Build on main
git push origin main

# Create release (auto-builds)
git tag v2.0.0
git push origin v2.0.0

# Manual trigger
gh workflow run build-wheel.yml
```

### Download Artifacts

```bash
# List latest artifacts
gh run list --workflow=build-wheel.yml --limit 1 --json artifacts

# Download wheel
gh run download -n python-3-10-wheel

# List files
ls python-3-10-wheel/
```

---

## 📦 Deploy to Databricks

### Via S3 (Recommended)

```bash
# 1. Push to trigger build
git push origin main

# 2. Download wheel
gh run download -n python-3-10-wheel
cd python-3-10-wheel

# 3. Upload to S3
aws s3 cp pydatashred-*.whl s3://your-bucket/libraries/

# 4. In Databricks notebook:
# %pip install s3://your-bucket/libraries/pydatashred-2.0.0-py3-none-any.whl
```

### Via Databricks CLI

```bash
# 1. Configure CLI
databricks configure --token

# 2. Download wheel
gh run download -n python-3-10-wheel
cd python-3-10-wheel

# 3. Upload to DBFS
databricks fs cp pydatashred-*.whl dbfs:/libraries/

# 4. In Databricks:
# Go to Cluster → Libraries → Install from DBFS
# dbfs:/libraries/pydatashred-2.0.0-py3-none-any.whl
```

---

## ⚡ Deploy to AWS Lambda

### Create Layer

```bash
# 1. Download lambda layer zip
gh run download -n lambda-layer

# 2. Publish to Lambda
aws lambda publish-layer-version \
  --layer-name pydatashred \
  --zip-file fileb://pydatashred-lambda-layer.zip \
  --compatible-runtimes python3.10 python3.11 python3.12

# 3. Note the LayerVersionArn from output

# 4. Add to function
aws lambda update-function-configuration \
  --function-name my-function \
  --layers arn:aws:lambda:region:account:layer:pydatashred:1
```

---

## 🔧 Deploy to AWS Glue

### S3 Method

```bash
# 1. Download wheel
gh run download -n python-3-10-wheel

# 2. Upload to S3
aws s3 cp pydatashred-*.whl s3://your-bucket/

# 3. In Glue job configuration:
# - Extra Python libraries: s3://your-bucket/pydatashred-2.0.0-py3-none-any.whl
```

---

## 🔄 Workflow Status

```bash
# View workflow runs
gh run list --workflow=build-wheel.yml

# Get latest status
gh run list --workflow=build-wheel.yml -L 1

# View specific run
gh run view RUN_ID --log

# Watch in real-time
gh run watch RUN_ID
```

---

## 🛠️ Configuration

### Update Version

```bash
# Edit pyproject.toml
version = "2.1.0"

# Commit and push
git add pyproject.toml
git commit -m "Bump version to 2.1.0"
git push origin main
```

### Configure S3 Bucket

```bash
# Set GitHub secret
gh secret set S3_BUCKET_PATH --body "s3://my-bucket/libs/"
```

### Configure Databricks

```bash
# Set GitHub secret
gh secret set DATABRICKS_HOST --body "https://your-workspace.cloud.databricks.com"
gh secret set DATABRICKS_TOKEN --body "your-pat-token"
```

---

## 🔍 Troubleshooting

### View Build Failure

```bash
# Get full logs
gh run view RUN_ID --log

# Or in GitHub UI:
# Actions → Workflow → Latest Run → See logs
```

### Test Locally

```bash
# Build wheel locally
pip install build
python -m build --wheel

# Test installation
pip install dist/pydatashred-*.whl
python -c "from datashredpy.datamesh import DataProduct; print('✓')"
```

### Check Python Compatibility

```bash
# Build for specific version
python3.10 -m build --wheel
python3.11 -m build --wheel
python3.12 -m build --wheel
```

---

## 📋 Checklists

### First Time Setup

- [ ] Clone repository
- [ ] Verify `.github/workflows/` contains .yml files
- [ ] Verify `pyproject.toml` has correct version
- [ ] Push to main to trigger first build
- [ ] Go to **Actions** tab and verify build succeeded
- [ ] Download artifact to verify wheel exists
- [ ] (Optional) Configure AWS OIDC
- [ ] (Optional) Add Databricks/AWS secrets

### Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Commit and push: `git push origin main`
- [ ] Wait for build to complete (check Actions)
- [ ] Verify wheel builds successfully
- [ ] Create tag: `git tag v2.0.0`
- [ ] Push tag: `git push origin v2.0.0`
- [ ] GitHub Release auto-created with wheels
- [ ] Download wheels from Release page
- [ ] Deploy to Databricks/Lambda/Glue

---

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `.github/workflows/build-wheel.yml` | Main build workflow |
| `.github/workflows/publish-s3.yml` | S3 upload workflow |
| `.github/workflows/deploy-databricks.yml` | Databricks deployment |
| `.github/workflows/deploy-lambda-glue.yml` | AWS Lambda/Glue |
| `pyproject.toml` | Package configuration |
| `CI_CD_DEPLOYMENT_GUIDE.md` | Full documentation |

---

## 🎯 Common Commands

```bash
# Build
git push origin main

# Release
git tag v2.0.0 && git push origin v2.0.0

# Download
gh run download -n python-3-10-wheel

# Deploy to S3
aws s3 cp dist/*.whl s3://bucket/libs/

# Deploy to Databricks
databricks fs cp dist/*.whl dbfs:/libraries/

# Deploy to Lambda
aws lambda publish-layer-version \
  --layer-name pydatashred \
  --zip-file fileb://pydatashred-lambda-layer.zip

# Deploy to Glue (reference S3)
# Set in job: Extra Python libraries = s3://bucket/libs/pydatashred.whl
```

---

**For full guide, see: [CI_CD_DEPLOYMENT_GUIDE.md](CI_CD_DEPLOYMENT_GUIDE.md)**
