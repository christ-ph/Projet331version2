import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './plugins/axios'


const app = createApp(App)
const pinia = createPinia()


app.use(pinia) 
app.use(router) 

// initialisation du auth store avant de monter l'app

// import { useAuthStore } from './stores/auth';
// const authStore = useAuthStore();
// authStore.initialize();


app.mount('#app') 









