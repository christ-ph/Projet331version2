<template>
  <div class="missions-page">
    <div class="header-row">
      <h1>Missions disponibles</h1>
      <div class="header-actions">
        <button class="my-deliverables-btn" @click="goToMyDeliverables">
          <i class="fas fa-file-alt"></i> Mes livrables
        </button>
        
        <button class="my-applications-btn" @click="goToMyApplications">
          <i class="fas fa-list"></i> Mes candidatures
        </button>
        
        <button class="reload-btn" @click="reload">
          <i class="fas fa-sync-alt"></i> Recharger
        </button>
      </div>
    </div>

    <!-- Chargement -->
    <div v-if="missionsStore.loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Chargement des missions...</p>
    </div>

    <!-- Erreur -->
    <div v-if="missionsStore.error" class="error-state">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ missionsStore.error }}</p>
      <button @click="reload" class="retry-btn">Réessayer</button>
    </div>

    <!-- Aucune mission -->
    <div
      v-if="!missionsStore.loading && !missionsStore.error && missionsStore.availableMissions.length === 0"
      class="empty-state"
    >
      <div class="empty-icon">📋</div>
      <h3>Aucune mission disponible</h3>
      <p class="empty-message">
        Aucune mission n'est disponible pour le moment. Revenez plus tard pour découvrir de nouvelles opportunités.
      </p>
      <button @click="reload" class="refresh-btn">
        <i class="fas fa-redo"></i> Vérifier les nouvelles missions
      </button>
    </div>

    <!-- Liste des missions -->
    <div v-if="missionsStore.availableMissions.length > 0" class="missions-grid">
      <div
        v-for="mission in missionsStore.availableMissions"
        :key="mission.id"
        class="mission-card"
        :class="{ 
          'applied-card': isApplied(mission.id),
          'assigned-card': isAssignedToMe(mission)
        }"
      >
        <div class="card-header">
          <div class="mission-title-section">
            <h3 class="mission-title">{{ mission.title }}</h3>
            <div class="mission-status">
              <span v-if="mission.status === 'open'" class="badge badge-open">
                <i class="fas fa-bullhorn"></i> Publiée
              </span>
              <span v-if="mission.status === 'in_progress'" class="badge badge-in-progress">
                <i class="fas fa-tasks"></i> En cours
              </span>
              <span v-if="mission.status === 'completed'" class="badge badge-completed">
                <i class="fas fa-check-circle"></i> Terminée
              </span>
            </div>
          </div>
          
          <div class="user-status">
            <span v-if="isApplied(mission.id)" class="badge badge-applied">
              <i class="fas fa-paper-plane"></i> Déjà postulé
            </span>
            <span v-if="isAssignedToMe(mission)" class="badge badge-assigned">
              <i class="fas fa-star"></i> Assigné à moi
            </span>
          </div>
        </div>

        <p class="mission-description">{{ truncateText(mission.description, 120) }}</p>

        <div class="mission-info">
          <div class="info-grid">
            <div class="info-item">
              <div class="info-icon">
                <i class="fas fa-money-bill-wave"></i>
              </div>
              <div class="info-content">
                <div class="info-label">Budget</div>
                <div class="info-value">{{ mission.budget ? mission.budget + ' €' : 'Non défini' }}</div>
              </div>
            </div>
            
            <div v-if="mission.deadline" class="info-item">
              <div class="info-icon">
                <i class="far fa-calendar-alt"></i>
              </div>
              <div class="info-content">
                <div class="info-label">Date limite</div>
                <div class="info-value">{{ formatDate(mission.deadline) }}</div>
              </div>
            </div>
          </div>

          <!-- Compétences -->
          <div v-if="mission.required_skills?.length" class="skills-section">
            <div class="section-title">
              <i class="fas fa-tools"></i>
              <span>Compétences requises</span>
            </div>
            <div class="skills-tags">
              <span 
                v-for="(skill, index) in mission.required_skills.slice(0, 4)" 
                :key="index" 
                class="skill-tag"
              >
                {{ skill }}
              </span>
              <span 
                v-if="mission.required_skills.length > 4" 
                class="skill-tag skill-tag-more"
              >
                +{{ mission.required_skills.length - 4 }}
              </span>
            </div>
          </div>
          
          <!-- Statistiques candidatures -->
          <div v-if="mission.postulations_total > 0" class="applications-stats">
            <div class="stats-item">
              <i class="fas fa-users"></i>
              <span>{{ mission.postulations_total }} candidature(s)</span>
            </div>
            <div v-if="mission.postulations_pending > 0" class="stats-item">
              <i class="fas fa-clock"></i>
              <span>{{ mission.postulations_pending }} en attente</span>
            </div>
          </div>

          <!-- Section livrables pour missions assignées -->
          <div v-if="isAssignedToMe(mission) && mission.status === 'in_progress'" class="deliverables-section">
            <div class="section-header">
              <div class="section-title">
                <i class="fas fa-file-alt"></i>
                <span>Livrables</span>
              </div>
              <button 
                @click="toggleDeliverables(mission.id)"
                class="toggle-deliverables-btn"
              >
                <i :class="showDeliverables[mission.id] ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                <span>{{ showDeliverables[mission.id] ? 'Masquer' : 'Voir les livrables' }}</span>
              </button>
            </div>

            <!-- Liste des livrables -->
            <div v-if="showDeliverables[mission.id]" class="deliverables-list">
              <!-- Chargement -->
              <div v-if="loadingDeliverables[mission.id]" class="deliverables-loading">
                <div class="small-spinner"></div>
                <span>Chargement des livrables...</span>
              </div>

              <!-- Aucun livrable -->
              <div v-else-if="!missionDeliverables[mission.id] || missionDeliverables[mission.id].length === 0" class="no-deliverables">
                <i class="fas fa-inbox"></i>
                <span>Aucun livrable créé</span>
              </div>

              <!-- Liste des livrables -->
              <div v-else class="deliverables-items">
                <div 
                  v-for="deliverable in missionDeliverables[mission.id]" 
                  :key="deliverable.id" 
                  class="deliverable-item"
                  :class="`status-${deliverable.status}`"
                >
                  <div class="deliverable-header">
                    <div class="deliverable-title">
                      <strong>{{ deliverable.title }}</strong>
                      <span :class="`status-badge status-${deliverable.status}`">
                        {{ getDeliverableStatusLabel(deliverable.status) }}
                      </span>
                    </div>
                    <div class="deliverable-actions">
                      <button
                        v-if="deliverable.status === 'draft' || deliverable.status === 'needs_revision'"
                        @click="submitDeliverable(deliverable.id, mission.id)"
                        class="action-btn btn-submit"
                        title="Soumettre"
                      >
                        <i class="fas fa-paper-plane"></i>
                      </button>
                      
                      <button
                        v-if="deliverable.status === 'draft'"
                        @click="editDeliverableInline(mission.id, deliverable)"
                        class="action-btn btn-edit"
                        title="Modifier"
                      >
                        <i class="fas fa-edit"></i>
                      </button>
                      
                      <button
                        v-if="deliverable.status === 'draft'"
                        @click="deleteDeliverable(deliverable.id, mission.id)"
                        class="action-btn btn-delete"
                        title="Supprimer"
                      >
                        <i class="fas fa-trash"></i>
                      </button>
                      
                      <button
                        v-if="deliverable.file_url"
                        @click="downloadDeliverableFile(deliverable.id)"
                        class="action-btn btn-download"
                        title="Télécharger"
                      >
                        <i class="fas fa-download"></i>
                      </button>
                    </div>
                  </div>
                  
                  <p class="deliverable-description">{{ truncateText(deliverable.description, 80) }}</p>
                  
                  <div class="deliverable-meta">
                    <span class="meta-date">
                      <i class="far fa-clock"></i>
                      {{ formatRelativeDate(deliverable.created_at) }}
                    </span>
                    <span v-if="deliverable.submitted_at" class="meta-date">
                      <i class="fas fa-paper-plane"></i>
                      Soumis {{ formatRelativeDate(deliverable.submitted_at) }}
                    </span>
                  </div>

                  <!-- Feedback client -->
                  <div v-if="deliverable.client_feedback" class="client-feedback">
                    <i class="fas fa-comment"></i>
                    <span>{{ deliverable.client_feedback }}</span>
                  </div>
                </div>
              </div>

              <!-- Bouton pour créer un nouveau livrable -->
              <div class="add-deliverable-btn-container">
                <button @click="addNewDeliverable(mission.id)" class="btn-add-deliverable">
                  <i class="fas fa-plus"></i>
                  <span>Ajouter un livrable</span>
                </button>
              </div>
            </div>

            <!-- Récapitulatif rapide -->
            <div v-else class="deliverables-summary">
              <div class="summary-stats">
                <div class="stat-item">
                  <div class="stat-value">{{ getDeliverableCountByStatus(mission.id, 'draft') }}</div>
                  <div class="stat-label">Brouillons</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ getDeliverableCountByStatus(mission.id, 'submitted') }}</div>
                  <div class="stat-label">Soumis</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ getDeliverableCountByStatus(mission.id, 'accepted') }}</div>
                  <div class="stat-label">Acceptés</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Message pour mission assignée -->
          <div v-if="isAssignedToMe(mission) && !showDeliverables[mission.id]" class="assigned-notice">
            <div class="notice-icon">
              <i class="fas fa-check-circle"></i>
            </div>
            <div class="notice-content">
              <strong>Mission assignée !</strong>
              <p>Gérez vos livrables directement depuis cette carte.</p>
            </div>
          </div>
        </div>

        <div class="mission-actions">
          <button class="btn btn-details" @click="goToDetails(mission.id)">
            <i class="fas fa-eye"></i>
            <span>Voir détails</span>
          </button>

          <div v-if="isAssignedToMe(mission) && mission.status === 'in_progress'" class="assigned-actions">
            <button @click="toggleDeliverables(mission.id)" class="btn btn-manage-deliverables">
              <i :class="showDeliverables[mission.id] ? 'fas fa-times' : 'fas fa-file-alt'"></i>
              <span>{{ showDeliverables[mission.id] ? 'Fermer' : 'Gérer livrables' }}</span>
            </button>
          </div>
          
          <button
            v-else-if="!isAssignedToMe(mission) && mission.status === 'open'"
            class="btn btn-apply"
            @click="applyToMission(mission.id)"
            :disabled="isApplied(mission.id) || missionsStore.loading"
          >
            <i class="fas fa-paper-plane"></i>
            <span>{{ isApplied(mission.id) ? 'Déjà postulé' : 'Postuler' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useMissionStore } from '@/stores/missions'
import { usePostulationStore } from '@/stores/postulations'
import { useAuthStore } from '@/stores/auth'
import { useDeliverablesStore } from '@/stores/deliverables'
import { useRouter } from 'vue-router'

const missionsStore = useMissionStore()
const postulationsStore = usePostulationStore()
const deliverablesStore = useDeliverablesStore()
const authStore = useAuthStore()
const router = useRouter()

const showDeliverables = ref({})
const loadingDeliverables = ref({})
const applyingMission = ref(null)

const user = computed(() => authStore.user)
const isFreelance = computed(() => user.value?.profile?.type === 'freelance')

const missionDeliverables = computed(() => {
  const result = {}
  missionsStore.availableMissions.forEach(mission => {
    if (mission.deliverables) {
      result[mission.id] = mission.deliverables
    }
  })
  return result
})

onMounted(async () => {
  await loadData()
})

const loadData = async () => {
  try {
    await missionsStore.fetchAvailableMissions()
    
    if (isFreelance.value) {
      await postulationsStore.fetchMyApplications()
    }
  } catch (error) {
    console.error('❌ Erreur chargement données:', error)
  }
}

const isAssignedToMe = (mission) => {
  if (!isFreelance.value || !user.value || !mission.postulations) return false
  
  return mission.postulations.some(
    postulation => 
      postulation.freelance_id === user.value.id && 
      postulation.status === 'accepted'
  )
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  } catch (error) {
    console.error('❌ Erreur formatage date:', error)
    return dateString
  }
}

