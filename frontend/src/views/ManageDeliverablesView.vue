<template>
  <div class="manage-deliverables-page">
    <!-- En-tête -->
    <div class="page-header">
      <h1 class="page-title">Livrables - {{ mission?.title }}</h1>
      <div class="page-subtitle">
        <router-link 
          :to="{ name: 'MissionDetails', params: { id: missionId } }"
          class="back-link"
        >
          ← Retour à la mission
        </router-link>
        <span class="divider">•</span>
        <span class="mission-info">
          Statut: <span :class="`mission-status-badge ${mission?.status}`">{{ getMissionStatusLabel(mission?.status) }}</span>
        </span>
      </div>
    </div>

    <!-- Deux colonnes -->
    <div class="main-grid">
      <!-- Colonne gauche: Liste des livrables -->
      <div class="deliverables-column">
        <div class="deliverables-card">
          <!-- En-tête avec filtres -->
          <div class="card-header">
            <div class="header-content">
              <h2 class="header-title">Tous les livrables</h2>
              <div class="header-controls">
                <!-- Filtre rapide -->
                <select 
                  v-model="activeFilter"
                  class="status-filter"
                >
                  <option value="">Tous les statuts</option>
                  <option value="draft">Brouillon</option>
                  <option value="submitted">Soumis</option>
                  <option value="under_review">En review</option>
                  <option value="accepted">Acceptés</option>
                  <option value="rejected">Rejetés</option>
                  <option value="needs_revision">Révision demandée</option>
                </select>
                
                <!-- Bouton créer (freelance seulement) -->
                <button
                  v-if="isFreelanceAssigned && mission?.status === 'in_progress'"
                  @click="showCreateForm = !showCreateForm"
                  :class="['new-deliverable-btn', { cancel: showCreateForm }]"
                >
                  {{ showCreateForm ? 'Annuler' : '+ Nouveau' }}
                </button>
              </div>
            </div>

            <!-- Statistiques -->
            <div class="stats-container">
              <div v-for="stat in statusStats" :key="stat.label" class="stat-item">
                <div class="stat-value" :style="{ color: stat.color }">
                  {{ stat.count }}
                </div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </div>
          </div>

          <!-- Liste des livrables -->
          <div v-if="loading" class="loading-state">
            <p>Chargement...</p>
          </div>

          <div v-else-if="filteredDeliverables.length === 0" class="empty-state">
            <div class="empty-icon">📁</div>
            <h3 class="empty-title">Aucun livrable</h3>
            <p class="empty-message">
              {{ 
                isFreelanceAssigned && mission?.status === 'in_progress'
                  ? 'Créez votre premier livrable pour cette mission'
                  : 'Aucun livrable disponible'
              }}
            </p>
            <button
              v-if="mission?.status === 'in_progress'"
              @click="showCreateForm = true"
              class="new-deliverable-btn"
            >
              Créer le premier livrable
            </button>
          </div>

          <div v-else class="deliverables-list">
            <div
              v-for="deliverable in filteredDeliverables"
              :key="deliverable.id"
              :class="['deliverable-item', { selected: deliverable.id === selectedDeliverableId }]"
              @click="selectDeliverable(deliverable)"
            >
              <div class="deliverable-header">
                <div class="deliverable-title-section">
                  <h3 class="deliverable-title">
                    {{ deliverable.title }}
                    <span :class="`status-badge ${deliverable.status}`">
                      {{ getStatusLabel(deliverable.status) }}
                    </span>
                  </h3>
                </div>

                <!-- Actions rapides -->
                <div class="deliverable-actions">
                  <!-- Actions freelance -->
                  <template v-if="isFreelance && deliverable.submitted_by === user.id">
                    <button
                      v-if="deliverable.status === 'draft'"
                      @click.stop="editDeliverable = deliverable"
                      class="action-btn edit"
                    >
                      Modifier
                    </button>
                    <button
                      v-if="deliverable.status === 'draft' || deliverable.status === 'needs_revision'"
                      @click.stop="submitDeliverable(deliverable.id)"
                      class="action-btn submit"
                    >
                      Soumettre
                    </button>
                    <button
                      v-if="deliverable.status === 'draft'"
                      @click.stop="deleteDeliverable(deliverable.id)"
                      class="action-btn delete"
                    >
                      Supprimer
                    </button>
                  </template>

                  <!-- Actions client -->
                  <template v-if="isClient && mission?.client_id === user.id">
                    <button
                      v-if="deliverable.status === 'submitted'"
                      @click.stop="startReview(deliverable.id)"
                      class="action-btn review"
                    >
                      Review
                    </button>
                    <button
                      v-if="deliverable.status === 'under_review'"
                      @click.stop="showAcceptModal = deliverable.id"
                      class="action-btn accept"
                    >
                      Accepter
                    </button>
                    <button
                      v-if="deliverable.status === 'under_review'"
                      @click.stop="showRejectModal = deliverable.id"
                      class="action-btn reject"
                    >
                      Rejeter
                    </button>
                  </template>
                </div>
              </div>

              <div class="deliverable-content">
                <p class="deliverable-description">
                  {{ deliverable.description || 'Pas de description' }}
                </p>
                
                <div class="deliverable-meta">
                  <span>Créé le {{ formatDate(deliverable.created_at) }}</span>
                  <span v-if="deliverable.submitted_at">
                    • Soumis le {{ formatDate(deliverable.submitted_at) }}
                  </span>
                  <button
                    v-if="deliverable.file_url"
                    @click.stop="downloadFile(deliverable.id)"
                    class="download-link"
                  >
                    Télécharger
                  </button>
                </div>

                <!-- Feedback client -->
                <div v-if="deliverable.client_feedback" class="client-feedback">
                  <div class="feedback-label">Feedback client:</div>
                  <p class="feedback-content">{{ deliverable.client_feedback }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Colonne droite: Formulaire ou Détails -->
      <div class="sidebar-column">
        <!-- Formulaire création/modification -->
        <div v-if="showCreateForm || editDeliverable" class="form-card">
          <h3 class="form-title">
            {{ editDeliverable ? 'Modifier le livrable' : 'Nouveau livrable' }}
          </h3>
          
          <DeliverableForm
            :mission-id="missionId"
            :deliverable="editDeliverable"
            @submit="handleFormSubmit"
            @cancel="handleFormCancel"
          />
        </div>

        <!-- Détails du livrable sélectionné -->
        <div v-else-if="selectedDeliverable" class="details-card">
          <div class="details-header">
            <h3 class="details-title">Détails du livrable</h3>
            
            <!-- Boutons Modifier, Supprimer, Soumettre dans l'en-tête -->
            <div v-if="isFreelance && selectedDeliverable.submitted_by === user.id" class="details-actions">
              <button
                v-if="selectedDeliverable.status === 'draft'"
                @click="editDeliverable = selectedDeliverable"
                class="details-action-btn edit"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Modifier
              </button>
              
              <button
                v-if="selectedDeliverable.status === 'draft' || selectedDeliverable.status === 'needs_revision'"
                @click="submitDeliverable(selectedDeliverable.id)"
                class="details-action-btn submit"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Soumettre
              </button>
              
              <button
                v-if="selectedDeliverable.status === 'draft'"
                @click="deleteDeliverable(selectedDeliverable.id)"
                class="details-action-btn delete"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Supprimer
              </button>
            </div>
            
            <!-- Actions client dans l'en-tête -->
            <div v-if="isClient && mission?.client_id === user.id" class="details-actions">
              <button
                v-if="selectedDeliverable.status === 'submitted'"
                @click="startReview(selectedDeliverable.id)"
                class="details-action-btn review"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                Commencer Review
              </button>
              
              <button
                v-if="selectedDeliverable.status === 'under_review'"
                @click="showAcceptModal = selectedDeliverable.id"
                class="details-action-btn accept"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Accepter
              </button>
              
              <button
                v-if="selectedDeliverable.status === 'under_review'"
                @click="showRejectModal = selectedDeliverable.id"
                class="details-action-btn reject"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                Rejeter
              </button>
            </div>
          </div>
          
          <div class="details-content">
            <div class="detail-item">
              <label class="detail-label">Titre</label>
              <p class="detail-value">{{ selectedDeliverable.title }}</p>
            </div>
            
            <div class="detail-item">
              <label class="detail-label">Description</label>
              <p class="detail-value" :class="{ empty: !selectedDeliverable.description }">
                {{ selectedDeliverable.description || '—' }}
              </p>
            </div>
            
            <div class="detail-item">
              <label class="detail-label">Statut</label>
              <span :class="`status-badge ${selectedDeliverable.status}`" class="detail-value">
                {{ getStatusLabel(selectedDeliverable.status) }}
              </span>
            </div>
            
            <div class="detail-item">
              <label class="detail-label">Créé par</label>
              <p class="detail-value">{{ selectedDeliverable.freelance_name || 'Utilisateur inconnu' }}</p>
            </div>
            
            <div v-if="selectedDeliverable.file_url" class="detail-item">
              <label class="detail-label">Fichier</label>
              <button
                @click="downloadFile(selectedDeliverable.id)"
                class="file-download"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Télécharger le fichier</span>
              </button>
            </div>
            
            <!-- Feedback client -->
            <div v-if="selectedDeliverable.client_feedback" class="feedback-section">
              <label class="detail-label">Feedback client</label>
              <div class="feedback-box">
                {{ selectedDeliverable.client_feedback }}
              </div>
            </div>
            
            <!-- Historique -->
            <div class="history-section">
              <h4 class="history-title">Historique</h4>
              <ul class="history-list">
                <li v-if="selectedDeliverable.created_at" class="history-item created">
                  <svg class="history-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <strong>Créé</strong>
                    <span>le {{ formatDateTime(selectedDeliverable.created_at) }}</span>
                  </div>
                </li>
                <li v-if="selectedDeliverable.submitted_at" class="history-item submitted">
                  <svg class="history-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <div>
                    <strong>Soumis pour review</strong>
                    <span>le {{ formatDateTime(selectedDeliverable.submitted_at) }}</span>
                  </div>
                </li>
                <li v-if="selectedDeliverable.reviewed_at" class="history-item reviewed">
                  <svg class="history-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <div>
                    <strong>Review commencée</strong>
                    <span>le {{ formatDateTime(selectedDeliverable.reviewed_at) }}</span>
                  </div>
                </li>
                <li v-if="selectedDeliverable.accepted_at" class="history-item accepted">
                  <svg class="history-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <strong>Accepté</strong>
                    <span>le {{ formatDateTime(selectedDeliverable.accepted_at) }}</span>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Aide/Info -->
        <div v-else class="help-card">
          <h3 class="help-title">Workflow des livrables</h3>
          <ul class="workflow-steps">
            <li class="step-item">
              <span class="step-number">1</span>
              <div class="step-content">
                <p class="step-text">Le freelance crée un <strong>brouillon</strong> de livrable</p>
              </div>
            </li>
            <li class="step-item">
              <span class="step-number">2</span>
              <div class="step-content">
                <p class="step-text">Il le <strong>soumet</strong> pour review par le client</p>
              </div>
            </li>
            <li class="step-item">
              <span class="step-number">3</span>
              <div class="step-content">
                <p class="step-text">Le client peut <strong>accepter, rejeter ou demander une révision</strong></p>
              </div>
            </li>
            <li class="step-item">
              <span class="step-number">4</span>
              <div class="step-content">
                <p class="step-text">Si révision demandée, le freelance modifie et resoumet</p>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <AcceptModal
      v-if="showAcceptModal"
      :deliverable-id="showAcceptModal"
      @accept="handleAccept"
      @close="showAcceptModal = null"
    />
    
    <RejectModal
      v-if="showRejectModal"
      :deliverable-id="showRejectModal"
      @reject="handleReject"
      @close="showRejectModal = null"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDeliverablesStore } from '@/stores/deliverables'
