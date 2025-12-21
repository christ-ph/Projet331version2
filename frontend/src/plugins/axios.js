import axios from "axios";
import router from "@/router";

axios.defaults.baseURL = 'http://37.60.250.220:5500'

// Intercepteur pour ajouter le token a chaque requette

axios.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Intercepteur pour gerer les erreurs 401 (token expire)
axios.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token expirer ou invalid
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');

            // netoyer les header Axios
            delete axios.defaults.headers.common['Authorization'];

            // redirection vers la page de connexion si on n'est pas deja sur /login
            if (router.currentRoute.value.path !== '/Login')
                router.push({ name: 'Login', query: {expired: 'true' } });
    }
    return Promise.reject(error);
    }
);
