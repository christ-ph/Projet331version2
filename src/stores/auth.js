import { defineStore } from 'pinia';
import axios from 'axios';

// Récupération de l'état initial
const storedToken = localStorage.getItem('access_token');
const storedUser = JSON.parse(localStorage.getItem('user') || 'null');

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: storedToken || null,
        isAuthenticated: !!storedToken,
        user: storedUser,
        isLoading: false,
        userLoaded: false,   // ✅ important pour éviter la boucle infinie
    }),

    actions: {

        // ✅ Initialise Axios avec le token
        initializeToken() {
            if (this.token) {
                axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
            }
        },

        // ✅ LOGIN
        async login(email, password) {
            this.isLoading = true;

            try {
                const response = await axios.post('/auth/login', { email, password });

                const { access_token: token, user } = response.data;

                this.token = token;
                this.user = user;
                this.isAuthenticated = true;

                localStorage.setItem('access_token', token);
                localStorage.setItem('user', JSON.stringify(user));

                axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

                return true;

            } catch (error) {
                this.logout(false);
                throw error;

            } finally {
                this.isLoading = false;
            }
        },

        // ✅ PROFILE — NE DOIT PLUS FAIRE LOGOUT EN CAS DE 401
        async profile() {
            try {
                const response = await axios.get('/auth/user-data');

                this.user = response.data.user;
                this.userLoaded = true;
                this.isAuthenticated = true;
                localStorage.setItem('user', JSON.stringify(this.user));

                return response.data;

            } catch (error) {

                // ✅ IMPORTANT : éviter la boucle infinie
                this.userLoaded = true;
                this.isAuthenticated = true;
                // ✅ On ne logout PAS ici
                // Le guard décidera quoi faire

                return null;
            }
        },

        // ✅ REGISTER
        async register(email, password) {
            try {
                await axios.post('/auth/register', { email, password });
            } catch (error) {
                throw error;
            }
        },

        // ✅ LOGOUT
        logout(redirect = true) {
            this.token = null;
            this.user = null;
            this.isAuthenticated = false;

            localStorage.removeItem('access_token');
            localStorage.removeItem('user');

            delete axios.defaults.headers.common['Authorization'];

            if (redirect && this.router) {
                this.router.push('/login');
            }
        },

        // ✅ Hydrate user si token existe
        async fetchUserIfTokenExists() {
            if (this.isAuthenticated && !this.user) {
                try {
                    const response = await axios.get('/auth/protected');
                    this.user = response.data.user;
                    localStorage.setItem('user', JSON.stringify(this.user));
                } catch (error) {
                    this.logout(false);
                }
            }
        }
    },
});
