import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import DashboardView from '../views/DashboardView.vue';
import AvailableMissionsview from '../views/AvailableMissionView.vue';
import MissionDetailsView from '@/views/MissionDetailsView.vue';
import CreateMissionView from '@/views/CreateMissionView.vue';
import ClientMissionView from '@/views/ClientMissionView.vue';
import ClientMissionDetailView from '@/views/ClientMissionDetailView.vue';
import ApplyMissionView from '@/views/ApplyMissionView.vue';
import ProfileFreeView from '@/views/ProfilesFreelance.vue';
import { useAuthStore } from '@/stores/auth';

const routes = [
  { path: '/', name: 'Home', component: HomeView },
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/register', name: 'Register', component: RegisterView },
  
  // Routes protégées
  { 
    path: '/dashboard', 
    name: 'Dashboard', 
    component: DashboardView, 
    meta: { requiresAuth: true, roles: ['FREELANCE', 'CLIENT', 'USER'] } 
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
    path: '/freelance-profile',
    name: 'PROFILES',
    component: ProfileFreeView,
    meta: { requiresAuth: true, roles: ['FREELANCE'] }
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

// Guard de navigation
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const requiresAuth = to.meta.requiresAuth;
  const requiredRoles = to.meta.roles;

  // Si la route nécessite une authentification
  if (requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'Login' });
  }

  // Si la route nécessite un rôle spécifique
  if (requiredRoles && !requiredRoles.includes(authStore.userRole)) {
    return next({ name: 'Home' });
  }

  next();
});

export default router;