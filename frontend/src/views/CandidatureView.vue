<template>
  <div class="my-applications-page">
    <div class="header-row">
      <h1><i class="fas fa-list"></i> Mes candidatures</h1>
        <button @click="livrables" class="create-deliverable-btns">
         <i class="fas fa-list"></i>  Mes livrables
        </button>
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
        <!-- En-tête avec statut -->
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
          
          <!-- Boutons d'action selon le statut -->
          <div class="action-buttons">
            <button 
              @click="cancelApplication(app.id)"
              v-if="app.status === 'pending'"
              class="cancel-btn"
              :disabled="cancellingApp === app.id"
            >
              <i class="fas fa-times"></i>
              Annuler
            </button>
            
            <!-- Bouton pour créer un livrable si accepté -->
            <button 
              @click="createDeliverableForMission(app)"
              v-if="app.status === 'accepted' && app.mission?.status === 'in_progress'"
              class="create-deliverable-btn"
            >
              <i class="fas fa-file-upload"></i>
              Créer livrable
            </button>
            
            <!-- Bouton de chat si mission acceptée -->
            <button
              v-if="app.status === 'accepted' && app.mission?.status === 'in_progress'"
              class="btn-chat"
              @click="openMissionChat(app.mission)"
              :disabled="actionLoading"
              :title="hasUnreadChatMessages(app.mission) ? 'Nouveaux messages disponibles' : 'Ouvrir la conversation'"
            >
              <i class="fas fa-comments"></i>
              <span>Messages</span>
              <span v-if="hasUnreadChatMessages(app.mission)" class="unread-chat-count">
                {{ getUnreadChatCount(app.mission) }}
              </span>
            </button>
          </div>
        </div>

        <!-- Informations de la mission -->
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
            
            <div class="detail">
              <i class="fas fa-info-circle"></i>
              <span>Statut mission: <strong>{{ getMissionStatusLabel(app.mission?.status) }}</strong></span>
            </div>
          </div>

          <!-- Message de candidature -->
          <div v-if="app.message" class="application-message">
            <i class="fas fa-comment"></i>
            <div class="message-content">
              <strong>Votre message:</strong>
              <p>{{ app.message }}</p>
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

        <!-- Informations client -->
        <div v-if="getClientInfo(app)" class="client-info">
          <div class="client-label">
            <i class="fas fa-user-tie"></i>
            <span>Client</span>
          </div>
          <div class="client-details">
            <p class="client-name">{{ getClientName(app) }}</p>
            <div v-if="getClientRating(app)" class="client-rating">
              <i class="fas fa-star"></i>
              <span>{{ getClientRating(app) }}/5</span>
            </div>
          </div>
        </div>

        <!-- Feedback si rejeté -->
        <div v-if="app.status === 'rejected' && app.feedback" class="feedback-section">
          <div class="feedback-label">
            <i class="fas fa-comment-alt"></i>
            <span>Feedback du client</span>
          </div>
          <p class="feedback-content">{{ app.feedback }}</p>
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
          
          <button 
            @click="viewMissionDeliverables(getMissionId(app))"
            v-if="app.status === 'accepted'"
            class="btn-deliverables"
          >
            <i class="fas fa-file-alt"></i>
            Voir livrables
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
    
    <!-- Modal de création de livrable -->
    <div v-if="showDeliverableModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3><i class="fas fa-file-upload"></i> Créer un livrable</h3>
          <button @click="closeDeliverableModal" class="modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <p class="modal-info">
            Pour la mission: <strong>{{ selectedMissionTitle }}</strong>
          </p>
          <DeliverableForm
            :mission-id="selectedMissionId"
            @submit="handleDeliverableSubmit"
            @cancel="closeDeliverableModal"
          />
        </div>
      </div>
    </div>

    <!-- Chat Modal -->
    <ChatModal 
      :is-open="isChatModalOpen" 
      @close="closeChatModal"
      @open-support="openSupportChat"
    />
  </div>
</template>


