<template>
  <div class="client-missions-page">
    <div class="header-row">
      <h1>Mes missions</h1>
      <button class="create-btn" @click="router.push('/missions/create')">
        <i class="fas fa-plus"></i> Nouvelle mission
      </button>
    </div>

    <!-- Chargement initial -->
    <div v-if="loading && missionsStore.myMissions.length === 0" class="loading">
      <div class="spinner"></div>
      <p>Chargement de vos missions...</p>
    </div>

    <!-- Erreur -->
    <div v-if="error" class="error">
      <i class="fas fa-exclamation-triangle"></i>
      {{ error }}
      <button @click="loadMissions" class="retry-btn">Réessayer</button>
    </div>

    <!-- Aucune mission -->
    <div
      v-if="!loading && missionsStore.myMissions.length === 0 && !error"
      class="no-missions"
    >
      <div class="empty-state">
        <i class="fas fa-clipboard-list"></i>
        <h3>Vous n'avez pas encore créé de mission</h3>
        <p>Commencez par créer votre première mission pour trouver le freelance idéal</p>
        <button @click="router.push('/missions/create')" class="create-first-btn">
          <i class="fas fa-rocket"></i> Créer ma première mission
        </button>
      </div>
    </div>

    <!-- Liste des missions -->
    <div v-if="missionsStore.myMissions.length > 0" class="missions-container">
      <!-- Filtres et statistiques -->
      <div class="filters">
        <div class="filter-section">
          <div class="filter-group">
            <label for="statusFilter">
              <i class="fas fa-filter"></i> Filtrer par statut :
            </label>
            <select id="statusFilter" v-model="selectedStatus" @change="filterMissions">
              <option value="">Tous les statuts</option>
              <option value="draft">Brouillons</option>
              <option value="open">Publiées</option>
              <option value="in_progress">En cours</option>
              <option value="completed">Terminées</option>
              <option value="cancelled">Annulées</option>
            </select>
          </div>
          
          <div class="search-group">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Rechercher une mission..."
              class="search-input"
            />
            <i class="fas fa-search search-icon"></i>
          </div>
        </div>

        <div class="stats-section">
          <div class="stats">
            <div class="stat-card total">
              <i class="fas fa-briefcase"></i>
              <div class="stat-info">
                <span class="stat-value">{{ missionsStore.myMissions.length }}</span>
                <span class="stat-label">Total</span>
              </div>
            </div>
            
            <div v-if="draftCount > 0" class="stat-card draft">
              <i class="fas fa-edit"></i>
              <div class="stat-info">
                <span class="stat-value">{{ draftCount }}</span>
                <span class="stat-label">Brouillons</span>
              </div>
            </div>
            
            <div v-if="publishedCount > 0" class="stat-card published">
              <i class="fas fa-globe"></i>
              <div class="stat-info">
                <span class="stat-value">{{ publishedCount }}</span>
                <span class="stat-label">Publiées</span>
              </div>
            </div>
            
            <div v-if="activeCount > 0" class="stat-card active">
              <i class="fas fa-play-circle"></i>
              <div class="stat-info">
                <span class="stat-value">{{ activeCount }}</span>
                <span class="stat-label">En cours</span>
              </div>
            </div>
            
            <div v-if="totalPendingApplications > 0" class="stat-card pending">
              <i class="fas fa-users"></i>
              <div class="stat-info">
                <span class="stat-value">{{ totalPendingApplications }}</span>
                <span class="stat-label">Candidatures en attente</span>
              </div>
            </div>
          </div>
          
          <div v-if="actionLoading" class="loading-indicator">
            <i class="fas fa-spinner fa-spin"></i>
            <span>Traitement en cours...</span>
          </div>
        </div>
      </div>

      <!-- Message si pas de résultats de recherche -->
      <div v-if="filteredMissions.length === 0 && searchQuery" class="no-results">
        <i class="fas fa-search"></i>
        <p>Aucune mission ne correspond à votre recherche</p>
        <button @click="clearSearch" class="clear-search-btn">
          Afficher toutes les missions
        </button>
      </div>

      <!-- Grid des missions -->
      <div class="missions-grid">
        <div
          v-for="mission in sortedMissions"
          :key="mission.id"
          class="mission-card"
          :class="getMissionCardClasses(mission)"
        >
          <!-- Badge d'état en haut -->
          <div class="mission-status-banner" :class="getStatusClass(mission.status)">
            <i :class="getStatusIcon(mission.status)"></i>
            <span>{{ getStatusText(mission.status) }}</span>
          </div>

          <!-- En-tête de la carte -->
          <div class="card-header">
            <div class="mission-title-section">
              <h3 class="mission-title">
                {{ mission.title }}
                <span v-if="mission.status === 'draft'" class="draft-indicator">
                  <i class="fas fa-pencil-alt"></i>
                </span>
              </h3>
              
              <div class="mission-urgency" v-if="mission.deadline && mission.status !== 'completed'">
                <i class="fas fa-clock"></i>
                <span :class="getUrgencyClass(mission.deadline)">
                  {{ formatDeadline(mission.deadline) }}
                </span>
              </div>
            </div>
            
            <div class="mission-meta">
              <span class="meta-item" title="Créée le">
                <i class="far fa-calendar-plus"></i>
                {{ formatDate(mission.created_at) }}
              </span>
              <span v-if="mission.updated_at !== mission.created_at" class="meta-item" title="Modifiée le">
                <i class="far fa-edit"></i>
                {{ formatDate(mission.updated_at) }}
              </span>
              <span class="meta-item" v-if="mission.views_count > 0">
                <i class="far fa-eye"></i>
                {{ mission.views_count }} vues
              </span>
            </div>
          </div>

          <!-- Description -->
          <div class="mission-description">
            <p class="desc">{{ truncateText(mission.description, 120) }}</p>
            <button 
              v-if="mission.description.length > 120" 
              class="read-more-btn"
              @click="toggleDescription(mission.id)"
            >
              {{ expandedDescriptions.has(mission.id) ? 'Voir moins' : 'Lire la suite' }}
            </button>
          </div>

          <!-- Informations détaillées -->
          <div class="mission-info">
            <div class="info-grid">
              <div class="info-item">
                <i class="fas fa-money-bill-wave"></i>
                <div class="info-content">
                  <span class="info-label">Budget</span>
                  <span class="info-value">
                    {{ mission.budget ? formatBudget(mission.budget) : 'Non spécifié' }}
                  </span>
                </div>
              </div>
              
              <div class="info-item">
                <i class="fas fa-calendar-alt"></i>
                <div class="info-content">
                  <span class="info-label">Deadline</span>
                  <span class="info-value">
                    {{ formatDate(mission.deadline) || 'Non spécifiée' }}
                  </span>
                </div>
              </div>
              
              <div class="info-item">
                <i class="fas fa-users"></i>
                <div class="info-content">
                  <span class="info-label">Candidatures</span>
                  <span class="info-value" :class="{'has-pending': mission.postulations_pending > 0}">
                    {{ mission.postulations_total || 0 }}
                    <span v-if="mission.postulations_pending > 0" class="pending-count">
                      (+{{ mission.postulations_pending }} nouvelles)
                    </span>
                  </span>
                </div>
              </div>
              
              <div class="info-item" v-if="mission.freelancer">
                <i class="fas fa-user-tie"></i>
                <div class="info-content">
                  <span class="info-label">Freelance</span>
                  <span class="info-value freelancer-name">
                    {{ mission.freelancer.full_name || 'À attribuer' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Compétences requises -->
            <div v-if="mission.required_skills && mission.required_skills.length > 0" class="skills-section">
              <div class="skills-header">
                <i class="fas fa-tools"></i>
                <h4>Compétences requises</h4>
              </div>
              <div class="skills-tags">
                <span v-for="(skill, index) in displayedSkills(mission)" :key="index" class="skill-tag">
                  {{ skill }}
                </span>
                <span v-if="mission.required_skills.length > 3" class="skill-tag more" 
                      @click="toggleSkills(mission.id)">
                  {{ expandedSkills.has(mission.id) ? 'Voir moins' : `+${mission.required_skills.length - 3}` }}
                </span>
              </div>
            </div>

            <!-- Notifications de chat -->
            <div v-if="hasUnreadChatMessages(mission)" class="chat-notification">
              <div class="chat-notification-content">
                <i class="fas fa-comment-dots"></i>
                <div class="notification-details">
                  <span class="notification-title">Nouveaux messages</span>
                  <span class="notification-count">
                    {{ getUnreadChatCount(mission) }} message(s) non lu(s)
                  </span>
                </div>
                <button class="open-chat-btn" @click="openMissionChat(mission)">
                  <i class="fas fa-external-link-alt"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Formulaire de modification -->
          <div v-if="editingMission === mission.id" class="edit-form">
            <div class="edit-form-header">
              <h4><i class="fas fa-edit"></i> Modifier la mission</h4>
              <button class="close-edit-btn" @click="closeEditForm">
                <i class="fas fa-times"></i>
              </button>
            </div>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="edit-title"><i class="fas fa-heading"></i> Titre</label>
                <input id="edit-title" v-model="editForm.title" type="text" placeholder="Titre de la mission" />
              </div>
              
              <div class="form-group">
                <label for="edit-description"><i class="fas fa-align-left"></i> Description</label>
                <textarea id="edit-description" v-model="editForm.description" 
                         placeholder="Décrivez votre mission en détail..." rows="4"></textarea>
              </div>
              
              <div class="form-group">
                <label for="edit-budget"><i class="fas fa-euro-sign"></i> Budget (€)</label>
                <input id="edit-budget" v-model.number="editForm.budget" type="number" min="0" placeholder="0" />
              </div>
              
              <div class="form-group">
                <label for="edit-deadline"><i class="fas fa-calendar-day"></i> Deadline</label>
                <input id="edit-deadline" v-model="editForm.deadline" type="date" />
              </div>
              
              <div class="form-group full-width">
                <label for="edit-skills">
                  <i class="fas fa-tools"></i> Compétences requises (séparées par des virgules)
                </label>
                <input id="edit-skills" v-model="editForm.required_skills" type="text" 
                       placeholder="Ex: JavaScript, React, Node.js" />
                <span class="form-hint">Séparez chaque compétence par une virgule</span>
              </div>
            </div>
            
            <div class="form-actions">
              <button class="btn-save" @click="saveEdit" :disabled="saving">
                <i class="fas fa-save"></i>
                {{ saving ? 'Enregistrement...' : 'Enregistrer les modifications' }}
              </button>
              <button class="btn-cancel" @click="closeEditForm" :disabled="saving">
                <i class="fas fa-times"></i>
                Annuler
              </button>
            </div>
          </div>

          <!-- Actions principales -->
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
                <span v-if="mission.postulations_pending > 0" class="pending-badge">
                  {{ mission.postulations_pending }}
                </span>
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
                @click="goToLivrables(mission.id)"
                :disabled="actionLoading"
              >
                <i class="fas fa-tasks"></i> Suivre la mission
              </button>
              
              <button
                v-else-if="mission.status === 'completed'"
                class="btn-completed"
                @click="goToFins(mission.id)"
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
              
              <!-- Bouton de chat -->
              <button
                v-if="mission.status === 'in_progress'" 
                class="btn-chat"
                @click="openMissionChat(mission)"
                :disabled="actionLoading"
                :title="hasUnreadChatMessages(mission) ? 'Nouveaux messages disponibles' : 'Ouvrir la conversation'"
              >
                <i class="fas fa-comments"></i>
                <span>Messages</span>
                <span v-if="hasUnreadChatMessages(mission)" class="unread-chat-count">
                  {{ getUnreadChatCount(mission) }}
                </span>
              </button>
            </div>

            <!-- Actions secondaires -->
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
                @click="openCompleteModal(mission)"
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
                :disabled="actionLoading || !canDeleteMission(mission)"
                :title="getDeleteTooltip(mission)"
              >
                <i class="fas fa-trash"></i> Supprimer
              </button>
              
              <button class="btn-more" @click="toggleMoreActions(mission.id)">
                <i class="fas fa-ellipsis-h"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          class="page-btn prev" 
          @click="prevPage" 
          :disabled="currentPage === 1"
        >
          <i class="fas fa-chevron-left"></i> Précédent
        </button>
        
        <div class="page-numbers">
          <button
            v-for="page in visiblePages"
            :key="page"
            class="page-number"
            :class="{ active: page === currentPage }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
          <span v-if="showEllipsis" class="ellipsis">...</span>
        </div>
        
        <button 
          class="page-btn next" 
          @click="nextPage" 
          :disabled="currentPage === totalPages"
        >
          Suivant <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>

    <!-- Modal de notation pour la complétion -->
    <div v-if="showCompleteModal" class="modal-overlay" @click.self="closeCompleteModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2><i class="fas fa-flag-checkered"></i> Finaliser la mission</h2>
          <button class="modal-close" @click="closeCompleteModal" :disabled="isCompleting">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <!-- Informations de la mission -->
          <div class="mission-summary">
            <h3>
              <i class="fas fa-briefcase"></i>
              Mission #{{ currentMissionForCompletion?.id }}: {{ currentMissionForCompletion?.title }}
            </h3>
            <p class="mission-desc">{{ currentMissionForCompletion?.description }}</p>
          </div>

          <!-- Freelance info -->
          <div class="freelance-info" v-if="acceptedFreelance">
            <h4><i class="fas fa-user-tie"></i> Freelance à évaluer :</h4>
            <div class="freelance-card">
              <div class="freelance-avatar">
                {{ freelanceInitials }}
              </div>
              <div class="freelance-details">
                <h5>{{ acceptedFreelance.full_name }}</h5>
                <p>{{ acceptedFreelance.title || 'Freelance' }}</p>
                <div class="freelance-rating">
                  <div class="stars">
                    <span v-for="i in 5" :key="i" class="star">
                      {{ i <= (acceptedFreelance.rating || 0) ? '★' : '☆' }}
                    </span>
                  </div>
                  <span class="rating-text">
                    {{ (acceptedFreelance.rating || 0).toFixed(1) }} ({{ acceptedFreelance.completed_projects || 0 }} projets)
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Évaluation -->
          <div class="evaluation-section">
            <h4><i class="fas fa-star"></i> Évaluation du freelance</h4>
            <p class="modal-subtitle">Donnez une note et un commentaire pour ce freelance (optionnel)</p>
            
            <!-- Note -->
            <div class="rating-input">
              <label>Note :</label>
              <div class="star-rating">
                <button
                  v-for="star in 5"
                  :key="star"
                  type="button"
                  @click="ratingValue = star"
                  :class="['star-btn', star <= ratingValue ? 'selected' : '']"
                >
                  ★
                </button>
                <span class="rating-display">{{ ratingValue }}/5</span>
              </div>
              <p class="rating-hint">Cliquez sur les étoiles pour attribuer une note</p>
            </div>

            <!-- Commentaire -->
            <div class="feedback-input">
              <label>Commentaire :</label>
              <textarea
                v-model="feedbackText"
                placeholder="Partagez votre expérience avec ce freelance..."
                rows="4"
                maxlength="500"
                class="feedback-textarea"
              ></textarea>
              <div class="char-counter">
                <span :class="feedbackText.length > 450 ? 'warning' : ''">
                  {{ feedbackText.length }}/500
                </span>
              </div>
            </div>

            <!-- Aperçu -->
            <div v-if="ratingValue > 0 || feedbackText" class="preview-section">
              <h5>Aperçu de votre évaluation :</h5>
              <div v-if="ratingValue > 0" class="preview-rating">
                <span>Note :</span>
                <div class="stars">
                  <span v-for="i in 5" :key="i" class="star">
                    {{ i <= ratingValue ? '★' : '☆' }}
                  </span>
                </div>
                <span class="rating-text">{{ ratingValue }}/5</span>
              </div>
              <div v-if="feedbackText" class="preview-feedback">
                <span>Commentaire :</span>
                <p>{{ feedbackText }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="closeCompleteModal" :disabled="isCompleting">
            <i class="fas fa-times"></i> Annuler
          </button>
          <button class="btn-modal-complete-no-eval" @click="completeWithoutEvaluation" :disabled="isCompleting">
            <i class="fas fa-flag"></i> Compléter sans évaluer
          </button>
          <button class="btn-modal-submit" @click="submitEvaluation" :disabled="isCompleting">
            <span v-if="isCompleting">
              <i class="fas fa-spinner fa-spin"></i> Traitement...
            </span>
            <span v-else>
              <i class="fas fa-check-circle"></i> Finaliser avec évaluation
            </span>
          </button>
        </div>

        <!-- Messages d'erreur -->
        <div v-if="completeError" class="modal-error">
          <i class="fas fa-exclamation-circle"></i> {{ completeError }}
        </div>
      </div>
    </div>

    <!-- Modal d'actions supplémentaires -->
    <div v-if="showMoreActions" class="modal-overlay" @click.self="closeMoreActions">
      <div class="modal-content small">
        <div class="modal-header">
          <h3>Actions supplémentaires</h3>
          <button class="modal-close" @click="closeMoreActions">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="more-actions-list">
            <button @click="exportMission(currentMissionMoreActions)" class="more-action-btn">
              <i class="fas fa-file-export"></i> Exporter
            </button>
            <button @click="shareMission(currentMissionMoreActions)" class="more-action-btn">
              <i class="fas fa-share-alt"></i> Partager
            </button>
            <button @click="archiveMission(currentMissionMoreActions)" class="more-action-btn">
              <i class="fas fa-archive"></i> Archiver
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Modal (UN SEUL APPEL) -->
    <ChatModal 
      :is-open="isChatModalOpen" 
      @close="closeChatModal"
      @open-support="openSupportChat"
    />
  </div>
</template>
<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useMissionStore } from '@/stores/missions'
import { useChatStore } from '@/stores/chat'
import { useRouter } from 'vue-router'
import axios from 'axios'
import ChatModal from '@/components/chats/ChatModal.vue'

const missionsStore = useMissionStore()
const chatStore = useChatStore()
const router = useRouter()

// ====== ÉTATS ======
const selectedStatus = ref('')
const searchQuery = ref('')
const editingMission = ref(null)
const loading = ref(false)
const saving = ref(false)
const actionLoading = ref(false)
const error = ref(null)
const expandedDescriptions = ref(new Set())
const expandedSkills = ref(new Set())

// États pour la modal de complétion
const showCompleteModal = ref(false)
const isCompleting = ref(false)
const currentMissionForCompletion = ref(null)
const acceptedFreelance = ref(null)
const ratingValue = ref(0)
const feedbackText = ref('')
const completeError = ref('')

// États pour les actions supplémentaires
const showMoreActions = ref(false)
const currentMissionMoreActions = ref(null)

// État pour le chat modal (simple et direct)
const isChatModalOpen = ref(false)

// Pagination
const currentPage = ref(1)
const pageSize = ref(10)

const editForm = reactive({
  title: '',
  description: '',
  budget: null,
  deadline: '',
  required_skills: ''
})

// ====== COMPUTED PROPERTIES ======
const draftCount = computed(() => missionsStore.draftMissions.length)
const publishedCount = computed(() => missionsStore.publishedMissions.length)
const activeCount = computed(() => missionsStore.myMissions.filter(m => m.status === 'in_progress').length)
const totalPendingApplications = computed(() => missionsStore.totalPendingApplications)

const filteredMissions = computed(() => {
  let missions = missionsStore.myMissions
  
  if (selectedStatus.value) {
    missions = missions.filter(m => m.status === selectedStatus.value)
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    missions = missions.filter(m => 
      m.title.toLowerCase().includes(query) ||
      m.description.toLowerCase().includes(query) ||
      (m.required_skills && m.required_skills.some(skill => 
        skill.toLowerCase().includes(query)
      ))
    )
  }
  
  return missions
})

const sortedMissions = computed(() => {
  return [...filteredMissions.value].sort((a, b) => {
    // Priorité aux messages non lus
    const aHasUnread = hasUnreadChatMessages(a)
    const bHasUnread = hasUnreadChatMessages(b)
    if (aHasUnread && !bHasUnread) return -1
    if (!aHasUnread && bHasUnread) return 1
    
    // Ensuite par date de mise à jour
    return new Date(b.updated_at) - new Date(a.updated_at)
  }).slice((currentPage.value - 1) * pageSize.value, currentPage.value * pageSize.value)
})

const totalPages = computed(() => Math.ceil(filteredMissions.value.length / pageSize.value))

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const showEllipsis = computed(() => totalPages.value > visiblePages.value.length)

const freelanceInitials = computed(() => {
  if (!acceptedFreelance.value?.full_name) return 'F'
  return acceptedFreelance.value.full_name
    .split(' ')
    .map(name => name[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

// ====== LIFECYCLE HOOKS ======
onMounted(async () => {
  await Promise.all([
    loadMissions(),
    loadChats()
  ])
})

// ====== FONCTIONS DE CHARGEMENT ======
const loadChats = async () => {
  try {
    await chatStore.fetchMyChats()
  } catch (error) {
    console.warn('Impossible de charger les conversations:', error)
  }
}

const loadMissions = async () => {
  loading.value = true
  error.value = null
  try {
    await missionsStore.fetchClientMissions()
  } catch (err) {
    console.error('Erreur lors du chargement:', err)
    error.value = err.response?.data?.error || err.message || 'Erreur de chargement'
  } finally {
    loading.value = false
  }
}

// ====== FONCTIONS UTILITAIRES ======
const formatDate = dateString => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric'
  })
}

const formatDeadline = deadline => {
  if (!deadline) return ''
  const now = new Date()
  const deadlineDate = new Date(deadline)
  const diffDays = Math.ceil((deadlineDate - now) / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return 'Dépassé'
  if (diffDays === 0) return "Aujourd'hui"
  if (diffDays === 1) return 'Demain'
  if (diffDays < 7) return `Dans ${diffDays} jours`
  if (diffDays < 30) return `Dans ${Math.floor(diffDays / 7)} semaines`
  return formatDate(deadline)
}

const getUrgencyClass = deadline => {
  if (!deadline) return ''
  const now = new Date()
  const deadlineDate = new Date(deadline)
  const diffDays = Math.ceil((deadlineDate - now) / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return 'urgent'
  if (diffDays <= 3) return 'urgent'
  if (diffDays <= 7) return 'warning'
  return 'normal'
}

const formatBudget = amount => {
  if (!amount) return 'Non spécifié'
  return new Intl.NumberFormat('fr-FR', { 
    style: 'currency', 
    currency: 'EUR',
    minimumFractionDigits: 0
  }).format(amount)
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

const getStatusIcon = status => ({
  draft: 'fas fa-edit',
  open: 'fas fa-globe',
  in_progress: 'fas fa-play-circle',
  completed: 'fas fa-check-circle',
  cancelled: 'fas fa-times-circle'
}[status] || 'fas fa-question-circle')

const getStatusClass = status => ({
  draft: 'status-draft',
  open: 'status-published',
  in_progress: 'status-in-progress',
  completed: 'status-completed',
  cancelled: 'status-cancelled'
}[status] || 'status-default')

const getMissionCardClasses = (mission) => ({
  'draft-card': mission.status === 'draft',
  'published-card': mission.status === 'open',
  'in-progress-card': mission.status === 'in_progress',
  'completed-card': mission.status === 'completed',
  'cancelled-card': mission.status === 'cancelled',
  'has-unread-chat': hasUnreadChatMessages(mission)
})

const canDeleteMission = (mission) => {
  if (mission.status === 'open' && mission.postulations_total > 0) return false
  if (mission.status === 'in_progress') return false
  return true
}

const getDeleteTooltip = mission => {
  if (!canDeleteMission(mission)) {
    return 'Impossible de supprimer cette mission'
  }
  return 'Supprimer définitivement cette mission'
}

// ====== FONCTIONS CHAT (SANS POLLING, SANS ÉVÉNEMENTS WINDOW) ======
const hasUnreadChatMessages = (mission) => {
  const missionChat = chatStore.missionChats.find(
    chat => chat.mission_id === mission.id
  )
  return missionChat?.unread_count > 0
}

const getUnreadChatCount = (mission) => {
  const missionChat = chatStore.missionChats.find(
    chat => chat.mission_id === mission.id
  )
  return missionChat?.unread_count || 0
}

// Ouvrir chat de mission - SIMPLE ET DIRECT
const openMissionChat = async (mission) => {
  if (!mission || !mission.id) {
    console.error('Mission non définie')
    return
  }
  
  actionLoading.value = true
  try {
    // Charger les chats si nécessaire
    if (chatStore.chats.length === 0) {
      await chatStore.fetchMyChats()
    }
    
    // Créer ou récupérer le chat
    const chat = await chatStore.getOrCreateMissionChat(mission.id)
    
    // Charger les messages
    await chatStore.fetchChatMessages(chat.id)
    
    // Marquer comme lu
    if (chat.unread_count > 0) {
      await chatStore.markChatAsRead(chat.id)
    }
    
    // Ouvrir le modal
    isChatModalOpen.value = true
    
  } catch (error) {
    console.error('Erreur lors de l\'ouverture du chat:', error)
    alert('Impossible d\'ouvrir la conversation. Veuillez réessayer.')
  } finally {
    actionLoading.value = false
  }
}

// Fermer le modal de chat
const closeChatModal = () => {
  isChatModalOpen.value = false
}

// Ouvrir le support
const openSupportChat = async () => {
  try {
    actionLoading.value = true
    
    await chatStore.manageSupportChat('get')
    
    const supportChat = chatStore.supportChat
    if (supportChat) {
      await chatStore.fetchChatMessages(supportChat.id)
      isChatModalOpen.value = true
    }
    
  } catch (error) {
    console.error('Erreur lors de l\'ouverture du support:', error)
    alert('Impossible d\'accéder au support. Veuillez réessayer.')
  } finally {
    actionLoading.value = false
  }
}

// ====== FONCTIONS DE COMPÉTENCES ======
const displayedSkills = (mission) => {
  if (!mission.required_skills) return []
  if (expandedSkills.value.has(mission.id)) {
    return mission.required_skills
  }
  return mission.required_skills.slice(0, 3)
}

// ====== ACTIONS DE NAVIGATION ======
const filterMissions = () => {
  currentPage.value = 1
}

const clearSearch = () => {
  searchQuery.value = ''
  selectedStatus.value = ''
  currentPage.value = 1
}

const goToDetails = id => router.push(`/client/missions/${id}`)
const goToLivrables = id => router.push(`/client/${id}/deliverables`)
const goToFins = id => router.push(`/missions/client/${id}/fins`)
const goToApplications = id => router.push(`/missions/${id}/applications`)

// ====== FONCTIONS D'AFFICHAGE ======
const toggleDescription = (missionId) => {
  if (expandedDescriptions.value.has(missionId)) {
    expandedDescriptions.value.delete(missionId)
  } else {
    expandedDescriptions.value.add(missionId)
  }
}

const toggleSkills = (missionId) => {
  if (expandedSkills.value.has(missionId)) {
    expandedSkills.value.delete(missionId)
  } else {
    expandedSkills.value.add(missionId)
  }
}

const toggleMoreActions = (missionId) => {
  const mission = missionsStore.myMissions.find(m => m.id === missionId)
  if (mission) {
    currentMissionMoreActions.value = mission
    showMoreActions.value = true
  }
}

const closeMoreActions = () => {
  showMoreActions.value = false
  currentMissionMoreActions.value = null
}

// ====== GESTION DES MISSIONS ======
const openEditForm = (mission) => {
  editingMission.value = mission.id
  editForm.title = mission.title
  editForm.description = mission.description
  editForm.budget = mission.budget
  editForm.deadline = mission.deadline ? mission.deadline.split('T')[0] : ''
  editForm.required_skills = mission.required_skills ? mission.required_skills.join(', ') : ''
}

const closeEditForm = () => {
  editingMission.value = null
  editForm.title = ''
  editForm.description = ''
  editForm.budget = null
  editForm.deadline = ''
  editForm.required_skills = ''
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
    
    const missionIndex = missionsStore.myMissions.findIndex(m => m.id === editingMission.value)
    if (missionIndex !== -1) {
      missionsStore.myMissions[missionIndex] = {
        ...missionsStore.myMissions[missionIndex],
        ...updatedMission,
        updated_at: new Date().toISOString()
      }
    }
    
    alert('Mission mise à jour avec succès !')
    closeEditForm()
  } catch (error) {
    console.error('Erreur lors de la mise à jour:', error)
    alert('Erreur lors de la mise à jour: ' + (error.response?.data?.error || error.message))
  } finally {
    saving.value = false
  }
}

const deleteMission = async (id) => {
  const mission = missionsStore.myMissions.find(m => m.id === id)
  if (!mission) return
  
  if (!canDeleteMission(mission)) {
    alert('Impossible de supprimer cette mission.')
    return
  }
  
  if (!confirm('Êtes-vous sûr de vouloir supprimer définitivement cette mission ? Cette action est irréversible.')) return
  
  actionLoading.value = true
  try {
    await missionsStore.deleteMission(id)
    
    const missionIndex = missionsStore.myMissions.findIndex(m => m.id === id)
    if (missionIndex !== -1) {
      missionsStore.myMissions.splice(missionIndex, 1)
    }
    
    alert('Mission supprimée avec succès !')
  } catch (error) {
    console.error('Erreur lors de la suppression:', error)
    alert('Erreur lors de la suppression: ' + (error.response?.data?.error || error.message))
  } finally {
    actionLoading.value = false
  }
}

const publishMission = async (id) => {
  const mission = missionsStore.myMissions.find(m => m.id === id)
  if (!mission || mission.status !== 'draft') return
  
  if (!confirm('Voulez-vous publier cette mission ? Elle sera visible par les freelances.')) return
  
  actionLoading.value = true
  try {
    await missionsStore.publishMission(id)
    
    const missionIndex = missionsStore.myMissions.findIndex(m => m.id === id)
    if (missionIndex !== -1) {
      missionsStore.myMissions[missionIndex].status = 'open'
      missionsStore.myMissions[missionIndex].updated_at = new Date().toISOString()
    }
    
    alert('Mission publiée avec succès !')
  } catch (error) {
    console.error('Erreur lors de la publication:', error)
    alert('Erreur lors de la publication: ' + (error.response?.data?.error || error.message))
  } finally {
    actionLoading.value = false
  }
}

const openCompleteModal = async (mission) => {
  if (!mission || mission.status !== 'in_progress') return
  
  ratingValue.value = 0
  feedbackText.value = ''
  completeError.value = ''
  
  try {
    currentMissionForCompletion.value = mission
    
    const token = localStorage.getItem('token')
    const response = await axios.get(`/api/missions/${mission.id}/applications/accepted`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (response.data.freelance) {
      acceptedFreelance.value = response.data.freelance
      if (acceptedFreelance.value.rating) {
        ratingValue.value = Math.round(acceptedFreelance.value.rating)
      }
    } else {
      acceptedFreelance.value = {
        full_name: 'Freelance non spécifié',
        title: '',
        rating: 0,
        completed_projects: 0
      }
    }
    
  } catch (error) {
    console.error('Erreur lors du chargement des informations:', error)
    acceptedFreelance.value = {
      full_name: 'Freelance non trouvé',
      title: '',
      rating: 0,
      completed_projects: 0
    }
  }
  
  showCompleteModal.value = true
}

const closeCompleteModal = () => {
  if (isCompleting.value) return
  
  showCompleteModal.value = false
  currentMissionForCompletion.value = null
  acceptedFreelance.value = null
  ratingValue.value = 0
  feedbackText.value = ''
  completeError.value = ''
}

const submitEvaluation = async () => {
  if (!currentMissionForCompletion.value) return
  
  isCompleting.value = true
  completeError.value = ''
  
  try {
    const evaluationData = {}
    
    if (ratingValue.value > 0) {
      evaluationData.rating = ratingValue.value
    }
    
    if (feedbackText.value.trim()) {
      evaluationData.feedback = feedbackText.value.trim()
    }
    
    await missionsStore.completeMission(currentMissionForCompletion.value.id, evaluationData)
    
    const missionIndex = missionsStore.myMissions.findIndex(m => m.id === currentMissionForCompletion.value.id)
    if (missionIndex !== -1) {
      missionsStore.myMissions[missionIndex].status = 'completed'
      missionsStore.myMissions[missionIndex].updated_at = new Date().toISOString()
    }
    
    showCompleteModal.value = false
    alert('Mission complétée avec succès ! L\'évaluation a été enregistrée.')
    
  } catch (error) {
    console.error('Erreur lors de la complétion:', error)
    completeError.value = error.response?.data?.error || error.message || 'Erreur lors de la complétion'
  } finally {
    isCompleting.value = false
  }
}

const completeWithoutEvaluation = async () => {
  if (!currentMissionForCompletion.value) return
  
  isCompleting.value = true
  completeError.value = ''
  
  try {
    await missionsStore.completeMission(currentMissionForCompletion.value.id, {})
    
    const missionIndex = missionsStore.myMissions.findIndex(m => m.id === currentMissionForCompletion.value.id)
    if (missionIndex !== -1) {
      missionsStore.myMissions[missionIndex].status = 'completed'
      missionsStore.myMissions[missionIndex].updated_at = new Date().toISOString()
    }
    
    showCompleteModal.value = false
    alert('Mission complétée sans évaluation !')
    
  } catch (error) {
    console.error('Erreur lors de la complétion:', error)
    completeError.value = error.response?.data?.error || error.message || 'Erreur lors de la complétion'
  } finally {
    isCompleting.value = false
  }
}

const cancelMission = async (id) => {
  const mission = missionsStore.myMissions.find(m => m.id === id)
  if (!mission || mission.status === 'completed' || mission.status === 'cancelled') return
  
  if (!confirm('Êtes-vous sûr de vouloir annuler cette mission ? Toutes les candidatures seront annulées.')) return
  
  actionLoading.value = true
  try {
    await missionsStore.cancelMission(id)
    
    const missionIndex = missionsStore.myMissions.findIndex(m => m.id === id)
    if (missionIndex !== -1) {
      missionsStore.myMissions[missionIndex].status = 'cancelled'
      missionsStore.myMissions[missionIndex].updated_at = new Date().toISOString()
    }
    
    alert('Mission annulée avec succès !')
  } catch (error) {
    console.error('Erreur lors de l\'annulation:', error)
    alert('Erreur lors de l\'annulation: ' + (error.response?.data?.error || error.message))
  } finally {
    actionLoading.value = false
  }
}

const duplicateMission = async (id) => {
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
    
    const newMission = await missionsStore.createMission(duplicateData)
    
    missionsStore.myMissions.unshift({
      ...newMission,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })
    
    alert('Mission dupliquée avec succès !')
  } catch (error) {
    console.error('Erreur lors de la duplication:', error)
    alert('Erreur lors de la duplication: ' + (error.response?.data?.error || error.message))
  } finally {
    actionLoading.value = false
  }
}

// ====== PAGINATION ======
const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const goToPage = (page) => {
  currentPage.value = page
}

// ====== MORE ACTIONS ======
const exportMission = async (mission) => {
  alert(`Export de la mission: ${mission.title}`)
  closeMoreActions()
}

const shareMission = async (mission) => {
  alert(`Partage de la mission: ${mission.title}`)
  closeMoreActions()
}

const archiveMission = async (mission) => {
  actionLoading.value = true
  try {
    await missionsStore.archiveMission(mission.id)
    
    const missionIndex = missionsStore.myMissions.findIndex(m => m.id === mission.id)
    if (missionIndex !== -1) {
      missionsStore.myMissions[missionIndex].is_archived = true
    }
    
    alert('Mission archivée avec succès !')
  } catch (error) {
    console.error('Erreur lors de l\'archivage:', error)
    alert('Erreur lors de l\'archivage: ' + (error.response?.data?.error || error.message))
  } finally {
    actionLoading.value = false
    closeMoreActions()
  }
}
</script>

<style scoped>
/* Base Styles */
.client-missions-page {
  margin-top: 100px;
  padding: 30px 40px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  min-height: 100vh;
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

/* Header */
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(226, 232, 240, 0.8);
}

h1 {
  font-size: 32px;
  font-weight: 800;
  color: #1e293b;
  margin: 0;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
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
  gap: 10px;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.create-btn i {
  font-size: 14px;
}

/* Loading State */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading p {
  color: #64748b;
  font-size: 16px;
  margin: 0;
}

/* Error State */
.error {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: #dc2626;
  padding: 20px 25px;
  border-radius: 12px;
  font-weight: 600;
  margin-bottom: 30px;
  text-align: center;
  border-left: 4px solid #dc2626;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.retry-btn {
  background: #dc2626;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.retry-btn:hover {
  background: #b91c1c;
}

/* Empty State */
.no-missions {
  margin-top: 60px;
}

.empty-state {
  text-align: center;
  padding: 60px 40px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  max-width: 500px;
  margin: 0 auto;
}

.empty-state i {
  font-size: 64px;
  color: #94a3b8;
  margin-bottom: 20px;
  opacity: 0.7;
}

.empty-state h3 {
  font-size: 24px;
  color: #1e293b;
  margin: 0 0 10px 0;
}

.empty-state p {
  color: #64748b;
  font-size: 16px;
  margin: 0 0 30px 0;
  line-height: 1.6;
}

.create-first-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 14px 32px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.create-first-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
}

/* Filters Section */
.filters {
  background: white;
  border-radius: 20px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.filter-section {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.filter-group {
  flex: 1;
  min-width: 250px;
}

.filter-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #475569;
  font-size: 14px;
  margin-bottom: 8px;
}

.filter-group select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  background: white;
  color: #334155;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-group select:hover {
  border-color: #94a3b8;
}

.filter-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-group {
  flex: 2;
  min-width: 300px;
  position: relative;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  color: #334155;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 14px;
}

/* Stats Section */
.stats-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.stats {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  flex: 1;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: #f8fafc;
  border-radius: 12px;
  min-width: 140px;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-card i {
  font-size: 20px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
}

.stat-card.total i {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
}

.stat-card.draft i {
  background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
  color: white;
}

.stat-card.published i {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.stat-card.active i {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.stat-card.pending i {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: #1e293b;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 4px;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  background: #fef3c7;
  color: #92400e;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
}

/* No Results */
.no-results {
  text-align: center;
  padding: 40px 20px;
  background: white;
  border-radius: 16px;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.no-results i {
  font-size: 48px;
  color: #94a3b8;
  margin-bottom: 16px;
  opacity: 0.7;
}

.no-results p {
  color: #64748b;
  font-size: 16px;
  margin: 0 0 20px 0;
}

.clear-search-btn {
  background: #e2e8f0;
  color: #475569;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-search-btn:hover {
  background: #cbd5e1;
  transform: translateY(-1px);
}

/* Missions Grid */
.missions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 28px;
  margin-bottom: 40px;
}

/* Mission Card */
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
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

/* Card Status Styles */
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

.has-unread-chat {
  border-right: 4px solid #3b82f6;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
}

/* Status Banner */
.mission-status-banner {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border: 2px solid transparent;
  align-self: flex-start;
}

.mission-status-banner.status-draft {
  background: #f1f5f9;
  color: #64748b;
  border-color: #e2e8f0;
}

.mission-status-banner.status-published {
  background: #dbeafe;
  color: #1d4ed8;
  border-color: #93c5fd;
}

.mission-status-banner.status-in-progress {
  background: #fef3c7;
  color: #92400e;
  border-color: #fcd34d;
}

.mission-status-banner.status-completed {
  background: #dcfce7;
  color: #166534;
  border-color: #86efac;
}

.mission-status-banner.status-cancelled {
  background: #fee2e2;
  color: #991b1b;
  border-color: #fca5a5;
}

/* Card Header */
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.draft-indicator {
  color: #94a3b8;
  font-size: 14px;
}

.mission-urgency {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.mission-urgency .urgent {
  color: #dc2626;
  background: #fef2f2;
}

.mission-urgency .warning {
  color: #d97706;
  background: #fef3c7;
}

.mission-urgency .normal {
  color: #059669;
  background: #dcfce7;
}

.mission-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #64748b;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-item i {
  font-size: 12px;
}

/* Description */
.mission-description {
  margin: 8px 0;
}

.desc {
  font-size: 15px;
  color: #475569;
  line-height: 1.6;
  margin: 0 0 8px 0;
}

.read-more-btn {
  background: none;
  border: none;
  color: #3b82f6;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 0;
  transition: color 0.2s ease;
}

.read-more-btn:hover {
  color: #1d4ed8;
  text-decoration: underline;
}

/* Mission Info */
.mission-info {
  background: #f8fafc;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-item i {
  font-size: 18px;
  color: #64748b;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.info-content {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-top: 2px;
}

.info-value.has-pending {
  color: #f59e0b;
}

.pending-count {
  font-size: 12px;
  color: #d97706;
  margin-left: 4px;
}

.freelancer-name {
  color: #3b82f6;
}

/* Skills Section */
.skills-section {
  margin-top: 8px;
}

.skills-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.skills-header i {
  color: #64748b;
  font-size: 16px;
}

.skills-header h4 {
  font-size: 14px;
  color: #475569;
  margin: 0;
  font-weight: 600;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag {
  background: white;
  color: #475569;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.skill-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.skill-tag.more {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
  cursor: pointer;
  font-weight: 600;
}

.skill-tag.more:hover {
  background: #2563eb;
}

/* Chat Notification */
.chat-notification {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border-radius: 12px;
  padding: 12px 16px;
  margin-top: 8px;
  animation: pulse-blue 2s infinite;
}

@keyframes pulse-blue {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

.chat-notification-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-notification i {
  font-size: 18px;
}

.notification-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.notification-title {
  font-weight: 600;
  font-size: 14px;
}

.notification-count {
  font-size: 12px;
  opacity: 0.9;
}

.open-chat-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
}

.open-chat-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Edit Form */
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

.edit-form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e2e8f0;
}

.edit-form-header h4 {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.close-edit-btn {
  background: none;
  border: none;
  color: #64748b;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.close-edit-btn:hover {
  background: #f1f5f9;
  color: #475569;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
}

.form-group input,
.form-group textarea {
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

.form-group textarea {
  min-height: 120px;
  resize: vertical;
  line-height: 1.5;
}

.form-hint {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.form-actions {
  display: flex;
  gap: 12px;
  padding-top: 20px;
  border-top: 2px solid #e2e8f0;
}

.btn-save {
  flex: 2;
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

.btn-save:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
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

.btn-cancel:hover:not(:disabled) {
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(100, 116, 139, 0.2);
}

/* Mission Actions */
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
  gap: 10px;
  position: relative;
}

/* Button Styles */
.btn-publish {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.btn-publish:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
}

.btn-view-applications {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.btn-view-applications:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
}

.pending-badge {
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
}

.btn-view-details {
  background: #e2e8f0;
  color: #475569;
}

.btn-view-details:hover:not(:disabled) {
  background: #cbd5e1;
  transform: translateY(-2px);
}

.btn-in-progress {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.btn-in-progress:hover:not(:disabled) {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.3);
}

.btn-completed {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  color: white;
}

.btn-completed:hover:not(:disabled) {
  background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
  transform: translateY(-2px);
}

.btn-chat {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
}

.btn-chat:hover:not(:disabled) {
  background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.3);
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
}

/* Secondary Actions */
.secondary-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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
  gap: 8px;
  min-width: 80px;
}

.btn-edit {
  background: #fef3c7;
  color: #92400e;
}

.btn-edit:hover:not(:disabled) {
  background: #fde68a;
  transform: translateY(-1px);
}

.btn-complete-action {
  background: #10b981;
  color: white;
}

.btn-complete-action:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-1px);
}

.btn-cancel-action {
  background: #ef4444;
  color: white;
}

.btn-cancel-action:hover:not(:disabled) {
  background: #dc2626;
  transform: translateY(-1px);
}

.btn-duplicate {
  background: #e0e7ff;
  color: #3730a3;
}

.btn-duplicate:hover:not(:disabled) {
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

.btn-more {
  background: #f1f5f9;
  color: #64748b;
  min-width: 40px !important;
  flex: none !important;
}

.btn-more:hover:not(:disabled) {
  background: #e2e8f0;
  transform: translateY(-1px);
}

/* Disabled State */
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.page-btn {
  padding: 10px 20px;
  border: 2px solid #e2e8f0;
  background: white;
  color: #475569;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-btn:hover:not(:disabled) {
  background: #f1f5f9;
  border-color: #94a3b8;
  transform: translateY(-1px);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 8px;
  align-items: center;
}

.page-number {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #e2e8f0;
  background: white;
  color: #475569;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-number:hover:not(.active) {
  background: #f1f5f9;
  border-color: #94a3b8;
}

.page-number.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.ellipsis {
  color: #94a3b8;
  padding: 0 4px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

.modal-content.small {
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 2px solid #e2e8f0;
}

.modal-header h2 {
  margin: 0;
  font-size: 24px;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: #1e293b;
}

.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.modal-close:hover:not(:disabled) {
  background: #f1f5f9;
  color: #475569;
}

.modal-body {
  padding: 24px;
}

.mission-summary {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.mission-summary h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 10px;
}

.mission-desc {
  color: #475569;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.freelance-info {
  margin-bottom: 24px;
}

.freelance-info h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #334155;
  display: flex;
  align-items: center;
  gap: 8px;
}

.freelance-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
}

.freelance-avatar {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 18px;
  flex-shrink: 0;
}

.freelance-details {
  flex: 1;
}

.freelance-details h5 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #1e293b;
}

.freelance-details p {
  margin: 0 0 8px 0;
  color: #64748b;
  font-size: 14px;
}

.freelance-rating {
  display: flex;
  align-items: center;
  gap: 8px;
}

.freelance-rating .stars {
  display: flex;
  gap: 2px;
}

.freelance-rating .star {
  font-size: 16px;
  color: #FFD700;
}

.rating-text {
  color: #64748b;
  font-size: 13px;
}

.evaluation-section {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
}

.evaluation-section h4 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-subtitle {
  color: #64748b;
  margin-bottom: 20px;
  font-size: 14px;
  line-height: 1.5;
}

.rating-input {
  margin-bottom: 24px;
}

.rating-input label {
  display: block;
  font-weight: 600;
  color: #475569;
  margin-bottom: 10px;
}

.star-rating {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.star-btn {
  background: none;
  border: none;
  font-size: 32px;
  cursor: pointer;
  color: #E5E7EB;
  transition: all 0.2s;
  padding: 4px;
  line-height: 1;
}

.star-btn.selected {
  color: #F59E0B;
  transform: scale(1.1);
}

.star-btn:hover:not(.selected) {
  color: #FBBF24;
  transform: scale(1.1);
}

.rating-display {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  min-width: 50px;
}

.rating-hint {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.feedback-input {
  margin-bottom: 20px;
}

.feedback-input label {
  display: block;
  font-weight: 600;
  color: #475569;
  margin-bottom: 10px;
}

.feedback-textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #E5E7EB;
  border-radius: 8px;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
  transition: border-color 0.2s;
  line-height: 1.5;
}

.feedback-textarea:focus {
  outline: none;
  border-color: #4A90E2;
}

.char-counter {
  text-align: right;
  margin-top: 5px;
  font-size: 12px;
  color: #666;
}

.char-counter .warning {
  color: #EF4444;
  font-weight: bold;
}

.preview-section {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-top: 20px;
  border: 1px solid #E5E7EB;
}

.preview-section h5 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #334155;
}

.preview-rating {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.preview-feedback span {
  font-weight: 600;
  color: #475569;
  display: block;
  margin-bottom: 4px;
}

.preview-feedback p {
  margin: 0;
  padding: 12px;
  background: #F9FAFB;
  border-radius: 6px;
  color: #4B5563;
  line-height: 1.5;
  font-size: 14px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 24px;
  border-top: 2px solid #e2e8f0;
}

.btn-modal-cancel,
.btn-modal-complete-no-eval,
.btn-modal-submit {
  flex: 1;
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

.btn-modal-cancel {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  color: #64748b;
}

.btn-modal-cancel:hover:not(:disabled) {
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  transform: translateY(-2px);
}

.btn-modal-complete-no-eval {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.btn-modal-complete-no-eval:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
}

.btn-modal-submit {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.btn-modal-submit:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
}

.modal-error {
  background: #FEF2F2;
  color: #DC2626;
  padding: 12px 16px;
  margin: 0 24px 24px;
  border-radius: 8px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  border-left: 4px solid #DC2626;
  font-size: 14px;
}

/* More Actions List */
.more-actions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.more-action-btn {
  padding: 12px 16px;
  border: none;
  background: white;
  color: #334155;
  text-align: left;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.more-action-btn:hover {
  background: #f8fafc;
}

/* Responsive Design */
@media (max-width: 1200px) {
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
    align-items: stretch;
    gap: 20px;
  }
  
  .create-btn {
    width: 100%;
    justify-content: center;
  }
  
  .filters {
    padding: 20px;
  }
  
  .filter-section {
    flex-direction: column;
  }
  
  .filter-group,
  .search-group {
    min-width: 100%;
  }
  
  .stats-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stats {
    justify-content: center;
  }
  
  .stat-card {
    min-width: 120px;
  }
  
  .missions-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .btn-modal-cancel,
  .btn-modal-complete-no-eval,
  .btn-modal-submit {
    width: 100%;
  }
  
  .pagination {
    flex-direction: column;
    gap: 15px;
  }
  
  .page-numbers {
    order: 1;
  }
  
  .page-btn.prev {
    order: 2;
  }
  
  .page-btn.next {
    order: 3;
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
    justify-content: center;
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
  
  .stat-card {
    min-width: 100px;
    padding: 10px 16px;
  }
  
  .stat-value {
    font-size: 20px;
  }
}

/* Animations pour les cartes */
.mission-card {
  animation: slideUp 0.5s ease-out;
}

.mission-card:nth-child(1) { animation-delay: 0.1s; }
.mission-card:nth-child(2) { animation-delay: 0.2s; }
.mission-card:nth-child(3) { animation-delay: 0.3s; }
.mission-card:nth-child(4) { animation-delay: 0.4s; }
.mission-card:nth-child(5) { animation-delay: 0.5s; }

/* Hover effects */
.mission-card:hover .mission-title {
  color: #3b82f6;
  transition: color 0.3s ease;
}

.mission-card:hover .desc {
  color: #334155;
  transition: color 0.3s ease;
}

/* Icon animations */
i {
  transition: transform 0.2s ease;
}

.btn-publish:hover i,
.btn-view-applications:hover i,
.btn-view-details:hover i,
.btn-in-progress:hover i,
.btn-completed:hover i,
.btn-chat:hover i,
.btn-save:hover i,
.btn-cancel:hover i {
  transform: translateX(3px);
}

/* Scrollbar */
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

/* Button loading state */
button:disabled::after {
  content: '';
  display: inline-block;
  width: 16px;
  height: 16px;
  margin-left: 8px;
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

/* Global transitions */
* {
  transition: background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

/* Z-index layering */
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

.modal-overlay {
  z-index: 1000;
}

/* Large screens */
@media (min-width: 1600px) {
  .missions-grid {
    grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  }
  
  .mission-card {
    padding: 32px;
  }
}
</style>