const formatRelativeDate = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return "aujourd'hui"
    if (diffDays === 1) return "hier"
    if (diffDays < 7) return `il y a ${diffDays} jours`
    if (diffDays < 30) return `il y a ${Math.floor(diffDays / 7)} semaines`
    return `le ${formatDate(dateString)}`
  } catch (error) {
    console.error('❌ Erreur formatage date relative:', error)
    return dateString
  }
}

const truncateText = (text, maxLength) => {
  if (!text) return 'Pas de description'
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength).trim() + '...'
}

const isApplied = (missionId) => {
  if (!isFreelance.value || !postulationsStore.myApplications?.length) {
    return false
  }
  
  return postulationsStore.myApplications.some(app => {
    return (app.mission_id === missionId) || (app.mission?.id === missionId)
  })
}

const getDeliverableStatusLabel = (status) => {
  const labels = {
    draft: 'Brouillon',
    submitted: 'Soumis',
    under_review: 'En review',
    accepted: 'Accepté',
    rejected: 'Rejeté',
    needs_revision: 'Révision demandée'
  }
  return labels[status] || status
}

const getDeliverableCountByStatus = (missionId, status) => {
  if (!missionDeliverables.value[missionId]) return 0
  return missionDeliverables.value[missionId].filter(d => d.status === status).length
}

