// // Fichier frontend/src/main.js (CODE CORRIGÉ)

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/auth.js' 

import App from './App.vue'
import router from './router'

import axios from 'axios'

axios.defaults.baseURL = 'http://127.0.0.1:5000';

const app = createApp(App)

const pinia = createPinia()
app.use(pinia) 


const authStore = useAuthStore();
authStore.initializeToken();


authStore.router = router;    

app.use(router) 

app.mount('#app') 









