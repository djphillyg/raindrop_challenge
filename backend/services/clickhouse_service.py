import json
import re
import time
import os
from typing import Optional, Union
import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()

class ClickhouseClient:
    def __init__(self):
        print("Connecting to ClickHouse Cloud...")
        try:
            self.client = clickhouse_connect.get_client(
                host=os.environ['CLICKHOUSE_HOST'],
                port=int(os.environ['CLICKHOUSE_PORT']),
                username=os.environ['CLICKHOUSE_USER'],
                password=os.environ['CLICKHOUSE_PASSWORD'],
                secure=True,  # Required for ClickHouse Cloud
                verify=True,  # Verify SSL certificate
                connect_timeout=30,  # Increase timeout from default 10s
                send_receive_timeout=60  # Increase query timeout
            )
            print("✓ Connected to ClickHouse successfully!")
        except Exception as e:
            print(f"✗ Failed to connect to ClickHouse: {e}")
            raise
    
    def call(self, sql_query: str):
        result = self.client.query(sql_query)
        return result