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
      v-if="!missionsStore.loading && missionsStore.availableMissions.length === 0"
      class="no-missions"
    >
      <p>Aucune mission disponible pour le moment.</p>
      <p class="hint">Les missions apparaissent ici lorsqu'elles sont publiées par les clients.</p>
    </div>

    <!-- Liste -->
    <div
      v-if="missionsStore.availableMissions.length > 0"
      class="missions-grid"
    >
      <div
        v-for="mission in missionsStore.availableMissions"
        :key="mission.id"
        class="mission-card"
        :class="{ 'applied-card': isApplied(mission.id) }"
      >
        <div class="card-header">
          <h3>{{ mission.title }}</h3>
          <div class="badges">
            <span v-if="mission.status === 'open'" class="badge-open">
              Publiée
            </span>
            <span v-if="isApplied(mission.id)" class="badge-applied">
              Déjà postulé
            </span>
          </div>
        </div>

        <p class="desc">{{ truncateText(mission.description, 120) }}</p>

        <div class="info">
          <div class="info-item">
            <i class="fas fa-money-bill-wave"></i>
            <span><strong>Budget :</strong> {{ mission.budget ? mission.budget + ' €' : 'Non défini' }}</span>
          </div>
          
          <div v-if="mission.deadline" class="info-item">
            <i class="far fa-calendar-alt"></i>
            <span><strong>Date limite :</strong> {{ formatDate(mission.deadline) }}</span>
          </div>

          <div v-if="mission.required_skills?.length" class="skills-section">
            <strong>Compétences :</strong>
            <div class="skills-tags">
              <span 
                v-for="(skill, index) in mission.required_skills.slice(0, 3)" 
                :key="index" 
                class="skill-tag"
              >
                {{ skill }}
              </span>
              <span 
                v-if="mission.required_skills.length > 3" 
                class="skill-tag more"
              >
                +{{ mission.required_skills.length - 3 }}
              </span>
            </div>
          </div>
          
          <div v-if="mission.postulations_total > 0" class="applications-info">
            <i class="fas fa-users"></i>
            <span>{{ mission.postulations_total }} candidature(s)</span>
          </div>
        </div>

        <div class="actions">
          <button
            class="details-btn"
            @click="goToDetails(mission.id)"
          >
            <i class="fas fa-eye"></i> Détails
          </button>

          <button
            class="apply-btn"
            @click="applyToMission(mission.id)"
            :disabled="isApplied(mission.id) || missionsStore.loading"
            :class="{ 'disabled': isApplied(mission.id) }"
          >
            <i class="fas fa-paper-plane"></i>
            {{ isApplied(mission.id) ? 'Déjà postulé' : 'Postuler' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useMissionStore } from '@/stores/missions'
import { usePostulationStore } from '@/stores/postulations'
import { useRouter } from 'vue-router'

const missionsStore = useMissionStore()
const postulationsStore = usePostulationStore()
const router = useRouter()

// État pour suivre les missions en cours de candidature
const applyingMission = ref(null)

onMounted(async () => {
  await loadData()
})

// Charger les données
const loadData = async () => {
  try {
    // Charger les missions disponibles
    await missionsStore.fetchAvailableMissions()
    
    // Charger mes candidatures si je suis un freelance
    await postulationsStore.fetchMyApplications()
  } catch (error) {
    console.error('Erreur chargement données:', error)
  }
}

// Formater la date
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

// Tronquer le texte
const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// Vérifier si l'utilisateur a déjà postulé
const isApplied = (missionId) => {
  if (!postulationsStore.myApplications || postulationsStore.myApplications.length === 0) {
    return false
  }
  
  // Vérifier selon la structure des données
  return postulationsStore.myApplications.some(app => {
    // Selon la structure de vos données
    if (app.mission_id) return app.mission_id === missionId
    if (app.mission && app.mission.id) return app.mission.id === missionId
    return false
  })
}

// Voir les détails d'une mission
const goToDetails = (id) => {
  router.push(`/missions/${id}`)
}

// Postuler à une mission
const applyToMission = async (id) => {
  if (isApplied(id)) {
    alert('Vous avez déjà postulé à cette mission.')
    return
  }
  
  if (!confirm('Voulez-vous postuler à cette mission ?')) return
  
  applyingMission.value = id
  
  try {
    // Demander un message optionnel
    const message = prompt('Message optionnel pour le client (laisser vide si aucun) :', '')
    
    // Appeler le store de postulations
    await postulationsStore.apply(id, message || '')
    
    // Recharger les données
    await loadData()
    
    alert('✅ Candidature envoyée avec succès !')
  } catch (error) {
    console.error('Erreur candidature:', error)
    alert(error.response?.data?.error || 'Erreur lors de la candidature')
  } finally {
    applyingMission.value = null
  }
}

// Recharger les missions
const reload = () => {
  loadData()
}
</script>

<style scoped>
/* =========================
   PAGE
========================= */
.missions-page {
  margin-top: 100px;
  padding: 30px 40px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  min-height: 100vh;
}

/* =========================
   HEADER
========================= */
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e2e8f0;
}

