import { defineStore } from 'pinia'
import axios from 'axios'

export const useMissionStore = defineStore('missions', {
  state: () => ({
    missions: [],        // toutes les missions (public / recherche)
    myMissions: [],      // missions du client connecté
    currentMission: null, // mission actuellement sélectionnée
    missionApplications: [], // candidatures pour la mission courante (client)
    availableMissions: [], // missions visibles par les freelances (statut "open")
    loading: false,
    error: null,
    selectedMission: null, // Mission sélectionnée pour les détails
    filters: {
      status: '',
      skills: [],
      budget_min: null,
      budget_max: null
    }
  }),

  getters: {
    // Getters pour filtrer par statut
    draftMissions: (state) => state.myMissions.filter(m => m.status === 'draft'),
    publishedMissions: (state) => state.myMissions.filter(m => m.status === 'open'),
    inProgressMissions: (state) => state.myMissions.filter(m => m.status === 'in_progress'),
    completedMissions: (state) => state.myMissions.filter(m => m.status === 'completed'),
    cancelledMissions: (state) => state.myMissions.filter(m => m.status === 'cancelled'),

    // Missions disponibles pour les freelances (statut "open" uniquement)
    openMissions: (state) => state.availableMissions.filter(m => m.status === 'open'),

    // Statistiques pour le client
    totalPendingApplications: (state) => {
      return state.myMissions.reduce((total, mission) => {
        return total + (mission.postulations_pending || 0)
      }, 0)
    },

    totalApplications: (state) => {
      return state.myMissions.reduce((total, mission) => {
        return total + (mission.postulations_total || 0)
      }, 0)
    },

    // NOUVEAUX GETTERS
    filteredAvailableMissions: (state) => {
      let filtered = state.availableMissions;
      
      // Filtrer par statut
      if (state.filters.status) {
        filtered = filtered.filter(m => m.status === state.filters.status);
      }
      
      // Filtrer par compétences
      if (state.filters.skills && state.filters.skills.length > 0) {
        filtered = filtered.filter(mission => {
          if (!mission.required_skills) return false;
          return state.filters.skills.some(skill => 
            mission.required_skills.includes(skill)
          );
        });
      }
      
      // Filtrer par budget
      if (state.filters.budget_min !== null) {
        filtered = filtered.filter(m => m.budget >= state.filters.budget_min);
      }
      
      if (state.filters.budget_max !== null) {
        filtered = filtered.filter(m => m.budget <= state.filters.budget_max);
      }
      
      return filtered;
    },

    // Trouver une mission par ID dans les différentes listes
    getMissionById: (state) => (id) => {
      // Chercher dans myMissions d'abord
      let mission = state.myMissions.find(m => m.id === id)
      if (mission) return mission
      
      // Chercher dans availableMissions
      mission = state.availableMissions.find(m => m.id === id)
      if (mission) return mission
      
      // Chercher dans missions (public)
      mission = state.missions.find(m => m.id === id)
      return mission
    },

    // Alias pour compatibilité avec ton composant
    missionDetails: (state) => state.currentMission,
    applications: (state) => state.missionApplications,
    
    // Statistiques supplémentaires
    missionStats: (state) => {
      const stats = {
        total: state.myMissions.length,
        draft: state.draftMissions.length,
        published: state.publishedMissions.length,
        inProgress: state.inProgressMissions.length,
        completed: state.completedMissions.length,
        cancelled: state.cancelledMissions.length,
        totalBudget: state.myMissions.reduce((sum, m) => sum + (m.budget || 0), 0),
        averageBudget: state.myMissions.length > 0 
          ? state.myMissions.reduce((sum, m) => sum + (m.budget || 0), 0) / state.myMissions.length
          : 0
      };
      return stats;
    }
  },

  actions: {
    // ======================
    // CLIENT - Gestion des missions
    // ======================

    // Récupérer toutes les missions du client (tous statuts)
    async fetchMyMissions(params = {}) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.get('/api/missions/my-missions', { params })
        this.myMissions = res.data
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur chargement des missions'
        console.error('Erreur fetchMyMissions:', e)
        return []
      } finally {
        this.loading = false
      }
    },

    // Alias pour la vue client
    fetchClientMissions(params = {}) {
      return this.fetchMyMissions(params)
    },

    // ======================
    // NOUVELLES ROUTES POUR GESTION CANDIDATURES
    // ======================

    // Accepter ou refuser une candidature
    async updateApplicationStatus(missionId, applicationId, status) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.put(
          `/api/missions/${missionId}/applications/${applicationId}/status`,
          { status }
        )
        
        // Mettre à jour localement le statut
        this.missionApplications = this.missionApplications.map(app =>
          app.id === applicationId ? { ...app, status: status } : app
        )
        
        // Si la candidature est acceptée, mettre à jour le statut de la mission
        if (status === 'accepted') {
          this.updateLocalMissionStatus(missionId, 'in_progress')
        }
        
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || `Erreur ${status === 'accepted' ? 'acceptation' : 'refus'} candidature`
        throw e
      } finally {
        this.loading = false
      }
    },

    // Alias pour accepter une candidature
    async acceptApplication(missionId, applicationId) {
      return this.updateApplicationStatus(missionId, applicationId, 'accepted')
    },

    // Alias pour refuser une candidature
    async rejectApplication(missionId, applicationId) {
      return this.updateApplicationStatus(missionId, applicationId, 'rejected')
    },

    // ======================
    // COMPLÉTION DE MISSION AVEC ÉVALUATION
    // ======================

    // Marquer une mission comme complétée avec évaluation optionnelle
    async completeMission(missionId, evaluationData = {}) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.put(`/api/missions/${missionId}/complete`, evaluationData)
        
        // Utiliser la méthode de mise à jour locale
        this.updateLocalMissionStatus(missionId, 'completed')
        
        // Si évaluation, stocker localement
        if (evaluationData.rating || evaluationData.feedback) {
          this.myMissions = this.myMissions.map(mission => {
            if (mission.id === missionId) {
              return {
                ...mission,
                client_rating: evaluationData.rating,
                client_feedback: evaluationData.feedback,
                evaluated_at: new Date().toISOString()
              }
            }
            return mission
          })
        }
        
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur complétion mission'
        throw e
      } finally {
        this.loading = false
      }
    },

    // Annuler une mission
    async cancelMission(missionId) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.put(`/api/missions/${missionId}/cancel`, {})
        
        // Mettre à jour localement
        this.updateLocalMissionStatus(missionId, 'cancelled')
        
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur annulation mission'
        throw e
      } finally {
        this.loading = false
      }
    },

    // ======================
    // CRUD MISSIONS
    // ======================

    // Créer une nouvelle mission (statut "draft" par défaut)
    async createMission(payload) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.post('/api/missions', payload)
        // Ajouter au début de la liste
        this.myMissions.unshift(res.data)
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur création mission'
        throw e
      } finally {
        this.loading = false
      }
    },

    // Mettre à jour une mission existante
    async updateMission(id, payload) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.put(`/api/missions/${id}`, payload)

        // Mettre à jour dans myMissions
        this.myMissions = this.myMissions.map(m =>
          m.id === id ? { ...m, ...res.data, updated_at: new Date().toISOString() } : m
        )

        // Mettre à jour la mission courante si c'est elle
        if (this.currentMission?.id === id) {
          this.currentMission = { ...this.currentMission, ...res.data }
        }

        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur modification mission'
        throw e
      } finally {
        this.loading = false
      }
    },

    // Supprimer une mission
    async deleteMission(id) {
      this.loading = true
      this.error = null
      try {
        await axios.delete(`/api/missions/${id}`)
        
        // Retirer de la liste
        this.myMissions = this.myMissions.filter(m => m.id !== id)
        
        // Si c'était la mission courante, la réinitialiser
        if (this.currentMission?.id === id) {
          this.currentMission = null
        }
        
        return true
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur suppression mission'
        throw e
      } finally {
        this.loading = false
      }
    },

    // ======================
    // CANDIDATURES (pour client)
    // ======================

    // Récupérer les candidatures pour une mission spécifique
    async fetchMissionApplications(missionId) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.get(`/api/missions/${missionId}/postulations`)
        this.missionApplications = res.data
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur chargement candidatures'
        console.error('Erreur fetchMissionApplications:', e.response?.data || e.message)
        return []
      } finally {
        this.loading = false
      }
    },

    // Récupérer le freelance accepté pour une mission
    async fetchAcceptedFreelance(missionId) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.get(`/api/missions/${missionId}/applications/accepted`)
        return res.data.freelance
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur chargement freelance'
        console.error('Erreur fetchAcceptedFreelance:', e)
        return null
      } finally {
        this.loading = false
      }
    },

    // ======================
    // PUBLICATION ET CHANGEMENT DE STATUT
    // ======================

    // Publier une mission (passer de "draft" à "open")
    async publishMission(id) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.post(`/api/missions/${id}/publish`)
        
        // Mettre à jour la mission dans myMissions
        this.updateLocalMissionStatus(id, 'open')
        
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur publication mission'
        throw e
      } finally {
        this.loading = false
      }
    },

    // Changer le statut d'une mission
    async changeMissionStatus(id, status) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.patch(`/api/missions/${id}/status`, { status })
        
        // Mettre à jour localement
        this.updateLocalMissionStatus(id, status)
        
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur changement statut'
        throw e
      } finally {
        this.loading = false
      }
    },

    // ======================
    // FREELANCE - Missions disponibles
    // ======================

    // Récupérer les missions disponibles pour les freelances (statut "open")
    async fetchAvailableMissions(filters = {}) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.get('/api/missions/available', { params: filters })
        this.availableMissions = res.data
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur chargement missions disponibles'
        return []
      } finally {
        this.loading = false
      }
    },

    // ======================
    // PUBLIC - Recherche et consultation
    // ======================

    // Récupérer toutes les missions (public)
    async fetchAllMissions(filters = {}) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.get('/api/missions', { params: filters })
        this.missions = res.data
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur chargement missions'
        return []
      } finally {
        this.loading = false
      }
    },

    // Récupérer les détails d'une mission spécifique
    async fetchMissionDetails(id) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.get(`/api/missions/${id}`)
        this.currentMission = res.data
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur chargement détails mission'
        console.error('Erreur fetchMissionDetails:', e.response?.data || e.message)
        throw e
      } finally {
        this.loading = false
      }
    },

    // Récupérer les détails d'une mission complétée
    async fetchMissionCompletionDetails(id) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.get(`/api/missions/${id}/completion`)
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur chargement détails complétion'
        console.error('Erreur fetchMissionCompletionDetails:', e)
        throw e
      } finally {
        this.loading = false
      }
    },

    // Recherche avancée de missions
    async searchMissions(queryParams = {}) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.get('/api/missions/search', { params: queryParams })
        this.missions = res.data.missions || res.data
        return res.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Erreur recherche missions'
        return []
      } finally {
        this.loading = false
      }
    },

    // ======================
    // UTILITAIRES
    // ======================

    // Rafraîchir les données d'une mission spécifique
    async refreshMission(id) {
      try {
        const mission = await this.fetchMissionDetails(id)
        
        // Mettre à jour dans les différentes listes
        this.myMissions = this.myMissions.map(m =>
          m.id === id ? mission : m
        )
        
        this.availableMissions = this.availableMissions.map(m =>
          m.id === id ? mission : m
        )
        
        this.missions = this.missions.map(m =>
          m.id === id ? mission : m
        )
        
        return mission
      } catch (e) {
        console.error('Erreur refreshMission:', e)
        return null
      }
    },

    // Dupliquer une mission existante avec options
    async duplicateMission(id, options = {}) {
      const original = this.getMissionById(id)
      if (!original) {
        throw new Error('Mission non trouvée')
      }

      const duplicateData = {
        title: options.title || `${original.title} (Copie)`,
        description: original.description,
        budget: options.budget || original.budget,
        required_skills: original.required_skills || [],
        status: options.status || 'draft',
        deadline: options.deadline || original.deadline
      }

      return await this.createMission(duplicateData)
    },

    // Télécharger la facture d'une mission
    async downloadInvoice(missionId) {
      try {
        const response = await axios.get(`/api/missions/${missionId}/invoice`, {
          responseType: 'blob'
        })
        
        // Créer un URL pour le fichier blob
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `facture-mission-${missionId}.pdf`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        
        return true
      } catch (e) {
        console.error('Erreur téléchargement facture:', e)
        throw e
      }
    },

    // ======================
    // NOUVELLES ACTIONS
    // ======================
    
    // Définir les filtres
    setFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
    },
    
    // Réinitialiser les filtres
    resetFilters() {
      this.filters = {
        status: '',
        skills: [],
        budget_min: null,
        budget_max: null
      }
    },
    
    // Sélectionner une mission
    selectMission(mission) {
      this.selectedMission = mission
    },
    
    // Désélectionner une mission
    clearSelectedMission() {
      this.selectedMission = null
    },
    
    // Mettre à jour le statut local d'une mission
    updateLocalMissionStatus(missionId, status) {
      // Mettre à jour dans myMissions
      this.myMissions = this.myMissions.map(mission =>
        mission.id === missionId ? { 
          ...mission, 
          status: status,
          updated_at: new Date().toISOString()
        } : mission
      )
      
      // Mettre à jour dans availableMissions (retirer si complétée/annulée)
      if (status === 'completed' || status === 'cancelled' || status === 'in_progress') {
        this.availableMissions = this.availableMissions.filter(m => m.id !== missionId)
      }
      
      // Mettre à jour la mission courante si c'est elle
      if (this.currentMission?.id === missionId) {
        this.currentMission = { 
          ...this.currentMission, 
          status: status,
          updated_at: new Date().toISOString()
        }
      }
      
      // Mettre à jour la mission sélectionnée si c'est elle
      if (this.selectedMission?.id === missionId) {
        this.selectedMission = { 
          ...this.selectedMission, 
          status: status,
          updated_at: new Date().toISOString()
        }
      }
    },

    // Recherche intelligente de missions
    async smartSearch(searchParams) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get('/api/missions/search/smart', { 
          params: searchParams 
        })
        
        // Note: Vous devrez implémenter cette fonction getUserRole() 
        // ou utiliser le store auth directement
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || 'Erreur lors de la recherche'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Récupérer les statistiques des missions
    async fetchMissionStats() {
      this.loading = true
      this.error = null
      try {
        const res = await axios.get('/api/missions/stats')
        return res.data
      } catch (error) {
        this.error = error.response?.data?.error || 'Erreur chargement statistiques'
        return null
      } finally {
        this.loading = false
      }
    },
    
    // Exporter les missions au format CSV
    async exportMissions(format = 'csv') {
      try {
        const response = await axios.get(`/api/missions/export?format=${format}`, {
          responseType: 'blob'
        })
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `missions-export.${format}`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        
        return true
      } catch (error) {
        console.error('Erreur export missions:', error)
        throw error
      }
    },

    // Réinitialiser le store
    reset() {
      this.missions = []
      this.myMissions = []
      this.availableMissions = []
      this.currentMission = null
      this.missionApplications = []
      this.error = null
      this.loading = false
      this.selectedMission = null
      this.resetFilters()
    },

    // Réinitialiser uniquement les erreurs
    clearError() {
      this.error = null
    },

    // Définir la mission courante
    setCurrentMission(mission) {
      this.currentMission = mission
    },

    // Vider la mission courante
    clearCurrentMission() {
      this.currentMission = null
    },

    // Mettre à jour une mission dans toutes les listes
    updateMissionInAllLists(missionId, updatedData) {
      // Mettre à jour dans myMissions
      this.myMissions = this.myMissions.map(mission =>
        mission.id === missionId ? { ...mission, ...updatedData } : mission
      )
      
      // Mettre à jour dans availableMissions
      this.availableMissions = this.availableMissions.map(mission =>
        mission.id === missionId ? { ...mission, ...updatedData } : mission
      )
      
      // Mettre à jour dans missions (public)
      this.missions = this.missions.map(mission =>
        mission.id === missionId ? { ...mission, ...updatedData } : mission
      )
      
      // Mettre à jour la mission courante si c'est elle
      if (this.currentMission?.id === missionId) {
        this.currentMission = { ...this.currentMission, ...updatedData }
      }
      
      // Mettre à jour la mission sélectionnée si c'est elle
      if (this.selectedMission?.id === missionId) {
        this.selectedMission = { ...this.selectedMission, ...updatedData }
      }
    }
  }
})