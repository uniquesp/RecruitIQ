// Authentication service that uses the real API
import { apiService, ApiError } from "./api"
import type { User } from "./types"

interface AuthState {
  user: User | null
  isLoading: boolean
  error: string | null
}

class AuthService {
  private listeners: Array<(state: AuthState) => void> = []
  private state: AuthState = {
    user: null,
    isLoading: false,
    error: null,
  }

  constructor() {
    // Initialize auth state from localStorage
    this.initializeAuth()
  }

  private async initializeAuth() {
    const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null
    if (token) {
      // TODO: Validate token with backend or decode to get user info
      // For now, we'll need to implement a /auth/me endpoint
      try {
        // This would call /auth/me endpoint to get current user
        // const user = await apiService.getCurrentUser()
        // this.setState({ user, isLoading: false, error: null })
      } catch (error) {
        // Token is invalid, clear it
        localStorage.removeItem("auth_token")
        this.setState({ user: null, isLoading: false, error: null })
      }
    }
  }

  private setState(newState: Partial<AuthState>) {
    this.state = { ...this.state, ...newState }
    this.listeners.forEach((listener) => listener(this.state))
  }

  subscribe(listener: (state: AuthState) => void) {
    this.listeners.push(listener)
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener)
    }
  }

  getState() {
    return this.state
  }

  async login(email: string, password: string): Promise<User> {
    this.setState({ isLoading: true, error: null })

    try {
      const response = await apiService.login(email, password)
      const user: User = {
        id: response.user.id,
        email: response.user.email,
        name: response.user.name,
        role: response.user.role as "candidate" | "recruiter" | "admin",
        createdAt: new Date(),
        updatedAt: new Date(),
      }

      this.setState({ user, isLoading: false, error: null })
      return user
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : "Login failed"
      this.setState({ user: null, isLoading: false, error: errorMessage })
      throw new Error(errorMessage)
    }
  }

  async register(email: string, password: string, name: string, role: "candidate" | "recruiter"): Promise<User> {
    this.setState({ isLoading: true, error: null })

    try {
      const response = await apiService.register(email, password, name, role)
      const user: User = {
        id: response.user.id,
        email: response.user.email,
        name: response.user.name,
        role: response.user.role as "candidate" | "recruiter" | "admin",
        createdAt: new Date(),
        updatedAt: new Date(),
      }

      this.setState({ user, isLoading: false, error: null })
      return user
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : "Registration failed"
      this.setState({ user: null, isLoading: false, error: errorMessage })
      throw new Error(errorMessage)
    }
  }

  async logout(): Promise<void> {
    this.setState({ isLoading: true, error: null })

    try {
      await apiService.logout()
    } catch (error) {
      console.warn("Logout API call failed:", error)
    }

    this.setState({ user: null, isLoading: false, error: null })
  }

  getCurrentUser(): User | null {
    return this.state.user
  }
}

// Export singleton instance
export const authService = new AuthService()
