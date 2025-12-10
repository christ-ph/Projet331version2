<template>
  <div class="client-mission-details-page">

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

    <!-- Détails de la mission -->
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
    </div>

    <!-- Candidatures reçues -->
    <div 
      v-if="applications.length > 0" 
      class="applications-section"
    >
      <h2>Candidatures reçues</h2>

      <div class="applications-grid">
        <div 
          v-for="app in applications" 
          :key="app.id" 
          class="application-card"
        >
          <h3>{{ app.freelancer_name }}</h3>

          <p class="cover">{{ app.cover_letter }}</p>

          <p><strong>Proposition :</strong> {{ app.proposed_budget }} €</p>

          <div class="actions">
            <button class="accept-btn" @click="accept(app.id)">Accepter</button>
            <button class="reject-btn" @click="reject(app.id)">Refuser</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Aucune candidature -->
    <div 
      v-if="applications.length === 0 && missionsStore.missionDetails" 
      class="no-applications"
    >
      <p>Aucune candidature reçue pour le moment.</p>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useMissionStore } from '@/stores/missions';
import { useRoute } from 'vue-router';

const missionsStore = useMissionStore();
const route = useRoute();

const missionId = route.params.id;
const applications = ref([]);

// Charger mission + candidatures
onMounted(async () => {
  await missionsStore.fetchMissionDetails(missionId);

  const res = await missionsStore.fetchMissionApplications(missionId);
  applications.value = missionsStore.applications;
});

// Accepter une candidature
async function accept(id) {
  await missionsStore.acceptApplication(id);
  applications.value = applications.value.filter(a => a.id !== id);
}

// Refuser une candidature
async function reject(id) {
  await missionsStore.rejectApplication(id);
  applications.value = applications.value.filter(a => a.id !== id);
}
</script>

<style scoped>
.client-mission-details-page {
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

/* ✅ Carte mission */
.mission-card {
  background: white;
  padding: 30px;
  border-radius: 14px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 650px;
  margin-bottom: 40px;
}

.mission-card h2 {
  font-size: 24px;
  color: #111827;
}

.description {
  color: #4b5563;
  line-height: 1.6;
  margin-top: 10px;
}

.info-block {
  background: #f9fafb;
  padding: 15px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  margin-top: 20px;
}

.info-block p {
  margin: 6px 0;
  color: #374151;
}

.label {
  font-weight: 600;
  color: #1f2937;
}

/* ✅ Section candidatures */
.applications-section {
  width: 100%;
  max-width: 900px;
}

.applications-section h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #1f2937;
}

.applications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
  gap: 20px;
}

/* ✅ Carte candidature */
.application-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.application-card h3 {
  font-size: 18px;
  color: #111827;
}

.cover {
  color: #4b5563;
  margin: 10px 0;
  font-size: 14px;
}

/* ✅ Actions */
.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
}

.accept-btn {
  background: #10b981;
  color: white;
  padding: 8px 14px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.2s;
}

.accept-btn:hover {
  background: #059669;
}

.reject-btn {
  background: #ef4444;
  color: white;
  padding: 8px 14px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.2s;
}

.reject-btn:hover {
  background: #dc2626;
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

.no-mission,
.no-applications {
  margin-top: 40px;
  color: #555;
  font-size: 18px;
}
</style>