import { useMissionStore } from '@/stores/missions'
import { useAuthStore } from '@/stores/auth'
import DeliverableForm from '@/components/deliverables/DeliverableForm.vue'
import AcceptModal from '@/components/deliverables/AcceptModal.vue'
import RejectModal from '@/components/deliverables/RejectModal.vue'

const route = useRoute()
const deliverablesStore = useDeliverablesStore()
const missionsStore = useMissionStore()
const authStore = useAuthStore()

const missionId = parseInt(route.params.missionId)
const activeFilter = ref('')
const showCreateForm = ref(false)
const editDeliverable = ref(null)
const selectedDeliverableId = ref(null)
const showAcceptModal = ref(null)
const showRejectModal = ref(null)
const loading = ref(false)

const user = computed(() => authStore.user)
const isFreelance = computed(() => user.value?.profile?.type === 'freelance')
const isClient = computed(() => user.value?.profile?.type === 'client')
const mission = computed(() => missionsStore.currentMission)
const deliverables = computed(() => deliverablesStore.deliverables)

// Vérifie si le freelance est assigné à cette mission
const isFreelanceAssigned = computed(() => {
  if (!isFreelance.value || !mission.value) return false
  
  return mission.value.postulations?.some(
    p => p.freelance_id === user.value.id && p.status === 'accepted'
  )
})

