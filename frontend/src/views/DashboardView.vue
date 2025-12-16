<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useProfileStore } from '@/stores/profile';

import ClientDashboard from '@/components/dashboard/ClientDashboard.vue';
import FreelanceDashboard from '@/components/dashboard/FreelanceDashboard.vue';
import CreateProfile from '@/components/dashboard/CreateProfile.vue';

const authStore = useAuthStore();
const profileStore = useProfileStore();
const router = useRouter();

const loading = ref(true);
const hasProfile = ref(false);
const role = ref(null);

onMounted(async () => {
  // ✅ 1. Vérifier si l'utilisateur est connecté
  if (!authStore.isAuthenticated || !authStore.user) {
    // ✅ Déconnecter proprement et rediriger
    authStore.logout();
    router.push('/login');
    return;
  }

  // ✅ 2. Récupérer le rôle depuis authStore
  role.value = authStore.user.role;

  // ✅ 3. Vérifier si le profil existe
  try {
    const profile = await profileStore.getMyProfile();
    hasProfile.value = !!profile;
  } catch (error) {
    console.error('Erreur lors de la récupération du profil:', error);
    // Si erreur 401, l'intercepteur Axios a déjà géré la déconnexion
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="dashboard-wrapper">
    <!-- ✅ Chargement -->
    <div v-if="loading" class="loading">
      Chargement du tableau de bord...
    </div>

    <!-- ✅ Pas de profil → afficher CreateProfile -->
    <CreateProfile v-else-if="!hasProfile" />

    <!-- ✅ Profil existe → afficher dashboard selon rôle -->
    <ClientDashboard v-else-if="role === 'CLIENT'" />
    <FreelanceDashboard v-else-if="role === 'FREELANCE'" />

    <!-- ✅ Cas improbable (rôle USER sans profil ne devrait pas arriver ici) -->
    <div v-else>
      <p>Rôle inconnu. Veuillez créer un profil.</p>
    </div>
  </div>
</template>

<style scoped>
.dashboard-wrapper {
  padding: 20px;
}

.loading {
  text-align: center;
  font-size: 18px;
  padding: 40px;
}
</style>