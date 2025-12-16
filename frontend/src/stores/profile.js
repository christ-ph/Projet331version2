import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

export const useProfileStore = defineStore('profile', {
  state: () => ({
    profile: null,
    loading: false,
    error: null,
  }),

  getters: {
    // ✅ Getter calculé automatiquement
    hasProfile: (state) => !!state.profile,
  },

  actions: {
    // ✅ Récupérer le profil du user connecté
    async getMyProfile() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get('/api/profiles/me');
        this.profile = response.data;
        return this.profile;
      } catch (error) {
        // Si 404 → pas de profil (c'est normal)
        if (error.response?.status === 404) {
          this.profile = null;
          return null;
        }
        
        // Autres erreurs
        console.error('Erreur lors de la récupération du profil:', error);
        this.error = 'Impossible de charger le profil.';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // ✅ Créer un profil freelance
    async createFreelanceProfile(data) {
      this.loading = true;
      this.error = null;

      try {
        const payload = {
          type: 'freelance',
          full_name: data.full_name,
          title: data.title,
          description: data.description,
          skills: data.skills,
          languages: data.languages,
          hourly_rate: data.hourly_rate,
          experience_years: data.experience_years,
          availability: data.availability,
        };

        const response = await axios.post('/api/profiles/', payload);

        // ✅ Synchroniser le user dans authStore
        const authStore = useAuthStore();
        authStore.updateUser(response.data.user);

        // ✅ Mettre à jour le profil local
        await this.getMyProfile();

        return response.data;
      } catch (error) {
        console.error('Erreur lors de la création du profil freelance:', error);
        this.error = 'Impossible de créer le profil.';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // ✅ Créer un profil client
    async createClientProfile(data) {
      this.loading = true;
      this.error = null;

      try {
        const payload = {
          type: 'client',
          client_type: data.client_type,
          fullname: data.fullname,
          company_name: data.company_name,
          company_website: data.company_website,
          industry: data.industry,
        };

        const response = await axios.post('/api/profiles/', payload);

        // ✅ Synchroniser le user dans authStore
        const authStore = useAuthStore();
        authStore.updateUser(response.data.user);

        // ✅ Mettre à jour le profil local
        await this.getMyProfile();

        return response.data;
      } catch (error) {
        console.error('Erreur lors de la création du profil client:', error);
        this.error = 'Impossible de créer le profil.';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // ✅ Mise à jour du profil
    async updateProfile(data) {
      this.loading = true;
      this.error = null;

      try {
        const response = await axios.put('/api/profiles/', data);

        // ✅ Mettre à jour le user si retourné (en cas de changement de rôle par exemple)
        if (response.data.user) {
          const authStore = useAuthStore();
          authStore.updateUser(response.data.user);
        }

        // ✅ Recharger le profil pour avoir les données fraîches
        await this.getMyProfile();

        return response.data;
      } catch (error) {
        console.error('Erreur lors de la mise à jour du profil:', error);
        this.error = 'Impossible de mettre à jour le profil.';
        throw error;
      } finally {
        this.loading = false;
      }
    },
  },
});