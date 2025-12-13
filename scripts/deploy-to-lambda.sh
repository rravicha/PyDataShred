#!/bin/bash
# Deploy PyDataShred as AWS Lambda Layer
# Usage: ./deploy-to-lambda.sh pydatashred-layer pydatashred-lambda-layer.zip

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Arguments
LAYER_NAME="${1:?Error: Layer name required. Usage: $0 layer-name [zip-file]}"
ZIP_FILE="${2:?Error: Zip file required. Usage: $0 layer-name zip-file}"
FUNCTION_NAME="${3:-}"  # Optional

echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo -e "${YELLOW}  PyDataShred → AWS Lambda Layer${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo ""

# Check if zip file exists
if [ ! -f "$ZIP_FILE" ]; then
    echo -e "${RED}✗ Error: Zip file not found: $ZIP_FILE${NC}"
    echo ""
    echo "Create layer zip first:"
    echo "  mkdir -p lambda-layer/python/lib/python3.10/site-packages"
    echo "  cd lambda-layer/python/lib/python3.10/site-packages"
    echo "  unzip ../../../../../dist/pydatashred-*.whl"
    echo "  cd ../../../../../"
    echo "  zip -r ../pydatashred-lambda-layer.zip ."
    exit 1
fi

echo -e "${GREEN}✓ Found zip file${NC}"
ls -lh "$ZIP_FILE"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}✗ Error: AWS CLI not found${NC}"
    echo "Install: pip install awscli"
    exit 1
fi

echo -e "${GREEN}✓ AWS CLI configured${NC}"
echo ""

# Check file size (Lambda layer limit is 262MB)
FILE_SIZE=$(stat -f%z "$ZIP_FILE" 2>/dev/null || stat -c%s "$ZIP_FILE" 2>/dev/null || echo 0)
FILE_SIZE_MB=$((FILE_SIZE / 1024 / 1024))

if [ "$FILE_SIZE_MB" -gt 262 ]; then
    echo -e "${RED}✗ Error: Layer too large (${FILE_SIZE_MB}MB > 262MB limit)${NC}"
    exit 1
fi

echo -e "${BLUE}Layer size: ${FILE_SIZE_MB}MB${NC}"
echo ""

# Publish layer version
echo -e "${YELLOW}Publishing Lambda layer...${NC}"
RESPONSE=$(aws lambda publish-layer-version \
    --layer-name "$LAYER_NAME" \
    --description "PyDataShred Python package" \
    --zip-file "fileb://$ZIP_FILE" \
    --compatible-runtimes python3.10 python3.11 python3.12 \
    --output json)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Layer published successfully${NC}"
    echo ""
    
    # Extract details
    LAYER_VERSION=$(echo "$RESPONSE" | grep -o '"Version": [0-9]*' | grep -o '[0-9]*')
    LAYER_ARN=$(echo "$RESPONSE" | grep -o '"LayerVersionArn": "[^"]*"' | cut -d'"' -f4)
    
    echo -e "${BLUE}Layer Details:${NC}"
    echo "  Name: $LAYER_NAME"
    echo "  Version: $LAYER_VERSION"
    echo "  ARN: $LAYER_ARN"
    echo ""
else
    echo -e "${RED}✗ Failed to publish layer${NC}"
    echo "$RESPONSE"
    exit 1
fi

# Optionally add to function
if [ -n "$FUNCTION_NAME" ]; then
    echo -e "${YELLOW}Adding layer to Lambda function...${NC}"
    aws lambda update-function-configuration \
        --function-name "$FUNCTION_NAME" \
        --layers "$LAYER_ARN" > /dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Layer added to $FUNCTION_NAME${NC}"
    else
        echo -e "${RED}✗ Failed to add layer to function${NC}"
    fi
    echo ""
fi

# Show usage instructions
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Deployment Complete${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo -e "${YELLOW}Option 1: Add to existing function${NC}"
echo "  aws lambda update-function-configuration \\"
echo "    --function-name my-function \\"
echo "    --layers $LAYER_ARN"
echo ""
echo -e "${YELLOW}Option 2: Add to new function${NC}"
echo "  aws lambda create-function \\"
echo "    --function-name my-function \\"
echo "    --runtime python3.10 \\"
echo "    --layers $LAYER_ARN \\"
echo "    ..."
echo ""
echo -e "${YELLOW}Option 3: Use in function code${NC}"
echo "  from datashredpy.datamesh import DataProduct"
echo ""
echo -e "${BLUE}Remove layer:${NC}"
echo "  aws lambda delete-layer-version \\"
echo "    --layer-name $LAYER_NAME \\"
echo "    --version-number $LAYER_VERSION"
echo ""
