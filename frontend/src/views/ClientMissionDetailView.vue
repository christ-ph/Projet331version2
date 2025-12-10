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
    <div v-if="!missionsStore.loading && !mission" class="no-mission">
      <p>Mission introuvable.</p>
    </div>

    <!-- ✅ Détails de la mission -->
    <div v-if="mission" class="mission-card">
      <h2>{{ mission.title }}</h2>

      <p class="description">{{ mission.description }}</p>

      <div class="info-block">
        <p><span class="label">Budget :</span> {{ mission.budget }} €</p>
        <p><span class="label">Durée :</span> {{ mission.duration }}</p>
        <p><span class="label">Compétences :</span> {{ mission.required_skills }}</p>
      </div>

      <!-- ✅ Si un freelance est déjà assigné -->
      <div v-if="mission.assigned_freelance_id" class="assigned-box">
        ✅ Freelance assigné : {{ assignedFreelancerName }}
        <button class="chat-btn" @click="openChat">Ouvrir le chat</button>
      </div>
    </div>

    <!-- ✅ Candidatures reçues -->
    <div v-if="applications.length > 0" class="applications-section">
      <h2>Candidatures reçues</h2>

      <div class="applications-grid">
        <div v-for="app in applications" :key="app.id" class="application-card">

          <!-- ✅ HEADER AVEC PHOTO + NOM + BADGE -->
          <div class="header-app">
            <img :src="app.photo" class="avatar" />

            <div class="freelancer-info">
              <h3>{{ app.freelancer_name }}</h3>

              <p class="rating">
                ⭐ {{ app.rating }} / 5  
                <span class="missions-count">({{ app.completed_missions }} missions)</span>
              </p>

              <p class="skills">{{ app.skills }}</p>
            </div>

            <!-- ✅ Badge statut -->
            <span v-if="app.status === 'PENDING'" class="badge-pending">Nouveau</span>
            <span v-if="app.status === 'ACCEPTED'" class="badge-accepted">Accepté</span>
            <span v-if="app.status === 'REJECTED'" class="badge-rejected">Refusé</span>
          </div>

          <!-- ✅ BIO -->
          <p class="bio">{{ app.bio }}</p>

          <!-- ✅ LETTRE DE MOTIVATION -->
          <p class="cover">{{ app.proposal }}</p>

          <p><strong>Proposition :</strong> {{ app.proposed_budget }} €</p>

          <!-- ✅ PORTFOLIO (aperçu factice si non géré) -->
          <div class="portfolio-preview">
            <h4>Portfolio</h4>
            <ul>
              <li v-for="item in app.portfolio" :key="item.id">
                {{ item.title }}
              </li>
            </ul>
          </div>

          <!-- ✅ Bouton voir profil -->
          <button class="profile-btn" @click="goToProfile(app.freelance_id)">
            Voir profil complet
          </button>

          <!-- ✅ Actions -->
          <div class="actions" v-if="mission.status === 'PUBLISHED'">
            <button 
              class="accept-btn" 
              @click="accept(app.id)"
              :disabled="mission.assigned_freelance_id"
            >
              Accepter
            </button>

            <button 
              class="reject-btn" 
              @click="reject(app.id)"
              :disabled="mission.assigned_freelance_id"
            >
              Refuser
            </button>
          </div>

        </div>
      </div>
    </div>

    <!-- ✅ Aucune candidature -->
    <div v-if="applications.length === 0 && mission" class="no-applications">
      <p>Aucune candidature reçue pour le moment.</p>
    </div>

  </div>
</template>


<script setup>
import { ref, onMounted, computed } from 'vue';
import { useMissionStore } from '@/stores/missions';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const missionsStore = useMissionStore();
const route = useRoute();
const router = useRouter();

const missionId = route.params.id;
const applications = ref([]);
const freelancerProfiles = ref({});

