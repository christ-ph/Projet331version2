<template>
  <div class="client-missions-page">

    <div class="header-row">
      <h1>Mes missions</h1>
      <button class="create-btn" @click="router.push('/missions/create')">
        + Nouvelle mission
      </button>
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
      <p>Vous n'avez pas encore créé de mission.</p>
      <button @click="router.push('/missions/create')" class="create-btn">
        Créer ma première mission
      </button>
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
        <div class="header-mission">
          <h3>{{ mission.title }}</h3>

          <!-- ✅ Badge candidatures -->
          <span 
            v-if="applicationsCount[mission.id] > 0" 
            class="badge"
          >
            {{ applicationsCount[mission.id] }} candidature(s)
          </span>

          <span 
            v-if="pendingCount[mission.id] > 0" 
            class="badge-new"
          >
            Nouveau !
          </span>
        </div>

        <p class="desc">{{ mission.description }}</p>

        <div class="info">
          <p><strong>Budget :</strong> {{ mission.budget }} €</p>
          <p><strong>Durée :</strong> {{ mission.duration }}</p>
          <p><strong>Compétences :</strong> {{ mission.required_skills }}</p>
        </div>

        <button 
          class="details-btn"
          @click="goToDetails(mission.id)"
        >
          Voir détails
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { onMounted, reactive } from 'vue';
import { useMissionStore } from '@/stores/missions';
import { useRouter } from 'vue-router';

const missionsStore = useMissionStore();
const router = useRouter();

// ✅ Stockage local du nombre de candidatures
const applicationsCount = reactive({});
const pendingCount = reactive({});

onMounted(async () => {
  await missionsStore.fetchClientMissions();

  // ✅ Pour chaque mission → charger ses candidatures
  for (const mission of missionsStore.missions) {
    await missionsStore.fetchMissionApplications(mission.id);

    const apps = missionsStore.applications;

    applicationsCount[mission.id] = apps.length;
    pendingCount[mission.id] = apps.filter(a => a.status === "PENDING").length;
  }
});

function goToDetails(id) {
  router.push(`/client/missions/${id}`);
}
</script>

<style scoped>
.client-missions-page {
  margin-top: 100px;
  padding: 20px;
  font-family: "Segoe UI", sans-serif;
}

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

.create-btn {
  background: #3b82f6;
  color: white;
  padding: 10px 18px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s;
}

.create-btn:hover {
  background: #2563eb;
}

.missions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.mission-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.header-mission {
  display: flex;
  align-items: center;
  gap: 10px;
}

.badge {
  background: #1f2937;
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
}

.badge-new {
  background: #dc2626;
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: bold;
}

.details-btn {
  margin-top: 10px;
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
</style>