const filteredDeliverables = computed(() => {
  if (!activeFilter.value) return deliverables.value
  return deliverables.value.filter(d => d.status === activeFilter.value)
})

const selectedDeliverable = computed(() => {
  if (!selectedDeliverableId.value) return null
  return deliverables.value.find(d => d.id === selectedDeliverableId.value)
})

const statusStats = computed(() => {
  const stats = [
    { label: 'Brouillons', value: 'draft', color: '#6b7280' },
    { label: 'Soumis', value: 'submitted', color: '#3b82f6' },
    { label: 'En review', value: 'under_review', color: '#f59e0b' },
    { label: 'Acceptés', value: 'accepted', color: '#10b981' },
  ]
  
  return stats.map(stat => ({
    ...stat,
    count: deliverables.value.filter(d => d.status === stat.value).length
  }))
})

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    await missionsStore.fetchMissionDetails(missionId)
    await deliverablesStore.fetchMissionDeliverables(missionId)
  } catch (error) {
    console.error('Erreur chargement:', error)
  } finally {
    loading.value = false
  }
}

function selectDeliverable(deliverable) {
  selectedDeliverableId.value = deliverable.id
  showCreateForm.value = false
  editDeliverable.value = null
}

function getStatusLabel(status) {
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

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('fr-FR')
}