const toggleDeliverables = async (missionId) => {
  showDeliverables.value[missionId] = !showDeliverables.value[missionId]
  
  if (showDeliverables.value[missionId] && !missionDeliverables.value[missionId]) {
    await fetchMissionDeliverables(missionId)
  }
}

const fetchMissionDeliverables = async (missionId) => {
  loadingDeliverables.value[missionId] = true
  try {
    await deliverablesStore.fetchMissionDeliverables(missionId)
    const missionIndex = missionsStore.availableMissions.findIndex(m => m.id === missionId)
    if (missionIndex !== -1) {
      missionsStore.availableMissions[missionIndex].deliverables = [...deliverablesStore.deliverables]
    }
  } catch (error) {
    console.error('❌ Erreur chargement livrables:', error)
  } finally {
    loadingDeliverables.value[missionId] = false
  }
}

const goToDetails = (id) => {
  router.push(`/missions/${id}`)
}

const goToMyDeliverables = () => {
  router.push('/my-deliverables')
}

const goToMyApplications = () => {
  router.push('/applications')
}

const applyToMission = async (missionId) => {
  if (!isFreelance.value) {
    alert('Seuls les freelances peuvent postuler aux missions.')
    return
  }
  
  if (isApplied(missionId)) {
    alert('Vous avez déjà postulé à cette mission.')
    return
  }
  
  if (!confirm('Voulez-vous postuler à cette mission ?')) return
  
  applyingMission.value = missionId
  
  try {
    await postulationsStore.apply(missionId, '')
    await loadData()
    alert('✅ Candidature envoyée avec succès !')
  } catch (error) {
    console.error('❌ Erreur candidature:', error)
    alert(error.response?.data?.error || 'Erreur lors de la candidature')
  } finally {
    applyingMission.value = null
  }
}

