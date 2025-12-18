import { defineStore } from 'pinia'
import axios from 'axios'

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
const storedAdminToken = localStorage.getItem('admin_access_token')
const storedAdmin = safeParse('admin_user', null)

export const useAdminStore = defineStore('admin', {
  state: () => ({
    token: storedAdminToken || null,
    admin: storedAdmin,
    isAuthenticated: !!storedAdminToken,
    isLoading: false,
    complaints: [],
    blockedAccounts: [],
    adminActions: [],
    stats: {
      totalComplaints: 0,
      pendingComplaints: 0,
      blockedUsers: 0
    }
  }),

  getters: {
    isAdmin: (state) => state.admin?.role === 'ADMIN',
    adminEmail: (state) => state.admin?.email || '',
    displayName: (state) => {
      if (state.admin?.email) return state.admin.email.split('@')[0]
      return 'Administrateur'
    }
  },

  actions: {
    /**
     * Initialisation Axios pour admin
     */
    initialize() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      }

      // Interceptor pour les erreurs 401
      axios.interceptors.response.use(
        res => res,
        err => {
          if (err.response?.status === 401) {
            console.warn('Token admin invalide → logout')
            this.logout()
          }
          return Promise.reject(err)
        }
      )
    },

    /**
     * CONNEXION ADMIN
     * POST /admin/login
     */
    async login(email, password) {
      this.isLoading = true
      try {
        const res = await axios.post('/admin/login', { email, password })
        
        this.token = res.data.access_token
        this.admin = res.data.admin
        this.isAuthenticated = true

        localStorage.setItem('admin_access_token', this.token)
        localStorage.setItem('admin_user', JSON.stringify(this.admin))

        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`

        return { 
          success: true, 
          admin: res.data.admin 
        }
      } catch (error) {
        console.error('Login admin error:', error)
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur de connexion admin'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * INSCRIPTION ADMIN
     * POST /admin/register
     */
    async register(email, password) {
      this.isLoading = true
      try {
        const res = await axios.post('/admin/register', { email, password })
        return {
          success: true,
          message: res.data.msg,
          admin: res.data.admin
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur d\'inscription admin'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * RÉCUPÉRER TOUTES LES PLAINTES
     * GET /admin/complaints
     */
    async fetchComplaints(status = null, page = 1, perPage = 20) {
      this.isLoading = true
      try {
        const params = { page, per_page: perPage }
        if (status) params.status = status

        const res = await axios.get('/admin/complaints', { params })
        this.complaints = res.data.complaints
        this.stats.totalComplaints = res.data.total
        
        // Calculer les plaintes en attente
        this.stats.pendingComplaints = this.complaints.filter(
          c => c.status === 'pending'
        ).length
        
        return {
          success: true,
          complaints: res.data.complaints,
          pagination: {
            total: res.data.total,
            page: res.data.page,
            pages: res.data.pages
          }
        }
      } catch (error) {
        console.error('Fetch complaints error:', error)
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur de récupération des plaintes'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * APPROUVER UNE PLAINTE
     * POST /admin/complaints/{id}/approve
     */
    async approveComplaint(complaintId) {
      this.isLoading = true
      try {
        const res = await axios.post(`/admin/complaints/${complaintId}/approve`)
        
        // Mettre à jour la plainte locale
        const index = this.complaints.findIndex(c => c.id === complaintId)
        if (index !== -1) {
          this.complaints[index] = res.data.complaint
        }
        
        return {
          success: true,
          message: res.data.msg,
          complaint: res.data.complaint
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur d\'approbation de la plainte'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * REJETER UNE PLAINTE
     * POST /admin/complaints/{id}/reject
     */
    async rejectComplaint(complaintId, notes = null) {
      this.isLoading = true
      try {
        const data = notes ? { notes } : {}
        const res = await axios.post(`/admin/complaints/${complaintId}/reject`, data)
        
        // Mettre à jour la plainte locale
        const index = this.complaints.findIndex(c => c.id === complaintId)
        if (index !== -1) {
          this.complaints[index] = res.data.complaint
        }
        
        return {
          success: true,
          message: res.data.msg,
          complaint: res.data.complaint
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur de rejet de la plainte'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * SUPPRIMER UNE PLAINTE
     * DELETE /admin/complaints/{id}
     */
    async deleteComplaint(complaintId) {
      this.isLoading = true
      try {
        await axios.delete(`/admin/complaints/${complaintId}`)
        
        // Retirer la plainte du tableau local
        this.complaints = this.complaints.filter(c => c.id !== complaintId)
        
        return {
          success: true,
          message: 'Plainte supprimée avec succès'
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur de suppression de la plainte'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * RÉCUPÉRER LES COMPTES BLOQUÉS
     * GET /admin/blocked-accounts
     */
    async fetchBlockedAccounts(page = 1, perPage = 20) {
      this.isLoading = true
      try {
        const res = await axios.get('/admin/blocked-accounts', {
          params: { page, per_page: perPage }
        })
        
        this.blockedAccounts = res.data.blocked_accounts
        this.stats.blockedUsers = res.data.total
        
        return {
          success: true,
          accounts: res.data.blocked_accounts,
          pagination: {
            total: res.data.total,
            page: res.data.page,
            pages: res.data.pages
          }
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur de récupération des comptes bloqués'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * DÉBLOQUER UN COMPTE
     * POST /admin/unblock/{userId}
     */
    async unblockUser(userId, notes = null) {
      this.isLoading = true
      try {
        const data = notes ? { notes } : {}
        const res = await axios.post(`/admin/unblock/${userId}`, data)
        
        // Retirer le compte du tableau des bloqués
        this.blockedAccounts = this.blockedAccounts.filter(a => a.id !== userId)
        
        return {
          success: true,
          message: res.data.msg
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur de déblocage du compte'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * RÉCUPÉRER L'HISTORIQUE DES ACTIONS ADMIN
     * GET /admin/actions
     */
    async fetchAdminActions(adminId = null, actionType = null, page = 1, perPage = 50) {
      this.isLoading = true
      try {
        const params = { page, per_page: perPage }
        if (adminId) params.admin_id = adminId
        if (actionType) params.action_type = actionType

        const res = await axios.get('/admin/actions', { params })
        this.adminActions = res.data.actions
        
        return {
          success: true,
          actions: res.data.actions,
          pagination: {
            total: res.data.total,
            page: res.data.page,
            pages: res.data.pages
          }
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur de récupération des actions admin'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * RÉCUPÉRER MES ACTIONS ADMIN
     * GET /admin/actions/me
     */
    async fetchMyAdminActions(page = 1, perPage = 50) {
      return this.fetchAdminActions(this.admin?.id, null, page, perPage)
    },

    /**
     * CRÉER UNE PLAINTE (pour les utilisateurs)
     * POST /admin/complaint
     */
    async createComplaint(reportedEmail, reason) {
      this.isLoading = true
      try {
        const res = await axios.post('/admin/complaint', {
          reported_email: reportedEmail,
          reason: reason
        })
        
        return {
          success: true,
          message: res.data.msg,
          complaint: res.data.complaint
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur de création de la plainte'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * RÉCUPÉRER MES PLAINTES (pour les utilisateurs)
     * GET /admin/my-complaints
     */
    async fetchMyComplaints() {
      this.isLoading = true
      try {
        const res = await axios.get('/admin/my-complaints')
        
        return {
          success: true,
          complaints: res.data.complaints,
          total: res.data.total
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur de récupération de vos plaintes'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * DÉCONNEXION ADMIN
     */
    logout() {
      this.token = null
      this.admin = null
      this.isAuthenticated = false
      this.complaints = []
      this.blockedAccounts = []
      this.adminActions = []

      localStorage.removeItem('admin_access_token')
      localStorage.removeItem('admin_user')
      delete axios.defaults.headers.common['Authorization']

      // Redirection vers login admin
      window.location.href = '/admin/login'
    },

    /**
     * Vérifier l'authentification admin
     */
    checkAuth() {
      if (this.token && this.admin) return true

      const token = localStorage.getItem('admin_access_token')
      const admin = safeParse('admin_user')

      if (token && admin) {
        this.token = token
        this.admin = admin
        this.isAuthenticated = true
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        return true
      }

      return false
    },

    /**
     * Rafraîchir les statistiques
     */
    async refreshStats() {
      await this.fetchComplaints('pending')
      await this.fetchBlockedAccounts()
      
      // Statistiques calculées automatiquement dans les fetch
      return this.stats
    }
  }
})