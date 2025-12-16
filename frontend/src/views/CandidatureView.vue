<template>
  <div class="my-applications-page">
    <div class="header-row">
      <h1><i class="fas fa-list"></i> Mes candidatures</h1>
      <div class="header-actions">
        <router-link to="/missions/available" class="btn-secondary">
          <i class="fas fa-arrow-left"></i> Retour aux missions
        </router-link>
        <button @click="reload" class="reload-btn">
          <i class="fas fa-sync-alt"></i>
        </button>
      </div>
    </div>

    <!-- Filtres par statut -->
    <div class="status-filters">
      <button 
        v-for="filter in statusFilters" 
        :key="filter.value"
        @click="setStatusFilter(filter.value)"
        :class="{ active: statusFilter === filter.value }"
        class="status-filter-btn"
      >
        {{ filter.label }} ({{ getCountByStatus(filter.value) }})
      </button>
    </div>

    <!-- Chargement -->
    <div v-if="postulationsStore.loading" class="loading-container">
      <div class="spinner"></div>
      <p>Chargement de vos candidatures...</p>
    </div>

    <!-- Erreur -->
    <div v-if="postulationsStore.error" class="error-container">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ postulationsStore.error }}</p>
      <button @click="reload" class="retry-btn">Réessayer</button>
    </div>

    <!-- Aucune candidature -->
    <div 
      v-if="!postulationsStore.loading && filteredApplications.length === 0" 
      class="empty-state"
    >
      <div class="empty-icon">
        <i class="fas fa-file-alt"></i>
      </div>
      <h3>Aucune candidature</h3>
      <p v-if="statusFilter === ''">
        Vous n'avez pas encore postulé à des missions.
      </p>
      <p v-else>
        Aucune candidature avec le statut "{{ getStatusLabel(statusFilter) }}".
      </p>
      <router-link to="/missions/available" class="btn-primary">
        <i class="fas fa-search"></i> Voir les missions disponibles
      </router-link>
    </div>

    <!-- Liste des candidatures -->
    <div 
      v-if="filteredApplications.length > 0 && !postulationsStore.loading" 
      class="applications-list"
    >
      <div 
        v-for="app in filteredApplications" 
        :key="app.id"
        class="application-card"
        :class="app.status"
      >
        <!-- En-tête -->
        <div class="card-header">
          <div class="application-status">
            <span :class="`status-badge ${app.status}`">
              <i :class="getStatusIcon(app.status)"></i>
              {{ getStatusLabel(app.status) }}
            </span>
            <span class="application-date">
              <i class="far fa-calendar"></i>
              Postulé le {{ formatDate(app.created_at) }}
            </span>
          </div>
          <button 
            @click="cancelApplication(app.id)"
            v-if="app.status === 'pending'"
            class="cancel-btn"
            :disabled="cancellingApp === app.id"
          >
            <i class="fas fa-times"></i>
            Annuler
          </button>
        </div>

        <!-- Mission -->
        <div class="mission-info">
          <h3 class="mission-title">
            <i class="fas fa-briefcase"></i>
            {{ getMissionTitle(app) }}
          </h3>
          
          <div class="mission-details">
            <div class="detail">
              <i class="fas fa-money-bill-wave"></i>
              <span>{{ getMissionBudget(app) }}</span>
            </div>
            
            <div v-if="getMissionDeadline(app)" class="detail">
              <i class="far fa-clock"></i>
              <span>Date limite: {{ formatDate(getMissionDeadline(app)) }}</span>
            </div>
          </div>

          <!-- Compétences requises -->
          <div v-if="getMissionSkills(app)?.length" class="skills-section">
            <div class="skills-label">
              <i class="fas fa-tools"></i>
              <span>Compétences requises</span>
            </div>
            <div class="skills-tags">
              <span 
                v-for="(skill, index) in getMissionSkills(app).slice(0, 3)" 
                :key="index" 
                class="skill-tag"
              >
                {{ skill }}
              </span>
              <span 
                v-if="getMissionSkills(app).length > 3" 
                class="skill-tag more"
              >
                +{{ getMissionSkills(app).length - 3 }}
              </span>
            </div>
          </div>
        </div>

        <!-- Client -->
        <div v-if="getClientInfo(app)" class="client-info">
          <div class="client-label">
            <i class="fas fa-user-tie"></i>
            <span>Client</span>
          </div>
          <p class="client-name">
            {{ getClientName(app) }}
          </p>
        </div>

        <!-- Actions -->
        <div class="card-actions">
          <button 
            @click="viewMission(getMissionId(app))"
            class="btn-details"
            :disabled="!getMissionId(app)"
          >
            <i class="fas fa-eye"></i>
            Voir la mission
          </button>
        </div>
      </div>
    </div>

    <!-- Statistiques -->
    <div 
      v-if="filteredApplications.length > 0 && !postulationsStore.loading" 
      class="stats-summary"
    >
      <div class="stat-item">
        <span class="stat-value">{{ filteredApplications.length }}</span>
        <span class="stat-label">Candidature(s)</span>
      </div>
      <div 
        v-for="stat in statusStats" 
        :key="stat.status"
        class="stat-item"
      >
        <span class="stat-value">{{ stat.count }}</span>
        <span class="stat-label">{{ stat.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePostulationStore } from '@/stores/postulations'

const router = useRouter()
const postulationsStore = usePostulationStore()

// États
const statusFilter = ref('')
const cancellingApp = ref(null)

// Filtres de statut
const statusFilters = [
  { value: '', label: 'Toutes' },
  { value: 'pending', label: 'En attente' },
  { value: 'accepted', label: 'Acceptées' },
  { value: 'rejected', label: 'Rejetées' },
  { value: 'cancelled', label: 'Annulées' }
]

// Chargement initial
onMounted(async () => {
  console.log('📱 Composant MyApplications monté')
  await loadData()
})

const loadData = async () => {
  console.log('📱 Chargement des candidatures...')
  try {
    await postulationsStore.fetchMyApplications()
    console.log('📱 Candidatures chargées:', postulationsStore.myApplications)
  } catch (error) {
    console.error('❌ Erreur chargement candidatures:', error)
  }
}

// Candidatures filtrées
const filteredApplications = computed(() => {
  if (!postulationsStore.myApplications || postulationsStore.myApplications.length === 0) {
    console.log('📱 Aucune candidature à filtrer')
    return []
  }
  
  let apps = postulationsStore.myApplications
  
  // Filtrer par statut
  if (statusFilter.value) {
    apps = apps.filter(app => app.status === statusFilter.value)
  }
  
  console.log('📱 Candidatures filtrées:', apps.length)
  return apps
})

// Statistiques par statut
const statusStats = computed(() => {
  const stats = {}
  
  statusFilters.forEach(filter => {
    if (filter.value) {
      stats[filter.value] = {
        count: getCountByStatus(filter.value),
        label: filter.label
      }
    }
  })
  
  return Object.values(stats)
})

// Compter par statut
const getCountByStatus = (status) => {
  if (!postulationsStore.myApplications || postulationsStore.myApplications.length === 0) {
    return 0
  }
  
  if (status === '') {
    return postulationsStore.myApplications.length
  }
  
  return postulationsStore.myApplications.filter(app => app.status === status).length
}

// ======================
// FONCTIONS D'ACCÈS AUX DONNÉES
// ======================

// Obtenir l'ID de la mission (support plusieurs formats)
const getMissionId = (app) => {
  if (app.mission_id) return app.mission_id
  if (app.mission?.id) return app.mission.id
  return null
}

// Obtenir le titre de la mission
const getMissionTitle = (app) => {
  if (app.mission?.title) return app.mission.title
  return 'Mission non trouvée'
}

// Obtenir le budget de la mission
const getMissionBudget = (app) => {
  const budget = app.mission?.budget
  if (budget !== undefined && budget !== null) {
    return budget + ' €'
  }
  return 'Budget non spécifié'
}

// Obtenir la date limite
const getMissionDeadline = (app) => {
  return app.mission?.deadline || null
}

// Obtenir les compétences
const getMissionSkills = (app) => {
  return app.mission?.required_skills || []
}

// Obtenir les infos client
const getClientInfo = (app) => {
  return app.client || null
}

// Obtenir le nom du client
const getClientName = (app) => {
  if (!app.client) return 'Client'
  
  if (app.client.fullname) return app.client.fullname
  if (app.client.company_name) return app.client.company_name
  
  return 'Client'
}

// Obtenir l'icône du statut
const getStatusIcon = (status) => {
  const icons = {
    'pending': 'fas fa-hourglass-half',
    'accepted': 'fas fa-check-circle',
    'rejected': 'fas fa-times-circle',
    'cancelled': 'fas fa-ban'
  }
  return icons[status] || 'fas fa-question-circle'
}

// Obtenir le label du statut
const getStatusLabel = (status) => {
  const labels = {
    'pending': 'En attente',
    'accepted': 'Acceptée',
    'rejected': 'Rejetée',
    'cancelled': 'Annulée'
  }
  return labels[status] || status
}

// Formater la date
const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  } catch (e) {
    return dateString
  }
}

