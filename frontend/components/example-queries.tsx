import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const EXAMPLE_QUERIES = [
  "Calculate the average daily distance for the last 30 days",
  "Sum the total calories burned in the last 7 days",
  "Count the days in the last 30 days where I burned more than 500 calories",
  "Show me all days where I ran more than 5 kilometers and burned over 400 calories",
  "List all days in the last week where I had zero active time",
  "Find the maximum distance in a single day over the last 6 months",
]

export function ExampleQueries() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Example Queries</CardTitle>
        <CardDescription>
          Try asking questions like these:
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2 text-sm text-gray-700">
          {EXAMPLE_QUERIES.map((query, index) => (
            <li key={index} className="flex items-start">
              <span className="text-gray-400 mr-2">•</span>
              <span>{query}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}