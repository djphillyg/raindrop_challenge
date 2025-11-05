/**
 * API client for FastAPI backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface QueryRequest {
  query: string
}

export interface QueryResponse {
  natural_query: string
  generated_sql: string
  results: {
    rows: any[]
    row_count: number
  } | null
  error: string | null
}

export async function submitQuery(query: string): Promise<QueryResponse> {
  const response = await fetch(`${API_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query } satisfies QueryRequest),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`)
  }

  return response.json()
}

export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${API_URL}/health`)
  return response.json()
}