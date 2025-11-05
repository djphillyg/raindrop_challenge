"""
FastAPI application with dependency injection for services
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Annotated, Union

from services.openai_service import OpenAIClient
from services.clickhouse_service import ClickhouseClient
from cfg.grammar import sql_grammar_tool
import json

# ============================================
# Models
# ============================================

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    natural_query: str
    generated_sql: str
    results: Union[dict, None] = None
    error: Union[str, None] = None

# ============================================
# Dependency Injection - Services initialized ONCE
# ============================================

class AppState:
    """Singleton to hold service instances"""
    _openai_client: Union[OpenAIClient, None] = None
    _clickhouse_client: Union[ClickhouseClient, None] = None

    @classmethod
    def get_openai_client(cls) -> OpenAIClient:
        if cls._openai_client is None:
            print("Initializing OpenAI client...")
            cls._openai_client = OpenAIClient()
        return cls._openai_client

    @classmethod
    def get_clickhouse_client(cls) -> ClickhouseClient:
        if cls._clickhouse_client is None:
            print("Initializing ClickHouse client...")
            cls._clickhouse_client = ClickhouseClient()
        return cls._clickhouse_client

# Dependency functions
def get_openai() -> OpenAIClient:
    """Dependency: Get OpenAI client instance"""
    return AppState.get_openai_client()

def get_clickhouse() -> ClickhouseClient:
    """Dependency: Get ClickHouse client instance"""
    return AppState.get_clickhouse_client()

# Type aliases for cleaner code
OpenAIDep = Annotated[OpenAIClient, Depends(get_openai)]
ClickHouseDep = Annotated[ClickhouseClient, Depends(get_clickhouse)]

# ============================================
# Lifespan Event Handler
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown"""
    # Startup
    print("=" * 60)
    print("Starting CFG SQL Query API...")
    print("=" * 60)

    try:
        print("\n1. Initializing OpenAI client...")
        AppState.get_openai_client()
        print("   ✓ OpenAI client ready")

        print("\n2. Initializing ClickHouse client...")
        AppState.get_clickhouse_client()
        print("   ✓ ClickHouse client ready")

        print("\n" + "=" * 60)
        print("All services initialized successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Startup failed: {e}")
        raise

    yield

    # Shutdown
    print("Shutting down API...")

# ============================================
# FastAPI App
# ============================================

app = FastAPI(title="CFG SQL Query API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Helper Functions
# ============================================


def build_english_to_sql_prompt(english_query: str) -> str:
    """Build a prompt to convert English query to SQL using grammar tool."""
    return f"""
    You are a SQL query generator for a personal fitness database.

    Schema:
    - Table: garmin_active_cal_data
    - Columns:
    - timestamp_day (Date/Timestamp): Daily timestamp
    - active_calories (Integer): Calories burned actively
    - active_time (Integer): Seconds of active time
    - distance (Integer): Distance in meters

    Important conversions:
    - "kilometers" or "km" → multiply by 1000 for meters
    - "minutes" → multiply by 60 for seconds
    - Time ranges: "last X days" → today() - toIntervalDay(X)
    
    <english_query> {english_query} </english_query>
    '
    Guidelines:
    - Use the sql_grammar tool to generate a query for the sql database on the english_query
    - Return back well formed sql output
    """

# ============================================
# Routes
# ============================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "CFG SQL Query API is running"
    }

@app.get("/health")
async def health(
    openai: OpenAIDep,
    clickhouse: ClickHouseDep
):
    """Health check for all services"""
    try:
        # Test ClickHouse
        ch_result = clickhouse.call("SELECT 1 as test")

        return {
            "status": "healthy",
            "services": {
                "openai": "connected",
                "clickhouse": "connected",
                "clickhouse_test": ch_result.result_rows
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    openai: OpenAIDep,
    clickhouse: ClickHouseDep
):
    """
    Convert natural language query to SQL using CFG, then execute on ClickHouse.

    Example request:
    {
        "query": "Calculate the average daily distance for the last 30 days"
    }
    """
    try:
        # Step 1: Generate SQL using OpenAI + CFG
        print(f"Processing query: {request.query}")

        prompt = build_english_to_sql_prompt(request.query)

        sql_query = openai.call_with_tool(
            input=prompt,
            tool=sql_grammar_tool
        )

        print(f"Generated SQL: {sql_query}")

        # Step 2: Execute on ClickHouse
        result = clickhouse.call(sql_query)

        return QueryResponse(
            natural_query=request.query,
            generated_sql=sql_query,
            results={
                "rows": result.result_rows,
                "row_count": len(result.result_rows)
            }
        )

    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )