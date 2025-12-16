<template>
  <div class="client-missions-page">
    <div class="header-row">
      <h1>Mes missions</h1>
      <button class="create-btn" @click="router.push('/missions/create')">
        + Nouvelle mission
      </button>
    </div>

    <!-- Chargement -->
    <div v-if="loading" class="loading">
      Chargement des missions...
    </div>

    <!-- Erreur -->
    <div v-if="error" class="error">
      {{ error }}
    </div>

    <!-- Aucune mission -->
    <div
      v-if="!loading && missionsStore.myMissions.length === 0"
      class="no-missions"
    >
      <p>Vous n'avez pas encore créé de mission.</p>
      <button @click="router.push('/missions/create')" class="create-first-btn">
        Créer ma première mission
      </button>
    </div>

    <!-- Liste des missions -->
    <div v-if="missionsStore.myMissions.length > 0" class="missions-container">
      <!-- Filtres -->
      <div class="filters">
        <div class="filter-group">
          <label for="statusFilter">Filtrer par statut :</label>
          <select id="statusFilter" v-model="selectedStatus" @change="filterMissions">
            <option value="">Tous les statuts</option>
            <option value="draft">Brouillons</option>
            <option value="open">Publiées</option>
            <option value="in_progress">En cours</option>
            <option value="completed">Terminées</option>
            <option value="cancelled">Annulées</option>
          </select>
        </div>
        <div class="stats">
          <span class="stat-item">
            <strong>{{ missionsStore.myMissions.length }}</strong> mission(s)
          </span>
          <span v-if="draftCount > 0" class="stat-item draft-stat">
            <strong>{{ draftCount }}</strong> brouillon(s)
          </span>
          <span v-if="publishedCount > 0" class="stat-item published-stat">
            <strong>{{ publishedCount }}</strong> publiée(s)
          </span>
          <span v-if="totalPendingApplications > 0" class="stat-item pending-stat">
            <strong>{{ totalPendingApplications }}</strong> candidature(s) en attente
          </span>
        </div>
      </div>

      <!-- Grid des missions -->
      <div class="missions-grid">
        <div
          v-for="mission in filteredMissions"
          :key="mission.id"
          class="mission-card"
          :class="{
            'draft-card': mission.status === 'draft',
            'published-card': mission.status === 'open',
            'in-progress-card': mission.status === 'in_progress',
            'completed-card': mission.status === 'completed',
            'cancelled-card': mission.status === 'cancelled'
          }"
        >
          <!-- En-tête de la carte -->
          <div class="card-header">
            <div class="mission-title-section">
              <h3 class="mission-title">{{ mission.title }}</h3>
              <div class="status-badges">
                <span class="badge-status" :class="getStatusClass(mission.status)">
                  {{ getStatusText(mission.status) }}
                </span>
                <span 
                  v-if="mission.status === 'open' && mission.postulations_pending > 0" 
                  class="badge-new"
                >
                  {{ mission.postulations_pending }} nouvelle(s)
                </span>
                <span 
                  v-if="mission.postulations_total > 0" 
                  class="badge-total"
                  :class="{'has-pending': mission.postulations_pending > 0}"
                >
                  {{ mission.postulations_total }} candidature(s)
                </span>
              </div>
            </div>
            <div class="mission-dates">
              <span class="date-item" title="Créée le">
                <i class="far fa-calendar-plus"></i>
                {{ formatDate(mission.created_at) }}
              </span>
              <span v-if="mission.updated_at !== mission.created_at" class="date-item" title="Modifiée le">
                <i class="far fa-edit"></i>
                {{ formatDate(mission.updated_at) }}
              </span>
            </div>
          </div>

          <!-- Description -->
          <div class="mission-description">
            <p class="desc">{{ truncateText(mission.description, 150) }}</p>
          </div>

          <!-- Informations détaillées -->
          <div class="mission-info">
            <div class="info-row">
              <div class="info-item">
                <i class="fas fa-money-bill-wave"></i>
                <span><strong>Budget :</strong> {{ mission.budget ? mission.budget + ' €' : 'Non spécifié' }}</span>
              </div>
              <div class="info-item">
                <i class="far fa-clock"></i>
                <span><strong>Deadline :</strong> {{ formatDate(mission.deadline) || 'Non spécifiée' }}</span>
              </div>
            </div>
            <div v-if="mission.required_skills && mission.required_skills.length > 0" class="skills-section">
              <strong>Compétences requises :</strong>
              <div class="skills-tags">
                <span v-for="(skill, index) in mission.required_skills.slice(0, 3)" :key="index" class="skill-tag">
                  {{ skill }}
                </span>
                <span v-if="mission.required_skills.length > 3" class="skill-tag more">
                  +{{ mission.required_skills.length - 3 }}
                </span>
              </div>
            </div>
          </div>

          <!-- Formulaire de modification -->
          <div v-if="editingMission === mission.id" class="edit-form">
            <h4>Modifier la mission</h4>
            <div class="form-group">
              <label>Titre</label>
              <input v-model="editForm.title" type="text" />
            </div>
            <div class="form-group">
              <label>Description</label>
              <textarea v-model="editForm.description"></textarea>
            </div>
            <div class="form-group">
              <label>Budget (€)</label>
              <input v-model.number="editForm.budget" type="number" min="0" />
            </div>
            <div class="form-group">
              <label>Deadline</label>
              <input v-model="editForm.deadline" type="date" />
            </div>
            <div class="form-group">
              <label>Compétences requises (séparées par des virgules)</label>
              <input v-model="editForm.required_skills" type="text" />
            </div>
            <div class="form-actions">
              <button class="btn-save" @click="saveEdit" :disabled="saving">Enregistrer</button>
              <button class="btn-cancel" @click="closeEditForm" :disabled="saving">Annuler</button>
            </div>
          </div>

          <!-- Actions -->
          <div class="mission-actions">
            <div class="primary-action">
              <button
                v-if="mission.status === 'draft'"
                class="btn-publish"
                @click="publishMission(mission.id)"
                :disabled="actionLoading"
              >
                <i class="fas fa-paper-plane"></i> Publier la mission
              </button>
              <button
                v-else-if="mission.status === 'open' && mission.postulations_total > 0"
                class="btn-view-applications"
                @click="goToApplications(mission.id)"
                :disabled="actionLoading"
              >
                <i class="fas fa-users"></i> Gérer les candidatures
              </button>
              <button
                v-else-if="mission.status === 'open'"
                class="btn-view-details"
                @click="goToDetails(mission.id)"
                :disabled="actionLoading"
              >
                <i class="fas fa-eye"></i> Voir détails
              </button>
              <button
                v-else-if="mission.status === 'in_progress'"
                class="btn-in-progress"
                @click="goToDetails(mission.id)"
                :disabled="actionLoading"
              >
                <i class="fas fa-tasks"></i> Suivre la mission
              </button>
              <button
                v-else-if="mission.status === 'completed'"
                class="btn-completed"
                @click="goToDetails(mission.id)"
                :disabled="actionLoading"
              >
                <i class="fas fa-check-circle"></i> Voir le résultat
              </button>
              <button
                v-else-if="mission.status === 'cancelled'"
                class="btn-view-details"
                @click="goToDetails(mission.id)"
                :disabled="actionLoading"
              >
                <i class="fas fa-eye"></i> Voir détails
              </button>
            </div>

            <div class="secondary-actions">
              <button
                v-if="mission.status === 'draft'"
                class="btn-edit"
                @click="openEditForm(mission)"
                :disabled="actionLoading"
              >
                <i class="fas fa-edit"></i> Modifier
              </button>
              
              <button 
                v-if="mission.status === 'in_progress'"
                class="btn-complete-action"
                @click="completeMission(mission.id)"
                :disabled="actionLoading"
              >
                <i class="fas fa-check-circle"></i> Terminer
              </button>
              
              <button 
                v-if="mission.status !== 'completed' && mission.status !== 'cancelled'"
                class="btn-cancel-action"
                @click="cancelMission(mission.id)"
                :disabled="actionLoading"
              >
                <i class="fas fa-times-circle"></i> Annuler
              </button>
              
              <button class="btn-duplicate" @click="duplicateMission(mission.id)" :disabled="actionLoading">
                <i class="fas fa-copy"></i> Dupliquer
              </button>
              
              <button
                class="btn-delete"
                @click="deleteMission(mission.id)"
                :disabled="actionLoading || (mission.status === 'open' && mission.postulations_total > 0) || mission.status === 'in_progress'"
                :title="getDeleteTooltip(mission)"
              >
                <i class="fas fa-trash"></i> Supprimer
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useMissionStore } from '@/stores/missions'
import { useRouter } from 'vue-router'

