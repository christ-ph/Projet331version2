<script setup>
import { useAuthStore } from '@/stores/auth';
import { ref } from 'vue';

const authStore = useAuthStore();

/* ✅ MOCK DATA — à remplacer plus tard par ton backend */
const stats = ref({
  missions_available: 12,
  applications_sent: 5,
  portfolio_items: 3,
});

const missions = ref([
  {
    id: 1,
    title: "Développer une API Flask",
    budget: "300€ - 500€",
    skills: ["Python", "Flask", "REST"],
  },
  {
    id: 2,
    title: "Créer un site vitrine Vue.js",
    budget: "200€ - 350€",
    skills: ["Vue.js", "CSS", "Frontend"],
  },
]);

const applications = ref([
  {
    id: 1,
    mission: "Refonte d’un dashboard admin",
    status: "En attente",
  },
  {
    id: 2,
    mission: "Développement d’un chatbot IA",
    status: "Acceptée",
  },
]);
</script>

<template>
  <div class="dashboard-container">

    <!-- ✅ HEADER -->
    <header class="dashboard-header">
      <h2>Bienvenue, {{ authStore.user.email }}</h2>
      <p class="subtitle">Voici un aperçu de votre activité freelance</p>
    </header>

    <!-- ✅ STATS -->
    <section class="stats-grid">
      <div class="stat-card">
        <h3>{{ stats.missions_available }}</h3>
        <p>Missions disponibles</p>
      </div>

      <div class="stat-card">
        <h3>{{ stats.applications_sent }}</h3>
        <p>Candidatures envoyées</p>
      </div>

      <div class="stat-card">
        <h3>{{ stats.portfolio_items }}</h3>
        <p>Éléments du portfolio</p>
      </div>
    </section>

    <!-- ✅ MISSIONS DISPONIBLES -->
    <section class="section">
      <h3 class="section-title">🔥 Missions disponibles</h3>

      <div class="mission-list">
        <div v-for="m in missions" :key="m.id" class="mission-card">
          <h4>{{ m.title }}</h4>
          <p class="budget">{{ m.budget }}</p>
          <div class="skills">
            <span v-for="s in m.skills" :key="s" class="skill">{{ s }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ✅ CANDIDATURES -->
    <section class="section">
      <h3 class="section-title">📌 Vos candidatures</h3>

      <div class="application-list">
        <div v-for="a in applications" :key="a.id" class="application-card">
          <h4>{{ a.mission }}</h4>
          <p class="status" :class="a.status.toLowerCase()">{{ a.status }}</p>
        </div>
      </div>
    </section>

    <!-- ✅ PORTFOLIO -->
    <section class="section">
      <h3 class="section-title">🎨 Portfolio</h3>
      <button class="portfolio-btn">Gérer mon portfolio</button>
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
.budget {
  color: #27ae60;
  font-weight: bold;
}
.skills {
  margin-top: 10px;
}
.skill {
  background: #eef2ff;
  color: #3b5bdb;
  padding: 5px 10px;
  border-radius: 6px;
  margin-right: 5px;
  font-size: 12px;
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
.status {
  font-weight: bold;
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

/* ✅ Portfolio */
.portfolio-btn {
  padding: 10px 20px;
  background: #3b5bdb;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
.portfolio-btn:hover {
  background: #4c6ef5;
}
</style>
