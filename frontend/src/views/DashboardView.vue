<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import router from '@/router';

import ClientDashboard from '@/components/dashboard/ClientDashboard.vue';
import FreelanceDashboard from '@/components/dashboard/FreelanceDashboard.vue';
import CreateProfile from '@/components/dashboard/CreateProfile.vue';

const authStore = useAuthStore();

const loading = ref(true);
const profileExists = ref(false);
const role = ref(null);

onMounted(async () => {
  // 1. Vérifier si l'utilisateur est connecté
  if (!authStore.isAuthenticated) {
    authStore.logout(true);
    return;
  }

  // 2. Charger les infos user + profil
  const result = await authStore.profile();

  role.value = result.user.role;

  if (result.state === "exist") {
    profileExists.value = true;
  } else {
    profileExists.value = false;
  }

  loading.value = false;
});
</script>

<template>
  <div class="dashboard-wrapper">

    <!-- Chargement -->
    <div v-if="loading">Chargement...</div>

    <!-- Pas de profil → afficher CreateProfile -->
    <CreateProfile v-else-if="!profileExists" />

    <!-- Profil existe → afficher dashboard selon rôle -->
    <ClientDashboard v-else-if="role === 'CLIENT'" />

    <FreelanceDashboard v-else-if="role === 'FREELANCE'" />

    <!-- Cas improbable -->
    <div v-else>
      <p>Rôle inconnu. Contactez le support.</p>
    </div>

  </div>
</template>

<style scoped>
.dashboard-wrapper {
  padding: 20px;
}
</style>
