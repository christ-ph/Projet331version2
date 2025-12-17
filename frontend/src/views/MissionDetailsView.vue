<template>
  <div class="mission-details-page">
    <!-- Chargement -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      Chargement des informations...
    </div>

    <!-- Erreur -->
    <div v-if="error" class="error">
      {{ error }}
    </div>

    <!-- Mission introuvable -->
    <div v-if="!loading && !mission" class="no-mission">
      <p>Mission introuvable.</p>
      <router-link to="/missions" class="back-link">
        ← Retour aux missions
      </router-link>
    </div>

    <!-- Carte des détails -->
    <div v-if="mission" class="mission-details-container">
      <div class="header-section">
        <h1>{{ mission.title }}</h1>
        <div class="mission-meta">
          <span class="mission-date">
            <i class="far fa-calendar-alt"></i>
            Créée le {{ formatDate(mission.created_at) }}
          </span>
          <span class="mission-status" :class="getStatusClass(mission.status)">
            {{ getStatusText(mission.status) }}
          </span>
        </div>
      </div>

      <div class="content-wrapper">
        <!-- Colonne principale -->
        <div class="main-column">
          <!-- Description -->
          <div class="description-section">
            <h2><i class="fas fa-file-alt"></i> Description</h2>
            <div class="description-content">
              {{ mission.description }}
            </div>
          </div>

          <!-- Compétences requises -->
          <div v-if="mission.required_skills && mission.required_skills.length > 0" class="skills-section">
            <h2><i class="fas fa-tools"></i> Compétences requises</h2>
            <div class="skills-list">
              <span 
                v-for="(skill, index) in mission.required_skills" 
                :key="index" 
                class="skill-tag"
              >
                {{ skill }}
              </span>
            </div>
          </div>
        </div>

        <!-- Colonne latérale -->
        <div class="sidebar">
          <!-- Informations clés -->
          <div class="info-card">
            <h3><i class="fas fa-info-circle"></i> Informations</h3>
            
            <div class="info-item">
              <div class="info-label">
                <i class="fas fa-money-bill-wave"></i>
                <span>Budget</span>
              </div>
              <div class="info-value">
                {{ mission.budget ? mission.budget + ' €' : 'Non spécifié' }}
              </div>
            </div>

            <div v-if="mission.deadline" class="info-item">
              <div class="info-label">
                <i class="far fa-clock"></i>
                <span>Date limite</span>
              </div>
              <div class="info-value">
                {{ formatDate(mission.deadline) }}
              </div>
            </div>

            <div v-if="mission.postulations_total > 0" class="info-item">
              <div class="info-label">
                <i class="fas fa-users"></i>
                <span>Candidatures</span>
              </div>
              <div class="info-value">
                {{ mission.postulations_total }}
              </div>
            </div>

            <div class="info-item">
              <div class="info-label">
                <i class="fas fa-user-tie"></i>
                <span>Client</span>
              </div>
              <div class="info-value">
                ID: {{ mission.client_id }}
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="actions-section">
            <!-- Message selon statut -->
            <div v-if="mission.status !== 'open'" class="status-message closed">
              <i class="fas fa-lock"></i>
              Cette mission n'est plus disponible
            </div>

            <div v-else-if="alreadyApplied" class="status-message applied">
              <i class="fas fa-check-circle"></i>
              Vous avez déjà postulé
            </div>

            <!-- Bouton postuler -->
            <button 
              v-else 
              class="apply-btn"
              @click="applyToMission"
              :disabled="applying"
            >
              <i class="fas fa-paper-plane"></i>
              {{ applying ? 'Envoi en cours...' : 'Postuler à cette mission' }}
            </button>

            <!-- Bouton retour -->
            <router-link to="/missions" class="back-btn">
              <i class="fas fa-arrow-left"></i>
              Retour aux missions
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMissionStore } from '@/stores/missions'
import { usePostulationStore } from '@/stores/postulations'

const route = useRoute()
const router = useRouter()
const missionsStore = useMissionStore()
const postulationsStore = usePostulationStore()

const missionId = parseInt(route.params.id)
const loading = ref(false)
const error = ref(null)
const applying = ref(false)

// Mission actuelle
const mission = computed(() => {
  // Chercher dans différentes sources
  return missionsStore.currentMission || 
         missionsStore.getMissionById(missionId) ||
         missionsStore.availableMissions.find(m => m.id === missionId)
})

// Vérifier si déjà postulé
const alreadyApplied = computed(() => {
  if (!postulationsStore.myApplications || postulationsStore.myApplications.length === 0) {
    return false
  }
  
  return postulationsStore.myApplications.some(app => {
    if (app.mission_id) return app.mission_id === missionId
    if (app.mission && app.mission.id) return app.mission.id === missionId
    return false
  })
})

// Charger les données
onMounted(async () => {
  await loadMissionDetails()
})

async function loadMissionDetails() {
  loading.value = true
  error.value = null
  
  try {
    // Charger les détails de la mission
    await missionsStore.fetchMissionDetails(missionId)
    
    // Charger les candidatures de l'utilisateur
    await postulationsStore.fetchMyApplications()
    
    // Vérifier si la mission existe
    if (!missionsStore.currentMission) {
      error.value = 'Mission introuvable'
    }
  } catch (err) {
    console.error('Erreur chargement mission:', err)
    error.value = err.response?.data?.error || 'Erreur lors du chargement'
  } finally {
    loading.value = false
  }
}

// Formatter la date
function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  })
}

