// stores/freelancers.js
import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from './auth';

export const useFreelancersStore = defineStore('freelancers', {
  state: () => ({
    freelancers: [],
    currentFreelancer: null,
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
    getFreelancerById: (state) => (id) => {
      return state.freelancers.find(freelancer => freelancer.id === id);
    },
    
    getTopRatedFreelancers: (state) => {
      return [...state.freelancers]
        .sort((a, b) => b.rating - a.rating)
        .slice(0, 5);
    },
    
    getFreelancersBySkills: (state) => (skills) => {
      if (!skills || skills.length === 0) return state.freelancers;
      
      return state.freelancers.filter(freelancer => {
        if (!freelancer.skills || !Array.isArray(freelancer.skills)) return false;
        return skills.some(skill => 
          freelancer.skills.some(fSkill => 
            fSkill.toLowerCase().includes(skill.toLowerCase())
          )
        );
      });
    }
  },

  actions: {
    async fetchAllFreelancers(filters = {}) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const params = new URLSearchParams();
        
        Object.keys(filters).forEach(key => {
          if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
            params.append(key, filters[key]);
          }
        });
        
        const response = await axios.get(`/api/freelancers/all?${params.toString()}`, {
          headers: authStore.authHeader
        });
        
        this.freelancers = response.data.freelancers || response.data;
        return this.freelancers;
      } catch (error) {
        console.error('❌ ERROR fetching freelancers:', error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchFreelancerById(id) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const response = await axios.get(`/api/freelancers/${id}`, {
          headers: authStore.authHeader
        });
        
        this.currentFreelancer = response.data;
        return response.data;
      } catch (error) {
        console.error(`❌ ERROR fetching freelancer ${id}:`, error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async searchFreelancers(filters = {}) {
      try {
        this.loading = true;
        const authStore = useAuthStore();
        const params = new URLSearchParams();
        
        Object.keys(filters).forEach(key => {
          if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
            params.append(key, filters[key]);
          }
        });
        
        const response = await axios.get(`/api/freelancers/search?${params.toString()}`, {
          headers: authStore.authHeader
        });
        
        this.freelancers = response.data.freelancers || response.data;
        this.pagination = {
          page: response.data.page || 1,
          perPage: response.data.per_page || 20,
          total: response.data.total || this.freelancers.length,
          pages: response.data.pages || 1
        };
        
        return response.data;
      } catch (error) {
        console.error('❌ ERROR searching freelancers:', error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchFreelancerStats() {
      try {
        const authStore = useAuthStore();
        const response = await axios.get('/api/freelancers/stats', {
          headers: authStore.authHeader
        });
        
        return response.data;
      } catch (error) {
        console.error('❌ ERROR fetching freelancer stats:', error);
        this.error = error.response?.data?.error || error.message;
        throw error;
      }
    },

    resetCurrentFreelancer() {
      this.currentFreelancer = null;
    }
  }
});