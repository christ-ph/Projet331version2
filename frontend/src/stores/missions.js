import { defineStore } from 'pinia';
import axios from 'axios';

export const useMissionStore = defineStore('missions', {
    state: () => ({
        missions: [],
        myApplications: [],
        applications: [],
        missionDetails: null,
        messages: [], // ✅ CHAT
        loading: false,
        error: null,
    }),

    actions: {

        // ✅ FREELANCE — récupérer les missions disponibles
        async fetchAvailableMissions(filters = {}) {
            this.loading = true;
            this.error = null;
            try {
                const response = await axios.get('/api/missions/available', {
                    params: filters
                });
                this.missions = response.data;
            } catch (error) {
                this.error = error.response?.data?.msg || "Erreur lors du chargement des missions";
            } finally {
                this.loading = false;
            }
        },

        // ✅ FREELANCE — détails d'une mission
        async fetchMissionDetails(id) {
            this.loading = true;
            this.error = null;
            try {
                const response = await axios.get(`/api/missions/${id}`);
                this.missionDetails = response.data;
            } catch (error) {
                this.error = error.response?.data?.msg || "Erreur lors du chargement de la mission";
            } finally {
                this.loading = false;
            }
        },

        // ✅ FREELANCE — postuler (corrigé pour ton backend)
        async applyToMission(missionId, payload) {
            this.loading = true;
            this.error = null;
            try {
                const response = await axios.post('/api/missions/apply', {
                    mission_id: missionId,
                    proposal: payload.proposal,
                    proposed_budget: payload.proposed_budget
                });
                return response.data;
            } catch (error) {
                this.error = error.response?.data?.msg || "Impossible de postuler à cette mission";
                throw error;
            } finally {
                this.loading = false;
            }
        },

        // ✅ FREELANCE — historique des candidatures
        async fetchMyApplications() {
            this.loading = true;
            this.error = null;
            try {
                const response = await axios.get('/api/missions/applications/my');
                this.myApplications = response.data;
            } catch (error) {
                this.error = error.response?.data?.msg || "Erreur lors du chargement des candidatures";
            } finally {
                this.loading = false;
            }
        },

        // ✅ CLIENT — créer une mission
        async createMission(payload) {
            this.loading = true;
            this.error = null;
            try {
                const response = await axios.post('/api/missions', payload);
                return response.data;
            } catch (error) {
                throw error;
            } finally {
                this.loading = false;
            }
        },

        // ✅ CLIENT — modifier une mission
        async updateMission(id, payload) {
            this.loading = true;
            this.error = null;
            try {
                const response = await axios.put(`/api/missions/${id}`, payload);
                return response.data;
            } catch (error) {
                throw error;
            } finally {
                this.loading = false;
            }
        },

        // ✅ CLIENT — supprimer une mission
        async deleteMission(id) {
            this.loading = true;
            this.error = null;
            try {
                const response = await axios.delete(`/api/missions/${id}`);
                return response.data;
            } catch (error) {
                throw error;
            } finally {
                this.loading = false;
            }
        },

        // ✅ CLIENT — récupérer ses missions
        async fetchClientMissions() {
            this.loading = true;
            this.error = null;
            try {
                const response = await axios.get('/api/missions/my');
                this.missions = response.data;
            } catch (error) {
                this.error = error.response?.data?.msg || "Erreur lors du chargement des missions client";
            } finally {
                this.loading = false;
            }
        },

        // ✅ CLIENT — candidatures reçues
        async fetchMissionApplications(id) {
            this.loading = true;
            this.error = null;
            try {
                const response = await axios.get(`/api/missions/${id}/applications`);
                this.applications = response.data;
            } catch (error) {
                this.error = error.response?.data?.msg || "Erreur lors du chargement des candidatures";
            } finally {
                this.loading = false;
            }
        },

        // ✅ CLIENT — accepter une candidature
        async acceptApplication(id) {
            try {
                const response = await axios.put(`/api/missions/applications/${id}/accept`);
                return response.data;
            } catch (error) {
                throw error;
            }
        },

        // ✅ CLIENT — refuser une candidature
        async rejectApplication(id) {
            try {
                const response = await axios.put(`/api/missions/applications/${id}/reject`);
                return response.data;
            } catch (error) {
                throw error;
            }
        },

        // ✅ CHAT — récupérer les messages
        async fetchMessages(missionId) {
            this.loading = true;
            this.error = null;
            try {
                const response = await axios.get(`/api/chat/${missionId}`);
                this.messages = response.data;
            } catch (error) {
                this.error = error.response?.data?.msg || "Erreur lors du chargement des messages";
            } finally {
                this.loading = false;
            }
        },

        // ✅ CHAT — envoyer un message
        async sendMessage(missionId, content) {
            this.error = null;
            try {
                const response = await axios.post(`/api/chat/${missionId}`, { content });

                // Mise à jour instantanée
                this.messages.push(response.data);

                return response.data;
            } catch (error) {
                this.error = error.response?.data?.msg || "Erreur lors de l'envoi du message";
                throw error;
            }
        }
    }
});