// Définir le filtre de statut
const setStatusFilter = (status) => {
  statusFilter.value = status
}

// Voir la mission
const viewMission = (missionId) => {
  if (missionId) {
    router.push(`/missions/${missionId}`)
  } else {
    alert('ID de mission non disponible')
  }
}

// Annuler une candidature
const cancelApplication = async (appId) => {
  if (!confirm('Voulez-vous vraiment annuler cette candidature ?')) return
  
  cancellingApp.value = appId
  
  try {
    // À implémenter dans votre backend
    await postulationsStore.cancelApplication(appId)
    await loadData() // Recharger après annulation
  } catch (error) {
    console.error('Erreur annulation:', error)
    alert(error.response?.data?.error || 'Erreur lors de l\'annulation')
  } finally {
    cancellingApp.value = null
  }
}

// Recharger
const reload = () => {
  statusFilter.value = ''
  loadData()
}
</script>

<style scoped>
/* =========================
   PAGE
========================= */
.my-applications-page {
  margin-top: 100px;
  padding: 30px 40px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  min-height: calc(100vh - 100px);
}

/* =========================
   HEADER
========================= */
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
}

h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.btn-secondary {
  padding: 12px 24px;
  background: #f1f5f9;
  color: #64748b;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #e2e8f0;
  transform: translateY(-2px);
}

