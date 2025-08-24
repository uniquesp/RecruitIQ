"use client"

import { useState, useEffect } from "react"
import { apiService } from "@/lib/api"
import { authService } from "@/lib/auth"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Calendar, Clock, CheckCircle, XCircle, AlertCircle } from "lucide-react"
import Link from "next/link"
import { useToast } from "@/hooks/use-toast"

interface Application {
  id: string
  job: {
    id: string
    title: string
    company: string
  }
  status: string
  overall_score?: number
  created_at: string
}

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    loadApplications()
  }, [])

  const loadApplications = async () => {
    try {
      setIsLoading(true)
      const user = authService.getCurrentUser()
      if (!user) {
        toast({
          title: "Error",
          description: "Please log in to view your applications.",
          variant: "destructive",
        })
        return
      }

      const applicationsData = await apiService.getCandidateApplications(user.id)
      setApplications(applicationsData)
    } catch (error) {
      console.error("Failed to load applications:", error)
      toast({
        title: "Error",
        description: "Failed to load applications. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "hired":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "rejected":
        return <XCircle className="h-4 w-4 text-red-500" />
      case "interview":
        return <Clock className="h-4 w-4 text-blue-500" />
      case "screening":
        return <Clock className="h-4 w-4 text-yellow-500" />
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "hired":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
      case "rejected":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
      case "interview":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
      case "screening":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "submitted":
        return "Submitted"
      case "screening":
        return "Under Review"
      case "interview":
        return "Interview Stage"
      case "hired":
        return "Hired"
      case "rejected":
        return "Rejected"
      default:
        return status
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Loading applications...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center gap-4">
          <Link href="/">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">My Applications</h1>
            <p className="text-sm text-muted-foreground">Track your job applications and screening status</p>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid gap-6">
          {applications.map((application) => (
            <Card key={application.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <CardTitle className="text-xl">{application.job.title}</CardTitle>
                    <CardDescription className="flex items-center gap-4">
                      <span>{application.job.company}</span>
                      <span>•</span>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        <span>Applied {new Date(application.created_at).toLocaleDateString()}</span>
                      </div>
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(application.status)}
                    <Badge className={getStatusColor(application.status)}>{getStatusText(application.status)}</Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <h4 className="font-medium mb-2">Application Status</h4>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(application.status)}
                        <span className="text-sm">{getStatusText(application.status)}</span>
                      </div>
                    </div>

                    {application.overall_score && (
                      <div>
                        <h4 className="font-medium mb-2">Overall Score</h4>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{application.overall_score.toFixed(1)}/10</Badge>
                          {application.overall_score >= 7 ? (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          ) : application.overall_score >= 5 ? (
                            <AlertCircle className="h-4 w-4 text-yellow-500" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-500" />
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t">
                    <div className="text-sm text-muted-foreground">
                      Last updated: {new Date(application.created_at).toLocaleDateString()}
                    </div>
                    <div className="flex gap-2">
                      <Link href={`/candidate/jobs/${application.job.id}`}>
                        <Button variant="outline" size="sm">
                          View Job
                        </Button>
                      </Link>
                      {application.status === "submitted" && (
                        <Link href={`/candidate/interview/${application.job.id}`}>
                          <Button size="sm">Start Interview</Button>
                        </Link>
                      )}
                      {application.status === "screening" && (
                        <Button size="sm" disabled>
                          Under Review
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {applications.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <div className="text-muted-foreground mb-4">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg mb-2">No Applications Yet</p>
              <p>Start by browsing available jobs and applying to positions that interest you.</p>
            </div>
            <Link href="/candidate/jobs">
              <Button>Browse Jobs</Button>
            </Link>
          </div>
        )}
      </main>
    </div>
  )
}
