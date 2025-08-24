// API service for communicating with FastAPI backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface ApiResponse<T> {
  data?: T
  error?: string
}

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message)
    this.name = "ApiError"
  }
}

class ApiService {
  private baseUrl: string
  private token: string | null = null

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
    // Load token from localStorage if available
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("auth_token")
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    }

    // Add authorization header if token exists
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new ApiError(response.status, errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      if (error instanceof ApiError) {
        throw error
      }
      throw new ApiError(0, `Network error: ${error instanceof Error ? error.message : "Unknown error"}`)
    }
  }

  // Authentication methods
  async login(email: string, password: string) {
    const response = await this.request<{
      access_token: string
      token_type: string
      user: {
        id: string
        email: string
        name: string
        role: string
      }
    }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    })

    // Store token
    this.token = response.access_token
    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", response.access_token)
    }

    return response
  }

  async register(email: string, password: string, name: string, role: string) {
    const response = await this.request<{
      access_token: string
      token_type: string
      user: {
        id: string
        email: string
        name: string
        role: string
      }
    }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, name, role }),
    })

    // Store token
    this.token = response.access_token
    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", response.access_token)
    }

    return response
  }

  async logout() {
    try {
      await this.request("/auth/logout", {
        method: "POST",
      })
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn("Logout API call failed:", error)
    }

    // Clear token
    this.token = null
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token")
    }
  }

  // AI-powered endpoints
  async analyzeCV(cvText: string, jobId: string) {
    return this.request<{
      overall_match_score: number
      skills_analysis: {
        matched_skills: string[]
        missing_skills: string[]
        skill_match_percentage: number
      }
      experience_analysis: {
        relevant_experience_years: number
        experience_match_score: number
        key_experiences: string[]
      }
      education_analysis: {
        education_match_score: number
        relevant_qualifications: string[]
      }
      strengths: string[]
      concerns: string[]
      recommendation: string
      summary: string
    }>("/ai/analyze-cv", {
      method: "POST",
      body: JSON.stringify({ cv_text: cvText, job_id: jobId }),
    })
  }

  async generateInterviewQuestions(jobId: string, cvAnalysis: any) {
    return this.request<
      Array<{
        id: string
        question: string
        type: string
        difficulty: string
        focus_area: string
        expected_answer_points: string[]
        evaluation_criteria: string[]
      }>
    >("/ai/generate-questions", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, cv_analysis: cvAnalysis }),
    })
  }

  async evaluateResponse(questionId: string, response: string, context: any) {
    return this.request<{
      score: number
      strengths: string[]
      weaknesses: string[]
      follow_up_questions: string[]
      overall_assessment: string
      detailed_feedback: string
    }>("/ai/evaluate-response", {
      method: "POST",
      body: JSON.stringify({ question_id: questionId, response, context }),
    })
  }

  async generateReport(applicationId: string) {
    return this.request<{
      overall_recommendation: string
      overall_score: number
      summary: string
      strengths: string[]
      concerns: string[]
      skill_assessment: {
        technical_skills: number
        communication: number
        problem_solving: number
        cultural_fit: number
      }
      interview_performance: {
        average_score: number
        best_responses: string[]
        areas_for_improvement: string[]
      }
      next_steps: string[]
      salary_recommendation: string
      confidence_level: number
    }>("/ai/generate-report", {
      method: "POST",
      body: JSON.stringify({ application_id: applicationId }),
    })
  }

  // Job management endpoints
  async getJobs() {
    return this.request<
      Array<{
        id: string
        title: string
        description: string
        required_skills: string[]
        experience_required: string
        salary_range?: string
        location: string
        created_at: string
        created_by: string
      }>
    >("/jobs")
  }

  async getJob(jobId: string) {
    return this.request<{
      id: string
      title: string
      description: string
      required_skills: string[]
      experience_required: string
      salary_range?: string
      location: string
      created_at: string
      created_by: string
    }>(`/jobs/${jobId}`)
  }

  async submitApplication(jobId: string, cvText: string, coverLetter?: string) {
    return this.request<{
      id: string
      job_id: string
      candidate_id: string
      status: string
      created_at: string
    }>("/applications", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, cv_text: cvText, cover_letter: coverLetter }),
    })
  }

  // Health check
  async healthCheck() {
    return this.request<{
      status: string
      timestamp: string
      services: {
        ai: string
        database: string
      }
    }>("/health")
  }
}

// Export singleton instance
export const apiService = new ApiService()
export { ApiError }
