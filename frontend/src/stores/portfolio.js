import { defineStore } from 'pinia';
import axios from 'axios';

export const usePortfolioStore = defineStore('portfolio', {
    state: () => ({
        items: [],        // ✅ Liste des portfolios du user
        loading: false,
        error: null,
    }),

    actions: {

        // ✅ Récupérer tous les portfolios du user
        async fetchPortfolio() {
            this.loading = true;
            this.error = null;

            try {
                const response = await axios.get('/api/portfolio/');
                this.items = response.data;
                return this.items;

            } catch (error) {
                this.error = "Impossible de charger le portfolio.";
                throw error;

            } finally {
                this.loading = false;
            }
        },

        // ✅ Ajouter un élément au portfolio
        async addPortfolio(data) {
            this.loading = true;
            this.error = null;

            try {
                const response = await axios.post('/api/portfolio/', data);

                // ✅ Ajouter localement
                this.items.push(response.data.portfolio);

                return response.data.portfolio;

            } catch (error) {
                this.error = "Erreur lors de l'ajout au portfolio.";
                throw error;

            } finally {
                this.loading = false;
            }
        },

        // ✅ Modifier un élément du portfolio
        async updatePortfolio(id, data) {
            this.loading = true;
            this.error = null;

            try {
                await axios.put(`/api/portfolio/${id}`, data);

                // ✅ Mise à jour locale
                const index = this.items.findIndex(p => p.id === id);
                if (index !== -1) {
                    this.items[index] = { ...this.items[index], ...data };
                }

                return true;

            } catch (error) {
                this.error = "Erreur lors de la mise à jour.";
                throw error;

            } finally {
                this.loading = false;
            }
        },

        // ✅ Supprimer un élément du portfolio
        async deletePortfolio(id) {
            this.loading = true;
            this.error = null;

            try {
                await axios.delete(`/api/portfolio/${id}`);

                // ✅ Suppression locale
                this.items = this.items.filter(p => p.id !== id);

                return true;

            } catch (error) {
                this.error = "Erreur lors de la suppression.";
                throw error;

            } finally {
                this.loading = false;
            }
        }
    }
});
