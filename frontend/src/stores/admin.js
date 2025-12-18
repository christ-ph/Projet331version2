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
const storedAdminToken = localStorage.getItem('admin_token')
const storedAdmin = safeParse('admin', null)

export const useAdminStore = defineStore('admin', {
  state: () => ({
    // Auth admin
    adminToken: storedAdminToken || null,
    admin: storedAdmin,
    isAdminAuthenticated: !!storedAdminToken,
    
    // Données
    complaints: [],
    blockedAccounts: [],
    adminActions: [],
    
    // Loading
    isLoading: false,
    
    // Pagination
    pagination: {
      complaints: { page: 1, perPage: 20, total: 0, pages: 0 },
      blockedAccounts: { page: 1, perPage: 20, total: 0, pages: 0 },
      actions: { page: 1, perPage: 50, total: 0, pages: 0 }
    }
  }),

  // ======================
  // GETTERS
  // ======================
  getters: {
    // Filtres plaintes
    pendingComplaints: (state) => 
      state.complaints.filter(c => c.status === 'pending'),
    
    approvedComplaints: (state) => 
      state.complaints.filter(c => c.status === 'approved'),
    
    rejectedComplaints: (state) => 
      state.complaints.filter(c => c.status === 'rejected'),
    
    // Stats
    totalComplaints: (state) => state.pagination.complaints.total,
    totalBlockedAccounts: (state) => state.pagination.blockedAccounts.total,
    totalAdminActions: (state) => state.pagination.actions.total,
    
    // Admin info
    adminEmail: (state) => state.admin?.email || null,
    adminId: (state) => state.admin?.id || null
  },

  // ======================
  // ACTIONS
  // ======================
  actions: {
    /**
     * Initialisation Axios pour admin
     */
    initializeAdmin() {
      if (this.adminToken) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.adminToken}`
      }
    },

    // ======================
    // ADMIN AUTH
    // ======================
    
    /**
     * ADMIN LOGIN
     * POST /admin/login
     */
    async adminLogin(email, password) {
      this.isLoading = true
      try {
        const res = await axios.post('/admin/login', { email, password })
        
        this.adminToken = res.data.access_token
        this.admin = res.data.admin
        this.isAdminAuthenticated = true

        localStorage.setItem('admin_token', this.adminToken)
        localStorage.setItem('admin', JSON.stringify(this.admin))
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.adminToken}`

        return { success: true, admin: this.admin }
      } catch (error) {
        this.adminLogout(false)
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur de connexion admin'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * ADMIN REGISTER
     * POST /admin/register
     */
    async registerAdmin(email, password) {
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
          message: error.response?.data?.msg || 'Erreur création admin'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * ADMIN LOGOUT
     */
    adminLogout(redirect = true) {
      this.adminToken = null
      this.admin = null
      this.isAdminAuthenticated = false
      this.complaints = []
      this.blockedAccounts = []
      this.adminActions = []

      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin')
      delete axios.defaults.headers.common['Authorization']

      if (redirect) {
        window.location.href = '/admin/login'
      }
    },

    /**
     * Vérification auth admin
     */
    checkAdminAuth() {
      if (this.adminToken && this.admin) return true

      const token = localStorage.getItem('admin_token')
      const admin = safeParse('admin')

      if (token && admin) {
        this.adminToken = token
        this.admin = admin
        this.isAdminAuthenticated = true
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        return true
      }

      return false
    },

    // ======================
    // COMPLAINTS (PLAINTES) - ADMIN
    // ======================
    
    /**
     * Récupérer toutes les plaintes (avec filtres)
     * GET /admin/complaints
     */
    async fetchComplaints(status = null, page = 1, perPage = 20) {
      this.isLoading = true
      try {
        const params = { page, per_page: perPage }
        if (status) params.status = status

        const res = await axios.get('/admin/complaints', { params })
        
        this.complaints = res.data.complaints
        this.pagination.complaints = {
          page: res.data.page,
          perPage: res.data.per_page,
          total: res.data.total,
          pages: res.data.pages
        }

        return { success: true }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur chargement plaintes'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * Approuver une plainte (bloque l'utilisateur)
     * POST /admin/complaints/:id/approve
     */
    async approveComplaint(complaintId) {
      this.isLoading = true
      try {
        const res = await axios.post(`/admin/complaints/${complaintId}/approve`)
        
        // Mettre à jour la plainte dans le state
        const index = this.complaints.findIndex(c => c.id === complaintId)
        if (index !== -1) {
          this.complaints[index] = res.data.complaint
        }

        return { 
          success: true, 
          message: res.data.msg,
          complaint: res.data.complaint,
          blockedUser: res.data.blocked_user
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur approbation plainte'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * Rejeter une plainte
     * POST /admin/complaints/:id/reject
     */
    async rejectComplaint(complaintId, notes = '') {
      this.isLoading = true
      try {
        const res = await axios.post(`/admin/complaints/${complaintId}/reject`, { notes })
        
        // Mettre à jour la plainte dans le state
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
          message: error.response?.data?.msg || 'Erreur rejet plainte'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * Supprimer une plainte
     * DELETE /admin/complaints/:id
     */
    async deleteComplaint(complaintId) {
      this.isLoading = true
      try {
        await axios.delete(`/admin/complaints/${complaintId}`)
        
        // Retirer la plainte du state
        this.complaints = this.complaints.filter(c => c.id !== complaintId)
        this.pagination.complaints.total -= 1

        return { success: true, message: 'Plainte supprimée avec succès' }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur suppression plainte'
        }
      } finally {
        this.isLoading = false
      }
    },

    // ======================
    // BLOCKED ACCOUNTS - ADMIN
    // ======================
    
    /**
     * Récupérer tous les comptes bloqués
     * GET /admin/blocked-accounts
     */
    async fetchBlockedAccounts(page = 1, perPage = 20) {
      this.isLoading = true
      try {
        const res = await axios.get('/admin/blocked-accounts', {
          params: { page, per_page: perPage }
        })
        
        this.blockedAccounts = res.data.blocked_accounts
        this.pagination.blockedAccounts = {
          page: res.data.page,
          perPage: res.data.per_page,
          total: res.data.total,
          pages: res.data.pages
        }

        return { success: true }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur chargement comptes bloqués'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * Débloquer un utilisateur
     * POST /admin/unblock/:id
     */
    async unblockUser(userId, notes = '') {
      this.isLoading = true
      try {
        const res = await axios.post(`/admin/unblock/${userId}`, { notes })
        
        // Retirer du state
        this.blockedAccounts = this.blockedAccounts.filter(u => u.id !== userId)
        this.pagination.blockedAccounts.total -= 1

        return { 
          success: true, 
          message: res.data.msg,
          user: res.data.user
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur déblocage utilisateur'
        }
      } finally {
        this.isLoading = false
      }
    },

    // ======================
    // ADMIN ACTIONS (HISTORIQUE) - ADMIN
    // ======================
    
    /**
     * Récupérer toutes les actions admin
     * GET /admin/actions
     */
    async fetchAdminActions(filters = {}, page = 1, perPage = 50) {
      this.isLoading = true
      try {
        const params = { page, per_page: perPage }
        
        // Ajouter les filtres optionnels
        if (filters.admin_id) params.admin_id = filters.admin_id
        if (filters.action_type) params.action_type = filters.action_type

        const res = await axios.get('/admin/actions', { params })
        
        this.adminActions = res.data.actions
        this.pagination.actions = {
          page: res.data.page,
          perPage: res.data.per_page,
          total: res.data.total,
          pages: res.data.pages
        }

        return { success: true }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur chargement historique'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * Récupérer mes actions admin
     * GET /admin/actions/me
     */
    async fetchMyAdminActions(page = 1, perPage = 50) {
      this.isLoading = true
      try {
        const res = await axios.get('/admin/actions/me', {
          params: { page, per_page: perPage }
        })
        
        this.adminActions = res.data.actions
        this.pagination.actions = {
          page: res.data.page,
          perPage: res.data.per_page,
          total: res.data.total,
          pages: res.data.pages
        }

        return { success: true }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur chargement mes actions'
        }
      } finally {
        this.isLoading = false
      }
    },

    // ======================
    // CLIENT/FREELANCE COMPLAINTS
    // ======================
    
    /**
     * Créer une plainte (CLIENT ou FREELANCE uniquement)
     * POST /admin/complaint
     */
    async createComplaint(reportedEmail, reason) {
      this.isLoading = true
      try {
        const res = await axios.post('/admin/complaint', {
          reported_email: reportedEmail,
          reason
        })

        return { 
          success: true, 
          message: res.data.msg, 
          complaint: res.data.complaint 
        }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.msg || 'Erreur création plainte'
        }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * Récupérer mes plaintes (CLIENT ou FREELANCE uniquement)
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
          message: error.response?.data?.msg || 'Erreur chargement mes plaintes'
        }
      } finally {
        this.isLoading = false
      }
    },

    // ======================
    // UTILS
    // ======================
    
    /**
     * Reset des données
     */
    resetAdminData() {
      this.complaints = []
      this.blockedAccounts = []
      this.adminActions = []
      this.pagination = {
        complaints: { page: 1, perPage: 20, total: 0, pages: 0 },
        blockedAccounts: { page: 1, perPage: 20, total: 0, pages: 0 },
        actions: { page: 1, perPage: 50, total: 0, pages: 0 }
      }
    }
  }
})
