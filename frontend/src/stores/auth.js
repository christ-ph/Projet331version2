import { defineStore } from 'pinia';
import axios from 'axios';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    isLoading: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    userRole: (state) => state.user?.role || null,
  },

  actions: {
    // ✅ Initialisation au démarrage de l'app
    // initialize() {
    //   if (this.token) {
    //     axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
    //   }
    // },

    // ✅ Login
    async login(email, password) {
      this.isLoading = true;
      try {
        const response = await axios.post('/auth/login', { email, password });
        const { access_token, user } = response.data;

        this.token = access_token;
        this.user = user;

        localStorage.setItem('access_token', access_token);
        localStorage.setItem('user', JSON.stringify(user));

        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

        return true;
      } catch (error) {
        if (error.response?.status === 403) {
          throw { type: 'unverified', message: 'Veuillez vérifier votre email.' };
        }
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
     updateUser(updatedUser) {
    this.user = updatedUser;
    localStorage.setItem('user', JSON.stringify(updatedUser));
  },
  async register(email, password) {
    this.isLoading = true;
    try {
      const response = await axios.post('/auth/register', { email, password });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de l\'inscription:', error);
      throw error;
    } finally {
      this.isLoading = false;
    }
  },

  // ✅ NOUVELLE ACTION : Vérifier l'email avec le code OTP
  async verifyEmail(email, code) {
    this.isLoading = true;
    try {
      const response = await axios.post('/auth/verify-email', { email, code });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la vérification:', error);
      throw error;
    } finally {
      this.isLoading = false;
    }
  },

  // ✅ NOUVELLE ACTION : Renvoyer le code OTP
  async resendCode(email) {
    this.isLoading = true;
    try {
      const response = await axios.post('/auth/resend-code', { email });
      return response.data;
    } catch (error) {
      console.error('Erreur lors du renvoi du code:', error);
      throw error;
    } finally {
      this.isLoading = false;
    }
  },
    // ✅ Logout
    logout() {
      this.token = null;
      this.user = null;

      localStorage.removeItem('access_token');
      localStorage.removeItem('user');

      delete axios.defaults.headers.common['Authorization'];
    },
  },
});