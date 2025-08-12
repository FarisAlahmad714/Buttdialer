import axios from 'axios'
import toast from 'react-hot-toast'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const message = error.response.data?.detail || 'An error occurred'
      toast.error(message)
      
      // Handle 401 errors (unauthorized)
      if (error.response.status === 401) {
        // Clear auth data and redirect to login
        localStorage.clear()
        window.location.href = '/login'
      }
    } else {
      toast.error('Network error occurred')
    }
    
    return Promise.reject(error)
  }
)

export default api