const missionsStore = useMissionStore()
const router = useRouter()

// États
const selectedStatus = ref('')
const editingMission = ref(null)
const loading = ref(false)
const saving = ref(false)
const actionLoading = ref(false)
const error = ref(null)

const editForm = reactive({
  title: '',
  description: '',
  budget: null,
  deadline: '',
  required_skills: ''
})

// Charger les missions
onMounted(async () => {
  await loadMissions()
})

const loadMissions = async () => {
  loading.value = true
  error.value = null
  try {
    await missionsStore.fetchClientMissions()
  } catch (err) {
    console.error('❌ Erreur lors du chargement:', err)
    error.value = err.response?.data?.error || err.message || 'Erreur de chargement'
  } finally {
    loading.value = false
  }
}

// Computed properties
const draftCount = computed(() => missionsStore.draftMissions.length)
const publishedCount = computed(() => missionsStore.publishedMissions.length)
const totalPendingApplications = computed(() => missionsStore.totalPendingApplications)
const filteredMissions = computed(() => {
  if (!selectedStatus.value) return missionsStore.myMissions
  return missionsStore.myMissions.filter(m => m.status === selectedStatus.value)
})

// Fonctions utilitaires
const formatDate = dateString => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const getStatusText = status => ({
  draft: 'Brouillon',
  open: 'Publiée',
  in_progress: 'En cours',
  completed: 'Terminée',
  cancelled: 'Annulée'
}[status] || status)