h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.reload-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
  display: flex;
  align-items: center;
  gap: 8px;
}

.reload-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.reload-btn:active {
  transform: translateY(0);
}

/* =========================
   CHARGEMENT / ERREUR
========================= */
.loading {
  text-align: center;
  padding: 60px;
  font-size: 18px;
  color: #64748b;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.loading::after {
  content: '';
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: #dc2626;
  padding: 20px;
  border-radius: 12px;
  font-weight: 600;
  margin-bottom: 30px;
  text-align: center;
  border-left: 4px solid #dc2626;
}

/* =========================
   AUCUNE MISSION
========================= */
.no-missions {
  margin-top: 60px;
  text-align: center;
  padding: 60px 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
}

.no-missions p {
  font-size: 18px;
  color: #64748b;
  margin-bottom: 10px;
}

.no-missions .hint {
  font-size: 14px;
  color: #94a3b8;
  font-style: italic;
}

/* =========================
   GRID DES MISSIONS
========================= */
.missions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 28px;
}

/* =========================
   CARTE MISSION
========================= */
.mission-card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid #dbeafe;
  position: relative;
  overflow: hidden;
}

.mission-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.12);
}

.mission-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
  opacity: 0.8;
}

.applied-card {
  border-color: #dcfce7;
  background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
}

.applied-card::before {
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
}

/* =========================
   EN-TÊTE CARTE
========================= */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.card-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  line-height: 1.4;
  flex: 1;
}

.badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.badge-open {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-applied {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* =========================
   DESCRIPTION
========================= */
.desc {
  font-size: 14px;
  color: #475569;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 63px; /* 3 lignes * 1.5 * 14px */
}

/* =========================
   INFORMATIONS
========================= */
.info {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #475569;
}

.info-item i {
  color: #64748b;
  font-size: 14px;
  min-width: 16px;
  text-align: center;
}

.info-item strong {
  color: #334155;
  margin-right: 4px;
}

/* Compétences */
.skills-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.skills-section strong {
  color: #334155;
  font-size: 14px;
  margin-bottom: 4px;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.skill-tag {
  background: #e2e8f0;
  color: #475569;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.skill-tag.more {
  background: #cbd5e1;
  color: #334155;
  font-weight: 600;
}

/* Informations candidatures */
.applications-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.applications-info i {
  color: #f59e0b;
  font-size: 12px;
}

/* =========================
   ACTIONS
========================= */
.actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.actions button {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.details-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.details-btn:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
}

.apply-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.apply-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
}

.apply-btn.disabled {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
  cursor: not-allowed;
  opacity: 0.7;
}

.apply-btn.disabled:hover {
  transform: none;
  box-shadow: none;
}

/* =========================
   ANIMATIONS
========================= */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.mission-card {
  animation: fadeIn 0.5s ease-out;
}

.mission-card:nth-child(1) { animation-delay: 0.1s; }
.mission-card:nth-child(2) { animation-delay: 0.2s; }
.mission-card:nth-child(3) { animation-delay: 0.3s; }
.mission-card:nth-child(4) { animation-delay: 0.4s; }
.mission-card:nth-child(5) { animation-delay: 0.5s; }

/* =========================
   RESPONSIVE
========================= */
@media (max-width: 1024px) {
  .missions-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}

@media (max-width: 768px) {
  .missions-page {
    margin-top: 80px;
    padding: 20px;
  }
  
  .header-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }
  
  .reload-btn {
    width: 100%;
    justify-content: center;
  }
  
  .missions-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .missions-page {
    padding: 16px;
  }
  
  h1 {
    font-size: 28px;
  }
  
  .mission-card {
    padding: 20px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .actions button {
    width: 100%;
  }
}

/* =========================
   EFFETS ICÔNES
========================= */
i {
  transition: transform 0.2s ease;
}

.details-btn:hover i,
.apply-btn:hover:not(.disabled) i {
  transform: translateX(3px);
}
</style>