"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface PasswordGateProps {
  onAuthenticated: () => void
}

export function PasswordGate({ onAuthenticated }: PasswordGateProps) {
  const [password, setPassword] = useState("")
  const [error, setError] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const correctPassword = process.env.NEXT_PUBLIC_PASSWORD || "default-password"

    if (password === correctPassword) {
      setError(false)
      onAuthenticated()
    } else {
      setError(true)
      setPassword("")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Access Protected</CardTitle>
          <CardDescription>
            Enter the password to access the CFG SQL Query Tool
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Input
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoFocus
              />
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>
                  Incorrect password. Please try again.
                </AlertDescription>
              </Alert>
            )}

            <Button type="submit" className="w-full">
              Unlock
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}