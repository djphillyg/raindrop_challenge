"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { ExampleQueries } from "@/components/example-queries"
import { submitQuery, type QueryResponse } from "@/lib/api"

interface QueryInterfaceProps {
  onLogout: () => void
}

export function QueryInterface({ onLogout }: QueryInterfaceProps) {
  const [query, setQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<QueryResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await submitQuery(query)
      setResult(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">CFG SQL Query Tool</h1>
            <p className="text-gray-600 mt-1">
              Natural language queries for your fitness data
            </p>
          </div>
          <Button variant="outline" onClick={onLogout}>
            Logout
          </Button>
        </div>

        {/* Example Queries */}
        <ExampleQueries />

        {/* Query Input */}
        <Card>
          <CardHeader>
            <CardTitle>Enter Your Query</CardTitle>
            <CardDescription>
              Ask a question about your fitness data in plain English
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                type="text"
                placeholder="e.g., Calculate the average daily distance for the last 30 days"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={loading}
              />
              <Button type="submit" disabled={loading || !query.trim()} className="w-full">
                {loading ? "Processing..." : "Submit Query"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Error Display */}
        {error && (
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Results Display */}
        {result && (
          <Card>
            <CardHeader>
              <CardTitle>Results</CardTitle>
              <CardDescription>
                Query: {result.natural_query}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {result.error ? (
                  <Alert variant="destructive">
                    <AlertTitle>Query Error</AlertTitle>
                    <AlertDescription>{result.error}</AlertDescription>
                  </Alert>
                ) : (
                  <div className="bg-gray-100 rounded-md p-4 overflow-auto">
                    <pre className="text-sm">
                      {JSON.stringify(result.results, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}