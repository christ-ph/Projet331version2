import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// =========================
// CONFIG AXIOS
// =========================
//axios.defaults.baseURL = 'http://127.0.0.1:5000'
axios.defaults.baseURL = 'http://37.60.250.220:5500'
axios.defaults.headers.common['Content-Type'] = 'application/json'

// =========================
// INTERCEPTEURS DEBUG
// =========================
axios.interceptors.request.use(
  config => {
    console.log('📤 Requête:', {
      method: config.method?.toUpperCase(),
      url: config.url
    })
    return config
  },
  error => {
    console.error('❌ Erreur requête:', error)
    return Promise.reject(error)
  }
)

axios.interceptors.response.use(
  response => {
    console.log('📥 Réponse:', {
      status: response.status,
      url: response.config.url
    })
    return response
  },
  error => {
    console.error('❌ Erreur réponse:', {
      status: error.response?.status,
      url: error.config?.url,
      message: error.message
    })
    return Promise.reject(error)
  }
)

// =========================
// CREATE APP
// =========================
const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// =========================
// INIT AUTH STORE (PROPRE)
// =========================
const authStore = useAuthStore()
authStore.initialize()

console.log('✅ Store auth initialisé')

// =========================
// MOUNT
// =========================
app.mount('#app')