const reload = () => {
  loadData()
}

// Opérations sur les livrables
const addNewDeliverable = (missionId) => {
  router.push({
    name: 'CreateDeliverable',
    params: { missionId }
  })
}

const editDeliverableInline = (missionId, deliverable) => {
  router.push({
    name: 'EditDeliverable',
    params: { 
      missionId,
      deliverableId: deliverable.id
    }
  })
}

const submitDeliverable = async (deliverableId, missionId) => {
  if (!confirm('Soumettre ce livrable pour review par le client ?')) return
  
  try {
    await deliverablesStore.submitDeliverable(deliverableId)
    await fetchMissionDeliverables(missionId)
    alert('✅ Livrable soumis avec succès !')
  } catch (error) {
    console.error('❌ Erreur soumission:', error)
    const errorMsg = error.response?.data?.error || 'Erreur lors de la soumission'
    alert(`❌ ${errorMsg}`)
  }
}

const deleteDeliverable = async (deliverableId, missionId) => {
  if (!confirm('Supprimer définitivement ce livrable ?')) return
  
  try {
    await deliverablesStore.deleteDeliverable(deliverableId)
    await fetchMissionDeliverables(missionId)
    alert('✅ Livrable supprimé !')
  } catch (error) {
    console.error('❌ Erreur suppression:', error)
    const errorMsg = error.response?.data?.error || 'Erreur lors de la suppression'
    alert(`❌ ${errorMsg}`)
  }
}

const downloadDeliverableFile = async (deliverableId) => {
  try {
    await deliverablesStore.downloadFile(deliverableId)
  } catch (error) {
    console.error('❌ Erreur téléchargement:', error)
    alert('Erreur lors du téléchargement du fichier')
  }
}
</script>
<style scoped>
/* =========================
   VARIABLES CSS
========================= */
.missions-page {
  --primary-blue: #3b82f6;
  --primary-blue-dark: #2563eb;
  --success-green: #10b981;
  --success-green-dark: #059669;
  --warning-orange: #f59e0b;
  --warning-orange-dark: #d97706;
  --purple: #8b5cf6;
  --purple-dark: #7c3aed;
  --error-red: #ef4444;
  --error-red-dark: #dc2626;
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
}

/* =========================
   PAGE PRINCIPALE
========================= */
.missions-page {
  max-width: 1200px;
  margin: 100px auto 50px;
  padding: 0 24px;
  font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
  min-height: calc(100vh - 150px);
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* =========================
   EN-TÊTE
========================= */
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--gray-200);
  flex-wrap: wrap;
  gap: 16px;
}

.header-row h1 {
  font-size: 32px;
  font-weight: 700;
  color: var(--gray-900);
  margin: 0;
  position: relative;
  padding-left: 16px;
  flex: 1;
  min-width: 200px;
}

.header-row h1::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 4px;
  background: linear-gradient(to bottom, var(--primary-blue), var(--primary-blue-dark));
  border-radius: 2px;
}

/* Actions d'en-tête */
.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.my-deliverables-btn,
.my-applications-btn,
.reload-btn {
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 2px solid transparent;
  min-height: 44px;
  white-space: nowrap;
  font-family: inherit;
  color: white;
  text-decoration: none;
}

.my-deliverables-btn {
  background: linear-gradient(135deg, var(--success-green), var(--success-green-dark));
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.2);
}

.my-deliverables-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
}

