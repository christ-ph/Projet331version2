<template>
  <div class="missions-page">

    <div class="header-row">
      <h1>Missions disponibles</h1>
      <button class="reload-btn" @click="reload">Recharger</button>
    </div>

    <!-- Chargement -->
    <div v-if="missionsStore.loading" class="loading">
      Chargement des missions...
    </div>

    <!-- Erreur -->
    <div v-if="missionsStore.error" class="error">
      {{ missionsStore.error }}
    </div>

    <!-- Aucune mission -->
    <div 
      v-if="!missionsStore.loading && missionsStore.missions.length === 0" 
      class="no-missions"
    >
      <p>Aucune mission disponible pour le moment.</p>
    </div>

    <!-- Liste des missions -->
    <div 
      v-if="missionsStore.missions.length > 0" 
      class="missions-grid"
    >
      <div 
        v-for="mission in missionsStore.missions" 
        :key="mission.id" 
        class="mission-card"
      >
        <h3>{{ mission.title }}</h3>

        <p class="desc">{{ mission.description }}</p>

        <div class="info">
          <p><strong>Budget :</strong> {{ mission.budget }} €</p>
          <p><strong>Durée :</strong> {{ mission.duration }}</p>
          <p><strong>Compétences :</strong> {{ mission.required_skills }}</p>
        </div>

        <div class="actions">
          <button class="details-btn" @click="goToDetails(mission.id)">
            Voir détails
          </button>

          <!-- ✅ Masquer si déjà postulé -->
          <button 
            v-if="!alreadyApplied(mission.id)" 
            class="apply-btn" 
            @click="goToApply(mission.id)"
          >
            Postuler
          </button>

          <p v-else class="already-applied">✅ Déjà postulé</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useMissionStore } from '@/stores/missions';
import { useRouter } from 'vue-router';

const missionsStore = useMissionStore();
const router = useRouter();

// ✅ Charger missions + candidatures
onMounted(async () => {
  await missionsStore.fetchAvailableMissions();
  await missionsStore.fetchMyApplications();
});

// ✅ Vérifier si déjà postulé
const alreadyApplied = (missionId) =>
  missionsStore.myApplications.some(app => app.mission_id === missionId);

// Aller vers les détails
function goToDetails(id) {
  router.push(`/missions/${id}`);
}

// Aller vers la page de candidature
function goToApply(id) {
  router.push(`/missions/${id}/apply`);
}

// Recharger la liste
function reload() {
  missionsStore.fetchAvailableMissions();
}
</script>

<style scoped>
.missions-page {
  margin-top: 100px;
  padding: 20px;
  font-family: "Segoe UI", sans-serif;
}

/* ✅ Header */
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

h1 {
  font-size: 28px;
  color: #1f2937;
}

.reload-btn {
  background: #3b82f6;
  color: white;
  padding: 10px 18px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s;
}

.reload-btn:hover {
  background: #2563eb;
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

.no-missions {
  text-align: center;
  margin-top: 40px;
  color: #555;
}

/* ✅ Grille */
.missions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
  gap: 20px;
}

/* ✅ Carte mission */
.mission-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mission-card h3 {
  font-size: 20px;
  color: #1f2937;
}

.desc {
  color: #4b5563;
  font-size: 14px;
}

.info p {
  margin: 4px 0;
  color: #374151;
}

/* ✅ Actions */
.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.details-btn {
  padding: 10px;
  background: #1f2937;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.2s;
}

.details-btn:hover {
  background: #111827;
}

.apply-btn {
  padding: 10px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.2s;
}

.apply-btn:hover {
  background: #059669;
}

.already-applied {
  color: #065f46;
  font-weight: 600;
  padding-top: 10px;
}
</style>
