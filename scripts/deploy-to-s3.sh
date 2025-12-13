#!/bin/bash
# Deploy PyDataShred wheel to AWS S3
# Usage: ./deploy-to-s3.sh s3://my-bucket/libs/ dist/pydatashred-2.0.0-py3-none-any.whl

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Arguments
S3_PATH="${1:?Error: S3 path required. Usage: $0 s3://bucket/path/ [wheel-file]}"
WHEEL_FILE="${2:-dist/pydatashred-*.whl}"

echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo -e "${YELLOW}  PyDataShred → AWS S3 Deployment${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo ""

# Check if wheel file exists
if ! ls $WHEEL_FILE 1> /dev/null 2>&1; then
    echo -e "${RED}✗ Error: Wheel file not found: $WHEEL_FILE${NC}"
    echo ""
    echo "Build wheel first:"
    echo "  python -m build --wheel"
    exit 1
fi

echo -e "${GREEN}✓ Found wheel file(s)${NC}"
ls -lh $WHEEL_FILE
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}✗ Error: AWS CLI not found${NC}"
    echo "Install: pip install awscli"
    exit 1
fi

echo -e "${GREEN}✓ AWS CLI configured${NC}"
echo ""

# Upload to S3
echo -e "${YELLOW}Uploading to S3...${NC}"
for wheel in $WHEEL_FILE; do
    if [ -f "$wheel" ]; then
        echo "  Uploading: $(basename $wheel)"
        aws s3 cp "$wheel" "$S3_PATH"
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✓ Success${NC}"
        else
            echo -e "  ${RED}✗ Failed${NC}"
            exit 1
        fi
    fi
done

echo ""
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Upload Complete${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""

# List uploaded files
echo -e "${YELLOW}Uploaded files in S3:${NC}"
aws s3 ls "$S3_PATH" | grep pydatashred || echo "  (List command may require additional permissions)"

echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  For Databricks:"
echo "    %pip install $S3_PATH<wheel-name>"
echo ""
echo "  For Glue:"
echo "    Set in job config: Extra Python libraries = $S3_PATH<wheel-name>"
echo ""