// ✅ Charger mission + candidatures + profils freelances
onMounted(async () => {
  await missionsStore.fetchMissionDetails(missionId);
  await missionsStore.fetchMissionApplications(missionId);

  applications.value = missionsStore.applications;

  for (const app of applications.value) {
    const res = await axios.get(`/api/profiles/${app.freelance_id}`);

    // ✅ Données réelles
    const profile = res.data;

    // ✅ Données factices (à remplacer par backend plus tard)
    profile.rating = 4.7; // ⭐ Factice
    profile.completed_missions = 12; // Factice
    profile.photo = "https://i.pravatar.cc/150?img=" + app.freelance_id; // Factice
    profile.portfolio = profile.portfolio || [
      { id: 1, title: "Projet Web — Landing Page" },
      { id: 2, title: "Application Mobile — React Native" }
    ];

    freelancerProfiles.value[app.freelance_id] = profile;

    // ✅ Injecter dans l'objet app
    app.freelancer_name = profile.full_name;
    app.bio = profile.bio;
    app.skills = profile.skills;
    app.rating = profile.rating;
    app.completed_missions = profile.completed_missions;
    app.photo = profile.photo;
    app.portfolio = profile.portfolio;
  }
});

// ✅ Mission actuelle
const mission = computed(() => missionsStore.missionDetails);

// ✅ Nom du freelance assigné
const assignedFreelancerName = computed(() => {
  if (!mission.value?.assigned_freelance_id) return null;
  return freelancerProfiles.value[mission.value.assigned_freelance_id]?.full_name;
});

// ✅ Accepter une candidature
async function accept(id) {
  await missionsStore.acceptApplication(id);
  await missionsStore.fetchMissionDetails(missionId);
  await missionsStore.fetchMissionApplications(missionId);
  applications.value = missionsStore.applications;
}

// ✅ Refuser une candidature
async function reject(id) {
  await missionsStore.rejectApplication(id);
  await missionsStore.fetchMissionApplications(missionId);
  applications.value = missionsStore.applications;
}

// ✅ Voir profil complet
function goToProfile(id) {
  router.push(`/profiles/${id}`);
}

// ✅ Ouvrir le chat
function openChat() {
  router.push(`/chat/${missionId}`);
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

/* ✅ TITRE PRINCIPAL */
h1 {
  font-size: 32px;
  margin-bottom: 30px;
  color: #111827;
  font-weight: 700;
}

/* ✅ CARTE MISSION */
.mission-card {
  background: white;
  padding: 30px;
  border-radius: 14px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
  width: 100%;
  max-width: 750px;
  margin-bottom: 40px;
  animation: fadeIn 0.3s ease-in-out;
}

.mission-card h2 {
  font-size: 26px;
  color: #1f2937;
  font-weight: 700;
}

.description {
  color: #4b5563;
  line-height: 1.7;
  margin-top: 12px;
  font-size: 15px;
}

/* ✅ BLOC D’INFOS */
.info-block {
  background: #f3f4f6;
  padding: 18px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  margin-top: 20px;
}

.info-block p {
  margin: 8px 0;
  color: #374151;
  font-size: 15px;
}

.label {
  font-weight: 600;
  color: #111827;
}

/* ✅ FREELANCE ASSIGNÉ */
.assigned-box {
  margin-top: 25px;
  padding: 15px;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  border-radius: 10px;
  color: #065f46;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-btn {
  padding: 8px 14px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s;
}

.chat-btn:hover {
  background: #2563eb;
}

/* ✅ SECTION CANDIDATURES */
.applications-section {
  width: 100%;
  max-width: 900px;
}

.applications-section h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #1f2937;
  font-weight: 700;
}

/* ✅ GRILLE DES CANDIDATURES */
.applications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
  gap: 20px;
}

/* ✅ CARTE CANDIDATURE */
.application-card {
  background: white;
  padding: 22px;
  border-radius: 12px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.08);
  animation: fadeIn 0.3s ease-in-out;
}

.header-app {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.application-card h3 {
  font-size: 18px;
  color: #111827;
  font-weight: 600;
}

/* ✅ BADGES */
.badge-pending {
  background: #f59e0b;
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.badge-accepted {
  background: #10b981;
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.badge-rejected {
  background: #ef4444;
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

/* ✅ LETTRE DE MOTIVATION */
.cover {
  color: #4b5563;
  margin: 12px 0;
  font-size: 14px;
  line-height: 1.6;
}

/* ✅ BOUTONS ACTIONS */
.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 18px;
}

.accept-btn {
  background: #10b981;
  color: white;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s;
}

.accept-btn:hover {
  background: #059669;
}

.reject-btn {
  background: #ef4444;
  color: white;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s;
}

.reject-btn:hover {
  background: #dc2626;
}

/* ✅ MESSAGES */
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
  color: #6b7280;
  font-size: 17px;
}

/* ✅ ANIMATION */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
