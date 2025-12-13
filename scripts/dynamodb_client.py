#!/usr/bin/env python3
"""
DynamoDB Query Tool for PyDataShred
Alternative to DataGrip for querying DynamoDB tables
"""

import boto3
import json
import argparse
from typing import Dict, List, Any, Optional
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


class DynamoDBClient:
    """Client for querying DynamoDB tables"""
    
    def __init__(self, table_name: str = 'pds-job-tracker-dev', region: str = None):
        """
        Initialize DynamoDB client
        
        Args:
            table_name: DynamoDB table name
            region: AWS region (uses default if not specified)
        """
        try:
            if region:
                self.dynamodb = boto3.resource('dynamodb', region_name=region)
            else:
                self.dynamodb = boto3.resource('dynamodb')
            
            self.table = self.dynamodb.Table(table_name)
            self.table_name = table_name
            
            # Verify connection
            self.table.load()
            print(f"✓ Connected to table: {table_name}")
        except ClientError as e:
            print(f"✗ Error connecting to DynamoDB: {e}")
            raise
    
    def scan_table(self, limit: int = None, filter_expression: Dict = None) -> List[Dict]:
        """
        Scan entire table
        
        Args:
            limit: Maximum items to return
            filter_expression: Optional filter criteria
        
        Returns:
            List of items
        """
        try:
            kwargs = {}
            if limit:
                kwargs['Limit'] = limit
            
            response = self.table.scan(**kwargs)
            items = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
                response = self.table.scan(**kwargs)
                items.extend(response.get('Items', []))
            
            print(f"✓ Scanned {len(items)} items from {self.table_name}")
            return items
        except ClientError as e:
            print(f"✗ Error scanning table: {e}")
            return []
    
    def query_by_key(self, key_name: str, key_value: Any, sort_key: Optional[Dict] = None) -> List[Dict]:
        """
        Query table by partition key
        
        Args:
            key_name: Partition key name
            key_value: Partition key value
            sort_key: Optional sort key condition
        
        Returns:
            List of matching items
        """
        try:
            key_condition = Key(key_name).eq(key_value)
            
            if sort_key:
                sort_key_name = list(sort_key.keys())[0]
                sort_key_value = sort_key[sort_key_name]
                key_condition = key_condition & Key(sort_key_name).eq(sort_key_value)
            
            response = self.table.query(KeyConditionExpression=key_condition)
            items = response.get('Items', [])
            
            print(f"✓ Query returned {len(items)} items")
            return items
        except ClientError as e:
            print(f"✗ Error querying table: {e}")
            return []
    
    def get_item(self, key: Dict) -> Optional[Dict]:
        """
        Get single item by key
        
        Args:
            key: Dictionary with partition key (and sort key if applicable)
        
        Returns:
            Item or None
        """
        try:
            response = self.table.get_item(Key=key)
            item = response.get('Item')
            
            if item:
                print(f"✓ Item found")
            else:
                print(f"✗ Item not found")
            
            return item
        except ClientError as e:
            print(f"✗ Error getting item: {e}")
            return None
    
    def put_item(self, item: Dict) -> bool:
        """
        Put item in table
        
        Args:
            item: Item to insert
        
        Returns:
            True if successful
        """
        try:
            self.table.put_item(Item=item)
            print(f"✓ Item inserted successfully")
            return True
        except ClientError as e:
            print(f"✗ Error putting item: {e}")
            return False
    
    def update_item(self, key: Dict, attributes: Dict) -> bool:
        """
        Update item attributes
        
        Args:
            key: Item key
            attributes: Attributes to update
        
        Returns:
            True if successful
        """
        try:
            update_expression = "SET " + ", ".join([f"{k}=:{k}" for k in attributes.keys()])
            expression_values = {f":{k}": v for k, v in attributes.items()}
            
            self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            print(f"✓ Item updated successfully")
            return True
        except ClientError as e:
            print(f"✗ Error updating item: {e}")
            return False
    
    def delete_item(self, key: Dict) -> bool:
        """
        Delete item from table
        
        Args:
            key: Item key
        
        Returns:
            True if successful
        """
        try:
            self.table.delete_item(Key=key)
            print(f"✓ Item deleted successfully")
            return True
        except ClientError as e:
            print(f"✗ Error deleting item: {e}")
            return False
    
    def get_table_info(self) -> Dict:
        """Get table metadata"""
        try:
            return {
                'table_name': self.table.name,
                'table_status': self.table.table_status,
                'item_count': self.table.item_count,
                'table_size_bytes': self.table.table_size_bytes,
                'creation_datetime': str(self.table.creation_datetime),
                'key_schema': self.table.key_schema,
                'attribute_definitions': self.table.attribute_definitions,
                'billing_mode': getattr(self.table, 'billing_mode_summary', {}).get('BillingMode', 'N/A'),
            }
        except Exception as e:
            print(f"✗ Error getting table info: {e}")
            return {}
    
    def export_to_json(self, items: List[Dict], filename: str) -> bool:
        """Export items to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(items, f, indent=2, default=str)
            print(f"✓ Exported {len(items)} items to {filename}")
            return True
        except Exception as e:
            print(f"✗ Error exporting to JSON: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Query DynamoDB tables from PyDataShred'
    )
    parser.add_argument(
        '--table',
        default='pds-job-tracker-dev',
        help='DynamoDB table name'
    )
    parser.add_argument(
        '--region',
        help='AWS region'
    )
    parser.add_argument(
        '--action',
        choices=['scan', 'info', 'query', 'get', 'put', 'update', 'delete', 'export'],
        default='info',
        help='Action to perform'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of items (for scan)'
    )
    parser.add_argument(
        '--key',
        type=json.loads,
        help='Item key as JSON (for get, update, delete)'
    )
    parser.add_argument(
        '--data',
        type=json.loads,
        help='Item data as JSON (for put, update)'
    )
    parser.add_argument(
        '--output',
        help='Output file for export (JSON)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print output'
    )
    
    args = parser.parse_args()
    
    try:
        client = DynamoDBClient(table_name=args.table, region=args.region)
        
        if args.action == 'info':
            info = client.get_table_info()
            print("\n" + "="*60)
            print("TABLE INFORMATION")
            print("="*60)
            print(json.dumps(info, indent=2))
        
        elif args.action == 'scan':
            items = client.scan_table(limit=args.limit)
            print("\n" + "="*60)
            if args.output:
                client.export_to_json(items, args.output)
            else:
                print(json.dumps(items, indent=2 if args.pretty else None, default=str))
        
        elif args.action == 'get':
            if not args.key:
                print("✗ Error: --key required for get action")
                return
            item = client.get_item(args.key)
            if item:
                print(json.dumps(item, indent=2 if args.pretty else None, default=str))
        
        elif args.action == 'put':
            if not args.data:
                print("✗ Error: --data required for put action")
                return
            client.put_item(args.data)
        
        elif args.action == 'update':
            if not args.key or not args.data:
                print("✗ Error: --key and --data required for update action")
                return
            client.update_item(args.key, args.data)
        
        elif args.action == 'delete':
            if not args.key:
                print("✗ Error: --key required for delete action")
                return
            client.delete_item(args.key)
        
        elif args.action == 'export':
            if not args.output:
                print("✗ Error: --output required for export action")
                return
            items = client.scan_table()
            client.export_to_json(items, args.output)
    
    except Exception as e:
        print(f"✗ Fatal error: {e}")


if __name__ == '__main__':
    main()