const getStatusClass = status => ({
  draft: 'status-draft',
  open: 'status-published',
  in_progress: 'status-in-progress',
  completed: 'status-completed',
  cancelled: 'status-cancelled'
}[status] || 'status-default')

const getDeleteTooltip = mission => {
  if (mission.status === 'open' && mission.postulations_total > 0) return 'Impossible de supprimer une mission publiée avec des candidatures'
  if (mission.status === 'in_progress') return 'Impossible de supprimer une mission en cours'
  return 'Supprimer cette mission'
}

// Actions
const filterMissions = () => {
  // La logique de filtrage est gérée par computed filteredMissions
}

const goToDetails = id => router.push(`/missions/${id}`)

const goToApplications = id => router.push(`/missions/${id}/applications`)

const openEditForm = mission => {
  editingMission.value = mission.id
  editForm.title = mission.title
  editForm.description = mission.description
  editForm.budget = mission.budget
  editForm.deadline = mission.deadline ? mission.deadline.split('T')[0] : ''
  editForm.required_skills = mission.required_skills ? mission.required_skills.join(', ') : ''
}

const closeEditForm = () => {
  editingMission.value = null
  Object.keys(editForm).forEach(key => editForm[key] = '')
}

const saveEdit = async () => {
  saving.value = true
  try {
    const updatedMission = {
      title: editForm.title,
      description: editForm.description,
      budget: editForm.budget,
      deadline: editForm.deadline,
      required_skills: editForm.required_skills.split(',').map(s => s.trim()).filter(s => s)
    }
    
    await missionsStore.updateMission(editingMission.value, updatedMission)
    await loadMissions() // Recharger les données
    alert('Mission mise à jour avec succès !')
    closeEditForm()
  } catch (error) {
    console.error('❌ Erreur lors de la mise à jour:', error)
    alert('Erreur lors de la mise à jour: ' + (error.response?.data?.error || error.message))
  } finally {
    saving.value = false
  }
}

const deleteMission = async id => {
  const mission = missionsStore.myMissions.find(m => m.id === id)
  if (!mission) return
  
  if ((mission.status === 'open' && mission.postulations_total > 0) || mission.status === 'in_progress') {
    alert('Impossible de supprimer cette mission.')
    return
  }
  
  if (!confirm('Êtes-vous sûr de vouloir supprimer cette mission ?')) return
  
  actionLoading.value = true
  try {
    await missionsStore.deleteMission(id)
    await loadMissions() // Recharger les données
    alert('Mission supprimée avec succès !')
  } catch (error) {
    console.error('❌ Erreur lors de la suppression:', error)
    alert('Erreur lors de la suppression: ' + (error.response?.data?.error || error.message))
  } finally {
    actionLoading.value = false
  }
}

