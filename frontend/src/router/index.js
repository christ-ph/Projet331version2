// src/router/index.js - CORRIGÉ
import { createRouter, createWebHistory } from 'vue-router';

// Vues principales
import HomeView from '@/views/HomeView.vue';
import LoginView from '@/views/LoginView.vue';
import RegisterView from '@/views/RegisterView.vue';
import DashboardView from '@/views/DashboardView.vue';
import MyDeliverablesView from '@/views/MyDeliverablesView.vue';
import ManageDeliverablesView from '@/views/ManageDeliverablesView.vue';
import ChatView from '@/views/ChatView.vue';


// Vues Freelance
import AvailableMissionsView from '@/views/AvailableMissionView.vue';
import MissionDetailsView from '@/views/MissionDetailsView.vue';
import ApplyMissionView from '@/views/ApplyMissionView.vue';
import CandidatureView from '@/views/CandidatureView.vue';
import ProfilesFreelance from '@/views/ProfilesFreelance.vue';

// Vues Client
import CreateMissionView from '@/views/CreateMissionView.vue';
import ClientMissionsView from '@/views/ClientMissionView.vue';
import ClientMissionDetailView from '@/views/ClientMissionDetailView.vue';
import ManageApplicationsView from '@/views/ManageApplicationsView.vue';
import ProfilesClient from '@/views/ProfilesClient.vue';


// Vues Admin
import AdminDashboardView from '@/views/admin/AdminDashboardView.vue';
import AdminLoginView from '@/views/AdminLoginView.vue';
import AdminRegisterFormView from '@/views/AdminRegisterFormView.vue';


// Store Auth pour le guard
import { useAuthStore } from '@/stores/auth';
import { useProfileStore } from '@/stores/profile';


