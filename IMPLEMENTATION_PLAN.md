# CFG + Eval Toy - Implementation Plan

## Project Overview
Build a natural language to SQL query system using GPT-5's Context Free Grammar feature to query personal fitness data from Tinybird.

**Timeline**: 6.5 hours over 3 days
**Stack**: Python (FastAPI) + Next.js + Tinybird + Railway

---

## Phase 0: Learning & Setup (1 hour)

### Learning CFG Basics
1. Read the [OpenAI GPT-5 CFG documentation](https://cookbook.openai.com/examples/gpt-5/gpt-5_new_params_and_tools#3-contextfree-grammar-cfg)
2. Understand key concepts:
   - **Context Free Grammar**: Rules that define valid output structure using **Lark syntax**
   - **Production rules**: Define how symbols can be expanded (lowercase for rules, UPPERCASE for terminals)
   - **Terminals**: Lexer tokens defined with regex patterns (e.g., `IDENTIFIER: /[A-Za-z_]+/`)
   - **Rules**: Combine terminals and other rules (e.g., `query: SELECT SP columns`)

### CFG for SQL Basics (Lark Syntax)
```lark
// Start rule
start: query

// Main query structure
query: SELECT SP select_clause SP FROM SP table where_clause? order_clause? limit_clause?

// Select clause
select_clause: STAR | column_list

// Column list
column_list: COLUMN (COMMA SP COLUMN)*

// Optional clauses
where_clause: SP WHERE SP condition
order_clause: SP ORDER_BY SP COLUMN order_dir?
limit_clause: SP LIMIT SP NUMBER

// Terminals (defined with regex)
SELECT: "SELECT"
FROM: "FROM"
WHERE: "WHERE"
ORDER_BY: "ORDER BY"
LIMIT: "LIMIT"
STAR: "*"
COMMA: ","
SP: " "
COLUMN: /[A-Za-z_][A-Za-z0-9_]*/
NUMBER: /[0-9]+/
```

**Key Notes**:
- Terminals (UPPERCASE) are matched by lexer using regex patterns
- Rules (lowercase) combine terminals and other rules
- Whitespace must be explicit (use `SP` for spaces)
- Optional elements use `?`, repetition uses `*` or `+`

### Setup Tasks
- [ ] Create Tinybird account
- [ ] Prepare fitness data CSV with columns: timestamp_day, active_calories, active_time, distance
- [ ] Upload fitness data CSV to Tinybird
- [ ] Get Tinybird API token
- [ ] Set up OpenAI API key (GPT-5 access)
- [ ] Initialize git repo

---

## Phase 1: Tinybird Setup (30 min)

### 1.1 Data Ingestion
1. Sign up at [tinybird.co](https://tinybird.co)
2. Create a new Data Source from CSV upload
3. Upload your fitness data CSV (must have columns: timestamp_day, active_calories, active_time, distance)
4. Note the table name (likely `garmin_active_cal_data`)

### 1.2 Schema Validation
Verify columns in Tinybird:
- `timestamp_day` (Date/Timestamp) - Daily timestamp
- `active_calories` (Integer) - Calories burned actively
- `active_time` (Integer) - Seconds of active time
- `distance` (Integer) - Distance in meters

### 1.3 Test Query
Run a test query in Tinybird console:
```sql
SELECT * FROM garmin_active_cal_data ORDER BY timestamp_day DESC LIMIT 5
```

---

## Phase 2: Define CFG for Fitness Schema (1 hour)

### 2.1 Create CFG Grammar File
**Goal**: Define a grammar that constrains GPT-5 to only generate valid SQL for our fitness schema.

**File**: `backend/cfg/grammar.py`

```python
# CFG for Fitness SQL queries using Lark syntax
FITNESS_SQL_CFG = """
// Start rule
start: query

// Main query structure
query: "SELECT " select_clause " FROM garmin_active_cal_data" where_clause? order_clause? limit_clause?

// Select clause
select_clause: "*"
             | column_list
             | agg_clause

// List of columns
column_list: column (", " column)*

// Valid column names from fitness schema
column: "timestamp_day"
      | "active_calories"
      | "active_time"
      | "distance"

// Aggregation clause
agg_clause: aggregation (", " (column | aggregation))*

// Single aggregation function
aggregation: agg_func "(" column ")"

// Aggregation functions
agg_func: "SUM" | "AVG" | "COUNT" | "MAX" | "MIN"

// WHERE clause for filtering
where_clause: " WHERE " condition (" AND " condition)*

// Single condition
condition: column " " operator " " value
         | column " " operator " CURRENT_DATE - INTERVAL " NUMBER " DAY"

// Comparison operators
operator: "=" | ">" | "<" | ">=" | "<=" | "!="

// Values (numbers only for fitness data)
value: NUMBER

// ORDER BY clause
order_clause: " ORDER BY " column (" " order_dir)?

// Sort direction
order_dir: "ASC" | "DESC"

// LIMIT clause
limit_clause: " LIMIT " NUMBER

// Terminals (lexer rules)
NUMBER: /[0-9]+/
"""
```

### 2.2 Simplified Approach
For initial implementation, this CFG covers:
- SELECT with specific columns or aggregations
- WHERE with basic comparisons and timestamp_day ranges
- ORDER BY
- LIMIT

Skip GROUP BY initially to reduce complexity.

---

## Phase 3: Backend Development (2 hours)

### 3.1 Project Structure
```
backend/
├── main.py              # FastAPI app
├── cfg/
│   └── grammar.py       # CFG definition
├── services/
│   ├── openai_service.py  # GPT-5 + CFG logic
│   └── tinybird_service.py # Tinybird API client
├── evals/
│   ├── test_cases.json    # Golden dataset
│   └── run_evals.py       # Eval runner
├── requirements.txt
└── .env
```

### 3.2 Dependencies (`requirements.txt`)
```
fastapi==0.104.1
uvicorn==0.24.0
openai==1.3.0
httpx==0.25.0
pydantic==2.5.0
python-dotenv==1.0.0
pytest==7.4.3
```

### 3.3 Core Files

#### `backend/.env`
```
OPENAI_API_KEY=sk-...
TINYBIRD_TOKEN=p.eyJ...
TINYBIRD_API_URL=https://api.tinybird.co/v0/sql
```

#### `backend/main.py`
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.openai_service import generate_sql_with_cfg
from services.tinybird_service import execute_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    sql: str
    results: dict
    error: str | None = None

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        # Generate SQL using GPT-5 + CFG
        sql = await generate_sql_with_cfg(request.query)

        # Execute on Tinybird
        results = await execute_query(sql)

        return QueryResponse(sql=sql, results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}
```

#### `backend/services/openai_service.py`
```python
import openai
import os
from cfg.grammar import FITNESS_SQL_CFG

openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_sql_with_cfg(natural_language_query: str) -> str:
    """
    Use GPT-5 with CFG to generate SQL from natural language.
    """

    system_prompt = """You are a SQL query generator for a personal fitness database.

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
- Time ranges: "last X days" → CURRENT_DATE - INTERVAL X DAY

Generate only the SQL query, no explanation."""

    response = await openai.ChatCompletion.acreate(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": natural_language_query}
        ],
        grammar=FITNESS_SQL_CFG,  # CFG constraint
        temperature=0.1
    )

    sql = response.choices[0].message.content.strip()
    return sql
```

#### `backend/services/tinybird_service.py`
```python
import httpx
import os

TINYBIRD_TOKEN = os.getenv("TINYBIRD_TOKEN")
TINYBIRD_URL = os.getenv("TINYBIRD_API_URL")

async def execute_query(sql: str) -> dict:
    """
    Execute SQL query on Tinybird and return results.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            TINYBIRD_URL,
            params={"q": sql},
            headers={"Authorization": f"Bearer {TINYBIRD_TOKEN}"}
        )
        response.raise_for_status()
        return response.json()
```

#### `backend/cfg/grammar.py`
(See the fitness grammar definition in Phase 2 and the ADAPTATION section at the end for the complete fitness-specific CFG)

---

## Phase 4: Evaluation Framework (1.5 hours)

**NOTE:** The test cases below are example structure. For the **actual fitness data test cases**, see the ADAPTATION section at the end of this document.

### 4.1 Golden Test Cases Structure
**File**: `backend/evals/test_cases.json`

Use the fitness test cases from the ADAPTATION section. The format will be:

```json
[
  {
    "id": 1,
    "natural_query": "Calculate the average daily distance for the last 30 days",
    "expected_sql": "SELECT AVG(distance) FROM garmin_active_cal_data WHERE timestamp_day >= CURRENT_DATE - INTERVAL 30 DAY",
    "description": "Date range handling with aggregation"
  },
  ...
]
```

### 4.2 Eval Runner
**File**: `backend/evals/run_evals.py`

```python
import json
import asyncio
from services.openai_service import generate_sql_with_cfg
from services.tinybird_service import execute_query
import sqlparse

class EvalMetrics:
    def __init__(self):
        self.total = 0
        self.syntactic_correct = 0
        self.semantic_correct = 0
        self.execution_success = 0
        self.results = []

async def run_eval(test_case: dict) -> dict:
    """Run a single eval test case."""
    result = {
        "id": test_case["id"],
        "natural_query": test_case["natural_query"],
        "expected_sql": test_case["expected_sql"],
        "generated_sql": None,
        "syntactic_match": False,
        "semantic_match": False,
        "execution_success": False,
        "error": None
    }

    try:
        # Generate SQL with CFG
        generated_sql = await generate_sql_with_cfg(test_case["natural_query"])
        result["generated_sql"] = generated_sql

        # Test 1: Syntactic Correctness (can it parse?)
        try:
            sqlparse.parse(generated_sql)
            result["syntactic_match"] = True
        except Exception as e:
            result["error"] = f"Parse error: {str(e)}"
            return result

        # Test 2: Semantic Similarity (normalize and compare)
        normalized_generated = normalize_sql(generated_sql)
        normalized_expected = normalize_sql(test_case["expected_sql"])
        result["semantic_match"] = normalized_generated == normalized_expected

        # Test 3: Execution Success (does it run on Tinybird?)
        try:
            await execute_query(generated_sql)
            result["execution_success"] = True
        except Exception as e:
            result["error"] = f"Execution error: {str(e)}"

    except Exception as e:
        result["error"] = f"Generation error: {str(e)}"

    return result

def normalize_sql(sql: str) -> str:
    """Normalize SQL for comparison."""
    parsed = sqlparse.parse(sql)[0]
    return sqlparse.format(
        str(parsed),
        reindent=False,
        keyword_case='upper',
        strip_whitespace=True
    )

async def run_all_evals():
    """Run all eval test cases."""
    with open("evals/test_cases.json", "r") as f:
        test_cases = json.load(f)

    metrics = EvalMetrics()
    metrics.total = len(test_cases)

    for test_case in test_cases:
        result = await run_eval(test_case)
        metrics.results.append(result)

        if result["syntactic_match"]:
            metrics.syntactic_correct += 1
        if result["semantic_match"]:
            metrics.semantic_correct += 1
        if result["execution_success"]:
            metrics.execution_success += 1

    # Print summary
    print("\n=== EVAL RESULTS ===")
    print(f"Total test cases: {metrics.total}")
    print(f"Syntactic correctness: {metrics.syntactic_correct}/{metrics.total} ({metrics.syntactic_correct/metrics.total*100:.1f}%)")
    print(f"Semantic correctness: {metrics.semantic_correct}/{metrics.total} ({metrics.semantic_correct/metrics.total*100:.1f}%)")
    print(f"Execution success: {metrics.execution_success}/{metrics.total} ({metrics.execution_success/metrics.total*100:.1f}%)")

    # Print detailed results
    print("\n=== DETAILED RESULTS ===")
    for result in metrics.results:
        print(f"\nTest {result['id']}: {result['natural_query']}")
        print(f"  Expected:  {result['expected_sql']}")
        print(f"  Generated: {result['generated_sql']}")
        print(f"  Syntactic: {'✓' if result['syntactic_match'] else '✗'}")
        print(f"  Semantic:  {'✓' if result['semantic_match'] else '✗'}")
        print(f"  Execution: {'✓' if result['execution_success'] else '✗'}")
        if result['error']:
            print(f"  Error: {result['error']}")

    return metrics

if __name__ == "__main__":
    asyncio.run(run_all_evals())
```

### 4.3 Add Eval Endpoint
Add to `backend/main.py`:

```python
@app.get("/evals")
async def run_evals():
    from evals.run_evals import run_all_evals
    metrics = await run_all_evals()
    return {
        "total": metrics.total,
        "syntactic_correct": metrics.syntactic_correct,
        "semantic_correct": metrics.semantic_correct,
        "execution_success": metrics.execution_success,
        "results": metrics.results
    }
```

---

## Phase 5: Frontend Development (1.5 hours)

### 5.1 Project Structure
```
frontend/
├── app/
│   ├── page.tsx           # Main query interface
│   ├── layout.tsx
│   └── api/
│       └── query/route.ts # API route to backend
├── components/
│   ├── QueryInput.tsx
│   ├── SQLDisplay.tsx
│   └── ResultsDisplay.tsx
├── package.json
└── .env.local
```

### 5.2 Setup Next.js
```bash
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
npm install axios
```

### 5.3 Core Components

#### `frontend/app/page.tsx`
```typescript
'use client';

import { useState } from 'react';
import axios from 'axios';

interface QueryResult {
  sql: string;
  results: any;
  error?: string;
}

export default function Home() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/query`,
        { query }
      );
      setResult(response.data);
    } catch (error: any) {
      setResult({
        sql: '',
        results: {},
        error: error.response?.data?.detail || error.message
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">CFG + SQL Query Tool</h1>
        <p className="text-gray-600 mb-8">
          Natural language queries for Twitch streamers data using GPT-5 Context Free Grammars
        </p>

        <form onSubmit={handleSubmit} className="mb-8">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Show me top 5 streamers with most followers"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Processing...' : 'Query'}
            </button>
          </div>
        </form>

        {result && (
          <div className="space-y-4">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-2">Generated SQL</h2>
              <pre className="bg-gray-100 p-4 rounded overflow-x-auto">
                <code>{result.sql}</code>
              </pre>
            </div>

            {result.error ? (
              <div className="bg-red-50 border border-red-200 p-6 rounded-lg">
                <h2 className="text-xl font-semibold text-red-800 mb-2">Error</h2>
                <p className="text-red-600">{result.error}</p>
              </div>
            ) : (
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-2">Results</h2>
                <pre className="bg-gray-100 p-4 rounded overflow-x-auto max-h-96">
                  <code>{JSON.stringify(result.results, null, 2)}</code>
                </pre>
              </div>
            )}
          </div>
        )}

        <div className="mt-8 bg-blue-50 border border-blue-200 p-6 rounded-lg">
          <h3 className="font-semibold mb-2">Example Queries:</h3>
          <ul className="space-y-1 text-sm text-gray-700">
            <li>• Show me the top 5 Twitch streamers with the most followers</li>
            <li>• Find 5 streamers with the most views gained but least followers</li>
            <li>• What is the average watch time for all streamers?</li>
            <li>• Show streamers with more than 1000000 followers</li>
          </ul>
        </div>
      </div>
    </main>
  );
}
```

#### `frontend/.env.local`
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Phase 6: Deployment (1 hour)

### 6.1 Backend Deployment (Railway)

1. **Prepare for deployment**:
   - Create `backend/Procfile`:
     ```
     web: uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

2. **Deploy to Railway**:
   - Go to [railway.app](https://railway.app)
   - Create new project
   - Deploy from GitHub repo (or local)
   - Add environment variables:
     - `OPENAI_API_KEY`
     - `TINYBIRD_TOKEN`
     - `TINYBIRD_API_URL`
   - Railway will auto-detect Python and install dependencies

3. **Get deployment URL**: `https://your-app.railway.app`

### 6.2 Frontend Deployment (Vercel)

1. **Uptimestamp_day environment variable**:
   - Set `NEXT_PUBLIC_API_URL` to Railway backend URL

2. **Deploy to Vercel**:
   ```bash
   cd frontend
   vercel deploy --prod
   ```

3. **Add environment variable in Vercel dashboard**:
   - `NEXT_PUBLIC_API_URL=https://your-app.railway.app`

---

## Phase 7: Testing & Documentation (30 min)

### 7.1 Manual Testing
- [ ] Test basic query: "Show top 5 streamers by followers"
- [ ] Test aggregation: "What's the average watch time?"
- [ ] Test complex query: "Find streamers with most views but least followers"
- [ ] Run evals: Visit `/evals` endpoint or run `python backend/evals/run_evals.py`

### 7.2 Create README
**File**: `README.md`

```markdown
# CFG + Eval Toy: Natural Language SQL for Twitch Data

Query Twitch streamer data using natural language, powered by GPT-5's Context Free Grammar feature.

## Features
- Natural language to SQL conversion using CFG constraints
- Query 1000+ Twitch streamers
- Built-in evaluation framework
- Simple web interface

## Tech Stack
- **Backend**: Python (FastAPI) + GPT-5 + Tinybird
- **Frontend**: Next.js + TypeScript + Tailwind
- **Deployment**: Railway + Vercel

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Run Evals
```bash
cd backend
python evals/run_evals.py
```

## Live Demo
- App: [Your Vercel URL]
- Evals: [Your Railway URL]/evals

## Example Queries
- "Show me the top 5 Twitch streamers with the most followers"
- "Find 5 streamers with the most views gained but least followers"
- "What is the average watch time for all streamers?"
- "Show streamers with more than 1000000 followers"
```

---

## Summary Checklist

### Setup Phase
- [ ] Read OpenAI CFG documentation
- [ ] Create Tinybird account and upload CSV
- [ ] Get API keys (OpenAI, Tinybird)
- [ ] Initialize git repo

### Backend Phase
- [ ] Create FastAPI project structure
- [ ] Define CFG grammar for Twitch schema
- [ ] Implement OpenAI service with CFG
- [ ] Implement Tinybird query service
- [ ] Create main API endpoint

### Eval Phase
- [ ] Create 8 golden test cases
- [ ] Implement eval runner with 3 metrics
- [ ] Add eval endpoint to API
- [ ] Test eval framework

### Frontend Phase
- [ ] Create Next.js app
- [ ] Build query interface
- [ ] Display SQL and results
- [ ] Add example queries

### Deployment Phase
- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Vercel
- [ ] Configure environment variables
- [ ] Test live deployment

### Documentation Phase
- [ ] Create README
- [ ] Document API endpoints
- [ ] Add example queries
- [ ] Test all features

---

## Time Breakdown
- Phase 0 (Learning): 1 hour
- Phase 1 (Tinybird): 30 min
- Phase 2 (CFG): 1 hour
- Phase 3 (Backend): 2 hours
- Phase 4 (Evals): 1.5 hours
- Phase 5 (Frontend): 1.5 hours
- Phase 6 (Deployment): 1 hour
- Phase 7 (Testing/Docs): 30 min

**Total: 8 hours** (includes buffer for debugging)

---

## Key Learnings: CFG Basics

### What is a Context Free Grammar?
A CFG defines rules for valid output structure using:
- **Production rules**: How to expand symbols
- **Terminals**: Actual tokens in output
- **Non-terminals**: Symbols that expand

### Example
```bnf
<query> ::= "SELECT" <columns> "FROM" <table>
<columns> ::= "*" | "Column1" | "Column2"
<table> ::= "twitchdata_uptimestamp_day"
```

Valid outputs:
- `SELECT * FROM twitchdata_uptimestamp_day`
- `SELECT Column1 FROM twitchdata_uptimestamp_day`

Invalid outputs:
- `SELECT Column3 FROM other_table` (not in grammar)

### Why CFG for SQL?
- **Safety**: Prevent SQL injection
- **Correctness**: Only valid SQL syntax
- **Schema enforcement**: Only query existing columns
- **Consistency**: Predictable output structure

---

## ADAPTATION: Fitness Data Implementation

### Uptimestamp_dayd Schema for Fitness Data

**Table**: `garmin_active_cal_data`

**Columns**:
- `timestamp_day` (Date/Timestamp) - Daily timestamp
- `active_calories` (Integer) - Calories burned actively
- `active_time` (Integer) - Seconds of active time
- `distance` (Integer) - Distance in meters

### Natural Language Queries (8 Total)

#### Basic Aggregations (Pattern Discovery)

**Query 1:** "Calculate the average daily distance for the last 30 days"
- **SQL Pattern**: `SELECT AVG(distance) FROM garmin_active_cal_data WHERE timestamp_day >= CURRENT_DATE - INTERVAL 30 DAY`
- **Tests**: Date range filtering, aggregation

**Query 2:** "Sum the total calories burned in the last 7 days"
- **SQL Pattern**: `SELECT SUM(active_calories) FROM garmin_active_cal_data WHERE timestamp_day >= CURRENT_DATE - INTERVAL 7 DAY`
- **Tests**: Simple aggregation with short time range

**Query 3:** "Get the total active time in seconds for the last 90 days"
- **SQL Pattern**: `SELECT SUM(active_time) FROM garmin_active_cal_data WHERE timestamp_day >= CURRENT_DATE - INTERVAL 90 DAY`
- **Tests**: Long-term aggregation

#### Filtering + Aggregation (Performance & Consistency)

**Query 4:** "Count the days in the last 30 days where I burned more than 500 calories"
- **SQL Pattern**: `SELECT COUNT(*) FROM garmin_active_cal_data WHERE active_calories > 500 AND timestamp_day >= CURRENT_DATE - INTERVAL 30 DAY`
- **Tests**: Threshold filtering with counting

**Query 5:** "Show me all days where I ran more than 5 kilometers and burned over 400 calories"
- **SQL Pattern**: `SELECT timestamp_day, distance, active_calories FROM garmin_active_cal_data WHERE distance > 5000 AND active_calories > 400`
- **Tests**: Multi-condition filtering, unit conversion (5km → 5000m)

**Query 6:** "Calculate the average distance for days when I was active for more than 30 minutes"
- **SQL Pattern**: `SELECT AVG(distance) FROM garmin_active_cal_data WHERE active_time > 1800`
- **Tests**: Filtering then aggregating (subset averaging), time conversion (30 min → 1800 sec)

#### Edge Cases (For Evals)

**Query 7:** "List all days in the last week where I had zero active time"
- **SQL Pattern**: `SELECT timestamp_day FROM garmin_active_cal_data WHERE active_time = 0 AND timestamp_day >= CURRENT_DATE - INTERVAL 7 DAY`
- **Tests**: Zero value handling, potentially empty result set

**Query 8:** "Find the maximum distance in a single day over the last 6 months"
- **SQL Pattern**: `SELECT MAX(distance) FROM garmin_active_cal_data WHERE timestamp_day >= CURRENT_DATE - INTERVAL 180 DAY`
- **Tests**: Extreme value extraction, medium-term range

### 3 Required Eval Test Cases

#### Eval 1: Date Range Handling (Query 1)
```json
{
  "id": 1,
  "natural_query": "Calculate the average daily distance for the last 30 days",
  "expected_sql": "SELECT AVG(distance) FROM garmin_active_cal_data WHERE timestamp_day >= CURRENT_DATE - INTERVAL 30 DAY",
  "description": "Date range handling with aggregation",
  "edge_cases": [
    "Empty dataset (no rows in timestamp_day range)",
    "Null values in distance column",
    "Leap year timestamp_day math"
  ]
}
```

#### Eval 2: Multi-Condition Filtering (Query 5)
```json
{
  "id": 2,
  "natural_query": "Show me all days where I ran more than 5 kilometers and burned over 400 calories",
  "expected_sql": "SELECT timestamp_day, distance, active_calories FROM garmin_active_cal_data WHERE distance > 5000 AND active_calories > 400",
  "description": "Multi-condition filtering with unit conversion",
  "edge_cases": [
    "Unit conversion correctness (5km → 5000m)",
    "Logical AND (not OR)",
    "Empty result set"
  ]
}
```

#### Eval 3: Zero/Boundary Values (Query 7)
```json
{
  "id": 3,
  "natural_query": "List all days in the last week where I had zero active time",
  "expected_sql": "SELECT timestamp_day FROM garmin_active_cal_data WHERE active_time = 0 AND timestamp_day >= CURRENT_DATE - INTERVAL 7 DAY",
  "description": "Zero value and boundary handling",
  "edge_cases": [
    "Handling zero vs null",
    "Empty result set (no zero days)",
    "Correct equality comparison (= 0, not < 1)"
  ]
}
```

### Uptimestamp_dayd CFG Grammar for Fitness Schema

**File**: `backend/cfg/fitness_grammar.py`

```python
# CFG for Fitness SQL queries using Lark syntax
FITNESS_SQL_CFG = """
// Start rule
start: query

// Main query structure
query: "SELECT " select_clause " FROM garmin_active_cal_data" where_clause? order_clause? limit_clause?

// Select clause
select_clause: "*"
             | column_list
             | agg_clause

// List of columns
column_list: column (", " column)*

// Valid column names from fitness schema
column: "timestamp_day"
      | "active_calories"
      | "active_time"
      | "distance"

// Aggregation clause
agg_clause: aggregation (", " (column | aggregation))*

// Single aggregation function
aggregation: agg_func "(" column ")"

// Aggregation functions
agg_func: "SUM" | "AVG" | "COUNT" | "MAX" | "MIN"

// WHERE clause for filtering
where_clause: " WHERE " condition (" AND " condition)*

// Single condition
condition: column " " operator " " value
         | column " " operator " CURRENT_DATE - INTERVAL " NUMBER " DAY"

// Comparison operators
operator: "=" | ">" | "<" | ">=" | "<=" | "!="

// Values (numbers only for fitness data)
value: NUMBER

// ORDER BY clause
order_clause: " ORDER BY " column (" " order_dir)?

// Sort direction
order_dir: "ASC" | "DESC"

// LIMIT clause
limit_clause: " LIMIT " NUMBER

// Terminals (lexer rules)
NUMBER: /[0-9]+/
"""
```

### Uptimestamp_dayd Eval Test Cases File

**File**: `backend/evals/fitness_test_cases.json`

```json
[
  {
    "id": 1,
    "natural_query": "Calculate the average daily distance for the last 30 days",
    "expected_sql": "SELECT AVG(distance) FROM garmin_active_cal_data WHERE timestamp_day >= CURRENT_DATE - INTERVAL 30 DAY",
    "description": "Date range handling with aggregation"
  },
  {
    "id": 2,
    "natural_query": "Sum the total calories burned in the last 7 days",
    "expected_sql": "SELECT SUM(active_calories) FROM garmin_active_cal_data WHERE timestamp_day >= CURRENT_DATE - INTERVAL 7 DAY",
    "description": "Simple aggregation with short time range"
  },
  {
    "id": 3,
    "natural_query": "Get the total active time in seconds for the last 90 days",
    "expected_sql": "SELECT SUM(active_time) FROM garmin_active_cal_data WHERE timestamp_day >= CURRENT_DATE - INTERVAL 90 DAY",
    "description": "Long-term aggregation"
  },
  {
    "id": 4,
    "natural_query": "Count the days in the last 30 days where I burned more than 500 calories",
    "expected_sql": "SELECT COUNT(*) FROM garmin_active_cal_data WHERE active_calories > 500 AND timestamp_day >= CURRENT_DATE - INTERVAL 30 DAY",
    "description": "Threshold filtering with counting"
  },
  {
    "id": 5,
    "natural_query": "Show me all days where I ran more than 5 kilometers and burned over 400 calories",
    "expected_sql": "SELECT timestamp_day, distance, active_calories FROM garmin_active_cal_data WHERE distance > 5000 AND active_calories > 400",
    "description": "Multi-condition filtering with unit conversion (EVAL 2)"
  },
  {
    "id": 6,
    "natural_query": "Calculate the average distance for days when I was active for more than 30 minutes",
    "expected_sql": "SELECT AVG(distance) FROM garmin_active_cal_data WHERE active_time > 1800",
    "description": "Filtering then aggregating with time conversion"
  },
  {
    "id": 7,
    "natural_query": "List all days in the last week where I had zero active time",
    "expected_sql": "SELECT timestamp_day FROM garmin_active_cal_data WHERE active_time = 0 AND timestamp_day >= CURRENT_DATE - INTERVAL 7 DAY",
    "description": "Zero value and boundary handling (EVAL 3)"
  },
  {
    "id": 8,
    "natural_query": "Find the maximum distance in a single day over the last 6 months",
    "expected_sql": "SELECT MAX(distance) FROM garmin_active_cal_data WHERE timestamp_day >= CURRENT_DATE - INTERVAL 180 DAY",
    "description": "Extreme value extraction"
  }
]
```

### CFG Implementation Notes for Fitness Data

Your GPT-5 CFG implementation must handle:

1. **Time Expressions**:
   - "last 30 days" → `CURRENT_DATE - INTERVAL 30 DAY`
   - "last 7 days" → `CURRENT_DATE - INTERVAL 7 DAY`
   - "last 6 months" → `CURRENT_DATE - INTERVAL 180 DAY`

2. **Unit Conversions**:
   - "5 kilometers" → `5000` (meters in schema)
   - "30 minutes" → `1800` (seconds in schema)

3. **Natural Language Mapping**:
   - "average" → `AVG()`
   - "sum/total" → `SUM()`
   - "count" → `COUNT()`
   - "maximum/max" → `MAX()`

4. **Threshold Recognition**:
   - "more than 500" → `> 500`
   - "over 400" → `> 400`
   - "zero" → `= 0`

5. **Condition Combination**:
   - "and" → `AND` in WHERE clause

distance - is in meters
active_time - is in seconds



### Uptimestamp_dayd Backend Service

**File**: `backend/services/openai_service.py` (adapted for fitness)

```python
import openai
import os
from cfg.fitness_grammar import FITNESS_SQL_CFG

openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_sql_with_cfg(natural_language_query: str) -> str:
    """
    Use GPT-5 with CFG to generate SQL from natural language.
    """

    system_prompt = """You are a SQL query generator for a personal fitness database.

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
- Time ranges: "last X days" → CURRENT_DATE - INTERVAL X DAY

Generate only the SQL query, no explanation."""

    response = await openai.ChatCompletion.acreate(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": natural_language_query}
        ],
        grammar=FITNESS_SQL_CFG,  # CFG constraint
        temperature=0.1
    )

    sql = response.choices[0].message.content.strip()
    return sql
```

### Tinybird Setup for Fitness Data

1. **Prepare Fitness CSV**:
   - Export your fitness data with columns: `timestamp_day,active_calories,active_time,distance`
   - Ensure at least 1000+ rows for meaningful queries

2. **Upload to Tinybird**:
   - Create Data Source → Upload CSV
   - Name it `garmin_active_cal_data`
   - Verify column types match schema

3. **Test Query**:
   ```sql
   SELECT * FROM garmin_active_cal_data ORDER BY timestamp_day DESC LIMIT 5
   ```

### Example Fitness Queries for Frontend

Uptimestamp_day `frontend/app/page.tsx` with these examples:

```typescript
<div className="mt-8 bg-blue-50 border border-blue-200 p-6 rounded-lg">
  <h3 className="font-semibold mb-2">Example Queries:</h3>
  <ul className="space-y-1 text-sm text-gray-700">
    <li>• Calculate the average daily distance for the last 30 days</li>
    <li>• Sum the total calories burned in the last 7 days</li>
    <li>• Count the days in the last 30 days where I burned more than 500 calories</li>
    <li>• Show me all days where I ran more than 5 kilometers and burned over 400 calories</li>
    <li>• List all days in the last week where I had zero active time</li>
  </ul>
</div>
```
