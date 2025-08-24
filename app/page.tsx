"use client"

import { useState, useEffect } from "react"
import { LoginForm } from "@/components/auth/login-form"
import { RegisterForm } from "@/components/auth/register-form"
import { authService } from "@/lib/auth"
import type { User } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"

export default function HomePage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [showRegister, setShowRegister] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = authService.subscribe((state) => {
      setCurrentUser(state.user)
      setIsLoading(state.isLoading)
    })

    // Initialize with current state
    const currentState = authService.getState()
    setCurrentUser(currentState.user)
    setIsLoading(false)

    return unsubscribe
  }, [])

  const handleLogin = (user: User) => {
    setCurrentUser(user)
  }

  const handleRegister = (user: User) => {
    setCurrentUser(user)
  }

  const handleLogout = async () => {
    await authService.logout()
    setCurrentUser(null)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">AI Candidate Screening</h1>
            <p className="text-muted-foreground">Intelligent pre-screening with AI-powered questions</p>
          </div>

          {showRegister ? (
            <RegisterForm onRegister={handleRegister} onSwitchToLogin={() => setShowRegister(false)} />
          ) : (
            <LoginForm onLogin={handleLogin} onSwitchToRegister={() => setShowRegister(true)} />
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">AI Candidate Screening</h1>
            <p className="text-sm text-muted-foreground">Welcome back, {currentUser.name}</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm bg-primary/10 text-primary px-2 py-1 rounded-full capitalize">
              {currentUser.role}
            </span>
            <Button variant="outline" onClick={handleLogout}>
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {currentUser.role === "candidate" && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>My Profile</CardTitle>
                  <CardDescription>Manage your personal information and CV</CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/candidate/profile">
                    <Button className="w-full">View Profile</Button>
                  </Link>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Available Jobs</CardTitle>
                  <CardDescription>Browse and apply to open positions</CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/candidate/jobs">
                    <Button className="w-full bg-transparent" variant="outline">
                      Browse Jobs
                    </Button>
                  </Link>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>My Applications</CardTitle>
                  <CardDescription>Track your applications and screening status</CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/candidate/applications">
                    <Button className="w-full bg-transparent" variant="outline">
                      View Applications
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </>
          )}

          {(currentUser.role === "recruiter" || currentUser.role === "admin") && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Recruiter Dashboard</CardTitle>
                  <CardDescription>Manage jobs and review applications</CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/recruiter/dashboard">
                    <Button className="w-full">Open Dashboard</Button>
                  </Link>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Create Job Posting</CardTitle>
                  <CardDescription>Post new positions and requirements</CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/recruiter/jobs/create">
                    <Button className="w-full bg-transparent" variant="outline">
                      Create Job
                    </Button>
                  </Link>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Application Reports</CardTitle>
                  <CardDescription>View detailed candidate screening reports</CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/recruiter/applications">
                    <Button className="w-full bg-transparent" variant="outline">
                      View Reports
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </>
          )}
        </div>

        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle>System Status</CardTitle>
              <CardDescription>Current application status and backend connectivity</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">FastAPI Backend</span>
                  <span className="text-sm text-yellow-600">⏳ Check localhost:8000</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Anthropic Claude API</span>
                  <span className="text-sm text-yellow-600">⏳ Requires API Key</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Authentication System</span>
                  <span className="text-sm text-green-600">✓ JWT Ready</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Frontend Integration</span>
                  <span className="text-sm text-green-600">✓ Complete</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Next: Database Setup</span>
                  <span className="text-sm text-yellow-600">⏳ Pending</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
