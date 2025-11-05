#!/usr/bin/env python3
"""
Test ClickHouse connection
Run: python3 backend/test_clickhouse.py
"""

import clickhouse_connect
from dotenv import load_dotenv
import os

load_dotenv()

print("Testing ClickHouse Connection...")
print(f"Host: {os.environ['CLICKHOUSE_HOST']}")
print(f"Port: {os.environ['CLICKHOUSE_PORT']}")
print(f"User: {os.environ['CLICKHOUSE_USER']}")
print()

try:
    print("Attempting to connect...")
    client = clickhouse_connect.get_client(
        host=os.environ['CLICKHOUSE_HOST'],
        port=int(os.environ['CLICKHOUSE_PORT']),
        username=os.environ['CLICKHOUSE_USER'],
        password=os.environ['CLICKHOUSE_PASSWORD'],
        secure=True,
        verify=True,
        connect_timeout=30,
        send_receive_timeout=60
    )
    print("✓ Connection successful!")
    print()

    # Test query
    print("Testing simple query...")
    result = client.query("SELECT 1 as test")
    print(f"✓ Query result: {result.result_rows}")
    print()

    # Test your table
    print("Testing garmin_active_cal_data table...")
    result = client.query("SELECT COUNT(*) as count FROM garmin_active_cal_data")
    print(f"✓ Table has {result.result_rows[0][0]} rows")
    print()

    # Show sample data
    print("Sample data:")
    result = client.query("SELECT * FROM garmin_active_cal_data LIMIT 3")
    for row in result.result_rows:
        print(f"  {row}")

    print()
    print("🎉 All tests passed!")

except Exception as e:
    print(f"✗ Error: {e}")
    print()
    print("Troubleshooting tips:")
    print("1. Check if you're behind a firewall/VPN")
    print("2. Verify credentials in ClickHouse Cloud console")
    print("3. Check if your IP is whitelisted in ClickHouse Cloud")
    print("4. Try increasing the timeout values")