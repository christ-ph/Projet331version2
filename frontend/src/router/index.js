
import { createRouter, createWebHistory } from 'vue-router';

import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import DashboardView from '../views/DashboardView.vue';
import AvailableMissionsview from '../views/AvailableMissionView.vue';
// import UserProfileView from '../views/UserProfileView.vue';
// import FreelanceProfileView from '../views/FreelanceProfileView.vue';
// import MissionsView from '../views/MissionsView.vue';

// import MissionsViewClient from '@/views/MissionsViewClient.vue';

import { useAuthStore } from '@/stores/auth'; // Import pour le guard
import MissionDetailsView from '@/views/MissionDetailsView.vue';
import CreateMissionView from '@/views/CreateMissionView.vue';
import ClientMissionView from '@/views/ClientMissionView.vue';
import ClientMissionDetailView from '@/views/ClientMissionDetailView.vue';
import ApplyMissionView from '@/views/ApplyMissionView.vue';
import PortfolioView from '@/views/PortfolioVue.vue'

const routes = [

    { path: '/', name: 'Home', component: HomeView },
    { path: '/login', name: 'Login', component: LoginView },
    { path: '/register', name: 'Register', component: RegisterView },
   
    // Les routes protégées
    { 
        path: '/dashboard', 
        name: 'Dashboard', 
        component: DashboardView, 
        meta: { requiresAuth: true, roles: ['FREELANCE','CLIENT','USER'] } 
    },
 {
  path: '/missions',
  name: 'AvailableMissions',
  component: AvailableMissionsview,
  meta: { requiresAuth: true, roles: ['FREELANCE'] }
},
{
  path: '/missions/:id',
  name: 'MissionDetails',
  component: MissionDetailsView,
  meta: { requiresAuth: true, roles: ['FREELANCE'] }
},
{
  path: '/missions/:id/apply',
  name: 'ApplyMission',
  component: ApplyMissionView,
  meta: { requiresAuth: true, roles: ['FREELANCE'] }
},
{
  path: '/missions/create',
  name: 'CreateMission',
  component: CreateMissionView,
  meta: { requiresAuth: true, roles: ['CLIENT'] }
},
{
  path: '/portfolio',
  name: 'PORTFOLIO',
  component: PortfolioView,
  meta: {requiresAuth: true,role: ['CLIENT']}
},
  {
  path: '/client/missions',
  name: 'ClientMissions',
  component: ClientMissionView,
  meta: { requiresAuth: true, roles: ['CLIENT'] }
  }, 
  {
  path: '/client/missions/:id',
  name: 'ClientMissionDetails',
  component: ClientMissionDetailView,
  meta: { requiresAuth: true, roles: ['CLIENT'] }
}
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
});

// Guard de Navigation GLOBAL
router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore();

    // ✅ Charger le user UNE SEULE FOIS
    if (!authStore.userLoaded) {
        await authStore.profile();   // profile() ne throw plus → pas de boucle
    }

    const isAuthenticated = authStore.isAuthenticated;
    const requiredAuth = to.meta.requiresAuth;
    const requiredRoles = to.meta.roles;

    // ✅ Si la route nécessite une auth mais user pas connecté
    if (requiredAuth && !isAuthenticated) {
        return next({ name: 'Login' });
    }

    // ✅ Si la route nécessite un rôle mais user pas chargé
    if (requiredRoles && (!authStore.user || !requiredRoles.includes(authStore.user.role))) {
        return next({ name: 'Home' });
    }

    // ✅ Toujours appeler next()
    next();
});
export default router;