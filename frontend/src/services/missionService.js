// frontend/src/services/missionService.js
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const missionService = {
  // Récupérer toutes les missions disponibles (pour freelance)
  async getAvailableMissions(filters = {}) {
    try {
      const authStore = useAuthStore();
      const token = authStore.token;
      
      const params = new URLSearchParams();
      
      // Ajouter les filtres
      if (filters.minBudget) params.append('min_budget', filters.minBudget);
      if (filters.maxBudget) params.append('max_budget', filters.maxBudget);
      if (filters.skills) params.append('skills', Array.isArray(filters.skills) ? filters.skills.join(',') : filters.skills);
      if (filters.q) params.append('q', filters.q);
      if (filters.page) params.append('page', filters.page);
      if (filters.perPage) params.append('per_page', filters.perPage);
      if (filters.sortBy) params.append('sort_by', filters.sortBy);
      if (filters.order) params.append('order', filters.order);
      
      const response = await axios.get(`${API_URL}/missions/available?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching available missions:', error);
      throw error;
    }
  },

  // Recherche de missions
  async searchMissions(searchParams = {}) {
    try {
      const params = new URLSearchParams();
      
      Object.keys(searchParams).forEach(key => {
        if (searchParams[key] !== undefined && searchParams[key] !== '') {
          params.append(key, searchParams[key]);
        }
      });
      
      const response = await axios.get(`${API_URL}/missions/search?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Error searching missions:', error);
      throw error;
    }
  },

  // Récupérer les détails d'une mission spécifique
  async getMissionById(missionId) {
    try {
      const response = await axios.get(`${API_URL}/missions/${missionId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching mission:', error);
      throw error;
    }
  },

  // Postuler à une mission
  async applyToMission(missionId) {
    try {
      const authStore = useAuthStore();
      const token = authStore.token;
      
      const response = await axios.post(
        `${API_URL}/missions/${missionId}/apply`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      return response.data;
    } catch (error) {
      console.error('Error applying to mission:', error);
      throw error;
    }
  },

  // Récupérer les postulations de l'utilisateur
  async getMyApplications() {
    try {
      const authStore = useAuthStore();
      const token = authStore.token;
      
      const response = await axios.get(`${API_URL}/missions/my-applications`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching applications:', error);
      throw error;
    }
  },

  // Sauvegarder une mission (bookmark)
  async saveMission(missionId) {
    try {
      // Note: Vous devrez créer cette route dans votre backend
      const authStore = useAuthStore();
      const token = authStore.token;
      
      const response = await axios.post(
        `${API_URL}/missions/${missionId}/save`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      return response.data;
    } catch (error) {
      console.error('Error saving mission:', error);
      throw error;
    }
  },

  // Récupérer les missions sauvegardées
  async getSavedMissions() {
    try {
      const authStore = useAuthStore();
      const token = authStore.token;
      
      const response = await axios.get(`${API_URL}/missions/saved`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching saved missions:', error);
      throw error;
    }
  },

  // Récupérer les compétences de l'utilisateur
  async getUserSkills() {
    try {
      const authStore = useAuthStore();
      const token = authStore.token;
      
      const response = await axios.get(`${API_URL}/profile/freelance/skills`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      return response.data.skills || [];
    } catch (error) {
      console.error('Error fetching user skills:', error);
      return [];
    }
  },
  async getAvailableMissions(filters = {}) {
  try {
    const authStore = useAuthStore();
    const token = authStore.token;
    
    const params = new URLSearchParams();
    
    // Pagination
    if (filters.page) params.append('page', filters.page);
    if (filters.perPage) params.append('per_page', filters.perPage || 10);
    
    // ... autres filtres
    
    const response = await axios.get(`${API_URL}/missions/available?${params.toString()}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching available missions:', error);
    throw error;
  }
},
// Dans missionService.js
async searchMissions(searchParams) {
  try {
    const params = new URLSearchParams();
    
    Object.keys(searchParams).forEach(key => {
      if (searchParams[key] !== undefined && searchParams[key] !== '') {
        params.append(key, searchParams[key]);
      }
    });
    
    const response = await axios.get(`${API_URL}/missions/search?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Error searching missions:', error);
    throw error;
  }
},
// Dans missionService.js
async getDashboardStats() {
  try {
    const authStore = useAuthStore();
    const token = authStore.token;
    
    const response = await axios.get(`${API_URL}/missions/freelance/stats`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching stats:', error);
    return {
      applied: 0,
      saved: 0,
      matching: 0
    };
  }
},
// missionService.js

// Récupérer TOUTES les missions (pour le dashboard)
async getAllMissions(filters = {}) {
  try {
    const authStore = useAuthStore();
    const token = authStore.token;
    
    const params = new URLSearchParams();
    
    // Ajouter les paramètres de pagination si besoin
    if (filters.page) params.append('page', filters.page);
    if (filters.perPage) params.append('per_page', filters.perPage || 10);
    if (filters.sortBy) params.append('sort_by', filters.sortBy);
    if (filters.order) params.append('order', filters.order);
    
    // Vous pouvez ajouter d'autres filtres si votre endpoint les supporte
    if (filters.q) params.append('q', filters.q);
    if (filters.category) params.append('category', filters.category);
    if (filters.minBudget) params.append('min_budget', filters.minBudget);
    if (filters.maxBudget) params.append('max_budget', filters.maxBudget);
    
    const queryString = params.toString();
    const url = `${API_URL}/missions${queryString ? `?${queryString}` : ''}`;
    
    const response = await axios.get(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching all missions:', error);
    throw error;
  }
},

// Récupérer les stats pour le dashboard
async getDashboardStats() {
  try {
    const authStore = useAuthStore();
    const token = authStore.token;
    
    // Vous pouvez créer un endpoint spécifique pour les stats
    // Ou calculer les stats côté client
    const [missions, applications, saved] = await Promise.all([
      this.getAllMissions({ perPage: 100 }), // Limiter à 100 pour les stats
      this.getMyApplications(),
      this.getSavedMissions()
    ]);
    
    return {
      totalMissions: missions.length || missions.total || 0,
      appliedMissions: applications.length,
      savedMissions: saved.length,
      // Missions correspondant aux compétences de l'utilisateur
      matchingMissions: await this.getMatchingMissionsCount()
    };
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    return {
      totalMissions: 0,
      appliedMissions: 0,
      savedMissions: 0,
      matchingMissions: 0
    };
  }
},

// Méthode utilitaire pour compter les missions correspondantes
async getMatchingMissionsCount() {
  try {
    const [missions, userSkills] = await Promise.all([
      this.getAllMissions({ perPage: 100 }),
      this.getUserSkills()
    ]);
    
    const missionList = Array.isArray(missions) ? missions : 
                       (missions.missions || []);
    
    return missionList.filter(mission => {
      if (!mission.required_skills || !userSkills.length) return false;
      
      const missionSkills = Array.isArray(mission.required_skills) ? 
                          mission.required_skills : 
                          (mission.required_skills || '').split(',').map(s => s.trim());
      
      return missionSkills.some(skill => 
        userSkills.some(userSkill => 
          userSkill.toLowerCase().includes(skill.toLowerCase()) ||
          skill.toLowerCase().includes(userSkill.toLowerCase())
        )
      );
    }).length;
  } catch (error) {
    console.error('Error counting matching missions:', error);
    return 0;
  }
}
};



export default missionService;