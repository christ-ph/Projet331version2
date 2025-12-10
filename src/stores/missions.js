import { defineStore } from 'pinia';
import axios from 'axios';

export const useMissionStore = defineStore('missions', {
    state: () => ({
        missions: [],
        myApplications: [],
        applications: [],
        missionDetails: null,
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
                console.log("MISSIONS DISPONIBLES :", response.data);
                this.missions = response.data;
            } catch (error) {
                console.error("ERREUR FETCH AVAILABLE :", error);
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
                console.log("DETAILS MISSION :", response.data);
                this.missionDetails = response.data;
            } catch (error) {
                console.error("ERREUR DETAILS MISSION :", error);
                this.error = error.response?.data?.msg || "Erreur lors du chargement de la mission";
            } finally {
                this.loading = false;
            }
        },

        // ✅ FREELANCE — postuler
        async applyToMission(payload) {
            this.loading = true;
            this.error = null;
            try {
                const response = await axios.post('/api/missions/apply', payload);
                console.log("CANDIDATURE ENVOYÉE :", response.data);
                return response.data;
            } catch (error) {
                console.error("ERREUR APPLY :", error);
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
                console.log("MES CANDIDATURES :", response.data);
                this.myApplications = response.data;
            } catch (error) {
                console.error("ERREUR MES CANDIDATURES :", error);
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
                console.log("MISSION CRÉÉE :", response.data);
                return response.data;
            } catch (error) {
                console.error("ERREUR CREATE MISSION :", error);
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
                console.log("MISSION MODIFIÉE :", response.data);
                return response.data;
            } catch (error) {
                console.error("ERREUR UPDATE MISSION :", error);
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
                console.log("MISSION SUPPRIMÉE :", response.data);
                return response.data;
            } catch (error) {
                console.error("ERREUR DELETE MISSION :", error);
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
                console.log("MISSIONS CLIENT :", response.data);
                this.missions = response.data;
            } catch (error) {
                console.error("ERREUR MISSIONS CLIENT :", error);
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
                console.log("CANDIDATURES REÇUES :", response.data);
                this.applications = response.data;
            } catch (error) {
                console.error("ERREUR CANDIDATURES REÇUES :", error);
                this.error = error.response?.data?.msg || "Erreur lors du chargement des candidatures";
            } finally {
                this.loading = false;
            }
        },

        // ✅ CLIENT — accepter une candidature
        async acceptApplication(id) {
            return axios.put(`/api/missions/applications/${id}/accept`);
        },

        // ✅ CLIENT — refuser une candidature
        async rejectApplication(id) {
            return axios.put(`/api/missions/applications/${id}/reject`);
        }
    }
});