const publishMission = async id => {
  const mission = missionsStore.myMissions.find(m => m.id === id)
  if (!mission || mission.status !== 'draft') return
  
  if (!confirm('Voulez-vous publier cette mission ? Elle sera visible par les freelances.')) return
  
  actionLoading.value = true
  try {
    await missionsStore.publishMission(id)
    await loadMissions() // Recharger les données
    alert('Mission publiée avec succès !')
  } catch (error) {
    console.error('❌ Erreur lors de la publication:', error)
    alert('Erreur lors de la publication: ' + (error.response?.data?.error || error.message))
  } finally {
    actionLoading.value = false
  }
}

const completeMission = async id => {
  const mission = missionsStore.myMissions.find(m => m.id === id)
  if (!mission || mission.status !== 'in_progress') return
  
  if (!confirm('Êtes-vous sûr de vouloir marquer cette mission comme complétée ?')) return
  
  actionLoading.value = true
  try {
    await missionsStore.completeMission(id)
    await loadMissions() // Recharger les données
    alert('Mission marquée comme complétée !')
  } catch (error) {
    console.error('❌ Erreur lors de la complétion:', error)
    alert('Erreur lors de la complétion: ' + (error.response?.data?.error || error.message))
  } finally {
    actionLoading.value = false
  }
}

const cancelMission = async id => {
  const mission = missionsStore.myMissions.find(m => m.id === id)
  if (!mission || mission.status === 'completed' || mission.status === 'cancelled') return
  
  if (!confirm('Êtes-vous sûr de vouloir annuler cette mission ? Toutes les candidatures seront annulées.')) return
  
  actionLoading.value = true
  try {
    await missionsStore.cancelMission(id)
    await loadMissions() // Recharger les données
    alert('Mission annulée avec succès !')
  } catch (error) {
    console.error('❌ Erreur lors de l\'annulation:', error)
    alert('Erreur lors de l\'annulation: ' + (error.response?.data?.error || error.message))
  } finally {
    actionLoading.value = false
  }
}

const duplicateMission = async id => {
  const mission = missionsStore.myMissions.find(m => m.id === id)
  if (!mission) return
  
  actionLoading.value = true
  try {
    const duplicateData = {
      title: `${mission.title} (Copie)`,
      description: mission.description,
      budget: mission.budget,
      required_skills: mission.required_skills || [],
      status: 'draft'
    }
    
    await missionsStore.createMission(duplicateData)
    await loadMissions() // Recharger les données
    alert('Mission dupliquée avec succès !')
  } catch (error) {
    console.error('❌ Erreur lors de la duplication:', error)
    alert('Erreur lors de la duplication: ' + (error.response?.data?.error || error.message))
  } finally {
    actionLoading.value = false
  }
}
</script>

<style scoped>
/* Ajoutez ces styles supplémentaires */
.pending-stat {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  border-left: 4px solid #f59e0b;
}

.badge-total.has-pending {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.btn-complete-action {
  background: #10b981;
  color: white;
  border: none;
}

.btn-complete-action:hover:not(:disabled) {
  background: #059669;
}

.btn-complete-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-cancel-action {
  background: #ef4444;
  color: white;
  border: none;
}

.btn-cancel-action:hover:not(:disabled) {
  background: #dc2626;
}

.btn-cancel-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Ajouter une animation pour les boutons en chargement */
button:disabled {
  position: relative;
  overflow: hidden;
}

button:disabled::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  margin: -10px 0 0 -10px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: button-spin 1s linear infinite;
}

@keyframes button-spin {
  to {
    transform: rotate(360deg);
  }
}

/* Styles existants (gardez tout le CSS existant) */
.client-missions-page {
  margin-top: 100px;
  padding: 30px 40px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  min-height: 100vh;
}

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

.create-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 14px 28px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
  display: flex;
  align-items: center;
  gap: 8px;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}


/* =========================
   PAGE
========================= */
.client-missions-page {
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

/* =========================
   BOUTON CRÉER
========================= */
.create-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 14px 28px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
  display: flex;
  align-items: center;
  gap: 8px;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.create-btn:active {
  transform: translateY(0);
}

/* =========================
   PREMIERE MISSION
========================= */
.create-first-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  margin-top: 15px;
  transition: all 0.3s ease;
}

