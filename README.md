# Raindrop Challenge: CFG SQL Query System

https://raindropfrontend-production.up.railway.app/

A natural language to SQL query application that uses GPT-5's Context Free Grammar (CFG) feature to generate structured SQL queries. 

Look at the backend/evals/README.md for specific instructions on evals

## Overview

This project demonstrates the power of Context Free Grammars in constraining LLM outputs to valid SQL syntax

## Data source
As a narcisstic person however.... how should I make this coding challenge... about me??? I requested download of my Garmin watch data and cleaned it into a dataset that tracks my active calories, distance and steps over the past 2 years, about 2500 rows! This project you can, yeah turn your english language queries into sql, but you can learn about ME haha. 

## Features

- **Natural Language to SQL**: Convert English queries to valid SQL using GPT-5's CFG feature
- **Context Free Grammar**: Ensures only valid SQL syntax for the fitness schema is generated
- **Personal Fitness Data**: Query Garmin active calorie data including:
  - Daily timestamps
  - Active calories burned
  - Active time (in seconds)
  - Distance traveled (in meters)
- **Evaluation Framework**: Built-in test suite with 3 types of assertions:
  - Grammar validation
  - Semantic correctness
  - Result validation
- **Modern Web Interface**: Clean Next.js frontend with example queries
- **Dockerized**: Easy deployment with Docker Compose

## Timing
- 1.5 hour - structure and initialization of clients in backend
- 3 hours - grammar + examples + issues w using OpenAI
- 1 hour - vibecoded frontend with password gate
- 1 hour - evals and verifying the sql output
- 0.5 hour - railway deploy

This project was allotted 6.5 hours, and I spent a majority of my time on the tiniest issues

The setup of the OpenAI grammar was the toughest part of this. I've only been building in Claude and so I had to learn some nuances of the API.

When I was blindly throwing my "lark-verified" parser at chatgpt5, it would just spin out and not say anything, it used 1.3M tokens in the matter of 15 minutes, all returning me no data and just spinning out. 

After figuring that out, the calls turned out not to be that expensive, and I wasn't blowing through so much money lol

I also went through the hassle figuring out a cohesive docker-compose to find that railway actually just lets you reach in and deploy

### If i had more time
- I would have made the output prettier
- i would have wanted to learn a bit more about eval procedures  and learn how to make one, like where you have it test against another LLM, but in the time frame i chose to intentionally vibecode
- i would have implemented JWT token on backend, because i didn't understand that railway needed it to be public as well to run the app. if any of you reading this wanna drain my tokens... good luck girl! ill fix this after if i choose to leave it up
- i would have spent more time validating against improper queries, i put in "hey girl hey" and the cfg just conformed it to a simple sql query of the first 10 rows haha
## Tech Stack

### Backend
- **Python 3.9+** with FastAPI
- **OpenAI GPT-5** for natural language processing with CFG
- **ClickHouse** database for analytics
- **FastAPI** for REST API
- **Uvicorn** ASGI server

### Frontend
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **shadcn/ui** component library

### Infrastructure
- **Docker** & Docker Compose for containerization
- **Railway** for backend deployment (optional)
- **Vercel** for frontend deployment (optional)

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Next.js   │─────▶│   FastAPI    │─────▶│  ClickHouse │
│   Frontend  │      │   Backend    │      │  Database   │
└─────────────┘      └──────┬───────┘      └─────────────┘
                            │
                            │
                     ┌──────▼──────┐
                     │  OpenAI     │
                     │  GPT-5 CFG  │
                     └─────────────┘
```

## Project Structure

```
raindrop_challenge/
├── backend/
│   ├── app.py                  # FastAPI application
│   ├── cfg/
│   │   └── grammar.py          # CFG definition for SQL
│   ├── services/
│   │   ├── openai_service.py   # OpenAI GPT-5 integration
│   │   └── clickhouse_service.py # ClickHouse client
│   ├── evals/
│   │   ├── test_cases_*.py     # Test case definitions
│   │   ├── assertions.py       # Assertion logic
│   │   └── run_evals.py        # Evaluation runner
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Main query interface
│   │   └── layout.tsx          # App layout
│   ├── components/
│   │   ├── query-interface.tsx # Query input/output
│   │   ├── example-queries.tsx # Example queries
│   │   └── password-gate.tsx   # Password protection
│   ├── lib/
│   │   └── api.ts              # API client
│   └── package.json
├── docker-compose.yml
├── IMPLEMENTATION_PLAN.md
└── README.md
```

## Setup

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **Docker** (optional, for containerized deployment)
- **OpenAI API Key** (with GPT-5 access)
- **ClickHouse** instance or credentials

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Backend Environment Variables
OPENAI_API_KEY=your_openai_api_key
CLICKHOUSE_HOST=your_clickhouse_host
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=your_password
CLICKHOUSE_DATABASE=default
```