<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePostulationStore } from '@/stores/postulations'
import { useDeliverablesStore } from '@/stores/deliverables'
import { useChatStore } from '@/stores/chat'
import DeliverableForm from '@/components/deliverables/DeliverableForm.vue'
import ChatModal from '@/components/chats/ChatModal.vue'

const router = useRouter()
const postulationsStore = usePostulationStore()
const deliverablesStore = useDeliverablesStore()
const chatStore = useChatStore()

// =======================
// STATE
// =======================
const statusFilter = ref('')
const cancellingApp = ref(null)
const showDeliverableModal = ref(false)
const selectedMissionId = ref(null)
const selectedMissionTitle = ref('')
const actionLoading = ref(false)

// =======================
// CONSTANTES
// =======================
const statusFilters = [
  { value: '', label: 'Toutes' },
  { value: 'pending', label: 'En attente' },
  { value: 'accepted', label: 'Acceptées' },
  { value: 'rejected', label: 'Rejetées' },
  { value: 'cancelled', label: 'Annulées' }
]

// =======================
// LIFECYCLE
// =======================
onMounted(async () => {
  try {
    await Promise.all([
      postulationsStore.fetchMyApplications(),
      chatStore.fetchMyChats()
    ])
    chatStore.startPolling()
  } catch (error) {
    console.error("Erreur lors de l'initialisation des données:", error)
  }
})

onUnmounted(() => {
  chatStore.stopPolling()
})

// =======================
// CHAT MODAL & ACTIONS
// =======================
const isChatModalOpen = computed(() => chatStore.isChatModalOpen)
const closeChatModal = () => chatStore.closeChatModal()

/**
 * ✅ Correction du warning : Cette fonction doit exister car elle est 
 * appelée par @open-support="openSupportChat" dans le template
 */
const openSupportChat = async () => {
  try {
    actionLoading.value = true
    await chatStore.openSupportChat()
  } catch (error) {
    console.error("Impossible d'ouvrir le support:", error)
  } finally {
    actionLoading.value = false
  }
}

const hasUnreadChatMessages = (mission) => {
  const mId = mission?.id || mission?._id
  if (!mId) return false
  return chatStore.hasUnreadMissionMessages(mId)
}

const getUnreadChatCount = (mission) => {
  const mId = mission?.id || mission?._id
  if (!mId) return 0
  return chatStore.getMissionChat(mId)?.unread_count || 0
}

/**
 * ✅ Correction de la redirection : On force la récupération du chat de mission
 * avant de l'activer pour éviter de tomber sur le support par défaut.
 */
const openMissionChat = async (mission) => {
  const mId = mission?.id || mission?._id
  if (!mId) return
  
  actionLoading.value = true
  try {
    // 1. Récupère ou crée spécifiquement le chat lié à la mission
    const chat = await chatStore.getOrCreateMissionChat(mId)
    
    // 2. Définit ce chat comme étant le chat actif
    if (chat) {
      await chatStore.setActiveChat(chat)
    }
  } catch (error) {
    console.error("Erreur lors de l'ouverture du chat mission:", error)
  } finally {
    actionLoading.value = false
  }
}