.create-first-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
}

/* =========================
   FILTRES ET STATS
========================= */
.filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-group label {
  font-weight: 600;
  color: #475569;
  font-size: 14px;
}

.filter-group select {
  padding: 10px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  background: white;
  color: #334155;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 180px;
}

.filter-group select:hover {
  border-color: #94a3b8;
}

.filter-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 14px;
  color: #64748b;
}

.stat-item strong {
  color: #1e293b;
  font-size: 16px;
}

.draft-stat {
  border-left: 4px solid #94a3b8;
}

.published-stat {
  border-left: 4px solid #3b82f6;
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
  margin-bottom: 20px;
}

/* =========================
   GRID DES MISSIONS
========================= */
.missions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 28px;
}

/* =========================
   CARTE MISSION
========================= */
.mission-card {
  background: white;
  padding: 28px;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 20px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.mission-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, transparent 0%, currentColor 50%, transparent 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.mission-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.mission-card:hover::before {
  opacity: 1;
}

/* Styles spécifiques par statut */
.draft-card {
  border-color: #e2e8f0;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
}

.draft-card::before {
  color: #94a3b8;
}

.published-card {
  border-color: #dbeafe;
}

.published-card::before {
  color: #3b82f6;
}

.in-progress-card {
  border-color: #fef3c7;
}

.in-progress-card::before {
  color: #f59e0b;
}

.completed-card {
  border-color: #dcfce7;
}

.completed-card::before {
  color: #10b981;
}

.cancelled-card {
  border-color: #fee2e2;
}

.cancelled-card::before {
  color: #ef4444;
}

/* =========================
   EN-TÊTE CARTE
========================= */
.card-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mission-title-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}

.mission-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  line-height: 1.4;
  flex: 1;
  min-width: 200px;
}

.status-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* =========================
   BADGES
========================= */
.badge-status {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border: 2px solid transparent;
}

.status-draft {
  background: #f1f5f9;
  color: #64748b;
  border-color: #e2e8f0;
}

.status-published {
  background: #dbeafe;
  color: #1d4ed8;
  border-color: #93c5fd;
}

.status-in-progress {
  background: #fef3c7;
  color: #92400e;
  border-color: #fcd34d;
}

.status-completed {
  background: #dcfce7;
  color: #166534;
  border-color: #86efac;
}

.status-cancelled {
  background: #fee2e2;
  color: #991b1b;
  border-color: #fca5a5;
}

.badge-new {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 700;
  animation: pulse 2s infinite;
}