function formatDateTime(dateString) {
  return new Date(dateString).toLocaleString('fr-FR')
}

function getMissionStatusLabel(status) {
  const labels = {
    draft: 'Brouillon',
    open: 'Ouverte',
    in_progress: 'En cours',
    completed: 'Terminée',
    cancelled: 'Annulée'
  }
  return labels[status] || status
}

async function submitDeliverable(id) {
  if (confirm('Soumettre ce livrable pour review ?')) {
    try {
      await deliverablesStore.submitDeliverable(id)
      await loadData()
    } catch (error) {
      console.error('Erreur soumission:', error)
    }
  }
}

async function deleteDeliverable(id) {
  if (confirm('Supprimer définitivement ce livrable ?')) {
    try {
      await deliverablesStore.deleteDeliverable(id)
      selectedDeliverableId.value = null
      await loadData()
    } catch (error) {
      console.error('Erreur suppression:', error)
    }
  }
}

async function startReview(id) {
  if (confirm('Commencer la review de ce livrable ?')) {
    try {
      await deliverablesStore.startReview(id)
      await loadData()
    } catch (error) {
      console.error('Erreur début review:', error)
    }
  }
}

async function handleAccept(deliverableId) {
  try {
    await deliverablesStore.acceptDeliverable(deliverableId)
    await loadData()
    showAcceptModal.value = null
  } catch (error) {
    console.error('Erreur acceptation:', error)
  }
}

async function handleReject(deliverableId, feedback) {
  try {
    await deliverablesStore.rejectDeliverable(deliverableId, feedback)
    await loadData()
    showRejectModal.value = null
  } catch (error) {
    console.error('Erreur rejet:', error)
  }
}

async function downloadFile(id) {
  try {
    await deliverablesStore.downloadFile(id)
  } catch (error) {
    console.error('Erreur téléchargement:', error)
  }
}

async function handleFormSubmit() {
  await loadData()
  showCreateForm.value = false
  editDeliverable.value = null
}

function handleFormCancel() {
  showCreateForm.value = false
  editDeliverable.value = null
}
</script>

<style scoped>
.manage-deliverables-page {
  max-width: 1200px;
  margin: 100px auto 50px;
  padding: 0 20px;
  font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
}

/* En-tête */
.page-header {
  margin-bottom: 40px;
}