// Texte du statut
function getStatusText(status) {
  const statusMap = {
    'draft': 'Brouillon',
    'open': 'Publiée',
    'in_progress': 'En cours',
    'completed': 'Terminée',
    'cancelled': 'Annulée'
  }
  return statusMap[status] || status
}

// Classe CSS pour le statut
function getStatusClass(status) {
  const classMap = {
    'draft': 'status-draft',
    'open': 'status-open',
    'in_progress': 'status-in-progress',
    'completed': 'status-completed',
    'cancelled': 'status-cancelled'
  }
  return classMap[status] || ''
}

// Postuler à la mission
async function applyToMission() {
  if (!mission.value) return
  
  if (alreadyApplied.value) {
    alert('Vous avez déjà postulé à cette mission.')
    return
  }
  
  if (mission.value.status !== 'open') {
    alert('Cette mission n\'est plus disponible.')
    return
  }
  
  if (!confirm('Voulez-vous postuler à cette mission ?')) return
  
  applying.value = true
  
  try {
    // // Demander un message optionnel
    const message = ' '
    
    // Postuler
    await postulationsStore.apply(missionId, message || '')
    
    // Recharger les données
    await postulationsStore.fetchMyApplications()
    
    alert('✅ Candidature envoyée avec succès !')
  } catch (err) {
    console.error('Erreur candidature:', err)
    alert(err.response?.data?.error || 'Erreur lors de la candidature')
  } finally {
    applying.value = false
  }
}
</script>

<style scoped>
/* =========================
   PAGE
========================= */
.mission-details-page {
  margin-top: 100px;
  padding: 30px 40px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  min-height: 100vh;
}

/* =========================
   CHARGEMENT
========================= */
.loading {
  text-align: center;
  padding: 100px;
  font-size: 18px;
  color: #64748b;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* =========================
   ERREUR
========================= */
.error {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: #dc2626;
  padding: 20px;
  border-radius: 12px;
  font-weight: 600;
  margin: 40px auto;
  text-align: center;
  max-width: 600px;
  border-left: 4px solid #dc2626;
}

/* =========================
   MISSION INTROUVABLE
========================= */
.no-mission {
  text-align: center;
  padding: 80px 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  max-width: 600px;
  margin: 40px auto;
}

.no-mission p {
  font-size: 18px;
  color: #64748b;
  margin-bottom: 20px;
}

.back-link {
  display: inline-block;
  padding: 12px 24px;
  background: #3b82f6;
  color: white;
  text-decoration: none;
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.back-link:hover {
  background: #2563eb;
  transform: translateY(-2px);
}

/* =========================
   CONTENEUR PRINCIPAL
========================= */
.mission-details-container {
  max-width: 1200px;
  margin: 0 auto;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* =========================
   EN-TÊTE
========================= */
.header-section {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.header-section h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 20px 0;
  line-height: 1.3;
}

.mission-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 2px solid #f1f5f9;
}

.mission-date {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 14px;
}

.mission-date i {
  color: #94a3b8;
}

.mission-status {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-draft {
  background: #f1f5f9;
  color: #64748b;
}

.status-open {
  background: #dbeafe;
  color: #1d4ed8;
}

.status-in-progress {
  background: #fef3c7;
  color: #92400e;
}

.status-completed {
  background: #dcfce7;
  color: #166534;
}

.status-cancelled {
  background: #fee2e2;
  color: #991b1b;
}

/* =========================
   CONTENU
========================= */
.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 30px;
}

@media (max-width: 1024px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
}

/* =========================
   COLONNE PRINCIPALE
========================= */
.main-column {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.description-section,
.skills-section {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

h2 i {
  color: #3b82f6;
  font-size: 18px;
}

.description-content {
  color: #475569;
  line-height: 1.7;
  font-size: 16px;
  white-space: pre-line;
}

/* =========================
   COMPÉTENCES
========================= */
.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
}

.skill-tag {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #3730a3;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

/* =========================
   SIDEBAR
========================= */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* =========================
   CARTE INFORMATIONS
========================= */
.info-card {
  background: white;
  padding: 25px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

h3 i {
  color: #3b82f6;
  font-size: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #64748b;
  font-size: 14px;
}

.info-label i {
  color: #94a3b8;
  width: 20px;
  text-align: center;
}

.info-value {
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

/* =========================
   ACTIONS
========================= */
.actions-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.status-message {
  padding: 20px;
  border-radius: 12px;
  font-weight: 600;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.status-message i {
  font-size: 18px;
}

.status-message.applied {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  color: #065f46;
}

.status-message.closed {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: #991b1b;
}

.apply-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 18px;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  text-decoration: none;
}

.apply-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
}

.apply-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.back-btn {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  color: #64748b;
  padding: 15px;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  text-decoration: none;
  text-align: center;
}

.back-btn:hover {
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  transform: translateY(-2px);
}

/* =========================
   RESPONSIVE
========================= */
@media (max-width: 768px) {
  .mission-details-page {
    padding: 20px;
    margin-top: 80px;
  }
  
  .header-section {
    padding: 20px;
  }
  
  .header-section h1 {
    font-size: 26px;
  }
  
  .mission-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .description-section,
  .skills-section,
  .info-card {
    padding: 20px;
  }
  
  .content-wrapper {
    gap: 20px;
  }
}

@media (max-width: 480px) {
  .mission-details-page {
    padding: 16px;
  }
  
  .header-section h1 {
    font-size: 24px;
  }
  
  .apply-btn,
  .back-btn {
    padding: 15px;
    font-size: 15px;
  }
}
</style>