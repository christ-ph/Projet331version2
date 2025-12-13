import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
export const useProfileStore = defineStore('profile', {
    state: () => ({
        profile: null,          // ✅ Données du profil complet
        hasProfile: false,      // ✅ Booléen pour dashboard
        loading: false,
    }),

    actions: {

        // ✅ Récupérer le profil du user connecté
        async getMyProfile() {
            this.loading = true;

            try {
                const response = await axios.get('/api/profiles/me');

                this.profile = response.data;
                this.hasProfile = true;

                return this.profile;

            } catch (error) {
                // ✅ Si 404 → pas de profil
                if (error.response?.status === 404) {
                    this.profile = null;
                    this.hasProfile = false;
                    return null;
                }

                throw error;

            } finally {
                this.loading = false;
            }
        },

        // ✅ Méthode clé pour le dashboard
        async checkProfileStatus() {
            const profile = await this.getMyProfile();
            return this.hasProfile;
        },

        // ✅ Créer un profil freelance
        async createFreelanceProfile(data) {
            this.loading = true;

            try {
                const payload = {
                    type: "freelance",
                    full_name: data.full_name,
                    title: data.title,
                    description: data.description,
                    skills: data.skills,
                    languages: data.languages,
                    hourly_rate: data.hourly_rate,
                    experience_years: data.experience_years,
                    availability: data.availability
                };

                const response = await axios.post('/api/profiles/', payload);
                
                const authStore = useAuthStore();
                authStore.user = response.data.user;
                localStorage.setItem('user', JSON.stringify(response.data.user));

                await this.getMyProfile(); // ✅ Mise à jour du store

                return response.data;

            } catch (error) {
                throw error;

            } finally {
                this.loading = false;
            }
        },

        // ✅ Créer un profil client
        async createClientProfile(data) {
            this.loading = true;

            try {
                const payload = {
                    type: "client",
                    client_type: data.client_type,
                    fullname: data.fullname,
                    company_name: data.company_name,
                    company_website: data.company_website,
                    industry: data.industry
                };

                const response = await axios.post('/api/profiles/', payload);
                const authStore = useAuthStore();
                authStore.user = response.data.user;
                localStorage.setItem('user', JSON.stringify(response.data.user));

                await this.getMyProfile(); // ✅ Mise à jour du store

                return response.data;

            } catch (error) {
                throw error;

            } finally {
                this.loading = false;
            }
        },

        // ✅ Mise à jour du profil (freelance ou client)
        async updateProfile(data) {
            this.loading = true;

            try {
                const response = await axios.put('/api/profiles/', data);

                await this.getMyProfile(); // ✅ Mise à jour du store

                return response.data;

            } catch (error) {
                throw error;

            } finally {
                this.loading = false;
            }
        }
    }
});
