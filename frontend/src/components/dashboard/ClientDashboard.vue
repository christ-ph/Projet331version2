<script setup>
import { useAuthStore } from '@/stores/auth';
import { ref } from 'vue';

const authStore = useAuthStore();

/* ✅ MOCK DATA — à remplacer plus tard par ton backend */
const stats = ref({
  missions_created: 4,
  applications_received: 12,
  active_missions: 2,
});

const missions = ref([
  {
    id: 1,
    title: "Développement d'une application mobile",
    status: "En cours",
    proposals: 5,
  },
  {
    id: 2,
    title: "Création d'un site e-commerce",
    status: "En attente",
    proposals: 2,
  },
]);

const applications = ref([
  {
    id: 1,
    mission: "Développement d'une API Flask",
    freelancer: "Jean Dupont",
    status: "En attente",
  },
  {
    id: 2,
    mission: "Refonte d’un site vitrine",
    freelancer: "Marie Kamga",
    status: "Acceptée",
  },
]);
</script>

<template>
  <div class="dashboard-container">

    <!-- ✅ HEADER -->
    <header class="dashboard-header">
      <h2>Bienvenue, {{ authStore.user.email }}</h2>
      <p class="subtitle">Voici un aperçu de votre activité client</p>
    </header>

    <!-- ✅ STATS -->
    <section class="stats-grid">
      <div class="stat-card">
        <h3>{{ stats.missions_created }}</h3>
        <p>Missions créées</p>
      </div>

      <div class="stat-card">
        <h3>{{ stats.active_missions }}</h3>
        <p>Missions actives</p>
      </div>

      <div class="stat-card">
        <h3>{{ stats.applications_received }}</h3>
        <p>Candidatures reçues</p>
      </div>
    </section>

    <!-- ✅ MISSIONS CRÉÉES -->
    <section class="section">
      <h3 class="section-title">📌 Vos missions</h3>

      <div class="mission-list">
        <div v-for="m in missions" :key="m.id" class="mission-card">
          <h4>{{ m.title }}</h4>
          <p class="status">{{ m.status }}</p>
          <p class="proposals">{{ m.proposals }} propositions</p>
        </div>
      </div>
    </section>

    <!-- ✅ CANDIDATURES -->
    <section class="section">
      <h3 class="section-title">📨 Candidatures reçues</h3>

      <div class="application-list">
        <div v-for="a in applications" :key="a.id" class="application-card">
          <h4>{{ a.mission }}</h4>
          <p class="freelancer">Freelance : {{ a.freelancer }}</p>
          <p class="status" :class="a.status.toLowerCase()">{{ a.status }}</p>
        </div>
      </div>
    </section>

    <!-- ✅ BOUTON CRÉER MISSION -->
    <section class="section">
      <button class="create-btn">Créer une nouvelle mission</button>
    </section>

  </div>
</template>

<style scoped>
/* ✅ Layout général */
.dashboard-container {
  width: 100%;
  max-width: 900px;
  margin: auto;
  padding: 20px;
  font-family: sans-serif;
}

/* ✅ Header */
.dashboard-header {
  text-align: center;
  margin-bottom: 30px;
}
.subtitle {
  color: #666;
  font-size: 14px;
}

/* ✅ Stats */
.stats-grid {
  display: flex;
  justify-content: space-between;
  gap: 15px;
  margin-bottom: 30px;
}
.stat-card {
  flex: 1;
  background: #f5f7fa;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
}
.stat-card h3 {
  font-size: 28px;
  margin: 0;
  color: #2c3e50;
}
.stat-card p {
  margin: 5px 0 0;
  color: #555;
}

/* ✅ Sections */
.section {
  margin-bottom: 30px;
}
.section-title {
  margin-bottom: 10px;
  font-size: 20px;
  color: #2c3e50;
}

/* ✅ Missions */
.mission-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.mission-card {
  background: white;
  padding: 15px;
  border-radius: 10px;
  border: 1px solid #eee;
}
.mission-card h4 {
  margin: 0 0 5px;
}
.status {
  color: #3b82f6;
  font-weight: bold;
}
.proposals {
  color: #555;
  font-size: 14px;
}

/* ✅ Applications */
.application-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.application-card {
  background: white;
  padding: 15px;
  border-radius: 10px;
  border: 1px solid #eee;
}
.freelancer {
  color: #374151;
  font-size: 14px;
}
.status.en\ attente {
  color: #f39c12;
}
.status.acceptée {
  color: #27ae60;
}
.status.rejetée {
  color: #e74c3c;
}

/* ✅ Bouton créer mission */
.create-btn {
  padding: 12px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: 0.2s;
}
.create-btn:hover {
  background: #2563eb;
}
</style>