.reload-btn {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.reload-btn:hover {
  transform: rotate(180deg);
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

/* =========================
   FILTRES
========================= */
.status-filters {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.status-filter-btn {
  padding: 10px 20px;
  background: white;
  color: #64748b;
  border: 2px solid #e2e8f0;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.status-filter-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.status-filter-btn.active {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border-color: #3b82f6;
}

/* =========================
   CHARGEMENT
========================= */
.loading-container {
  text-align: center;
  padding: 60px;
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
.error-container {
  background: #fef2f2;
  color: #dc2626;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  border-left: 4px solid #dc2626;
  display: flex;
  align-items: center;
  gap: 15px;
}

.error-container i {
  font-size: 24px;
}

.retry-btn {
  margin-left: auto;
  padding: 8px 16px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

/* =========================
   AUCUNE CANDIDATURE
========================= */
.empty-state {
  margin-top: 60px;
  text-align: center;
  padding: 60px 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
}

.empty-icon {
  font-size: 60px;
  color: #cbd5e1;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 24px;
  color: #1e293b;
  margin-bottom: 10px;
}

.empty-state p {
  font-size: 16px;
  color: #64748b;
  margin-bottom: 20px;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.btn-primary {
  display: inline-block;
  padding: 14px 28px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  max-width: 300px;
  margin: 0 auto;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
}

/* =========================
   LISTE DES CANDIDATURES
========================= */
.applications-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.application-card {
  background: white;
  border-radius: 16px;
  padding: 25px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border-left: 4px solid #cbd5e1;
}

.application-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.application-card.pending {
  border-left-color: #f59e0b;
}

.application-card.accepted {
  border-left-color: #10b981;
}

.application-card.rejected {
  border-left-color: #ef4444;
}

.application-card.cancelled {
  border-left-color: #6b7280;
  opacity: 0.7;
}

/* En-tête de la carte */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.application-status {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: fit-content;
}

.status-badge.pending {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.accepted {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.rejected {
  background: #fee2e2;
  color: #b91c1c;
}

.status-badge.cancelled {
  background: #f3f4f6;
  color: #4b5563;
}

.application-date {
  font-size: 14px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 6px;
}

.cancel-btn {
  padding: 8px 16px;
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.cancel-btn:hover:not(:disabled) {
  background: #fee2e2;
}

.cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Mission info */
.mission-info {
  margin-bottom: 20px;
}

.mission-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.mission-details {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.detail {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #475569;
}

.detail i {
  color: #64748b;
  min-width: 16px;
}

/* Compétences */
.skills-section {
  margin-top: 15px;
}

.skills-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #374151;
  margin-bottom: 8px;
  font-weight: 600;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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

/* Client info */
.client-info {
  padding: 15px;
  background: #f8fafc;
  border-radius: 10px;
  margin-bottom: 20px;
}

.client-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #374151;
  margin-bottom: 8px;
  font-weight: 600;
}

.client-name {
  font-size: 16px;
  color: #1e293b;
  font-weight: 600;
  margin: 0;
}

/* Actions */
.card-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-details {
  padding: 10px 20px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-details:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
}

.btn-details:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  opacity: 0.7;
}

/* Statistiques */
.stats-summary {
  display: flex;
  gap: 20px;
  margin-top: 40px;
  padding-top: 30px;
  border-top: 2px solid #e2e8f0;
  flex-wrap: wrap;
  justify-content: center;
}

.stat-item {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  min-width: 120px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #3b82f6;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 600;
}

/* =========================
   RESPONSIVE
========================= */
@media (max-width: 768px) {
  .my-applications-page {
    margin-top: 80px;
    padding: 20px;
  }
  
  .header-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .btn-secondary,
  .btn-primary {
    width: 100%;
    justify-content: center;
  }
  
  .mission-details {
    flex-direction: column;
    gap: 10px;
  }
  
  .stats-summary {
    flex-direction: column;
    align-items: center;
  }
  
  .stat-item {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .my-applications-page {
    padding: 16px;
  }
  
  .application-card {
    padding: 20px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .cancel-btn {
    align-self: flex-start;
  }
  
  .card-actions {
    justify-content: stretch;
  }
  
  .btn-details {
    width: 100%;
    justify-content: center;
  }
}
</style>