// =======================
// COMPUTED (Filtrage)
// =======================
const filteredApplications = computed(() => {
  let apps = postulationsStore.myApplications || []
  if (statusFilter.value) {
    apps = apps.filter(app => app.status === statusFilter.value)
  }
  return [...apps].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const statusStats = computed(() =>
  statusFilters
    .filter(f => f.value)
    .map(f => ({
      status: f.value,
      label: f.label,
      count: getCountByStatus(f.value)
    }))
)

// =======================
// HELPERS (Formatage & UI)
// =======================
const getCountByStatus = (status) =>
  (postulationsStore.myApplications || []).filter(a =>
    status ? a.status === status : true
  ).length

const getMissionId = (app) => app?.mission_id || app?.mission?.id || null
const getMissionTitle = (app) => app?.mission?.title || 'Mission non trouvée'
const getMissionBudget = (app) => app?.mission?.budget ? `${app.mission.budget} €` : 'Budget non spécifié'
const getMissionDeadline = (app) => app?.mission?.deadline || null
const getMissionSkills = (app) => Array.isArray(app?.mission?.required_skills) ? app.mission.required_skills : []

const getMissionStatusLabel = (status) => ({
  draft: 'Brouillon', open: 'Publiée', in_progress: 'En cours', completed: 'Terminée', cancelled: 'Annulée'
}[status] || status)

const getStatusLabel = (status) => ({
  pending: 'En attente', accepted: 'Acceptée', rejected: 'Rejetée', cancelled: 'Annulée'
}[status] || status)

const getStatusIcon = (status) => ({
  pending: 'fas fa-hourglass-half', accepted: 'fas fa-check-circle', rejected: 'fas fa-times-circle', cancelled: 'fas fa-ban'
}[status] || 'fas fa-question-circle')

const formatDate = (date) => date ? new Date(date).toLocaleDateString('fr-FR') : ''
const getClientInfo = (app) => !!app?.client
const getClientName = (app) => app?.client?.fullname || app?.client?.company_name || app?.client?.username || 'Client'
const getClientRating = (app) => app?.client?.rating || null

// =======================
// ACTIONS (Boutons)
// =======================
const setStatusFilter = (status) => { statusFilter.value = status }
const viewMission = (missionId) => { if (missionId) router.push(`/missions/${missionId}`) }
const viewMissionDeliverables = (missionId) => { if (missionId) router.push(`/missions/${missionId}/deliverables`) }
const livrables = () => { router.push('/my-deliverables') }

const reload = async () => {
  statusFilter.value = ''
  actionLoading.value = true
  await Promise.all([
    postulationsStore.fetchMyApplications(),
    chatStore.fetchMyChats()
  ])
  actionLoading.value = false
}

const cancelApplication = async (appId) => {
  if (!confirm('Annuler cette candidature ?')) return
  cancellingApp.value = appId
  try {
    await postulationsStore.cancelApplication(appId)
    await postulationsStore.fetchMyApplications()
  } finally {
    cancellingApp.value = null
  }
}

// =======================
// DELIVERABLES
// =======================
const createDeliverableForMission = (app) => {
  selectedMissionId.value = getMissionId(app)
  selectedMissionTitle.value = getMissionTitle(app)
  showDeliverableModal.value = true
}

const closeDeliverableModal = () => {
  showDeliverableModal.value = false
  selectedMissionId.value = null
}

const handleDeliverableSubmit = async (formData) => {
  try {
    await deliverablesStore.createDeliverable(formData)
    closeDeliverableModal()
    router.push(`/missions/${selectedMissionId.value}/deliverables`)
  } catch (error) {
    console.error("Erreur création livrable:", error)
  }
}
</script>


<style scoped>
/* =========================
   STYLES POUR LE CHAT MODAL (AJOUTÉS)
========================= */
.chat-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.3s ease;
}

.chat-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 2px solid #e5e7eb;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-body {
  padding: 40px 20px;
}

.chat-placeholder {
  text-align: center;
}

.placeholder-icon {
  color: #cbd5e1;
  margin-bottom: 20px;
}

.placeholder-icon i {
  opacity: 0.5;
}

.chat-placeholder h4 {
  font-size: 24px;
  color: #1e293b;
  margin-bottom: 10px;
}

.chat-placeholder p {
  color: #64748b;
  font-size: 16px;
  margin-bottom: 30px;
  line-height: 1.6;
}

.placeholder-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-support {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-support:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
}

