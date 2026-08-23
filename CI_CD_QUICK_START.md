# 🚀 CI/CD Quick Start Checklist

## ✅ Step 1: Verify Setup (2 min)

```bash
# Check all files are in place
echo "=== Checking GitHub Workflows ==="
ls -la .github/workflows/
# Should show: build-wheel.yml, publish-s3.yml, deploy-databricks.yml, deploy-lambda-glue.yml

echo "=== Checking Deployment Scripts ==="
ls -la scripts/
# Should show: deploy-to-s3.sh, deploy-to-databricks.sh, deploy-to-lambda.sh

echo "=== Checking Documentation ==="
ls -la CI_CD*.md
# Should show: CI_CD_README.md, CI_CD_DEPLOYMENT_GUIDE.md, CI_CD_QUICK_REFERENCE.md
```

---

## ✅ Step 2: Commit and Push (3 min)

```bash
# Add all new files
git add .github/ scripts/ CI_CD*.md pyproject.toml

# Commit
git commit -m "Add CI/CD pipeline for wheel building and distribution"

# Push to GitHub
git push origin main

# Verify: Go to https://github.com/YOUR_REPO/actions
```

---

## ✅ Step 3: Monitor First Build (5 min)

```bash
# Check workflow status
gh run list --workflow=build-wheel.yml

# View latest run (real-time)
gh run view --log

# Or use GitHub UI:
# GitHub → Actions → build-wheel workflow → latest run
```

**Success indicators:**
- ✅ build job: 4-6 wheels created
- ✅ test-wheel job: All wheels tested
- ✅ validate job: Code validated
- ✅ create-release: Only if you push a tag

---

## ✅ Step 4 (Optional): Configure AWS

### Option A: OIDC (Recommended - No API Keys)

```bash
# 1. View setup instructions
cat CI_CD_QUICK_REFERENCE.md | grep -A 20 "AWS OIDC"

# 2. Go to AWS Console (or use CloudFormation from CI_CD_README.md)

# 3. Add GitHub secret
gh secret set AWS_ROLE_TO_ASSUME --body "arn:aws:iam::ACCOUNT_ID:role/github-actions-role"

# Done! Next build will auto-upload to S3
```

### Option B: Access Keys (Simpler but Less Secure)

```bash
gh secret set AWS_ACCESS_KEY_ID --body "your-access-key"
gh secret set AWS_SECRET_ACCESS_KEY --body "your-secret-key"
```

### Option C: Skip for Now

✅ Wheels still available in GitHub Actions artifacts  
✅ You can manually upload using scripts later

---

## ✅ Step 5: Test Locally (Optional)

```bash
# Build wheel locally
pip install build
python -m build --wheel

# Check output
ls dist/

# Install from wheel
pip install dist/pydatashred-*.whl

# Test import
python -c "from datashredpy import *; print('✓ Success')"
```

---

## ✅ Step 6: Deploy to Platform

### Deploy to Databricks

**Option 1: From GitHub Release (Easiest)**
```bash
# 1. Create release: git tag v2.0.0 && git push origin v2.0.0
# 2. Go to GitHub → Releases
# 3. Download wheel
# 4. In Databricks, upload to workspace or cluster
```

**Option 2: From S3**
```bash
# If AWS configured:
# 1. Wheel auto-uploaded to S3 on build
# 2. In Databricks: pip install s3://bucket/pydatashred-*.whl
```

**Option 3: Script**
```bash
./scripts/deploy-to-databricks.sh "dbfs:/libraries/" dist/pydatashred-*.whl
```

### Deploy to Lambda

**Option 1: Using Workflow (If AWS Configured)**
```bash
# Workflow auto-creates layer zip as artifact
# Download: gh run download -n lambda-layer-zip
```

**Option 2: Manual Script**
```bash
./scripts/deploy-to-lambda.sh "pydatashred-layer" pydatashred-lambda-layer.zip
```

### Deploy to Glue

```bash
# Method 1: Reference from S3
# In Glue job config → Python library path → s3://bucket/pydatashred-*.whl

# Method 2: Upload to S3 and reference
./scripts/deploy-to-s3.sh "s3://my-bucket/libs/" dist/pydatashred-*.whl
```

---

## 📋 Workflow Triggers

### Automatic Triggers

```bash
# Trigger 1: Every push to main/master/develop
git push origin main
# → build-wheel starts automatically

# Trigger 2: Every pull request
git push origin feature-branch
# → build-wheel runs in PR checks

# Trigger 3: Git tag (for releases)
git tag v2.0.0
git push origin v2.0.0
# → build-wheel + create-release + publish-s3

# View triggers in: .github/workflows/build-wheel.yml
```

### Manual Triggers

```bash
# From command line (requires gh CLI)
gh workflow run build-wheel.yml

# From GitHub UI:
# GitHub → Actions → Select workflow → "Run workflow" button
```

---

## 📊 Common Commands

