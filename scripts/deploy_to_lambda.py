#!/usr/bin/env python3
"""
Deploy PyDataShred wheel to AWS Lambda
Automated deployment script for Lambda Layers or Functions
"""

import os
import sys
import zipfile
import argparse
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Tuple


class LambdaDeployer:
    """Deploy Python packages to AWS Lambda"""
    
    def __init__(self, wheel_path: str, region: str = 'us-east-1', profile: Optional[str] = None):
        """
        Initialize Lambda deployer
        
        Args:
            wheel_path: Path to wheel file
            region: AWS region
            profile: AWS profile name
        """
        self.wheel_path = Path(wheel_path)
        self.region = region
        self.profile = profile
        self.aws_cmd = ['aws']
        
        if profile:
            self.aws_cmd.extend(['--profile', profile])
        self.aws_cmd.extend(['--region', region])
        
        # Validate wheel file
        if not self.wheel_path.exists():
            raise FileNotFoundError(f"Wheel file not found: {wheel_path}")
        if not self.wheel_path.suffix == '.whl':
            raise ValueError(f"File must be a .whl file: {wheel_path}")
        
        print(f"✓ Wheel file found: {self.wheel_path.name}")
        print(f"✓ Region: {region}")
        if profile:
            print(f"✓ Profile: {profile}")
    
    def create_layer_package(self, output_dir: str = None) -> Path:
        """
        Create Lambda Layer-compatible ZIP file
        
        Args:
            output_dir: Directory to save ZIP file
        
        Returns:
            Path to created ZIP file
        """
        if output_dir is None:
            output_dir = self.wheel_path.parent
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        work_dir = output_dir / 'lambda_layer_work'
        python_dir = work_dir / 'python' / 'lib' / 'python3.11' / 'site-packages'
        python_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"\n📦 Creating Lambda Layer package...")
            
            # Extract wheel to layer directory
            print(f"  Extracting wheel file...")
            with zipfile.ZipFile(self.wheel_path, 'r') as zip_ref:
                zip_ref.extractall(python_dir)
            
            # Create layer ZIP
            layer_zip = output_dir / f"{self.wheel_path.stem}-layer.zip"
            print(f"  Creating ZIP file: {layer_zip.name}")
            
            with zipfile.ZipFile(layer_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(work_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(work_dir)
                        zipf.write(file_path, arcname)
            
            # Cleanup
            import shutil
            shutil.rmtree(work_dir)
            
            print(f"✓ Layer package created: {layer_zip.name}")
            print(f"  Size: {layer_zip.stat().st_size / (1024*1024):.2f} MB")
            
            return layer_zip
        
        except Exception as e:
            print(f"✗ Error creating layer package: {e}")
            raise
    
    def create_function_package(self, handler_code: str = None, output_dir: str = None) -> Path:
        """
        Create Lambda Function deployment package
        
        Args:
            handler_code: Python handler code (optional)
            output_dir: Directory to save ZIP file
        
        Returns:
            Path to created ZIP file
        """
        if output_dir is None:
            output_dir = self.wheel_path.parent
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        work_dir = output_dir / 'lambda_function_work'
        work_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"\n📦 Creating Lambda Function package...")
            
            # Create default handler if not provided
            if handler_code is None:
                handler_code = '''import json
import sys
from datashredpy.helper.models import Client

def lambda_handler(event, context):
    """
    Lambda handler function using PyDataShred
    """
    try:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'PyDataShred Lambda handler working!',
                'event': event
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
'''
            
            # Write handler code
            handler_file = work_dir / 'lambda_function.py'
            handler_file.write_text(handler_code)
            print(f"  Created handler: lambda_function.py")
            
            # Copy wheel file
            import shutil
            shutil.copy(self.wheel_path, work_dir / self.wheel_path.name)
            print(f"  Copied wheel file: {self.wheel_path.name}")
            
            # Create ZIP
            func_zip = output_dir / f"{self.wheel_path.stem}-function.zip"
            print(f"  Creating ZIP file: {func_zip.name}")
            
            with zipfile.ZipFile(func_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(work_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(work_dir)
                        zipf.write(file_path, arcname)
            
            # Cleanup
            shutil.rmtree(work_dir)
            
            print(f"✓ Function package created: {func_zip.name}")
            print(f"  Size: {func_zip.stat().st_size / (1024*1024):.2f} MB")
            
            return func_zip
        
        except Exception as e:
            print(f"✗ Error creating function package: {e}")
            raise
    
    def upload_to_s3(self, file_path: Path, bucket: str, prefix: str = '') -> str:
        """
        Upload file to S3
        
        Args:
            file_path: File to upload
            bucket: S3 bucket name
            prefix: S3 prefix/folder
        
        Returns:
            S3 URI
        """
        try:
            print(f"\n☁️  Uploading to S3...")
            
            s3_path = f"s3://{bucket}/{prefix}{file_path.name}".replace('//', '/')
            
            cmd = self.aws_cmd + [
                's3', 'cp',
                str(file_path),
                s3_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✓ Uploaded to S3: {s3_path}")
            
            return s3_path
        
        except subprocess.CalledProcessError as e:
            print(f"✗ Error uploading to S3: {e.stderr.decode()}")
            raise
    
    def publish_layer(self, zip_file: Path, layer_name: str, 
                     compatible_runtimes: list = None) -> Dict:
        """
        Publish Lambda Layer
        
        Args:
            zip_file: Layer ZIP file
            layer_name: Name for the layer
            compatible_runtimes: Compatible Python runtimes
        
        Returns:
            Layer metadata
        """
        if compatible_runtimes is None:
            compatible_runtimes = ['python3.11', 'python3.12']
        
        try:
            print(f"\n🚀 Publishing Lambda Layer...")
            
            with open(zip_file, 'rb') as f:
                zip_content = f.read()
            
            cmd = self.aws_cmd + [
                'lambda', 'publish-layer-version',
                '--layer-name', layer_name,
                '--zip-file', f'fileb://{str(zip_file)}',
                '--compatible-runtimes'
            ] + compatible_runtimes + ['--output', 'json']
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            layer_info = json.loads(result.stdout)
            
            print(f"✓ Layer published successfully!")
            print(f"  Layer ARN: {layer_info['LayerVersionArn']}")
            print(f"  Version: {layer_info['Version']}")
            
            return layer_info
        
        except subprocess.CalledProcessError as e:
            print(f"✗ Error publishing layer: {e.stderr}")
            raise
    
    def create_function(self, function_name: str, zip_file: Path, 
                       role_arn: str, handler: str = 'lambda_function.lambda_handler',
                       runtime: str = 'python3.11', timeout: int = 60,
                       memory_size: int = 256, layers: list = None) -> Dict:
        """
        Create Lambda function
        
        Args:
            function_name: Name for the function
            zip_file: Function ZIP file
            role_arn: IAM role ARN
            handler: Handler path
            runtime: Python runtime
            timeout: Timeout in seconds
            memory_size: Memory in MB
            layers: Layer ARNs to attach
        
        Returns:
            Function metadata
        """
        try:
            print(f"\n🚀 Creating Lambda Function...")
            
            with open(zip_file, 'rb') as f:
                zip_content = f.read()
            
            cmd = self.aws_cmd + [
                'lambda', 'create-function',
                '--function-name', function_name,
                '--runtime', runtime,
                '--role', role_arn,
                '--handler', handler,
                '--zip-file', f'fileb://{str(zip_file)}',
                '--timeout', str(timeout),
                '--memory-size', str(memory_size),
                '--output', 'json'
            ]
            
            if layers:
                cmd.extend(['--layers'] + layers)
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            function_info = json.loads(result.stdout)
            
            print(f"✓ Function created successfully!")
            print(f"  Function ARN: {function_info['FunctionArn']}")
            print(f"  Handler: {function_info['Handler']}")
            
            return function_info
        
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr
            if 'already exists' in error_msg.lower():
                print(f"⚠️  Function already exists. Use update-function-code to update it.")
            print(f"✗ Error creating function: {error_msg}")
            raise
    
    def test_function(self, function_name: str, test_payload: Dict = None) -> Dict:
        """
        Test Lambda function
        
        Args:
            function_name: Function name
            test_payload: Test event payload
        
        Returns:
            Function response
        """
        if test_payload is None:
            test_payload = {'test': 'payload'}
        
        try:
            print(f"\n🧪 Testing Lambda Function...")
            
            cmd = self.aws_cmd + [
                'lambda', 'invoke',
                '--function-name', function_name,
                '--payload', json.dumps(test_payload),
                '--output', 'json',
                'response.json'
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Read response
            with open('response.json', 'r') as f:
                response = json.load(f)
            
            print(f"✓ Function invoked successfully!")
            print(f"  Status Code: {response.get('StatusCode')}")
            
            return response
        
        except subprocess.CalledProcessError as e:
            print(f"✗ Error testing function: {e.stderr}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description='Deploy PyDataShred wheel to AWS Lambda'
    )
    parser.add_argument('wheel_file', help='Path to wheel file')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--profile', help='AWS profile name')
    parser.add_argument('--action', 
                       choices=['layer', 'function', 'both', 'upload'],
                       default='layer',
                       help='Deployment action')
    parser.add_argument('--layer-name', default='pydatashred-layer',
                       help='Lambda Layer name')
    parser.add_argument('--function-name', default='pydatashred-handler',
                       help='Lambda Function name')
    parser.add_argument('--role-arn', help='IAM role ARN for Lambda execution')
    parser.add_argument('--s3-bucket', help='S3 bucket for uploading')
    parser.add_argument('--s3-prefix', default='lambda-packages/',
                       help='S3 prefix for uploads')
    parser.add_argument('--test', action='store_true',
                       help='Test the function after creation')
    parser.add_argument('--output-dir', default='.',
                       help='Output directory for packages')
    
    args = parser.parse_args()
    
    try:
        deployer = LambdaDeployer(
            wheel_path=args.wheel_file,
            region=args.region,
            profile=args.profile
        )
        
        if args.action in ['layer', 'both']:
            layer_zip = deployer.create_layer_package(args.output_dir)
            
            if args.s3_bucket:
                deployer.upload_to_s3(layer_zip, args.s3_bucket, args.s3_prefix)
            
            layer_info = deployer.publish_layer(layer_zip, args.layer_name)
            print(f"\n✅ Layer deployment complete!")
            print(f"Layer ARN: {layer_info['LayerVersionArn']}")
        
        if args.action in ['function', 'both']:
            if not args.role_arn:
                print("✗ Error: --role-arn is required for function deployment")
                return
            
            func_zip = deployer.create_function_package(output_dir=args.output_dir)
            
            func_info = deployer.create_function(
                function_name=args.function_name,
                zip_file=func_zip,
                role_arn=args.role_arn
            )
            
            if args.test:
                deployer.test_function(args.function_name)
            
            print(f"\n✅ Function deployment complete!")
            print(f"Function ARN: {func_info['FunctionArn']}")
        
        if args.action == 'upload':
            layer_zip = deployer.create_layer_package(args.output_dir)
            if args.s3_bucket:
                deployer.upload_to_s3(layer_zip, args.s3_bucket, args.s3_prefix)
            else:
                print("✗ Error: --s3-bucket is required for upload")
    
    except Exception as e:
        print(f"\n✗ Deployment failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
