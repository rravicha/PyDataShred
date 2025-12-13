#!/bin/bash
# Deploy PyDataShred wheel to Databricks
# Usage: ./deploy-to-databricks.sh dbfs:/path/to/ dist/pydatashred-2.0.0-py3-none-any.whl

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Arguments
DBFS_PATH="${1:?Error: DBFS path required. Usage: $0 dbfs:/path/ [wheel-file]}"
WHEEL_FILE="${2:-dist/pydatashred-*.whl}"

echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo -e "${YELLOW}  PyDataShred → Databricks Deployment${NC}"
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

# Check Databricks CLI
if ! command -v databricks &> /dev/null; then
    echo -e "${RED}✗ Error: Databricks CLI not found${NC}"
    echo "Install: pip install databricks-cli"
    exit 1
fi

echo -e "${GREEN}✓ Databricks CLI found${NC}"

# Check Databricks configuration
if ! databricks workspace list /Shared 2>/dev/null > /dev/null; then
    echo -e "${RED}✗ Error: Databricks not configured${NC}"
    echo ""
    echo "Configure:"
    echo "  databricks configure --token"
    echo ""
    echo "Then run:"
    echo "  $0 $DBFS_PATH $WHEEL_FILE"
    exit 1
fi

echo -e "${GREEN}✓ Databricks configured and accessible${NC}"
echo ""

# Upload to DBFS
echo -e "${YELLOW}Uploading to Databricks DBFS...${NC}"
for wheel in $WHEEL_FILE; do
    if [ -f "$wheel" ]; then
        WHEEL_NAME=$(basename "$wheel")
        FULL_DBFS_PATH="${DBFS_PATH%/}/$WHEEL_NAME"
        
        echo "  Uploading: $WHEEL_NAME"
        echo "  To: $FULL_DBFS_PATH"
        
        databricks fs cp "$wheel" "$FULL_DBFS_PATH" --overwrite
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

# Show usage instructions
echo -e "${BLUE}Installation instructions:${NC}"
echo ""
echo -e "${YELLOW}Option 1: Install in Notebook${NC}"
echo "  %pip install $FULL_DBFS_PATH"
echo ""
echo -e "${YELLOW}Option 2: Add to Cluster Libraries${NC}"
echo "  1. Cluster Configuration → Libraries"
echo "  2. Install from DBFS → $FULL_DBFS_PATH"
echo ""
echo -e "${YELLOW}Option 3: Import in Code${NC}"
echo "  from datashredpy.datamesh import DataProduct"
echo ""

# Verify upload
echo -e "${BLUE}Verifying upload...${NC}"
if databricks fs ls "$DBFS_PATH" | grep -q pydatashred; then
    echo -e "${GREEN}✓ Verified in DBFS${NC}"
else
    echo -e "${YELLOW}⚠ Could not verify (list may require additional permissions)${NC}"
fi

echo ""
