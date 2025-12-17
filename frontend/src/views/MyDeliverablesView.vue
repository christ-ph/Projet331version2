<template>
  <div class="my-deliverables-page">
    <!-- En-tête adaptatif -->
    <div class="page-header">
      <h1 class="page-title">
        {{ isClient ? 'Livrables à review' : 'Mes livrables' }}
      </h1>
      <p class="page-subtitle">
        {{ isClient ? 'Livrables soumis par les freelances' : 'Tous vos livrables' }}
      </p>
    </div>

    <!-- Bouton Nouveau Livrable (visible uniquement pour le freelance) -->
    <div v-if="!isClient" class="action-header">
      <button
        @click="showCreateModal = true"
        class="action-btn primary"
      >
        <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        <span>Nouveau livrable</span>
      </button>
    </div>

    <!-- Filtres et recherche -->
    <div class="filters-card">
      <div class="filters-grid">
        <!-- Filtre statut -->
        <div class="filter-group">
          <label class="filter-label">Statut</label>
          <select 
            v-model="activeFilter"
            class="filter-select"
          >
            <option value="">Tous les statuts</option>
            <option v-if="!isClient" value="draft">Brouillon</option>
            <option value="submitted">Soumis</option>
            <option value="under_review">En review</option>
            <option value="accepted">Acceptés</option>
            <option value="rejected">Rejetés</option>
            <option value="needs_revision">Révision demandée</option>
          </select>
        </div>

        <!-- Filtre mission (si freelance) -->
        <div v-if="!isClient" class="filter-group">
          <label class="filter-label">Mission</label>
          <select 
            v-model="missionFilter"
            class="filter-select"
          >
            <option value="">Toutes les missions</option>
            <option v-for="m in myMissions" :key="m.id" :value="m.id">
              {{ m.title }}
            </option>
          </select>
        </div>

        <!-- Recherche -->
        <div class="filter-group">
          <label class="filter-label">Recherche</label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher un livrable..."
            class="filter-input"
          />
        </div>
      </div>
    </div>

    <!-- Statistiques -->
    <div class="stats-grid">
      <div v-for="stat in stats" :key="stat.label" class="stat-card">
        <div class="stat-value" :class="stat.value">{{ stat.count }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </div>
    </div>

    <!-- Liste des livrables -->
    <div v-if="loading" class="loading-state">
      <p>Chargement...</p>
    </div>

    <div v-else-if="filteredDeliverables.length === 0" class="empty-state">
      <div class="empty-icon">📁</div>
      <h3 class="empty-title">Aucun livrable trouvé</h3>
      <p class="empty-message">
        {{ 
          isClient 
            ? 'Aucun livrable soumis par les freelances pour le moment'
            : 'Vous n\'avez pas encore créé de livrables'
        }}
      </p>
      <button
        v-if="!isClient"
        @click="showCreateModal = true"
        class="action-btn submit"
      >
        <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        <span>Créer un livrable</span>
      </button>
    </div>

    <div v-else class="deliverables-list">
      <div
        v-for="deliverable in filteredDeliverables"
        :key="deliverable.id"
        class="deliverable-card"
      >
        <div class="deliverable-content">
          <div class="deliverable-header">
            <!-- En-tête avec mission -->
            <div class="mission-header">
              <span class="mission-label">Mission:</span>
              <router-link
                :to="{ name: 'MissionDetails', params: { id: deliverable.mission_id } }"
                class="mission-link"
              >
                {{ deliverable.mission_title }}
              </router-link>
            </div>
          </div>

          <div class="deliverable-title-section">
            <h3 class="deliverable-title">{{ deliverable.title }}</h3>
            <span :class="`status-badge ${deliverable.status}`">
              {{ getStatusLabel(deliverable.status) }}
            </span>
          </div>

          <!-- Description -->
          <p class="deliverable-description" :class="{ empty: !deliverable.description }">
            {{ deliverable.description || 'Pas de description' }}
          </p>

          <!-- Métadonnées -->
          <div class="deliverable-meta">
            <span class="meta-item">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Créé le {{ formatDate(deliverable.created_at) }}
            </span>
            
            <button
              v-if="deliverable.file_url"
              @click="downloadFile(deliverable.id)"
              class="meta-link download"
            >
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Télécharger</span>
            </button>
            
            <router-link
              :to="{ name: 'ManageDeliverables', params: { missionId: deliverable.mission_id } }"
              class="meta-link view-mission"
            >
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <span>Voir dans la mission</span>
            </router-link>
          </div>

          <!-- Feedback client -->
          <div v-if="deliverable.client_feedback" class="client-feedback">
            <div class="feedback-label">Feedback client:</div>
            <p class="feedback-content">{{ deliverable.client_feedback }}</p>
          </div>

          <!-- Actions -->
          <div class="deliverable-actions">
            <!-- Actions freelance -->
            <template v-if="!isClient && deliverable.submitted_by === user.id">
              <button
                v-if="deliverable.status === 'draft'"
                @click="editDeliverable(deliverable)"
                class="action-btn edit"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                <span>Modifier</span>
              </button>
              <button
                v-if="deliverable.status === 'draft' || deliverable.status === 'needs_revision'"
                @click="submitDeliverable(deliverable.id)"
                class="action-btn submit"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>Soumettre</span>
              </button>
              <button
                v-if="deliverable.status === 'draft'"
                @click="deleteDeliverable(deliverable.id)"
                class="action-btn delete"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span>Supprimer</span>
              </button>
            </template>

            <!-- Actions client -->
            <template v-if="isClient">
              <button
                v-if="deliverable.status === 'submitted'"
                @click="startReview(deliverable.id)"
                class="action-btn review"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                <span>Commencer review</span>
              </button>
              <button
                v-if="deliverable.status === 'under_review'"
                @click="showAcceptModal = deliverable.id"
                class="action-btn accept"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>Accepter</span>
              </button>
              <button
                v-if="deliverable.status === 'under_review'"
                @click="showRejectModal = deliverable.id"
                class="action-btn reject"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                <span>Rejeter</span>
              </button>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de création -->
    <div v-if="showCreateModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title">Nouveau livrable</h3>
          <button @click="showCreateModal = false" class="modal-close">
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="modal-body">
          <DeliverableForm
            @submit="handleCreateSubmit"
            @cancel="showCreateModal = false"
          />
        </div>
      </div>
    </div>

    <!-- Modal d'édition -->
    <div v-if="editingDeliverable" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title">Modifier le livrable</h3>
          <button @click="editingDeliverable = null" class="modal-close">
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="modal-body">
          <DeliverableForm
            :mission-id="editingDeliverable.mission_id"
            :deliverable="editingDeliverable"
            @submit="handleEditSubmit"
            @cancel="editingDeliverable = null"
          />
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
import { useDeliverablesStore } from '@/stores/deliverables'
import { useMissionStore } from '@/stores/missions'
import { useAuthStore } from '@/stores/auth'
import AcceptModal from '@/components/deliverables/AcceptModal.vue'
import RejectModal from '@/components/deliverables/RejectModal.vue'
import DeliverableForm from '@/components/deliverables/DeliverableForm.vue'

const deliverablesStore = useDeliverablesStore()
const missionsStore = useMissionStore()
const authStore = useAuthStore()

const activeFilter = ref('')
const missionFilter = ref('')
const searchQuery = ref('')
const showAcceptModal = ref(null)
const showRejectModal = ref(null)
const showCreateModal = ref(false)
const editingDeliverable = ref(null)
const loading = ref(false)

const user = computed(() => authStore.user)
const isClient = computed(() => user.value?.profile?.type === 'client')
const isFreelance = computed(() => user.value?.profile?.type === 'freelance')

// Récupérer les données appropriées
const deliverables = computed(() => deliverablesStore.deliverables)
const myMissions = computed(() => missionsStore.missions)

// Stats adaptatives
const stats = computed(() => {
  const baseStats = [
    { label: 'Soumis', value: 'submitted' },
    { label: 'En review', value: 'under_review' },
    { label: 'Acceptés', value: 'accepted' },
  ]
  
  if (!isClient.value) {
    baseStats.unshift({ label: 'Brouillons', value: 'draft' })
  }
  
  baseStats.push({ label: 'Rejetés', value: 'rejected' })
  
  return baseStats.map(stat => ({
    ...stat,
    count: deliverables.value.filter(d => d.status === stat.value).length
  }))
})

// Filtrage combiné
const filteredDeliverables = computed(() => {
  let filtered = deliverables.value
  
  // Filtre statut
  if (activeFilter.value) {
    filtered = filtered.filter(d => d.status === activeFilter.value)
  }
  
  // Filtre mission (freelance seulement)
  if (missionFilter.value && !isClient.value) {
    filtered = filtered.filter(d => d.mission_id === parseInt(missionFilter.value))
  }
  
  // Recherche
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(d => 
      d.title.toLowerCase().includes(query) ||
      d.description?.toLowerCase().includes(query) ||
      d.mission_title?.toLowerCase().includes(query)
    )
  }
  
  return filtered
})

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    if (isClient.value) {
      // Client: charger les livrables à review
      await deliverablesStore.fetchClientDeliverables()
    } else {
      // Freelance: charger mes livrables et mes missions
      await deliverablesStore.fetchMyDeliverables()
      await missionsStore.fetchMyMissions()
    }
  } catch (error) {
    console.error('Erreur chargement:', error)
  } finally {
    loading.value = false
  }
}