const routes = [
  // Routes publiques
  { 
    path: '/', 
    name: 'Home', 
    component: HomeView,
    meta: { title: 'Accueil - Plateforme Freelance' }
  },
  { 
    path: '/login', 
    name: 'Login', 
    component: LoginView,
    meta: { 
      requiresGuest: true, // ✅ NOUVEAU: empêche les utilisateurs connectés d'accéder
      title: 'Connexion'
    }
  },
  { 
    path: '/register', 
    name: 'Register', 
    component: RegisterView,
    meta: { 
      requiresGuest: true, // ✅ NOUVEAU: empêche les utilisateurs connectés d'accéder
      title: 'Inscription'
    }
  },

  // Dashboard (auth toutes roles)
  { 
    path: '/dashboard', 
    name: 'Dashboard', 
    component: DashboardView, 
     meta: { 
       requiresAuth: true, 
       title: 'Tableau de bord'
     }
  },
  // chat
  {
    path:'/chat/:id',
    name:'chatView',
    component:ChatView,
    meta:{
      requiresAuth:true,
      title:'Messagerie'
    }

  },

  // Routes Freelance
  {
    path: '/missions',
    name: 'AvailableMissions',
    component: AvailableMissionsView,
    meta: { 
      requiresAuth: true, 
      requiresRole: 'FREELANCE', // ✅ NOUVEAU: plus spécifique
      title: 'Missions Disponibles'
    }
  },
  {
    path: '/missions/:id',
    name: 'MissionDetails',
    component: MissionDetailsView,
    meta: { 
      requiresAuth: true, 
      requiresRole: 'FREELANCE',
      title: 'Détails Mission'
    }
  },
  {
    path: '/missions/:id/apply',
    name: 'ApplyMission',
    component: ApplyMissionView,
    meta: { 
      requiresAuth: true, 
      requiresRole: 'FREELANCE',
      title: 'Postuler à une Mission'
    }
  },
    {
    path: '/applications',
    name: 'candidatureView',
    component: CandidatureView,
    meta: { 
      requiresAuth: true, 
      requiresRole: 'FREELANCE',
      title: 'Mission postulées'
    }
  },
  {
    path: '/freelance-profile',
    name: 'ProfileFreelance',
    component: ProfilesFreelance,
    meta: { 
      requiresAuth: true, 
      requiresRole: 'FREELANCE',
      title: 'Profils Freelance'
    }
  },
  // Routes Client
  {
    path: '/missions/create',
    name: 'CreateMission',
    component: CreateMissionView,
    meta: { 
      requiresAuth: true, 
      requiresRole: 'CLIENT',
      title: 'Créer une Mission'
    }
  },
  {
    path: '/client/missions',
    name: 'ClientMissions',
    component: ClientMissionsView,
    meta: { 
      requiresAuth: true, 
      requiresRole: 'CLIENT',
      title: 'Mes Missions'
    }
  },
  {
    path: '/client/missions/:id',
    name: 'ClientMissionDetails',
    component: ClientMissionDetailView,
    meta: { 
      requiresAuth: true, 
      requiresRole: 'CLIENT',
      title: 'Détails Mission Client'
    }
  },
  {
    path: '/client-profile',
    name: 'PROFILECLIENT',
    component: ProfilesClient,
    meta: { 
      requiresAuth: true,
      title: 'Profils Client',
      requiresRole: 'CLIENT'
    }
  },
  {
    path: '/missions/:id/applications',
    name: 'manage-applications',
    component: ManageApplicationsView,
    meta: { requiresAuth: true, requiresRole: 'CLIENT' }
  },
{
  path: '/admin/dashboard',
  name: 'AdminDashboard',
  component: AdminDashboardView,
  meta: { 
    requiresAuth: true, 
    requiresRole: 'ADMIN',
    title: 'Tableau de bord Admin'
  }
},
{
  path: 'admin/login',
  name: 'AdminLogin',
  component: AdminLoginView,
  meta: { 
    requiresGuest: true,
    title: 'Connexion Admin'
  }
},
{
  path: 'admin/register',
  name: 'AdminRegister',
  component: AdminRegisterFormView,
  meta: { 
    requiresGuest: true,
    title: "Inscription Admin"
  }
},
  // Route 404
  {
    path: '/:catchAll(.*)',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: 'Page non trouvée' }
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// Gestion du titre de page
router.beforeEach((to) => {
  document.title = to.meta.title || 'Plateforme Freelance'
})

// Guard de navigation global
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  
  // Récupérer les métadonnées
  const requiresAuth = to.meta.requiresAuth;
  const requiresGuest = to.meta.requiresGuest;
  const requiresRole = to.meta.requiresRole;
  const allowedRoles = to.meta.roles;

  // ✅ 1. Gestion des routes pour invités (login, register)
  if (requiresGuest) {
    if (authStore.isAuthenticated) {
      // Utilisateur déjà connecté → rediriger vers dashboard
      return next({ name: 'Dashboard' });
    }
    return next();
  }

  // ✅ 2. Vérification si la route nécessite une authentification
  if (requiresAuth) {
    // Si non authentifié, rediriger vers login avec redirect
    if (!authStore.isAuthenticated) {
      return next({ 
        name: 'Login', 
        query: { redirect: to.fullPath } 
      });
    }

    // ✅ CORRECTION ICI: Utiliser getProfile() au lieu de profile()
    // Charger le profil utilisateur s'il n'est pas déjà chargé
    if (!authStore.userLoaded && authStore.isAuthenticated) {
      try {

        const profileStore = useProfileStore();
        await profileStore.getMyProfile(); // ✅ LA BONNE MÉTHODE
      } catch (error) {
        console.error('Erreur chargement profil:', error);
        // En cas d'erreur, déconnecter et rediriger
        authStore.logout(false);
        return next({ name: 'Login' });
      }
    }

    // ✅ 3. Vérification des rôles (ancienne méthode avec roles array)
    if (allowedRoles && allowedRoles.length > 0) {
      const userRole = authStore.user?.role?.name || authStore.user?.role;
      
      if (!userRole || !allowedRoles.includes(userRole)) {
        // Rôle non autorisé → rediriger vers page d'accueil
        console.warn(`Accès refusé: ${userRole} n'a pas accès à cette route`);
        return next({ name: 'Home' });
      }
    }

    // ✅ 4. Vérification des rôles (nouvelle méthode avec requiresRole)
    if (requiresRole) {
      const userRole = authStore.user?.role?.name || authStore.user?.role;
      
      if (!userRole) {
        console.warn('Rôle utilisateur non défini');
        return next({ name: 'Home' });
      }
      
      // Normaliser les rôles pour la comparaison
      const userRoleUpper = userRole.toUpperCase();
      const requiredRoleUpper = requiresRole.toUpperCase();
      
      if (userRoleUpper !== requiredRoleUpper) {
        // Rôle incorrect → rediriger vers le dashboard approprié
        if (authStore.isClient) {
          return next({ name: 'Dashboard' });
        } else if (authStore.isFreelance) {
          return next({ name: 'Dashboard' });
        }
        return next({ name: 'Home' });
      }
    }

    // ✅ 5. Tout est bon, autoriser l'accès
    return next();
  }

  // ✅ 6. Routes publiques (pas de requiresAuth)
  next();
});

// Intercepteur pour les erreurs de navigation
router.onError((error, to, from) => {
  console.error('Erreur navigation:', error);
  
  // Si c'est une erreur de chargement de module, recharger la page
  if (error.message.includes('Failed to fetch dynamically imported module')) {
    window.location.reload();
  }
});

export default router;
