import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import { login as apiLogin, register as apiRegister } from '../api/client'

interface AuthState {
  token: string | null
  email: string | null
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => ({
    token: localStorage.getItem('tf_token'),
    email: localStorage.getItem('tf_email'),
  }))

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await apiLogin(email, password)
    localStorage.setItem('tf_token', access_token)
    localStorage.setItem('tf_email', email)
    setState({ token: access_token, email })
  }, [])

  const register = useCallback(async (email: string, password: string) => {
    await apiRegister(email, password)
    await login(email, password)
  }, [login])

  const logout = useCallback(() => {
    localStorage.removeItem('tf_token')
    localStorage.removeItem('tf_email')
    setState({ token: null, email: null })
  }, [])

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
