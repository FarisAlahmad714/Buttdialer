import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'

interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  role: string
  is_active: boolean
  created_at: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  register: (userData: RegisterData) => Promise<void>
}

interface RegisterData {
  email: string
  password: string
  first_name: string
  last_name: string
  role?: string
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        try {
          const response = await api.post('/auth/login', { email, password })
          const { access_token, user } = response.data
          
          set({ 
            user, 
            token: access_token, 
            isAuthenticated: true 
          })
          
          // Set default authorization header
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        } catch (error) {
          throw error
        }
      },

      register: async (userData: RegisterData) => {
        try {
          const response = await api.post('/auth/register', userData)
          const { access_token, user } = response.data
          
          set({ 
            user, 
            token: access_token, 
            isAuthenticated: true 
          })
          
          // Set default authorization header
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        } catch (error) {
          throw error
        }
      },

      logout: () => {
        set({ user: null, token: null, isAuthenticated: false })
        delete api.defaults.headers.common['Authorization']
      },
    }),
    {
      name: 'auth-storage',
      onRehydrateStorage: () => (state) => {
        if (state?.token) {
          api.defaults.headers.common['Authorization'] = `Bearer ${state.token}`
        }
      },
    }
  )
)