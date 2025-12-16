import { defineStore } from 'pinia'
import axios from 'axios'

/**
 * Parse sécurisé du localStorage
 */
const safeParse = (key, defaultValue = null) => {
  try {
    const item = localStorage.getItem(key)
    if (!item || item === 'null' || item === 'undefined') {
      return defaultValue
    }
    return JSON.parse(item)
  } catch (error) {
    console.error(`Erreur parsing ${key}:`, error)
    localStorage.removeItem(key)
    return defaultValue
  }
}

// Données persistées
const storedToken = localStorage.getItem('access_token')
const storedUser = safeParse('user', null)

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: storedToken || null,
    user: storedUser,
    isAuthenticated: !!storedToken,
    isLoading: false,
    userLoaded: false
  }),

  // ======================
  // GETTERS
  // ======================
  getters: {
    role: (state) => state.user?.role || null,

    isUser: (state) => state.user?.role === 'USER',
    isAdmin: (state) => state.user?.role === 'ADMIN',

    displayName: (state) => {
      if (state.user?.email) return state.user.email.split('@')[0]
      return 'Utilisateur'
    }
  },

  // ======================
  // ACTIONS
  // ======================
  actions: {
    /**
     * Initialisation Axios + interceptor 401
     */
    initialize() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      }

      axios.interceptors.response.use(
        res => res,
        err => {
          if (err.response?.status === 401) {
            console.warn('Token invalide → logout')
            this.logout(false)
          }
          return Promise.reject(err)
        }
      )
    },

    /**
     * LOGIN
     * POST /auth/login
     */
    async login(email, password) {
      this.isLoading = true
      try {
        const res = await axios.post('/auth/login', { email, password })

        this.token = res.data.access_token
        this.user = res.data.user
        this.isAuthenticated = true
        this.userLoaded = true

        localStorage.setItem('access_token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))

        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`

        return { success: true }
      } catch (error) {
        if (error.response?.status === 403) {
          return {
            success: false,
            type: 'unverified',
            message: 'Veuillez vérifier votre email.'
          }
        }

        this.logout(false)
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur de connexion'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * REGISTER
     * POST /auth/register
     */
    async register(payload) {
      this.isLoading = true
      try {
        const res = await axios.post('/auth/register', payload)
        return {
          success: true,
          message: res.data.msg
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur inscription'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * VERIFY EMAIL
     * POST /auth/verify-email
     */
    async verifyEmail(email, code) {
      this.isLoading = true
      try {
        const res = await axios.post('/auth/verify-email', { email, code })
        return {
          success: true,
          message: res.data.msg
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Code invalide'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * RESEND CODE
     * POST /auth/resend-code
     */
    async resendCode(email) {
      this.isLoading = true
      try {
        const res = await axios.post('/auth/resend-code', { email })
        return {
          success: true,
          message: res.data.msg
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur envoi code'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * ROUTE PROTÉGÉE (équivalent profil simple)
     * GET /auth/protected
     */
    async fetchUser() {
      if (!this.token) return false

      this.isLoading = true
      try {
        const res = await axios.get('/auth/protected')

        this.user = {
          email: res.data.email,
          role: res.data.role_id
        }

        localStorage.setItem('user', JSON.stringify(this.user))
        this.isAuthenticated = true
        this.userLoaded = true
        return true
      } catch (error) {
        this.logout(false)
        return false
      } finally {
        this.isLoading = false
      }
    },

    /**
     * LOGOUT
     */
    logout(redirect = true) {
      this.token = null
      this.user = null
      this.isAuthenticated = false
      this.userLoaded = false

      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      delete axios.defaults.headers.common['Authorization']

      if (redirect) {
        window.location.href = '/login'
      }
    },

    /**
     * Vérification auth (router guards)
     */
    checkAuth() {
      if (this.token && this.user) return true

      const token = localStorage.getItem('access_token')
      const user = safeParse('user')

      if (token && user) {
        this.token = token
        this.user = user
        this.isAuthenticated = true
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        return true
      }

      return false
    }
  }
})
    