.my-applications-btn {
  background: linear-gradient(135deg, var(--purple), var(--purple-dark));
  box-shadow: 0 4px 20px rgba(139, 92, 246, 0.2);
}

.my-applications-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(139, 92, 246, 0.3);
}

.reload-btn {
  background: linear-gradient(135deg, var(--primary-blue), var(--primary-blue-dark));
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.2);
}

.reload-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
}

/* =========================
   ÉTATS (CHARGEMENT, ERREUR, VIDE)
========================= */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  min-height: 300px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--gray-200);
  border-top-color: var(--primary-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: var(--gray-600);
  font-size: 16px;
  margin: 0;
}

.error-state {
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  border: 2px solid var(--error-red);
  border-radius: 12px;
  padding: 32px 24px;
  text-align: center;
  margin: 20px 0;
  animation: slideIn 0.5s ease-out;
}

.error-state i {
  color: var(--error-red);
  font-size: 32px;
  margin-bottom: 12px;
  display: block;
}

.error-state p {
  color: var(--error-red-dark);
  font-weight: 600;
  margin: 0 0 20px 0;
  font-size: 16px;
}

.retry-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, var(--error-red), var(--error-red-dark));
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: inherit;
  font-size: 14px;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: linear-gradient(135deg, var(--gray-50), #f0f4f8);
  border-radius: 16px;
  border: 2px dashed var(--gray-300);
  margin: 20px 0;
  animation: fadeInUp 0.6s ease-out;
}

.empty-icon {
  font-size: 48px;
  color: var(--gray-400);
  margin-bottom: 20px;
  display: block;
}

.empty-state h3 {
  font-size: 20px;
  color: var(--gray-700);
  margin: 0 0 12px 0;
  font-weight: 600;
}

.empty-message {
  color: var(--gray-600);
  font-size: 15px;
  line-height: 1.6;
  max-width: 400px;
  margin: 0 auto 24px;
}

.refresh-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--gray-200), var(--gray-300));
  color: var(--gray-700);
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: inherit;
  font-size: 14px;
}

.refresh-btn:hover {
  background: linear-gradient(135deg, var(--gray-300), var(--gray-400));
  transform: translateY(-2px);
}

/* =========================
   GRILLE DES MISSIONS
========================= */
.missions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
  margin-top: 20px;
}

/* Animation d'entrée */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.mission-card {
  animation: fadeInUp 0.5s ease-out;
  animation-fill-mode: both;
}

.mission-card:nth-child(1) { animation-delay: 0.1s; }
.mission-card:nth-child(2) { animation-delay: 0.2s; }
.mission-card:nth-child(3) { animation-delay: 0.3s; }
.mission-card:nth-child(4) { animation-delay: 0.4s; }

/* =========================
   CARTE MISSION
========================= */
.mission-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  border: 2px solid var(--gray-200);
  padding: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
  overflow: hidden;
  height: 100%;
}

.mission-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.12);
  border-color: var(--primary-blue);
}

/* Cartes spéciales */
.mission-card.applied-card {
  border-color: var(--success-green);
  background: linear-gradient(to bottom right, white, #f0fdf4);
}

.mission-card.applied-card:hover {
  border-color: var(--success-green-dark);
}

.mission-card.assigned-card {
  border-color: var(--warning-orange);
  background: linear-gradient(to bottom right, white, #fffbeb);
  position: relative;
}

.mission-card.assigned-card:hover {
  border-color: var(--warning-orange-dark);
}

/* =========================
   EN-TÊTE DE CARTE
========================= */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.mission-title-section {
  flex: 1;
  min-width: 0;
}

.mission-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--gray-900);
  margin: 0 0 12px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
}

.mission-status {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.user-status {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-end;
}

/* Badges */
.badge {
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  line-height: 1;
  border: 1px solid transparent;
}

.badge-open {
  background: linear-gradient(135deg, #dbeafe, #93c5fd);
  color: var(--primary-blue-dark);
  border-color: #bfdbfe;
}

.badge-in-progress {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: var(--warning-orange-dark);
  border-color: #fde68a;
}

.badge-completed {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: var(--success-green-dark);
  border-color: #a7f3d0;
}

.badge-applied {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: var(--success-green-dark);
  border-color: #a7f3d0;
}

.badge-assigned {
  background: linear-gradient(135deg, #fff8e1, #ffecb3);
  color: var(--warning-orange-dark);
  border-color: #ffecb3;
}

/* =========================
   DESCRIPTION
========================= */
.mission-description {
  color: var(--gray-600);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
}

/* =========================
   INFORMATIONS
========================= */
.mission-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--gray-50);
  border-radius: 10px;
  border: 1px solid var(--gray-200);
  transition: transform 0.2s;
}

.info-item:hover {
  transform: translateY(-2px);
  background: white;
}

.info-icon {
  width: 32px;
  height: 32px;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-blue);
  font-size: 14px;
  border: 1px solid var(--gray-200);
  flex-shrink: 0;
}