// Fonctions utilitaires
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

// Actions
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

function editDeliverable(deliverable) {
  editingDeliverable.value = deliverable
}

async function handleCreateSubmit() {
  await loadData()
  showCreateModal.value = false
}

async function handleEditSubmit() {
  await loadData()
  editingDeliverable.value = null
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
    alert('Erreur lors du téléchargement du fichier')
  }
}
</script>

<style scoped>
.my-deliverables-page {
  max-width: 1200px;
  margin: 100px auto 50px;
  padding: 0 20px;
  font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
}

/* En-tête */
.page-header {
  margin-bottom: 30px;
}

.page-title {
  font-size: 32px;
  margin-bottom: 10px;
  color: #111827;
  font-weight: 700;
}

.page-subtitle {
  color: #6b7280;
  font-size: 16px;
  margin: 0;
}

/* Bouton Nouveau Livrable */
.action-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 24px;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.action-btn.primary:active {
  transform: translateY(0);
}

/* Filtres */
.filters-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
  padding: 24px;
  margin-bottom: 24px;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 20px;
}

@media (min-width: 768px) {
  .filters-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
  margin-bottom: 8px;
}

.filter-input,
.filter-select {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  color: #374151;
  background: white;
  transition: border-color 0.2s;
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Statistiques */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

@media (min-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.stat-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  padding: 20px;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-value.draft {
  color: #6b7280;
}

.stat-value.submitted {
  color: #3b82f6;
}

.stat-value.under_review {
  color: #f59e0b;
}

.stat-value.accepted {
  color: #10b981;
}

.stat-value.rejected {
  color: #ef4444;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

/* Liste des livrables */
.deliverables-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.deliverable-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.deliverable-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.deliverable-content {
  padding: 24px;
}

/* En-tête mission */
.mission-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.mission-label {
  font-size: 13px;
  color: #6b7280;
}

.mission-link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: color 0.2s;
}

.mission-link:hover {
  color: #2563eb;
  text-decoration: underline;
}

/* Titre et statut */
.deliverable-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.deliverable-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.deliverable-title {
  font-size: 18px;
  color: #111827;
  font-weight: 700;
  margin: 0;
}

/* Description */
.deliverable-description {
  color: #4b5563;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 20px 0;
}

.deliverable-description.empty {
  color: #9ca3af;
  font-style: italic;
}

/* Métadonnées */
.deliverable-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
  font-size: 14px;
}

.meta-link {
  color: #3b82f6;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: color 0.2s;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
}

.meta-link:hover {
  color: #2563eb;
}

.meta-link.download:hover {
  color: #2563eb;
}

.meta-link.view-mission {
  color: #6b7280;
}

.meta-link.view-mission:hover {
  color: #374151;
}

.icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* Feedback client */
.client-feedback {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.feedback-label {
  font-size: 12px;
  color: #92400e;
  font-weight: 600;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.feedback-content {
  color: #92400e;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
}

/* Actions */
.deliverable-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  text-decoration: none;
}

.action-btn.edit {
  background: #fef3c7;
  color: #d97706;
  border: 1px solid #fde68a;
}

.action-btn.edit:hover {
  background: #fde68a;
  transform: translateY(-1px);
}

.action-btn.submit {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.action-btn.submit:hover {
  background: #a7f3d0;
  transform: translateY(-1px);
}

.action-btn.delete {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fca5a5;
}

.action-btn.delete:hover {
  background: #fca5a5;
  transform: translateY(-1px);
}

.action-btn.review {
  background: #dbeafe;
  color: #1d4ed8;
  border: 1px solid #93c5fd;
}

.action-btn.review:hover {
  background: #93c5fd;
  transform: translateY(-1px);
}

.action-btn.accept {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.action-btn.accept:hover {
  background: #a7f3d0;
  transform: translateY(-1px);
}

.action-btn.reject {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fca5a5;
}

.action-btn.reject:hover {
  background: #fca5a5;
  transform: translateY(-1px);
}

/* Badges de statut */
.status-badge {
  padding: 4px 10px;
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

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  margin-bottom: 20px;
}

.modal-title {
  font-size: 20px;
  color: #111827;
  font-weight: 700;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #6b7280;
}

.modal-body {
  padding: 0 24px 24px 24px;
}

/* États */
.loading-state {
  text-align: center;
  padding: 80px 20px;
  color: #6b7280;
  font-size: 16px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: #f9fafb;
  border-radius: 16px;
  border: 2px dashed #d1d5db;
  margin-top: 20px;
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
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

/* Responsive */
@media (max-width: 768px) {
  .my-deliverables-page {
    margin-top: 80px;
    padding: 0 16px;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .action-header {
    justify-content: center;
  }
  
  .action-btn.primary {
    width: 100%;
    justify-content: center;
  }
  
  .filters-card {
    padding: 20px;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .deliverable-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .deliverable-title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .deliverable-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .deliverable-actions {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
    justify-content: center;
  }
  
  .modal-content {
    margin: 0 16px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-value {
    font-size: 28px;
  }
}
.my-deliverables-page {
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
  color: #6b7280;
  font-size: 16px;
  margin: 0;
}

/* Filtres */
.filters-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
  padding: 24px;
  margin-bottom: 24px;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 20px;
}

@media (min-width: 768px) {
  .filters-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
  margin-bottom: 8px;
}

.filter-input,
.filter-select {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  color: #374151;
  background: white;
  transition: border-color 0.2s;
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Statistiques */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

@media (min-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.stat-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  padding: 20px;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-value.draft {
  color: #6b7280;
}

.stat-value.submitted {
  color: #3b82f6;
}

.stat-value.under_review {
  color: #f59e0b;
}

.stat-value.accepted {
  color: #10b981;
}

.stat-value.rejected {
  color: #ef4444;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

/* Liste des livrables */
.deliverables-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.deliverable-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.deliverable-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.deliverable-content {
  padding: 24px;
}

/* En-tête mission */
.mission-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.mission-label {
  font-size: 13px;
  color: #6b7280;
}

.mission-link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: color 0.2s;
}

.mission-link:hover {
  color: #2563eb;
  text-decoration: underline;
}

/* Titre et statut */
.deliverable-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.deliverable-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.deliverable-title {
  font-size: 18px;
  color: #111827;
  font-weight: 700;
  margin: 0;
}

/* Description */
.deliverable-description {
  color: #4b5563;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 20px 0;
}

.deliverable-description.empty {
  color: #9ca3af;
  font-style: italic;
}

/* Métadonnées */
.deliverable-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
  font-size: 14px;
}

.meta-link {
  color: #3b82f6;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: color 0.2s;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
}

.meta-link:hover {
  color: #2563eb;
}

.meta-link.download:hover {
  color: #2563eb;
}

.meta-link.view-mission {
  color: #6b7280;
}

.meta-link.view-mission:hover {
  color: #374151;
}

.icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* Feedback client */
.client-feedback {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.feedback-label {
  font-size: 12px;
  color: #92400e;
  font-weight: 600;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.feedback-content {
  color: #92400e;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
}

/* Actions */
.deliverable-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  text-decoration: none;
}

.action-btn.edit {
  background: #fef3c7;
  color: #d97706;
  border: 1px solid #fde68a;
}

.action-btn.edit:hover {
  background: #fde68a;
}

.action-btn.submit {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.action-btn.submit:hover {
  background: #a7f3d0;
}

.action-btn.delete {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fca5a5;
}

.action-btn.delete:hover {
  background: #fca5a5;
}

.action-btn.review {
  background: #dbeafe;
  color: #1d4ed8;
  border: 1px solid #93c5fd;
}

.action-btn.review:hover {
  background: #93c5fd;
}

.action-btn.accept {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.action-btn.accept:hover {
  background: #a7f3d0;
}

.action-btn.reject {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fca5a5;
}

.action-btn.reject:hover {
  background: #fca5a5;
}

/* Badges de statut */
.status-badge {
  padding: 4px 10px;
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

/* Modal d'édition */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  margin-bottom: 20px;
}

.modal-title {
  font-size: 20px;
  color: #111827;
  font-weight: 700;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #6b7280;
}

.modal-body {
  padding: 0 24px 24px 24px;
}

/* États */
.loading-state {
  text-align: center;
  padding: 80px 20px;
  color: #6b7280;
  font-size: 16px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: #f9fafb;
  border-radius: 16px;
  border: 2px dashed #d1d5db;
  margin-top: 20px;
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
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

/* Responsive */
@media (max-width: 768px) {
  .my-deliverables-page {
    margin-top: 80px;
    padding: 0 16px;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .filters-card {
    padding: 20px;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .deliverable-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .deliverable-title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .deliverable-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .deliverable-actions {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
    justify-content: center;
  }
  
  .modal-content {
    margin: 0 16px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-value {
    font-size: 28px;
  }
}
</style>