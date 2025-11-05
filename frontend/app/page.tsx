"use client"

import { useState } from "react"
import { PasswordGate } from "@/components/password-gate"
import { QueryInterface } from "@/components/query-interface"

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  if (!isAuthenticated) {
    return <PasswordGate onAuthenticated={() => setIsAuthenticated(true)} />
  }

  return <QueryInterface onLogout={() => setIsAuthenticated(false)} />
}