<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useProfileStore } from '@/stores/profile';
import router from '@/router';

import ClientDashboard from '@/components/dashboard/ClientDashboard.vue';
import FreelanceDashboard from '@/components/dashboard/FreelanceDashboard.vue';
import CreateProfile from '@/components/dashboard/CreateProfile.vue';

const authStore = useAuthStore();
const profileStore = useProfileStore();

const loading = ref(true);
const hasProfile = ref(false);
const role = ref(null);

onMounted(async () => {
  // ✅ 1. Vérifier si l'utilisateur est connecté
  if (!authStore.isAuthenticated || !authStore.user) {
    authStore.logout(true);
    return;
  }

  // ✅ 2. Récupérer le rôle depuis authStore
  role.value = authStore.user.role;

  // ✅ 3. Vérifier si le profil existe
  const profile = await profileStore.getMyProfile();

  hasProfile.value = !!profile;

  loading.value = false;
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

    <!-- ✅ Cas improbable -->
    <div v-else>
      <p>Rôle inconnu. Contactez le support.</p>
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