.info-content {
  flex: 1;
  min-width: 0;
}

.info-label {
  font-size: 12px;
  color: var(--gray-500);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 2px;
  display: block;
}

.info-value {
  font-size: 14px;
  color: var(--gray-800);
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

/* =========================
   COMPÉTENCES
========================= */
.skills-section {
  margin-top: 4px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--gray-700);
  font-weight: 600;
  margin-bottom: 12px;
}

.section-title i {
  color: var(--gray-500);
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.skill-tag {
  background: linear-gradient(135deg, #e2e8f0, #cbd5e1);
  color: var(--gray-700);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid var(--gray-300);
  line-height: 1;
}

.skill-tag-more {
  background: var(--gray-300);
  color: var(--gray-600);
  font-style: italic;
}

/* =========================
   STATISTIQUES CANDIDATURES
========================= */
.applications-stats {
  display: flex;
  gap: 16px;
  padding: 12px;
  background: var(--gray-50);
  border-radius: 10px;
  border: 1px solid var(--gray-200);
  flex-wrap: wrap;
}

.stats-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--gray-600);
  line-height: 1;
}

.stats-item i {
  color: var(--primary-blue);
  font-size: 14px;
}

.stats-item:nth-child(2) i {
  color: var(--warning-orange);
}

/* =========================
   SECTION LIVRABLES
========================= */
.deliverables-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--gray-200);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.toggle-deliverables-btn {
  background: var(--gray-100);
  color: var(--gray-700);
  border: 1px solid var(--gray-300);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.toggle-deliverables-btn:hover {
  background: var(--gray-200);
  transform: translateY(-1px);
}

.deliverables-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--gray-50);
  border-radius: 8px;
  color: var(--gray-600);
  font-size: 13px;
}

