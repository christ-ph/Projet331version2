import { defineStore } from 'pinia'
import axios from 'axios'

export  const useMissionStore = defineStore('missions', {
  state: () => ({
    missions: [],        // toutes les missions (public / recherche)
    myMissions: [],      // missions du client connecté
    currentMission: null, // mission actuellement sélectionnée
    missionApplications: [], // candidatures pour la mission courante (client)
    availableMissions: [], // missions visibles par les freelances (statut "open")
    loading: false,
    error: null
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
    applications: (state) => state.missionApplications
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
          this.myMissions = this.myMissions.map(mission =>
            mission.id === missionId ? { 
              ...mission, 
              status: 'in_progress',
              updated_at: new Date().toISOString()
            } : mission
          )
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

    // Marquer une mission comme complétée
    async completeMission(missionId) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.put(`/api/missions/${missionId}/complete`, {})
        
        // Mettre à jour localement le statut
        this.myMissions = this.myMissions.map(mission =>
          mission.id === missionId ? { 
            ...mission, 
            status: 'completed',
            updated_at: new Date().toISOString()
          } : mission
        )
        
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
        
        // Mettre à jour localement le statut
        this.myMissions = this.myMissions.map(mission =>
          mission.id === missionId ? { 
            ...mission, 
            status: 'cancelled',
            updated_at: new Date().toISOString()
          } : mission
        )
        
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
        this.myMissions = this.myMissions.map(mission =>
          mission.id === id ? { 
            ...mission, 
            status: 'open',
            updated_at: new Date().toISOString()
          } : mission
        )
        
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
        
        // Mettre à jour la mission dans myMissions
        this.myMissions = this.myMissions.map(mission =>
          mission.id === id ? { 
            ...mission, 
            status: status,
            updated_at: new Date().toISOString()
          } : mission
        )
        
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

    // Dupliquer une mission existante
    async duplicateMission(id) {
      const original = this.getMissionById(id)
      if (!original) {
        throw new Error('Mission non trouvée')
      }

      const duplicateData = {
        title: `${original.title} (Copie)`,
        description: original.description,
        budget: original.budget,
        required_skills: original.required_skills || [],
        status: 'draft' // Toujours créer la copie en brouillon
      }

      return await this.createMission(duplicateData)
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
    }
  }
})