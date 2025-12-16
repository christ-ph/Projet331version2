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
  this.isLoading = true;
  
  try {
    const response = await axios.post('/auth/login', { email, password });
    const { access_token, user } = response.data;

    // ✅ Mettre à jour le state
    this.token = access_token;
    this.user = user;

    // ✅ Sauvegarder dans localStorage
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('user', JSON.stringify(user));

    // ✅ L'intercepteur Axios ajoutera automatiquement le header
    // Mais on peut le faire manuellement aussi (optionnel)
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

    return true;

  } catch (error) {
    // ✅ Cas spécial : Email non vérifié (403)
    if (error.response?.status === 403) {
      throw { 
        type: 'unverified', 
        message: error.response.data?.msg || 'Veuillez vérifier votre email.' 
      };
    }

    // ✅ Toutes les autres erreurs (401, 500, etc.)
    console.error('Erreur lors du login:', error);
    throw error;

  } finally {
    this.isLoading = false;
  }
},

  /**
 * REGISTER
 * POST /auth/register
 */
async register(email, password) {
  this.isLoading = true;
  
  try {
    const response = await axios.post('/auth/register', { email, password });
    return response.data;
    
  } catch (error) {
    console.error('Erreur lors de l\'inscription:', error);
    throw error;  // ✅ Throw l'erreur
    
  } finally {
    this.isLoading = false;
  }
},

/**
 * VERIFY EMAIL
 * POST /auth/verify-email
 */
async verifyEmail(email, code) {
  this.isLoading = true;
  
  try {
    const response = await axios.post('/auth/verify-email', { email, code });
    return response.data;
    
  } catch (error) {
    console.error('Erreur lors de la vérification:', error);
    throw error;  // ✅ Throw l'erreur
    
  } finally {
    this.isLoading = false;
  }
},

/**
 * RESEND CODE
 * POST /auth/resend-code
 */
async resendCode(email) {
  this.isLoading = true;
  
  try {
    const response = await axios.post('/auth/resend-code', { email });
    return response.data;
    
  } catch (error) {
    console.error('Erreur lors du renvoi du code:', error);
    throw error;  // ✅ Throw l'erreur
    
  } finally {
    this.isLoading = false;
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
    