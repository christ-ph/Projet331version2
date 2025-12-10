<template>
  <div class="create-mission-page">
    <h1>Créer une mission</h1>

    <form @submit.prevent="submitMission" class="mission-form">

      <label>Titre</label>
      <input v-model="form.title" required />

      <label>Description</label>
      <textarea v-model="form.description" required></textarea>

      <label>Budget (€)</label>
      <input type="number" v-model="form.budget" required />

      <label>Durée</label>
      <input v-model="form.duration" required />

      <label>Compétences requises</label>
      <input v-model="form.required_skills" required />

      <button type="submit">Créer la mission</button>

      <p v-if="missionsStore.error" class="error">{{ missionsStore.error }}</p>
    </form>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { useMissionStore } from '@/stores/missions';
import { useRouter } from 'vue-router';

const missionsStore = useMissionStore();
const router = useRouter();

const form = reactive({
  title: "",
  description: "",
  budget: "",
  duration: "",
  required_skills: ""
});

async function submitMission() {
  const result = await missionsStore.createMission(form);

  if (result) {
    router.push('/client/missions'); // redirection vers la liste des missions du client
  }
}
</script>

<style scoped>
/* ✅ Page globale */
.create-mission-page {
  margin-top: 100px; /* espace sous le header fixe */
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  font-family: "Segoe UI", sans-serif;
}

/* ✅ Titre */
h1 {
  font-size: 28px;
  margin-bottom: 25px;
  color: #1f2937;
}

/* ✅ Carte du formulaire */
.mission-form {
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

/* ✅ Labels */
label {
  font-weight: 600;
  color: #374151;
}

/* ✅ Inputs */
input,
textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 15px;
  transition: 0.2s;
}

input:focus,
textarea:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.2);
}

/* ✅ Textarea */
textarea {
  min-height: 120px;
  resize: vertical;
}

/* ✅ Bouton */
button {
  padding: 12px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: 0.2s;
  font-weight: 600;
}

button:hover {
  background: #2563eb;
}

/* ✅ Message d’erreur */
.error {
  color: #dc2626;
  font-weight: 600;
  margin-top: 10px;
  text-align: center;
}
</style>