Create a `.env.local` file in the `frontend/` directory:

```bash
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Local Development

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the development server:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Running with Docker

To run the entire stack with Docker Compose:

```bash
docker-compose up --build
```

This will start:
- Backend API on `http://localhost:8000`
- Frontend on `http://localhost:3000`

## Running Evaluations

The evaluation framework tests the CFG SQL generation with multiple assertion types:

### From the Backend Directory

```bash
cd backend
python -m evals.run_evals
```

### Via API Endpoint

```bash
curl http://localhost:8000/evals
```

### Evaluation Metrics

The evaluation framework tests:

1. **Grammar Assertions**: Validates SQL conforms to the CFG
2. **Semantic Assertions**: Checks SQL logic matches intent
3. **Result Assertions**: Verifies query returns expected data

Example test cases:
- Date range filtering with aggregations
- Multi-condition filtering with unit conversions
- Zero/boundary value handling
- Complex aggregations

## API Endpoints

### `POST /query`
Convert natural language to SQL and execute.

**Request:**
```json
{
  "query": "Calculate the average daily distance for the last 30 days"
}
```

**Response:**
```json
{
  "natural_query": "Calculate the average daily distance for the last 30 days",
  "generated_sql": "SELECT AVG(distance) FROM garmin_active_cal_data WHERE timestamp_day >= today() - toIntervalDay(30)",
  "results": {
    "rows": [[4523.45]],
    "row_count": 1
  }
}
```

### `GET /health`
Health check for all services.

### `GET /evals`
Run evaluation suite and return results.

## Example Queries

Try these natural language queries:

- "Calculate the average daily distance for the last 30 days"
- "Sum the total calories burned in the last 7 days"
- "Count the days in the last 30 days where I burned more than 500 calories"
- "Show me all days where I ran more than 5 kilometers and burned over 400 calories"
- "List all days in the last week where I had zero active time"
- "Find the maximum distance in a single day over the last 6 months"

## Context Free Grammar (CFG)

The CFG defines the valid SQL structure for our fitness schema. It ensures:

- **Safety**: Prevents SQL injection
- **Correctness**: Only valid SQL syntax is generated
- **Schema enforcement**: Only existing columns can be queried
- **Consistency**: Predictable output structure

### Key Grammar Features

The CFG handles:
- Time expressions: "last 30 days" → `today() - toIntervalDay(30)`
- Unit conversions: "5 kilometers" → `5000` (meters)
- Aggregations: "average" → `AVG()`, "sum" → `SUM()`
- Threshold comparisons: "more than 500" → `> 500`
- Complex conditions with `AND` operators

## Deployment

### Backend Deployment (Railway)

1. this project is deployed on railway, 

### Frontend Deployment (Vercel)



3. Add environment variables in Vercel dashboard

## Data Schema

**Table**: `garmin_active_cal_data`

| Column | Type | Description |
|--------|------|-------------|
| `timestamp_day` | Date | Daily timestamp |
| `active_calories` | Integer | Calories burned actively |
| `active_time` | Integer | Active time in seconds |
| `distance` | Integer | Distance in meters |
| `setpes` | Integer | Number of steps

## Development Notes

### Unit Conversions

The system automatically handles:
- **Distance**: kilometers → meters (multiply by 1000)
- **Time**: minutes → seconds (multiply by 60)
- **Date ranges**: "last X days" → ClickHouse interval syntax

### Adding New Test Cases

To add new evaluation test cases, edit the files in `backend/evals/`:
- `test_cases_grammar.py` - Grammar validation tests
- `test_cases_semantic.py` - Semantic correctness tests
- `test_cases_results.py` - Result validation tests