#!/usr/bin/env python3
"""
Upload wheel file to Databricks Volumes
"""

import os
import sys
from pathlib import Path
from databricks.sdk import WorkspaceClient
# from databricks.sdk.service.iam import GetTokenRequest


def upload_wheel_to_databricks(
    wheel_path: str,
    databricks_host: str = None,
    databricks_token: str = None,
    target_path: str = "/Volumes/workspace/default/dist/"
) -> bool:
    """
    Upload wheel file to Databricks Volumes
    
    Args:
        wheel_path: Path to the wheel file to upload
        databricks_host: Databricks workspace URL (uses DATABRICKS_HOST env var if not provided)
        databricks_token: Databricks API token (uses DATABRICKS_TOKEN env var if not provided)
        target_path: Target path in Databricks Volumes
    
    Returns:
        bool: True if upload successful, False otherwise
    """
    
    # Validate wheel file exists
    wheel_file = Path(wheel_path)
    if not wheel_file.exists():
        print(f"Error: Wheel file not found: {wheel_path}")
        return False
    
    if not wheel_file.suffix == '.whl':
        print(f"Error: File is not a wheel file (must end with .whl): {wheel_path}")
        return False
    
    # Get Databricks credentials from arguments or environment
    host = databricks_host or os.getenv("DATABRICKS_HOST")
    token = databricks_token or os.getenv("DATABRICKS_TOKEN")
    
    if not host:
        print("Error: DATABRICKS_HOST not provided or set in environment")
        return False
    
    if not token:
        print("Error: DATABRICKS_TOKEN not provided or set in environment")
        return False
    
    try:
        # Initialize Databricks client
        print(f"Connecting to Databricks workspace: {host}")
        client = WorkspaceClient(host=host, token=token)
        
        # Verify connection
        user = client.current_user.me()
        print(f"Authenticated as: {user.display_name}")
        
        # Read wheel file content
        with open(wheel_file, 'rb') as f:
            wheel_content = f.read()
        
        # Construct full target path with filename
        wheel_filename = wheel_file.name
        full_target_path = f"{target_path.rstrip('/')}/{wheel_filename}"
        
        print(f"Uploading {wheel_filename} to {full_target_path}")
        print(f"File size: {len(wheel_content) / (1024*1024):.2f} MB")
        
        # Upload file using workspace file system API
        client.workspace.upload(
            path=full_target_path,
            contents=wheel_content,
            overwrite=True
        )
        
        print(f"✓ Successfully uploaded wheel file to {full_target_path}")
        return True
        
    except Exception as e:
        print(f"Error uploading wheel file: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Upload wheel file to Databricks Volumes"
    )
    parser.add_argument(
        "wheel_file",
        help="Path to the wheel file to upload"
    )
    parser.add_argument(
        "--host",
        help="Databricks workspace URL (or use DATABRICKS_HOST env var)",
        default="https://dbc-467986f9-3e2c.cloud.databricks.com"
    )
    parser.add_argument(
        "--token",
        help="Databricks API token (or use DATABRICKS_TOKEN env var)",
        default="dapi75cbe414671e3bfaf02a79648be6eed6"
    )
    parser.add_argument(
        "--target",
        help="Target path in Databricks Volumes",
        default="/Volumes/workspace/default/dist/"
    )
    
    args = parser.parse_args()
    
    success = upload_wheel_to_databricks(
        wheel_path=args.wheel_file,
        databricks_host=args.host,
        databricks_token=args.token,
        target_path=args.target
    )
    
    sys.exit(0 if success else 1)