.btn-close {
  background: #f1f5f9;
  color: #64748b;
  border: 2px solid #e2e8f0;
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-close:hover {
  background: #e2e8f0;
  transform: translateY(-2px);
}

/* =========================
   STYLES POUR LE BOUTON CHAT DANS LA CARTE
========================= */
.btn-chat {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
}

.btn-chat:hover:not(:disabled) {
  background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
}

.btn-chat:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.unread-chat-count {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

/* =========================
   AJOUTER AUX BOUTONS D'ACTION EXISTANTS
========================= */
.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
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
  transform: translateY(-1px);
}

.cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.create-deliverable-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.create-deliverable-btn:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

/* =========================
   RESPONSIVE POUR LES NOUVEAUX BOUTONS
========================= */
@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .cancel-btn,
  .create-deliverable-btn,
  .btn-chat {
    width: 100%;
    justify-content: center;
  }
  
  .chat-modal {
    width: 95%;
    margin: 0 10px;
  }
  
  .modal-body {
    padding: 30px 15px;
  }
  
  .placeholder-actions {
    flex-direction: column;
  }
  
  .btn-support,
  .btn-close {
    width: 100%;
    justify-content: center;
  }
}
.create-deliverable-btns {
 padding: 10px 20px;
 font-size: 27px;
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
@media (max-width: 480px) {
  .application-card {
    padding: 20px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .action-buttons {
    margin-top: 15px;
    width: 100%;
  }
}

/*===================
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
  position: relative;
  overflow: hidden;
}

.application-card.accepted::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
  clip-path: polygon(100% 0, 0 0, 100% 100%);
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
  animation: pulse 2s infinite;
}

.status-badge.rejected {
  background: #fee2e2;
  color: #b91c1c;
}

.status-badge.cancelled {
  background: #f3f4f6;
  color: #4b5563;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(16, 185, 129, 0);
  }
}

.application-date {
  font-size: 14px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Boutons d'action */
.action-buttons {
  display: flex;
  gap: 10px;
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
  transform: translateY(-1px);
}

.cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.create-deliverable-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.create-deliverable-btn:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
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

/* Message de candidature */
.application-message {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 15px;
  display: flex;
  gap: 10px;
}

.application-message i {
  color: #0ea5e9;
  font-size: 16px;
  margin-top: 2px;
}

.message-content {
  flex: 1;
}

.message-content strong {
  display: block;
  font-size: 13px;
  color: #0369a1;
  margin-bottom: 4px;
}

.message-content p {
  margin: 0;
  font-size: 14px;
  color: #0c4a6e;
  line-height: 1.4;
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

.client-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.client-name {
  font-size: 16px;
  color: #1e293b;
  font-weight: 600;
  margin: 0;
}

.client-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #fffbeb;
  color: #f59e0b;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}

/* Feedback */
.feedback-section {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 20px;
}

.feedback-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #dc2626;
  margin-bottom: 8px;
  font-weight: 600;
}

.feedback-content {
  font-size: 14px;
  color: #991b1b;
  margin: 0;
  line-height: 1.4;
}

/* Actions */
.card-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
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

.btn-deliverables {
  padding: 10px 20px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
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

.btn-deliverables:hover {
  background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.3);
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
}

.stat-item:nth-child(1) .stat-value {
  color: #3b82f6;
}

.stat-item:nth-child(2) .stat-value {
  color: #f59e0b;
}

.stat-item:nth-child(3) .stat-value {
  color: #10b981;
}

.stat-item:nth-child(4) .stat-value {
  color: #ef4444;
}

.stat-item:nth-child(5) .stat-value {
  color: #6b7280;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 600;
}

/* =========================
   MODAL
========================= */
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
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  margin-bottom: 20px;
}

.modal-header h3 {
  font-size: 20px;
  color: #111827;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
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

.modal-info {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 10px;
  padding: 12px 16px;
  color: #0369a1;
  margin-bottom: 20px;
  font-size: 14px;
}

.modal-info strong {
  color: #1e293b;
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
  
  .action-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .cancel-btn,
  .create-deliverable-btn {
    width: 100%;
    justify-content: center;
  }
  
  .client-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .card-actions {
    flex-direction: column;
  }
  
  .btn-details,
  .btn-deliverables {
    width: 100%;
    justify-content: center;
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
  
  .status-filters {
    justify-content: center;
  }
  
  .status-filter-btn {
    flex: 1;
    min-width: 100px;
    text-align: center;
  }
  
  .modal-content {
    margin: 0 16px;
  }
}
</style>