.badge-total {
  background: linear-gradient(135deg, #475569 0%, #334155 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 700;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

/* =========================
   DATES
========================= */
.mission-dates {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #64748b;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.date-item i {
  font-size: 12px;
}

/* =========================
   DESCRIPTION
========================= */
.mission-description {
  margin: 8px 0;
}

.desc {
  font-size: 15px;
  color: #475569;
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* =========================
   INFORMATIONS
========================= */
.mission-info {
  background: #f8fafc;
  border-radius: 12px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.info-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
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

/* =========================
   FORMULAIRE DE MODIFICATION
========================= */
.edit-form {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  margin: 16px 0;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.edit-form h4 {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.edit-form h4::before {
  content: '✏️';
  font-size: 16px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.form-group label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, #e2e8f0 0%, transparent 100%);
  margin-left: 8px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  color: #334155;
  background: white;
  transition: all 0.2s ease;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group input:hover,
.form-group textarea:hover {
  border-color: #94a3b8;
}

.form-group textarea {
  min-height: 120px;
  resize: vertical;
  line-height: 1.5;
}

.form-group input[type="number"] {
  -moz-appearance: textfield;
}

.form-group input[type="number"]::-webkit-outer-spin-button,
.form-group input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 2px solid #e2e8f0;
}

.btn-save {
  flex: 1;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 14px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-save:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
}

.btn-save:active {
  transform: translateY(0);
}

.btn-cancel {
  flex: 1;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  color: #64748b;
  padding: 14px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-cancel:hover {
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(100, 116, 139, 0.2);
}

.btn-cancel:active {
  transform: translateY(0);
}

/* =========================
   ACTIONS
========================= */
.mission-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.primary-action {
  width: 100%;
}

.primary-action button {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-publish {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.btn-publish:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
}

.btn-view-applications {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.btn-view-applications:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
}

.btn-view-details {
  background: #e2e8f0;
  color: #475569;
}

.btn-view-details:hover {
  background: #cbd5e1;
  transform: translateY(-2px);
}

.btn-in-progress {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.btn-in-progress:hover {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.3);
}

.btn-completed {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  color: white;
}

.btn-completed:hover {
  background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
  transform: translateY(-2px);
}

/* Actions secondaires */
.secondary-actions {
  display: flex;
  gap: 8px;
}

.secondary-actions button {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-edit {
  background: #fef3c7;
  color: #92400e;
}

.btn-edit:hover {
  background: #fde68a;
  transform: translateY(-1px);
}

.btn-duplicate {
  background: #e0e7ff;
  color: #3730a3;
}

.btn-duplicate:hover {
  background: #c7d2fe;
  transform: translateY(-1px);
}

.btn-delete {
  background: #fee2e2;
  color: #dc2626;
}

.btn-delete:hover:not(:disabled) {
  background: #fecaca;
  transform: translateY(-1px);
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f1f5f9;
  color: #94a3b8;
}

/* =========================
   RESPONSIVE
========================= */
@media (max-width: 1024px) {
  .missions-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
}

@media (max-width: 768px) {
  .client-missions-page {
    margin-top: 80px;
    padding: 20px;
  }
  
  .header-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }
  
  .create-btn {
    width: 100%;
    justify-content: center;
  }
  
  .filters {
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group select {
    width: 100%;
  }
  
  .stats {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .missions-grid {
    grid-template-columns: 1fr;
  }
  
  .info-row {
    flex-direction: column;
    gap: 12px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn-save,
  .btn-cancel {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .client-missions-page {
    padding: 16px;
  }
  
  h1 {
    font-size: 28px;
  }
  
  .mission-card {
    padding: 20px;
  }
  
  .mission-title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .secondary-actions {
    flex-wrap: wrap;
  }
  
  .secondary-actions button {
    flex: 1 0 calc(50% - 4px);
    min-width: 120px;
  }
  
  .edit-form {
    padding: 16px;
  }
  
  .form-group input,
  .form-group textarea {
    padding: 10px 14px;
    font-size: 13px;
  }
}

/* =========================
   ANIMATIONS SUPPLEMENTAIRES
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
   EFFETS DE SURVOL AMELIORES
========================= */
.mission-card:hover .mission-title {
  color: #3b82f6;
  transition: color 0.3s ease;
}

.mission-card:hover .desc {
  color: #334155;
  transition: color 0.3s ease;
}

/* =========================
   STYLE POUR LES ICÔNES FONTAWESOME
========================= */
i {
  transition: transform 0.2s ease;
}

.btn-publish:hover i,
.btn-view-applications:hover i,
.btn-view-details:hover i,
.btn-in-progress:hover i,
.btn-completed:hover i,
.btn-save:hover i,
.btn-cancel:hover i {
  transform: translateX(3px);
}

/* =========================
   SCROLLBAR PERSONNALISEE
========================= */
@media (min-width: 769px) {
  .missions-grid {
    max-height: calc(100vh - 250px);
    overflow-y: auto;
    padding-right: 10px;
  }
  
  .missions-grid::-webkit-scrollbar {
    width: 8px;
  }
  
  .missions-grid::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 4px;
  }
  
  .missions-grid::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 4px;
  }
  
  .missions-grid::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
  }
}

/* =========================
   EFFET DE CHARGEMENT
========================= */
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
  to {
    transform: rotate(360deg);
  }
}

/* =========================
   TRANSITIONS GLOBALES
========================= */
* {
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

/* =========================
   Z-INDEX POUR LES ELEMENTS SUPERPOSES
========================= */
.mission-card {
  z-index: 1;
}

.mission-card:hover {
  z-index: 2;
}

.edit-form {
  z-index: 3;
  position: relative;
}

/* =========================
   MEDIA QUERIES POUR TRES GRANDS ECRANS
========================= */
@media (min-width: 1600px) {
  .missions-grid {
    grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  }
  
  .mission-card {
    padding: 32px;
  }
}
</style>