### Check Workflow Status
```bash
# List recent runs
gh run list --workflow=build-wheel.yml

# View specific run
gh run view RUN_ID

# Follow live
gh run watch RUN_ID

# Download artifacts
gh run download RUN_ID -n python-3-10-wheel
```

### Manage Secrets
```bash
# List secrets
gh secret list

# Set secret
gh secret set SECRET_NAME --body "value"

# Delete secret
gh secret delete SECRET_NAME
```

### Test Build Locally
```bash
# Clean old builds
rm -rf build dist *.egg-info

# Build wheels
python -m build --wheel

# Check output
ls -lh dist/

# Install and test
pip install dist/pydatashred-*.whl
python -c "import datashredpy; print('✓')"
```

---

## 🔍 Verification Checklist

### Before First Build
- [ ] All 4 workflows created in `.github/workflows/`
- [ ] All 3 scripts created in `scripts/` with execute permissions
- [ ] All 3 documentation files created
- [ ] `pyproject.toml` updated
- [ ] Files pushed to GitHub

### After First Build
- [ ] GitHub Actions tab shows successful build
- [ ] 6 wheel artifacts generated (one per Python version + universal)
- [ ] Wheel files in `dist/` directory
- [ ] Release created (if tagged)

### Before Deployment
- [ ] Have wheel file (from GitHub artifacts or local build)
- [ ] Know target platform (Databricks/Lambda/Glue)
- [ ] Have access credentials for target platform
- [ ] (Optional) AWS configured for S3 auto-upload

---

## 🆘 Quick Troubleshooting

### Build Failed
```bash
# Check logs
gh run view RUN_ID --log

# Common causes:
# - Missing dependencies in pyproject.toml
# - Python syntax errors
# - Missing __init__.py files

# Fix and retry
git push origin main
```

### Wheel Won't Install
```bash
# Check Python version matches wheel name
python --version  # e.g., 3.10.x

# Try specific wheel
pip install dist/pydatashred-py310-none-any.whl

# Check dependencies
pip install -e .
```

### AWS Upload Not Working
```bash
# Check secret is set
gh secret list | grep AWS

# Verify role exists
aws iam get-role --role-name github-actions-role

# Check workflow logs
gh run view RUN_ID --log | grep -i aws
```

### Can't Download Artifacts
```bash
# Check gh CLI installed
gh --version

# Authenticate
gh auth login

# List available artifacts
gh run download RUN_ID --dir .

# Or download from GitHub UI:
# GitHub → Actions → Latest run → Artifacts
```

---

## 📚 Documentation Reference

| File | Purpose | Read Time |
|------|---------|-----------|
| **CI_CD_README.md** | Overview & setup | 10 min |
| **CI_CD_QUICK_REFERENCE.md** | Commands & checklists | 5 min |
| **CI_CD_DEPLOYMENT_GUIDE.md** | Complete reference | 30+ min |
| **CI_CD_IMPLEMENTATION_SUMMARY.md** | This document | 5 min |

---

## ✨ Success Criteria

### Build Works
- ✅ Push triggers automatic build
- ✅ Wheels created for all Python versions
- ✅ Tests pass
- ✅ Code validated

### Deployment Works
- ✅ Wheel can be installed: `pip install pydatashred-*.whl`
- ✅ Package imports successfully: `from datashredpy import *`
- ✅ Scripts work: `./deploy-to-*.sh`
- ✅ All documentation accurate

### You're Done When
- ✅ First build runs and completes
- ✅ You've downloaded at least one wheel
- ✅ You understand how to deploy to your platform

---

## 🎯 Next Steps

1. **Immediate**: Run verification checklist ✓
2. **Today**: Push and monitor first build
3. **This week**: Configure AWS (optional)
4. **This week**: Test deployment to your platform
5. **Ongoing**: Use workflows for all releases

---

## 💡 Pro Tips

1. **Version automatically**: Use git tags (`v1.2.3`) - no manual changes needed
2. **Test locally first**: Run `python -m build` before pushing big changes
3. **Watch the logs**: `gh run watch` shows real-time build progress
4. **Keep docs updated**: Platform-specific docs are auto-generated by workflows
5. **Use manual triggers**: Perfect for testing without git commits
6. **Archive old builds**: Workflows run free, artifacts count toward storage

---

## 📞 Need Help?

- **GitHub Actions**: https://docs.github.com/en/actions
- **Packaging**: https://packaging.python.org/
- **setuptools**: https://setuptools.pypa.io/
- **Your docs**: See CI_CD_DEPLOYMENT_GUIDE.md for platform-specific help

---

## ✅ TL;DR - Just Get Started

```bash
# 1. Push
git push origin main

# 2. Wait for build (5-10 min)

# 3. Download wheel
gh run download -n python-3-10-wheel

# 4. Deploy
pip install dist/pydatashred-*.whl

# Done! 🎉
```

---

**Created:** $(date)  
**Updated:** See commit history  
**Status:** ✅ Production Ready  

