#!/usr/bin/env python3
"""
Upload wheel file to Databricks Volumes using REST API
Alternative approach without SDK dependency
"""

import os
import sys
import requests
import base64
from pathlib import Path
from typing import Optional


def upload_wheel_rest_api(
    wheel_path: str,
    databricks_host: str = None,
    databricks_token: str = None,
    target_path: str = "/Volumes/workspace/default/dist/"
) -> bool:
    """
    Upload wheel file to Databricks using REST API
    
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
    
    # Normalize host URL
    host = host.rstrip('/')
    
    try:
        # Test connection first
        print(f"Testing connection to Databricks workspace: {host}")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{host}/api/2.0/workspace/get-status",
            params={"path": "/"},
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"Error: Failed to authenticate with Databricks: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print("✓ Successfully authenticated with Databricks")
        
        # Read wheel file
        with open(wheel_file, 'rb') as f:
            wheel_content = f.read()
        
        # Construct full target path
        wheel_filename = wheel_file.name
        full_target_path = f"{target_path.rstrip('/')}/{wheel_filename}"
        
        print(f"Uploading {wheel_filename}")
        print(f"Target path: {full_target_path}")
        print(f"File size: {len(wheel_content) / (1024*1024):.2f} MB")
        
        # Encode content in base64 for API transmission
        encoded_content = base64.b64encode(wheel_content).decode('utf-8')
        
        # Upload using Workspace Files API
        upload_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        upload_data = {
            "path": full_target_path,
            "contents": encoded_content,
            "overwrite": True
        }
        
        response = requests.post(
            f"{host}/api/2.1/workspace/import",
            json=upload_data,
            headers=upload_headers,
            timeout=300  # 5 minute timeout for large files
        )
        
        if response.status_code not in [200, 201]:
            print(f"Error: Upload failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print(f"✓ Successfully uploaded wheel file to {full_target_path}")
        return True
        
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Failed to connect to Databricks: {str(e)}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"Error: Request timeout: {str(e)}")
        return False
    except Exception as e:
        print(f"Error uploading wheel file: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Upload wheel file to Databricks Volumes using REST API"
    )
    parser.add_argument(
        "wheel_file",
        help="Path to the wheel file to upload"
    )
    parser.add_argument(
        "--host",
        help="Databricks workspace URL (or use DATABRICKS_HOST env var)",
        default=None
    )
    parser.add_argument(
        "--token",
        help="Databricks API token (or use DATABRICKS_TOKEN env var)",
        default=None
    )
    parser.add_argument(
        "--target",
        help="Target path in Databricks Volumes",
        default="/Volumes/workspace/default/dist/"
    )
    
    args = parser.parse_args()
    
    success = upload_wheel_rest_api(
        wheel_path=args.wheel_file,
        databricks_host=args.host,
        databricks_token=args.token,
        target_path=args.target
    )
    
    sys.exit(0 if success else 1)
