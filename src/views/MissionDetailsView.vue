<template>
  <div class="mission-details-page">

    <!-- Titre -->
    <h1>Détails de la mission</h1>

    <!-- Chargement -->
    <div v-if="missionsStore.loading" class="loading">
      Chargement des informations...
    </div>

    <!-- Erreur -->
    <div v-if="missionsStore.error" class="error">
      {{ missionsStore.error }}
    </div>

    <!-- Mission introuvable -->
    <div 
      v-if="!missionsStore.loading && !missionsStore.missionDetails" 
      class="no-mission"
    >
      <p>Mission introuvable.</p>
    </div>

    <!-- Carte des détails -->
    <div 
      v-if="missionsStore.missionDetails" 
      class="mission-card"
    >
      <h2>{{ missionsStore.missionDetails.title }}</h2>

      <p class="description">{{ missionsStore.missionDetails.description }}</p>

      <div class="info-block">
        <p><span class="label">Budget :</span> {{ missionsStore.missionDetails.budget }} €</p>
        <p><span class="label">Durée :</span> {{ missionsStore.missionDetails.duration }}</p>
        <p><span class="label">Compétences :</span> {{ missionsStore.missionDetails.required_skills }}</p>
      </div>

      <button class="apply-btn" @click="goToApply">
        Postuler à cette mission
      </button>
    </div>

  </div>
</template>

<script setup>
import { useMissionStore } from '@/stores/missions';
import { useRoute, useRouter } from 'vue-router';

const missionsStore = useMissionStore();
const route = useRoute();
const router = useRouter();

const missionId = route.params.id;

// Charger les détails
missionsStore.fetchMissionDetails(missionId);

function goToApply() {
  router.push(`/missions/${missionId}/apply`);
}
</script>

<style scoped>
/* ✅ Page globale */
.mission-details-page {
  margin-top: 100px;
  padding: 20px;
  font-family: "Segoe UI", sans-serif;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* ✅ Titre */
h1 {
  font-size: 30px;
  margin-bottom: 25px;
  color: #1f2937;
}

/* ✅ Carte */
.mission-card {
  background: white;
  padding: 30px;
  border-radius: 14px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 650px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ✅ Sous-titre */
.mission-card h2 {
  font-size: 24px;
  color: #111827;
}

/* ✅ Description */
.description {
  color: #4b5563;
  line-height: 1.6;
  font-size: 15px;
}

/* ✅ Bloc d’infos */
.info-block {
  background: #f9fafb;
  padding: 15px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
}

.info-block p {
  margin: 6px 0;
  font-size: 15px;
  color: #374151;
}

.label {
  font-weight: 600;
  color: #1f2937;
}

/* ✅ Bouton Postuler */
.apply-btn {
  padding: 12px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s;
}

.apply-btn:hover {
  background: #059669;
}

/* ✅ Messages */
.loading {
  font-size: 18px;
  color: #555;
}

.error {
  color: #dc2626;
  font-weight: bold;
  margin-bottom: 20px;
}

.no-mission {
  margin-top: 40px;
  color: #555;
  font-size: 18px;
}
</style>
