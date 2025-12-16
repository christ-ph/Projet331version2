import { defineStore } from 'pinia'
import axios from 'axios'

export const usePostulationStore = defineStore('postulations', {
  state: () => ({
    postulations: [], // Toutes les postulations récupérées
    myApplications: [], // Mes candidatures (pour freelances)
    missionApplications: [], // Candidatures pour une mission spécifique (pour clients)
    currentPostulation: null, // Postulation actuellement sélectionnée
    
    loading: false,
    error: null
  }),

  getters: {
    // Filtrage par statut
    pendingPostulations: (state) => state.postulations.filter(p => p.status === 'pending'),
    acceptedPostulations: (state) => state.postulations.filter(p => p.status === 'accepted'),
    rejectedPostulations: (state) => state.postulations.filter(p => p.status === 'rejected'),
    cancelledPostulations: (state) => state.postulations.filter(p => p.status === 'cancelled'),

    // Mes candidatures par statut
    myPendingApplications: (state) => state.myApplications.filter(a => a.status === 'pending'),
    myAcceptedApplications: (state) => state.myApplications.filter(a => a.status === 'accepted'),
    myRejectedApplications: (state) => state.myApplications.filter(a => a.status === 'rejected'),

    // Candidatures par mission (pour client)
    pendingApplications: (state) => state.missionApplications.filter(a => a.status === 'pending'),
    acceptedApplications: (state) => state.missionApplications.filter(a => a.status === 'accepted'),

    // Trouver une postulation par ID
    getPostulationById: (state) => (id) => {
      return state.postulations.find(p => p.id === id) ||
             state.myApplications.find(a => a.id === id) ||
             state.missionApplications.find(a => a.id === id)
    },

    // Statistiques
    totalApplications: (state) => state.postulations.length,
    totalPending: (state) => state.postulations.filter(p => p.status === 'pending').length,
    totalAccepted: (state) => state.postulations.filter(p => p.status === 'accepted').length,

    // Compter le nombre de candidatures pour une mission spécifique
    getApplicationCountForMission: (state) => (missionId) => {
      return state.myApplications.filter(app => {
        // Vérifier de différentes façons pour être sûr
        if (app.mission_id === missionId) return true
        if (app.mission && app.mission.id === missionId) return true
        return false
      }).length
    },

    // Vérifier si l'utilisateur a déjà postulé à une mission
    hasAppliedToMission: (state) => (missionId) => {
      if (!state.myApplications || state.myApplications.length === 0) {
        return false
      }
      
      return state.myApplications.some(app => {
        // Vérifier de différentes façons
        if (app.mission_id === missionId) return true
        if (app.mission && app.mission.id === missionId) return true
        return false
      })
    },

    // Obtenir la postulation pour une mission spécifique
    getApplicationForMission: (state) => (missionId) => {
      return state.myApplications.find(app => {
        if (app.mission_id === missionId) return true
        if (app.mission && app.mission.id === missionId) return true
        return false
      })
    }
  },

  actions: {
    // ======================
    // FREELANCE - Candidatures
    // ======================

    // Postuler à une mission (CORRIGÉ : pas de message dans le backend)
    async apply(missionId) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.post(`/api/missions/${missionId}/apply`)
        
        // Créer un objet postulation pour l'ajouter à la liste
        const newApplication = {
          id: res.data.postulation_id,
          postulation_id: res.data.postulation_id,
          status: res.data.status,
          created_at: res.data.created_at || new Date().toISOString(),
          mission_id: missionId,
          mission: {
            id: missionId
          }
        }
        
        // Ajouter à mes candidatures
        this.myApplications.unshift(newApplication) // Ajouter au début
        
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur lors de la candidature'
        throw e
      } finally {
        this.loading = false
      }
    },

    // Récupérer mes candidatures (CORRIGÉ : bonne URL)
    async fetchMyApplications() {
      this.loading = true
      this.error = null
      try {
        // IMPORTANT : URL corrigée - pas /api/postulations/ mais /api/missions/
        const res = await axios.get('/api/missions/my-applications')
        this.myApplications = res.data
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur chargement candidatures'
        console.error('Erreur fetchMyApplications:', e.response?.data || e.message)
        return []
      } finally {
        this.loading = false
      }
    },

    // Retirer une candidature (à implémenter dans le backend)
    async withdrawApplication(postulationId) {
      this.loading = true
      this.error = null
      try {
        // À implémenter : route DELETE /api/missions/postulations/{id}
        // Pour l'instant, simulons la suppression
        console.log(`Simulation: suppression de la candidature ${postulationId}`)
        
        // Retirer des listes
        this.myApplications = this.myApplications.filter(app => app.id !== postulationId)
        this.postulations = this.postulations.filter(p => p.id !== postulationId)
        
        // En production, utiliser :
        // await axios.delete(`/api/missions/postulations/${postulationId}`)
        
        return true
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur retrait candidature'
        throw e
      } finally {
        this.loading = false
      }
    },

    // Annuler une candidature (status = cancelled)
    async cancelApplication(postulationId) {
      this.loading = true
      this.error = null
      try {
        // À implémenter dans le backend
        // Pour l'instant, simulons
        console.log(`Simulation: annulation de la candidature ${postulationId}`)
        
        // Mettre à jour le statut
        this.updatePostulationInLists(postulationId, { status: 'cancelled' })
        
        // En production, utiliser :
        // await axios.post(`/api/missions/postulations/${postulationId}/cancel`, { status: 'cancelled' })
        
        return true
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur annulation candidature'
        throw e
      } finally {
        this.loading = false
      }
    },

    // ======================
    // CLIENT - Gestion des candidatures
    // ======================

    // Récupérer les candidatures pour une mission spécifique (URL correcte)
    async fetchMissionPostulations(missionId) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.get(`/api/missions/${missionId}/postulations`)
        this.missionApplications = res.data
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur chargement candidatures'
        return []
      } finally {
        this.loading = false
      }
    },

    // Accepter une candidature (à implémenter dans le backend)
    async acceptApplication(postulationId) {
      this.loading = true
      this.error = null
      try {
        // À implémenter : route POST /api/missions/postulations/{id}/accept
        console.log(`Simulation: acceptation de la candidature ${postulationId}`)
        
        // Mettre à jour le statut
        this.updatePostulationInLists(postulationId, { status: 'accepted' })
        
        // En production, utiliser :
        // await axios.post(`/api/missions/postulations/${postulationId}/accept`)
        
        return { success: true }
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur acceptation candidature'
        throw e
      } finally {
        this.loading = false
      }
    },

    // Rejeter une candidature (à implémenter dans le backend)
    async rejectApplication(postulationId) {
      this.loading = true
      this.error = null
      try {
        // À implémenter : route POST /api/missions/postulations/{id}/reject
        console.log(`Simulation: rejet de la candidature ${postulationId}`)
        
        // Mettre à jour le statut
        this.updatePostulationInLists(postulationId, { status: 'rejected' })
        
        // En production, utiliser :
        // await axios.post(`/api/missions/postulations/${postulationId}/reject`)
        
        return { success: true }
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur rejet candidature'
        throw e
      } finally {
        this.loading = false
      }
    },

    // ======================
    // UTILITAIRES
    // ======================

    // Mettre à jour une postulation dans toutes les listes
    updatePostulationInLists(postulationId, updates) {
      // Mettre à jour dans missionApplications
      this.missionApplications = this.missionApplications.map(app =>
        app.id === postulationId ? { ...app, ...updates } : app
      )

      // Mettre à jour dans myApplications
      this.myApplications = this.myApplications.map(app =>
        app.id === postulationId ? { ...app, ...updates } : app
      )

      // Mettre à jour dans postulations
      this.postulations = this.postulations.map(p =>
        p.id === postulationId ? { ...p, ...updates } : p
      )

      // Mettre à jour currentPostulation si c'est elle
      if (this.currentPostulation?.id === postulationId) {
        this.currentPostulation = { ...this.currentPostulation, ...updates }
      }
    },

    // Rafraîchir une candidature spécifique (pour recharger depuis l'API)
    async refreshApplication(applicationId) {
      try {
        // Recharger toutes les candidatures
        await this.fetchMyApplications()
        
        // Retourner l'application mise à jour
        return this.myApplications.find(app => app.id === applicationId)
      } catch (e) {
        console.error('Erreur refreshApplication:', e)
        return null
      }
    },

    // Vérifier et mettre à jour les candidatures pour une mission
    async checkAndUpdateMissionApplications(missionId) {
      try {
        // Vérifier si on a déjà des applications pour cette mission
        const hasApplications = this.myApplications.some(app => {
          return app.mission_id === missionId || 
                (app.mission && app.mission.id === missionId)
        })
        
        if (!hasApplications) {
          // Recharger les applications
          await this.fetchMyApplications()
        }
        
        return this.hasAppliedToMission(missionId)
      } catch (e) {
        console.error('Erreur checkAndUpdate:', e)
        return false
      }
    },

    // Réinitialiser le store
    reset() {
      this.postulations = []
      this.myApplications = []
      this.missionApplications = []
      this.currentPostulation = null
      this.error = null
      this.loading = false
    },

    // Réinitialiser uniquement les erreurs
    clearError() {
      this.error = null
    },

    // Définir la postulation courante
    setCurrentPostulation(postulation) {
      this.currentPostulation = postulation
    },

    // Vider la postulation courante
    clearCurrentPostulation() {
      this.currentPostulation = null
    },

    // Ajouter une application manuellement (pour tests)
    addApplication(application) {
      this.myApplications.unshift(application)
    },

    // Supprimer une application
    removeApplication(applicationId) {
      this.myApplications = this.myApplications.filter(a => a.id !== applicationId)
      this.missionApplications = this.missionApplications.filter(a => a.id !== applicationId)
      
      if (this.currentPostulation?.id === applicationId) {
        this.currentPostulation = null
      }
    },

    // Synchroniser les données (pour éviter les incohérences)
    async syncData() {
      try {
        await this.fetchMyApplications()
        return true
      } catch (e) {
        console.error('Erreur syncData:', e)
        return false
      }
    },

    // Force reload avec cache busting
    async forceReload() {
      this.myApplications = []
      return await this.fetchMyApplications()
    }
  }
})