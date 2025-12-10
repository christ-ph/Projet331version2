<template>
  <div class="apply-page">

    <h1>Postuler à la mission</h1>

    <!-- ✅ Détails de la mission -->
    <div v-if="mission" class="mission-details-card">
      <h2>{{ mission.title }}</h2>

      <p class="desc">{{ mission.description }}</p>

      <div class="info">
        <p><strong>Budget :</strong> {{ mission.budget }} €</p>
        <p><strong>Durée :</strong> {{ mission.duration }}</p>
        <p><strong>Compétences :</strong> {{ mission.required_skills }}</p>
      </div>
    </div>

    <!-- Chargement -->
    <div v-if="missionsStore.loading" class="loading">
      Envoi de la candidature...
    </div>

    <!-- Erreur -->
    <div v-if="missionsStore.error" class="error">
      {{ missionsStore.error }}
    </div>

    <!-- Formulaire -->
    <form v-if="!submitted" @submit.prevent="submit" class="apply-form">

      <label>Lettre de motivation</label>
      <textarea v-model="form.proposal" required></textarea>

      <label>Budget proposé (€)</label>
      <input type="number" v-model="form.proposed_budget" required />

      <button type="submit" class="submit-btn">Envoyer ma candidature</button>
    </form>

    <!-- Confirmation -->
    <div v-if="submitted" class="success">
      ✅ Votre candidature a été envoyée avec succès !
      <button @click="goBack">Retour aux missions</button>
    </div>

  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from 'vue';
import { useMissionStore } from '@/stores/missions';
import { useRoute, useRouter } from 'vue-router';

const missionsStore = useMissionStore();
const route = useRoute();
const router = useRouter();

const missionId = route.params.id;
const submitted = ref(false);

const form = reactive({
  proposal: "",
  proposed_budget: ""
});

// ✅ Charger les détails de la mission
onMounted(async () => {
  await missionsStore.fetchMissionDetails(missionId);
});

const mission = computed(() => missionsStore.missionDetails);

async function submit() {
  try {
    await missionsStore.applyToMission(missionId, form);
    submitted.value = true;
  } catch (err) {
    console.error("Erreur lors de la candidature :", err);
  }
}

function goBack() {
  router.push('/missions');
}
</script>

<style scoped>
.apply-page {
  margin-top: 100px;
  padding: 20px;
  font-family: "Segoe UI", sans-serif;
  display: flex;
  flex-direction: column;
  align-items: center;
}

h1 {
  font-size: 28px;
  margin-bottom: 25px;
  color: #1f2937;
}

/* ✅ Carte détails mission */
.mission-details-card {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 650px;
  margin-bottom: 30px;
}

.mission-details-card h2 {
  font-size: 22px;
  color: #1f2937;
  margin-bottom: 10px;
}

.desc {
  color: #4b5563;
  margin-bottom: 15px;
}

.info p {
  margin: 4px 0;
  color: #374151;
}

/* ✅ Formulaire */
.apply-form {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 550px;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

label {
  font-weight: 600;
  color: #374151;
}

textarea,
input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 15px;
  transition: 0.2s;
}

textarea:focus,
input:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.2);
}

textarea {
  min-height: 120px;
  resize: vertical;
}

.submit-btn {
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

.submit-btn:hover {
  background: #059669;
}

/* ✅ Confirmation */
.success {
  background: #ecfdf5;
  padding: 20px;
  border-radius: 10px;
  border: 1px solid #a7f3d0;
  color: #065f46;
  font-size: 16px;
  text-align: center;
  max-width: 450px;
}

.success button {
  margin-top: 15px;
  padding: 10px 15px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.success button:hover {
  background: #2563eb;
}

.error {
  color: #dc2626;
  font-weight: bold;
  margin-bottom: 20px;
}
</style>