.page-title {
  font-size: 32px;
  margin-bottom: 10px;
  color: #111827;
  font-weight: 700;
}

.page-subtitle {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #6b7280;
  font-size: 16px;
  margin-top: 15px;
}

.back-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.back-link:hover {
  color: #2563eb;
}

.divider {
  color: #d1d5db;
}

.mission-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mission-status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
}

.mission-status-badge.draft {
  background-color: #f3f4f6;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.mission-status-badge.open {
  background-color: #dbeafe;
  color: #1d4ed8;
  border: 1px solid #93c5fd;
}

.mission-status-badge.in_progress {
  background-color: #fef3c7;
  color: #d97706;
  border: 1px solid #fcd34d;
}

.mission-status-badge.completed {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.mission-status-badge.cancelled {
  background-color: #fee2e2;
  color: #dc2626;
  border: 1px solid #fca5a5;
}

/* Grille principale */
.main-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
}

@media (min-width: 1024px) {
  .main-grid {
    grid-template-columns: 2fr 1fr;
  }
}

.deliverables-column {
  width: 100%;
}

/* Carte livrables */
.deliverables-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.card-header {
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-title {
  font-size: 20px;
  color: #111827;
  font-weight: 700;
  margin: 0;
}

.header-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.status-filter {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  color: #374151;
  font-size: 14px;
  cursor: pointer;
  min-width: 150px;
}

.status-filter:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.new-deliverable-btn {
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.new-deliverable-btn:hover {
  background: #2563eb;
}

.new-deliverable-btn.cancel {
  background: #6b7280;
}

.new-deliverable-btn.cancel:hover {
  background: #4b5563;
}

/* Statistiques */
.stats-container {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding: 12px 0;
}

.stat-item {
  text-align: center;
  min-width: 80px;
  flex-shrink: 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Liste des livrables */
.deliverables-list {
  max-height: 600px;
  overflow-y: auto;
}

.deliverable-item {
  padding: 20px 24px;
  border-bottom: 1px solid #f3f4f6;
  transition: background-color 0.2s;
  cursor: pointer;
}

.deliverable-item:hover {
  background-color: #f9fafb;
}

.deliverable-item.selected {
  background-color: #eff6ff;
  border-left: 4px solid #3b82f6;
}

.deliverable-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.deliverable-title-section {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.deliverable-title {
  font-size: 16px;
  color: #111827;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.deliverable-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.action-btn.edit {
  background: #fef3c7;
  color: #d97706;
}

.action-btn.edit:hover {
  background: #fde68a;
}

.action-btn.submit {
  background: #d1fae5;
  color: #065f46;
}

.action-btn.submit:hover {
  background: #a7f3d0;
}

.action-btn.delete {
  background: #fee2e2;
  color: #dc2626;
}

.action-btn.delete:hover {
  background: #fca5a5;
}

.action-btn.review {
  background: #dbeafe;
  color: #1d4ed8;
}

.action-btn.review:hover {
  background: #93c5fd;
}

.action-btn.accept {
  background: #d1fae5;
  color: #065f46;
}

.action-btn.accept:hover {
  background: #a7f3d0;
}

.action-btn.reject {
  background: #fee2e2;
  color: #dc2626;
}

.action-btn.reject:hover {
  background: #fca5a5;
}

.deliverable-content {
  margin-bottom: 16px;
}

.deliverable-description {
  color: #4b5563;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 12px 0;
}

.deliverable-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  color: #6b7280;
  font-size: 13px;
  flex-wrap: wrap;
}

.download-link {
  color: #3b82f6;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 13px;
  padding: 0;
  transition: color 0.2s;
}

.download-link:hover {
  color: #2563eb;
}

/* Feedback client */
.client-feedback {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 12px;
}

.feedback-label {
  font-size: 12px;
  color: #92400e;
  font-weight: 600;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.feedback-content {
  color: #92400e;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
}

/* Colonne droite */
.sidebar-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Formulaire */
.form-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
  padding: 24px;
}

.form-title {
  font-size: 18px;
  color: #111827;
  font-weight: 700;
  margin: 0 0 20px 0;
}

/* Détails du livrable */
.details-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.details-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
}

.details-title {
  font-size: 18px;
  color: #111827;
  font-weight: 700;
  margin: 0;
  flex: 1;
}

.details-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.details-action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  text-decoration: none;
}

.details-action-btn.edit {
  background: #fef3c7;
  color: #d97706;
  border: 1px solid #fde68a;
}

.details-action-btn.edit:hover {
  background: #fde68a;
}

.details-action-btn.submit {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.details-action-btn.submit:hover {
  background: #a7f3d0;
}

.details-action-btn.delete {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fca5a5;
}

.details-action-btn.delete:hover {
  background: #fca5a5;
}

.details-action-btn.review {
  background: #dbeafe;
  color: #1d4ed8;
  border: 1px solid #93c5fd;
}

.details-action-btn.review:hover {
  background: #93c5fd;
}

.details-action-btn.accept {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.details-action-btn.accept:hover {
  background: #a7f3d0;
}

.details-action-btn.reject {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fca5a5;
}

.details-action-btn.reject:hover {
  background: #fca5a5;
}

.details-action-btn .icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.details-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  margin-bottom: 0;
}

.detail-label {
  display: block;
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
  margin-bottom: 6px;
}

.detail-value {
  color: #111827;
  font-size: 15px;
  display: block;
}

.detail-value.empty {
  color: #9ca3af;
  font-style: italic;
}

.file-download {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #eff6ff;
  color: #1d4ed8;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 4px;
}

.file-download:hover {
  background: #dbeafe;
}

.file-download .icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* Section feedback */
.feedback-section {
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
  margin-top: 8px;
}

.feedback-box {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 16px;
  color: #92400e;
  font-size: 14px;
  line-height: 1.6;
  margin-top: 8px;
}

/* Historique */
.history-section {
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
  margin-top: 16px;
}

.history-title {
  font-size: 14px;
  color: #6b7280;
  font-weight: 600;
  margin: 0 0 16px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 0;
  font-size: 14px;
}

.history-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.history-item > div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.history-item strong {
  font-weight: 600;
}

.history-item span {
  color: #6b7280;
  font-size: 13px;
}

.history-item.created .history-icon {
  color: #6b7280;
}

.history-item.submitted .history-icon {
  color: #3b82f6;
}

.history-item.reviewed .history-icon {
  color: #f59e0b;
}

.history-item.accepted .history-icon {
  color: #10b981;
}

/* Carte aide */
.help-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 24px;
  color: white;
}

.help-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 20px 0;
}

