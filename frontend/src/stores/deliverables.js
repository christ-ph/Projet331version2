import { defineStore } from 'pinia'

//const API_BASE = 'http://127.0.0.1:5000/api'
const API_BASE = 'http://37.60.250.220:5500/api'
export const useDeliverablesStore = defineStore('deliverables', {
  state: () => ({
    deliverables: [],
    currentDeliverable: null,
    loading: false,
    error: null
  }),

  actions: {
    // ============================
    // ACTIONS FREELANCE
    // ============================

    async createDeliverable(formData) {
      this.loading = true
      this.error = null
      try {
        if (!(formData instanceof FormData)) {
          if (typeof formData === 'object' && formData !== null) {
            const newFormData = new FormData()
            for (const key in formData) {
              if (formData[key] instanceof File) {
                newFormData.append(key, formData[key])
              } else {
                newFormData.append(key, String(formData[key]))
              }
            }
            formData = newFormData
          } else {
            throw new Error('Données de formulaire invalides')
          }
        }

        const token = await this.getAuthToken()
        if (!token) throw new Error('Session expirée - Veuillez vous reconnecter')

        const response = await fetch(`${API_BASE}/deliverables`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        })

        if (!response.ok) {
          let errorMessage = `Erreur ${response.status}`
          try {
            const errorData = await response.json()
            errorMessage = errorData.error || errorMessage
          } catch {}
          throw new Error(errorMessage)
        }

        const data = await response.json()
        const newDeliverable = data.deliverable || data
        if (newDeliverable) this.deliverables.unshift(newDeliverable)
        return newDeliverable

      } catch (error) {
        const handledError = this.handleError(error, 'lors de la création du livrable')
        this.error = handledError.message
        throw handledError
      } finally {
        this.loading = false
      }
    },

    async updateDeliverable(id, formData) {
      this.loading = true
      this.error = null
      try {
        const token = await this.getAuthToken()
        if (!token) throw new Error('Session expirée - Veuillez vous reconnecter')

        const response = await fetch(`${API_BASE}/deliverables/${id}`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `Erreur ${response.status}`)
        }

        const data = await response.json()
        const updatedDeliverable = data.deliverable || data
        this.updateDeliverableInStore(updatedDeliverable)
        return updatedDeliverable

      } catch (error) {
        const handledError = this.handleError(error, 'lors de la modification du livrable')
        this.error = handledError.message
        throw handledError
      } finally {
        this.loading = false
      }
    },

    async deleteDeliverable(id) {
      this.loading = true
      this.error = null
      try {
        const token = await this.getAuthToken()
        if (!token) throw new Error('Session expirée - Veuillez vous reconnecter')

        const response = await fetch(`${API_BASE}/deliverables/${id}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `Erreur ${response.status}`)
        }

        this.deliverables = this.deliverables.filter(d => d.id !== id)
        if (this.currentDeliverable?.id === id) this.currentDeliverable = null
        return true

      } catch (error) {
        const handledError = this.handleError(error, 'lors de la suppression du livrable')
        this.error = handledError.message
        throw handledError
      } finally {
        this.loading = false
      }
    },

    async submitDeliverable(id) {
      this.loading = true
      this.error = null
      try {
        const token = await this.getAuthToken()
        if (!token) throw new Error('Session expirée - Veuillez vous reconnecter')

        const response = await fetch(`${API_BASE}/deliverables/${id}/submit`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `Erreur ${response.status}`)
        }

        const data = await response.json()
        const updatedDeliverable = data.deliverable || data
        this.updateDeliverableInStore(updatedDeliverable)
        return updatedDeliverable

      } catch (error) {
        const handledError = this.handleError(error, 'lors de la soumission du livrable')
        this.error = handledError.message
        throw handledError
      } finally {
        this.loading = false
      }
    },

    // ============================
    // ACTIONS CLIENT
    // ============================

    async startReview(deliverableId) {
      this.loading = true
      try {
        const token = await this.getAuthToken()
        if (!token) throw new Error('Session expirée - Veuillez vous reconnecter')

        const response = await fetch(`${API_BASE}/deliverables/${deliverableId}/review`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `Erreur ${response.status}`)
        }

        const data = await response.json()
        const updatedDeliverable = data.deliverable || data
        this.updateDeliverableInStore(updatedDeliverable)
        return updatedDeliverable

      } catch (error) {
        const handledError = this.handleError(error, 'lors du début de la review')
        this.error = handledError.message
        throw handledError
      } finally {
        this.loading = false
      }
    },

    async acceptDeliverable(deliverableId) {
      this.loading = true
      try {
        const token = await this.getAuthToken()
        if (!token) throw new Error('Session expirée - Veuillez vous reconnecter')

        const response = await fetch(`${API_BASE}/deliverables/${deliverableId}/accept`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `Erreur ${response.status}`)
        }

        const data = await response.json()
        const updatedDeliverable = data.deliverable || data
        this.updateDeliverableInStore(updatedDeliverable)
        return updatedDeliverable

      } catch (error) {
        const handledError = this.handleError(error, "lors de l'acceptation du livrable")
        this.error = handledError.message
        throw handledError
      } finally {
        this.loading = false
      }
    },

    async rejectDeliverable(deliverableId, feedback) {
      this.loading = true
      try {
        const token = await this.getAuthToken()
        if (!token) throw new Error('Session expirée - Veuillez vous reconnecter')
        if (!feedback || feedback.trim().length < 5) throw new Error('Un feedback détaillé est requis')

        const response = await fetch(`${API_BASE}/deliverables/${deliverableId}/reject`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ feedback: feedback.trim() })
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `Erreur ${response.status}`)
        }

        const data = await response.json()
        const updatedDeliverable = data.deliverable || data
        this.updateDeliverableInStore(updatedDeliverable)
        return updatedDeliverable

      } catch (error) {
        const handledError = this.handleError(error, 'lors du rejet du livrable')
        this.error = handledError.message
        throw handledError
      } finally {
        this.loading = false
      }
    },

    async requestRevision(deliverableId, feedback) {
      this.loading = true
      try {
        const token = await this.getAuthToken()
        if (!token) throw new Error('Session expirée - Veuillez vous reconnecter')
        if (!feedback || feedback.trim().length < 5) throw new Error('Un feedback détaillé est requis')

        const response = await fetch(`${API_BASE}/deliverables/${deliverableId}/request-revision`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ feedback: feedback.trim() })
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `Erreur ${response.status}`)
        }

        const data = await response.json()
        const updatedDeliverable = data.deliverable || data
        this.updateDeliverableInStore(updatedDeliverable)
        return updatedDeliverable

      } catch (error) {
        const handledError = this.handleError(error, 'lors de la demande de révision')
        this.error = handledError.message
        throw handledError
      } finally {
        this.loading = false
      }
    },

    // ============================
    // FETCH LIVRABLES
    // ============================

    async fetchMissionDeliverables(missionId, status = null) {
      this.loading = true
      this.error = null
      try {
        const token = await this.getAuthToken()
        if (!token) throw new Error('Session expirée - Veuillez vous reconnecter')

        let url = `${API_BASE}/deliverables/mission/${missionId}`
        if (status) url += `?status=${encodeURIComponent(status)}`

        const response = await fetch(url, { headers: { 'Authorization': `Bearer ${token}` } })
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `Erreur ${response.status}`)
        }

        const data = await response.json()
        // 🔹 Ne pas écraser les livrables d'autres missions
        this.deliverables = [
          ...this.deliverables.filter(d => d.mission_id !== missionId),
          ...data
        ]
        return data

      } catch (error) {
        const handledError = this.handleError(error, 'lors du chargement des livrables de la mission')
        this.error = handledError.message
        throw handledError
      } finally {
        this.loading = false
      }
    },

    async fetchDeliverable(id) {
      this.loading = true
      this.error = null
      try {
        const token = await this.getAuthToken()
        if (!token) throw new Error('Session expirée - Veuillez vous reconnecter')

        const response = await fetch(`${API_BASE}/deliverables/${id}`, { headers: { 'Authorization': `Bearer ${token}` } })
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `Erreur ${response.status}`)
        }

        const data = await response.json()
        this.currentDeliverable = data
        return data

      } catch (error) {
        const handledError = this.handleError(error, 'lors du chargement du livrable')
        this.error = handledError.message
        throw handledError
      } finally {
        this.loading = false
      }
    },

    async downloadFile(deliverableId) {
      try {
        const token = await this.getAuthToken()
        if (!token) throw new Error('Session expirée - Veuillez vous reconnecter')

        const response = await fetch(`${API_BASE}/deliverables/${deliverableId}/download`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (!response.ok) {
          try {
            const errorData = await response.json()
            throw new Error(errorData.error || `Erreur ${response.status}`)
          } catch {
            const errorText = await response.text()
            throw new Error(errorText || `Erreur ${response.status}`)
          }
        }

        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url

        let filename = `livrable_${deliverableId}`
        const contentDisposition = response.headers.get('content-disposition')
        if (contentDisposition) {
          const matches = contentDisposition.match(/filename="?([^"]+)"?/)
          if (matches && matches[1]) filename = decodeURIComponent(matches[1])
        }

        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        setTimeout(() => {
          link.remove()
          window.URL.revokeObjectURL(url)
        }, 100)

        return true

      } catch (error) {
        const handledError = this.handleError(error, 'lors du téléchargement')
        throw handledError
      }
    },

    // ============================
// FETCH MES LIVRABLES
// ============================

async fetchMyDeliverables() {
  this.loading = true
  this.error = null
  try {
    const token = await this.getAuthToken()
    if (!token) throw new Error('Session expirée - Veuillez vous reconnecter')

    const response = await fetch(`${API_BASE}/deliverables/my-deliverables`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `Erreur ${response.status}`)
    }

    const data = await response.json()
    this.deliverables = data
    return data

  } catch (error) {
    const handledError = this.handleError(error, 'lors du chargement de vos livrables')
    this.error = handledError.message
    throw handledError
  } finally {
    this.loading = false
  }
},

async fetchClientDeliverables() {
  this.loading = true
  this.error = null
  try {
    const token = await this.getAuthToken()
    if (!token) throw new Error('Session expirée - Veuillez vous reconnecter')

    const response = await fetch(`${API_BASE}/deliverables/client-deliverables`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `Erreur ${response.status}`)
    }

    const data = await response.json()
    this.deliverables = data
    return data

  } catch (error) {
    const handledError = this.handleError(error, 'lors du chargement des livrables client')
    this.error = handledError.message
    throw handledError
  } finally {
    this.loading = false
  }
},

    // ============================
    // UTILITAIRES
    // ============================

    async getAuthToken() {
      try {
        const { useAuthStore } = await import('@/stores/auth')
        const authStore = useAuthStore()
        let token = authStore.token || authStore.accessToken

        if (token?.startsWith('Bearer ')) token = token.replace('Bearer ', '')

        if (token?.trim()) return token.trim()

        const storageToken = localStorage.getItem('token') || sessionStorage.getItem('token')
        if (storageToken?.trim()) return storageToken.trim()

        return null
      } catch {
        const storageToken = localStorage.getItem('token') || sessionStorage.getItem('token')
        if (storageToken?.trim()) return storageToken.trim()
        return null
      }
    },

    updateDeliverableInStore(updatedDeliverable) {
      const index = this.deliverables.findIndex(d => d.id === updatedDeliverable.id)
      if (index !== -1) this.deliverables[index] = updatedDeliverable
      if (this.currentDeliverable?.id === updatedDeliverable.id) this.currentDeliverable = updatedDeliverable
    },

    handleError(error, context = '') {
      if (error.message.includes('Token') || error.message.includes('Session') || error.message.includes('expirée')) {
        localStorage.removeItem('token')
        sessionStorage.removeItem('token')
        if (!['/login','/connexion'].includes(window.location.pathname)) {
          setTimeout(() => window.location.href = '/login', 1500)
        }
        return new Error('Session expirée - Veuillez vous reconnecter')
      } else if (/network|failed to fetch/i.test(error.message)) {
        return new Error('Erreur réseau - Vérifiez votre connexion internet')
      } else if (/timeout/i.test(error.message) || error.name === 'TimeoutError') {
        return new Error('Délai d\'attente dépassé - Le serveur met trop de temps à répondre')
      }
      return error
    },

    clearError() { this.error = null },
    reset() {
      this.deliverables = []
      this.currentDeliverable = null
      this.error = null
      this.loading = false
    }
  },

  getters: {
    draftDeliverables: state => state.deliverables.filter(d => d.status === 'draft'),
    submittedDeliverables: state => state.deliverables.filter(d => d.status === 'submitted'),
    underReviewDeliverables: state => state.deliverables.filter(d => d.status === 'under_review'),
    acceptedDeliverables: state => state.deliverables.filter(d => d.status === 'accepted'),
    rejectedDeliverables: state => state.deliverables.filter(d => d.status === 'rejected'),
    needsRevisionDeliverables: state => state.deliverables.filter(d => d.status === 'needs_revision'),

    deliverablesByMissionId: state => missionId => state.deliverables.filter(d => d.mission_id === missionId),
    deliverableById: state => id => state.deliverables.find(d => d.id === id) || state.currentDeliverable,

    deliverablesStats: state => ({
      total: state.deliverables.length,
      draft: state.deliverables.filter(d => d.status === 'draft').length,
      submitted: state.deliverables.filter(d => d.status === 'submitted').length,
      under_review: state.deliverables.filter(d => d.status === 'under_review').length,
      accepted: state.deliverables.filter(d => d.status === 'accepted').length,
      rejected: state.deliverables.filter(d => d.status === 'rejected').length,
      needs_revision: state.deliverables.filter(d => d.status === 'needs_revision').length
    }),

    isDeliverableEditable: state => deliverableId => {
      const deliverable = state.deliverables.find(d => d.id === deliverableId) || state.currentDeliverable
      return deliverable ? ['draft','needs_revision'].includes(deliverable.status) : false
    }
  }
})