.small-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--gray-200);
  border-top-color: var(--primary-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.no-deliverables {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: var(--gray-50);
  border-radius: 8px;
  color: var(--gray-500);
  font-size: 13px;
}

.deliverables-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.deliverable-item {
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  padding: 12px;
  transition: all 0.2s;
  position: relative;
}

.deliverable-item:hover {
  background: white;
  border-color: var(--gray-300);
  transform: translateY(-1px);
}

.deliverable-item.selected {
  border-color: var(--primary-blue);
  background: #eff6ff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.deliverable-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  gap: 8px;
}

.deliverable-title {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  flex-wrap: wrap;
}

.deliverable-title strong {
  font-size: 14px;
  color: var(--gray-800);
  line-height: 1.4;
}

.status-badge {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  white-space: nowrap;
  height: fit-content;
}

.status-draft .status-badge {
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.status-submitted .status-badge {
  background: #dbeafe;
  color: #1d4ed8;
  border: 1px solid #93c5fd;
}

.status-under-review .status-badge {
  background: #fef3c7;
  color: #d97706;
  border: 1px solid #fde68a;
}

.status-accepted .status-badge {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.status-rejected .status-badge {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.deliverable-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.action-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
  background: white;
  border: 1px solid var(--gray-300);
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-submit {
  color: #1d4ed8;
  border-color: #93c5fd;
  background: #dbeafe;
}

.btn-submit:hover {
  background: #bfdbfe;
}

.btn-edit {
  color: #d97706;
  border-color: #fde68a;
  background: #fef3c7;
}

.btn-edit:hover {
  background: #fde68a;
}

.btn-delete {
  color: #dc2626;
  border-color: #fecaca;
  background: #fee2e2;
}

.btn-delete:hover {
  background: #fecaca;
}

.btn-download {
  color: #4b5563;
  background: #f3f4f6;
}

.btn-download:hover {
  background: #e5e7eb;
}

.deliverable-description {
  font-size: 13px;
  color: var(--gray-600);
  margin: 0 0 8px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.deliverable-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: var(--gray-500);
  flex-wrap: wrap;
}

.meta-date {
  display: flex;
  align-items: center;
  gap: 4px;
}

.client-feedback {
  margin-top: 8px;
  padding: 8px 12px;
  background: #fefce8;
  border-left: 3px solid #f59e0b;
  font-size: 12px;
  color: #92400e;
  display: flex;
  gap: 8px;
  border-radius: 0 4px 4px 0;
  line-height: 1.4;
}

.client-feedback i {
  margin-top: 2px;
}

/* =========================
   FORMULAIRE LIVRABLE
========================= */
.deliverable-form-inline {
  background: var(--gray-50);
  border: 1px solid var(--gray-300);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.form-header h4 {
  margin: 0;
  font-size: 14px;
  color: var(--gray-800);
  font-weight: 600;
}

.close-form-btn {
  background: none;
  border: none;
  color: var(--gray-500);
  cursor: pointer;
  padding: 4px;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-form-btn:hover {
  background: var(--gray-200);
  color: var(--gray-700);
}

.form-group {
  margin-bottom: 12px;
}

.form-group label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--gray-700);
  margin-bottom: 6px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--gray-300);
  border-radius: 6px;
  font-family: inherit;
  font-size: 13px;
  transition: all 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 60px;
}

.form-file {
  width: 100%;
  padding: 8px;
  font-size: 12px;
  border: 1px solid var(--gray-300);
  border-radius: 6px;
  background: white;
  cursor: pointer;
}

.form-file::-webkit-file-upload-button {
  background: var(--gray-100);
  border: 1px solid var(--gray-300);
  padding: 6px 12px;
  border-radius: 4px;
  margin-right: 12px;
  cursor: pointer;
  font-size: 12px;
  color: var(--gray-700);
}

.form-file:hover::-webkit-file-upload-button {
  background: var(--gray-200);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border: 1px solid var(--gray-200);
  border-radius: 6px;
  margin-top: 8px;
  font-size: 12px;
}

.remove-file-btn {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--error-red);
  cursor: pointer;
  padding: 2px;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-file-btn:hover {
  background: #fee2e2;
}

.form-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.btn-cancel,
.btn-save {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-cancel {
  background: var(--gray-200);
  color: var(--gray-700);
  border-color: var(--gray-300);
}

.btn-cancel:hover {
  background: var(--gray-300);
  transform: translateY(-1px);
}

.btn-save {
  background: var(--primary-blue);
  color: white;
  border-color: var(--primary-blue);
  flex: 1;
  justify-content: center;
}

.btn-save:hover:not(:disabled) {
  background: var(--primary-blue-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

/* =========================
   BOUTON AJOUTER LIVRABLE
========================= */
.add-deliverable-btn-container {
  margin-top: 12px;
}

.btn-add-deliverable {
  width: 100%;
  padding: 10px;
  background: #f8fafc;
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-add-deliverable:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
  color: var(--gray-700);
  transform: translateY(-1px);
}

/* =========================
   RÉCAPITULATIF LIVRABLES
========================= */
.deliverables-summary {
  padding: 12px;
  background: var(--gray-50);
  border-radius: 8px;
}

.summary-stats {
  display: flex;
  justify-content: space-around;
  gap: 8px;
}

.summary-stats .stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.summary-stats .stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--gray-800);
}

.summary-stats .stat-label {
  font-size: 11px;
  color: var(--gray-500);
  text-transform: uppercase;
  font-weight: 600;
  text-align: center;
}

/* =========================
   NOTICE MISSION ASSIGNÉE
========================= */
.assigned-notice {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, #fff8e1, #ffecb3);
  border-radius: 10px;
  border: 1px solid #fde68a;
  margin-top: 8px;
  animation: slideIn 0.5s ease-out;
}

.notice-icon {
  width: 32px;
  height: 32px;
  background: var(--warning-orange);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
  line-height: 1;
}

.notice-content {
  flex: 1;
}

.notice-content strong {
  display: block;
  color: var(--warning-orange-dark);
  font-size: 14px;
  margin-bottom: 4px;
  line-height: 1.4;
}

.notice-content p {
  font-size: 13px;
  color: var(--warning-orange-dark);
  margin: 0;
  line-height: 1.4;
  opacity: 0.9;
}

/* =========================
   ACTIONS
========================= */
.mission-actions {
  display: flex;
  gap: 12px;
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid var(--gray-200);
  flex-wrap: wrap;
}

.btn {
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 2px solid transparent;
  flex: 1;
  min-height: 44px;
  min-width: 120px;
  text-align: center;
  font-family: inherit;
  color: var(--gray-700);
}

.btn:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.btn:active:not(.disabled) {
  transform: translateY(0);
}

.btn-details {
  background: var(--gray-100);
  color: var(--gray-700);
  border-color: var(--gray-300);
}

.btn-details:hover {
  background: var(--gray-200);
  border-color: var(--gray-400);
}

.btn-apply {
  background: linear-gradient(135deg, var(--primary-blue), var(--primary-blue-dark));
  color: white;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

.btn-apply:hover:not(.disabled) {
  background: linear-gradient(135deg, var(--primary-blue-dark), #1d4ed8);
  box-shadow: 0 6px 25px rgba(59, 130, 246, 0.4);
}

.btn-apply.disabled {
  background: var(--gray-400);
  color: var(--gray-600);
  cursor: not-allowed;
  opacity: 0.7;
  box-shadow: none;
  transform: none !important;
}

/* Actions pour mission assignée */
.assigned-actions {
  display: flex;
  gap: 12px;
  width: 100%;
  flex-wrap: wrap;
}

.btn-create-deliverable {
  background: linear-gradient(135deg, var(--success-green), var(--success-green-dark));
  color: white;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.btn-create-deliverable:hover {
  background: linear-gradient(135deg, var(--success-green-dark), #047857);
  box-shadow: 0 6px 25px rgba(16, 185, 129, 0.4);
}

.btn-manage-deliverables {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
}

.btn-manage-deliverables:hover {
  background: linear-gradient(135deg, #7c3aed, #6d28d9);
  box-shadow: 0 6px 25px rgba(139, 92, 246, 0.4);
}

/* =========================
   RESPONSIVE
========================= */
@media (max-width: 1200px) {
  .missions-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}

@media (max-width: 1024px) {
  .missions-page {
    margin-top: 80px;
    padding: 0 20px;
  }
  
  .header-row {
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
  }
  
  .header-row h1 {
    text-align: center;
    padding-left: 0;
  }
  
  .header-row h1::before {
    display: none;
  }
  
  .header-actions {
    justify-content: center;
    width: 100%;
  }
  
  .my-deliverables-btn,
  .my-applications-btn,
  .reload-btn {
    min-width: 200px;
  }
}

@media (max-width: 768px) {
  .missions-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .mission-card {
    padding: 20px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .assigned-actions {
    flex-direction: column;
  }
  
  .mission-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
  
  .applications-stats {
    flex-direction: column;
    gap: 12px;
  }
  
  .header-actions {
    flex-direction: column;
  }
  
  .my-deliverables-btn,
  .my-applications-btn,
  .reload-btn {
    width: 100%;
    min-width: unset;
  }
}

@media (max-width: 640px) {
  .missions-page {
    margin-top: 70px;
    padding: 0 16px;
  }
  
  .header-row h1 {
    font-size: 28px;
    text-align: left;
    padding-left: 16px;
  }
  
  .header-row h1::before {
    display: block;
  }
  
  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .user-status {
    align-items: stretch;
    width: 100%;
  }
  
  .badge {
    width: 100%;
    justify-content: center;
  }
  
  .badge:not(:last-child) {
    margin-bottom: 4px;
  }
  
  .deliverable-header {
    flex-direction: column;
    gap: 8px;
  }
  
  .deliverable-actions {
    align-self: stretch;
    justify-content: flex-end;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn-cancel,
  .btn-save {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .mission-card {
    padding: 16px;
    gap: 16px;
  }
  
  .mission-title {
    font-size: 16px;
  }
  
  .btn {
    padding: 10px 16px;
    font-size: 13px;
  }
  
  .info-item {
    padding: 10px;
  }
  
  .skills-tags {
    justify-content: center;
  }
  
  .assigned-notice {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
  
  .notice-icon {
    align-self: center;
  }
  
  .summary-stats {
    flex-direction: column;
    gap: 12px;
  }
  
  .summary-stats .stat-item {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
  
  .deliverable-meta {
    flex-direction: column;
    gap: 8px;
  }
}

@media (max-width: 360px) {
  .missions-grid {
    gap: 16px;
  }
  
  .mission-card {
    padding: 14px;
  }
  
  .header-row h1 {
    font-size: 24px;
  }
  
  .my-deliverables-btn,
  .my-applications-btn,
  .reload-btn {
    padding: 10px 14px;
    font-size: 13px;
  }
}

/* =========================
   ACCESSIBILITÉ
========================= */
@media (prefers-reduced-motion: reduce) {
  .missions-page,
  .mission-card,
  .error-state,
  .empty-state,
  .assigned-notice,
  .deliverable-form-inline,
  .btn,
  .my-deliverables-btn,
  .my-applications-btn,
  .reload-btn,
  .retry-btn,
  .refresh-btn,
  .info-item,
  .action-btn,
  .btn-add-deliverable {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  
  .mission-card {
    animation: none;
  }
}

/* Focus visible pour accessibilité */
.btn:focus-visible,
.my-deliverables-btn:focus-visible,
.my-applications-btn:focus-visible,
.reload-btn:focus-visible,
.retry-btn:focus-visible,
.refresh-btn:focus-visible,
.toggle-deliverables-btn:focus-visible,
.action-btn:focus-visible,
.btn-add-deliverable:focus-visible,
.form-input:focus-visible,
.form-textarea:focus-visible {
  outline: 3px solid var(--primary-blue);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.3);
}

/* Style pour les écrans très larges */
@media (min-width: 1400px) {
  .missions-page {
    max-width: 1320px;
  }
  
  .missions-grid {
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  }
}
</style>