.workflow-steps {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.step-number {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
}

.step-content {
  flex: 1;
}

.step-text {
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
  opacity: 0.9;
}

.step-text strong {
  font-weight: 700;
  opacity: 1;
}

/* État vide */
.empty-state {
  text-align: center;
  padding: 60px 24px;
}

.empty-icon {
  font-size: 48px;
  color: #9ca3af;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 18px;
  color: #111827;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.empty-message {
  color: #6b7280;
  font-size: 14px;
  margin: 0 0 24px 0;
  max-width: 300px;
  margin-left: auto;
  margin-right: auto;
}

/* Badges de statut */
.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.draft {
  background-color: #f3f4f6;
  color: #6b7280;
}

.status-badge.submitted {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.status-badge.under_review {
  background-color: #fef3c7;
  color: #d97706;
}

.status-badge.accepted {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.rejected {
  background-color: #fee2e2;
  color: #dc2626;
}

.status-badge.needs_revision {
  background-color: #fed7aa;
  color: #c2410c;
}

/* Chargement et erreurs */
.loading-state {
  text-align: center;
  padding: 60px 24px;
  color: #6b7280;
  font-size: 16px;
}

/* Responsive */
@media (max-width: 1023px) {
  .manage-deliverables-page {
    margin-top: 80px;
    padding: 0 16px;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .page-subtitle {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .header-controls {
    flex-direction: column;
    width: 100%;
  }
  
  .status-filter,
  .new-deliverable-btn {
    width: 100%;
  }
  
  .deliverable-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .deliverable-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .details-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .details-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .details-action-btn {
    flex: 1;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .main-grid {
    gap: 20px;
  }
  
  .card-header,
  .form-card,
  .details-card,
  .help-card {
    padding: 20px;
  }
  
  .stats-container {
    gap: 12px;
  }
  
  .stat-item {
    min-width: 70px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .deliverable-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>