<script setup>
import { defineProps } from 'vue';
import { RouterLink } from 'vue-router';

// On utilise defineProps pour typer ce qui vient de la vue parente
const props = defineProps({
  user: {
    type: Object,
    required: true
  }
});

const isFreelance = props.user.role === 'FREELANCE';
const isClient = props.user.role === 'CLIENT';

// Les messages dynamiques
const welcomeSubtitle = isFreelance 
  ? 'Prêt à trouver votre prochaine mission ?' 
  : 'Trouvez le talent parfait pour votre projet.';
</script>

<template>
    <div class="dashboard-header">
      <div class="welcome-section">
        <h1>Tableau de bord</h1>
        <p class="welcome-message">Bon retour, <strong>{{ user.email }}</strong> !</p>
        <p class="welcome-subtitle">
          {{ welcomeSubtitle }}
        </p>
      </div>
      
      <div class="header-actions">
        <RouterLink 
          v-if="isFreelance" 
          to="/freelance-profile" 
          class="btn btn-primary"
        >
          ✨ Compléter mon profil
        </RouterLink>
        
        <RouterLink 
          :to="isClient ? '/missions-client' : '/missions'" 
          class="btn btn-secondary"
        >
          {{ isClient ? 'Gérer mes missions' : '📋 Voir les missions' }}
        </RouterLink>

      </div>
    </div>
</template>

<style scoped>

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  /* ... (autres styles) ... */
}
/* ... (Votre CSS du header) ... */
</style>