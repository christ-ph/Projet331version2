// stores/missions.js
import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from './auth';

export const useMissionsStore = defineStore('missions', {
  state: () => ({
    missions: [],
    currentMission: null,
    clientStats: null,
    loading: false,
    error: null,
    pagination: {
      page: 1,
      perPage: 20,
      total: 0,
      pages: 1
    }
  }),

  getters: {
    getMissionById: (state) => (id) => {
      return state.missions.find(mission => mission.id === id);
    },
    
    getClientStats: (state) => state.clientStats,
    
    getMissionsByStatus: (state) => (status) => {
      return state.missions.filter(mission => mission.status === status);
    },
    
    getActiveMissions: (state) => {
      return state.missions.filter(mission => 
        ['open', 'in_progress'].includes(mission.status)
      );
    },
    
    getCompletedMissions: (state) => {
      return state.missions.filter(mission => mission.status === 'completed');
    }
  },

  actions: {
    async fetchMyMissions() {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const response = await axios.get('/api/missions/my-missions', {
          headers: authStore.authHeader
        });
        
        this.missions = response.data;
        return response.data;
      } catch (error) {
        console.error('❌ ERROR fetching missions:', error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchMissionById(id) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const response = await axios.get(`/api/missions/${id}`, {
          headers: authStore.authHeader
        });
        
        this.currentMission = response.data;
        return response.data;
      } catch (error) {
        console.error(`❌ ERROR fetching mission ${id}:`, error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async createMission(missionData) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const response = await axios.post('/api/missions', missionData, {
          headers: authStore.authHeader
        });
        
        // Ajouter la nouvelle mission à la liste
        this.missions.unshift(response.data);
        return response.data;
      } catch (error) {
        console.error('❌ ERROR creating mission:', error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateMission(id, missionData) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const response = await axios.put(`/api/missions/${id}`, missionData, {
          headers: authStore.authHeader
        });
        
        // Mettre à jour la mission dans la liste
        const index = this.missions.findIndex(m => m.id === id);
        if (index !== -1) {
          this.missions[index] = response.data.mission;
        }
        
        // Mettre à jour la mission courante si c'est la même
        if (this.currentMission && this.currentMission.id === id) {
          this.currentMission = response.data.mission;
        }
        
        return response.data;
      } catch (error) {
        console.error(`❌ ERROR updating mission ${id}:`, error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async deleteMission(id) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        await axios.delete(`/api/missions/${id}`, {
          headers: authStore.authHeader
        });
        
        // Supprimer la mission de la liste
        this.missions = this.missions.filter(mission => mission.id !== id);
        
        // Réinitialiser la mission courante si c'est la même
        if (this.currentMission && this.currentMission.id === id) {
          this.currentMission = null;
        }
        
        return true;
      } catch (error) {
        console.error(`❌ ERROR deleting mission ${id}:`, error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async publishMission(id) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const response = await axios.post(`/api/missions/${id}/publish`, {}, {
          headers: authStore.authHeader
        });
        
        // Mettre à jour la mission dans la liste
        const index = this.missions.findIndex(m => m.id === id);
        if (index !== -1) {
          this.missions[index] = response.data.mission;
        }
        
        return response.data;
      } catch (error) {
        console.error(`❌ ERROR publishing mission ${id}:`, error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async changeMissionStatus(id, status) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const response = await axios.patch(`/api/missions/${id}/status`, {
          status
        }, {
          headers: authStore.authHeader
        });
        
        // Mettre à jour la mission dans la liste
        const index = this.missions.findIndex(m => m.id === id);
        if (index !== -1) {
          this.missions[index] = response.data.mission;
        }
        
        return response.data;
      } catch (error) {
        console.error(`❌ ERROR changing mission status ${id}:`, error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchMissionApplications(id) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const response = await axios.get(`/api/missions/${id}/postulations`, {
          headers: authStore.authHeader
        });
        
        return response.data;
      } catch (error) {
        console.error(`❌ ERROR fetching mission applications ${id}:`, error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchClientStats() {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const response = await axios.get('/api/missions/stats', {
          headers: authStore.authHeader
        });
        
        this.clientStats = response.data;
        return response.data;
      } catch (error) {
        console.error('❌ ERROR fetching client stats:', error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchMissionCompletionDetails(id) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const response = await axios.get(`/api/missions/${id}/completion`, {
          headers: authStore.authHeader
        });
        
        return response.data;
      } catch (error) {
        console.error(`❌ ERROR fetching mission completion ${id}:`, error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateApplicationStatus(missionId, applicationId, status) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const response = await axios.put(`/api/missions/${missionId}/applications/${applicationId}/status`, {
          status
        }, {
          headers: authStore.authHeader
        });
        
        return response.data;
      } catch (error) {
        console.error(`❌ ERROR updating application status:`, error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async completeMission(missionId, data) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const response = await axios.put(`/api/missions/${missionId}/complete`, data, {
          headers: authStore.authHeader
        });
        
        return response.data;
      } catch (error) {
        console.error(`❌ ERROR completing mission ${missionId}:`, error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async cancelMission(missionId) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const response = await axios.put(`/api/missions/${missionId}/cancel`, {}, {
          headers: authStore.authHeader
        });
        
        return response.data;
      } catch (error) {
        console.error(`❌ ERROR cancelling mission ${missionId}:`, error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async exportMissions(format = 'pdf', missionId = null) {
      try {
        const authStore = useAuthStore();
        let url = `/api/missions/export?format=${format}`;
        
        if (missionId) {
          url += `&mission_id=${missionId}`;
        }
        
        const response = await axios.get(url, {
          headers: authStore.authHeader,
          responseType: 'blob'
        });
        
        // Créer un URL pour le blob
        const blob = new Blob([response.data], {
          type: response.headers['content-type']
        });
        
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        
        // Déterminer le nom du fichier
        const timestamp = new Date().getTime();
        let filename = `missions_export_${timestamp}`;
        
        if (missionId) {
          filename = `mission_${missionId}_export_${timestamp}`;
        }
        
        switch (format) {
          case 'csv':
            filename += '.csv';
            break;
          case 'excel':
            filename += '.xlsx';
            break;
          case 'pdf':
            filename += '.pdf';
            break;
        }
        
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(downloadUrl);
        
        return true;
      } catch (error) {
        console.error('❌ ERROR exporting missions:', error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      }
    },

    async searchMissions(filters = {}) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const params = new URLSearchParams();
        
        Object.keys(filters).forEach(key => {
          if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
            params.append(key, filters[key]);
          }
        });
        
        const response = await axios.get(`/api/missions/search?${params.toString()}`, {
          headers: authStore.authHeader
        });
        
        this.missions = response.data.missions;
        this.pagination = {
          page: response.data.page,
          perPage: response.data.per_page,
          total: response.data.total,
          pages: response.data.pages
        };
        
        return response.data;
      } catch (error) {
        console.error('❌ ERROR searching missions:', error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    resetCurrentMission() {
      this.currentMission = null;
    }
  }
});