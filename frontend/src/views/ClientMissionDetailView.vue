<template>
  <div class="client-mission-details-page">
    <h1>Détails de la mission</h1>

    <!-- Chargement -->
    <div v-if="loading" class="loading">
      Chargement des informations...
    </div>

    <!-- Erreur -->
    <div v-if="error" class="error">
      {{ error }}
    </div>

    <!-- Mission introuvable -->
    <div v-if="!loading && !mission" class="no-mission">
      <p>Mission introuvable.</p>
      <button @click="router.back()" class="back-btn">Retour</button>
    </div>

    <!-- Détails mission -->
    <div v-if="mission" class="mission-card">
      <div class="mission-header">
        <h2>{{ mission.title }}</h2>
        <span class="mission-status" :class="mission.status.toLowerCase()">
          {{ getStatusText(mission.status) }}
        </span>
      </div>

      <p class="description">{{ mission.description }}</p>

      <div class="info-block">
        <p><strong>Budget :</strong> {{ mission.budget ? mission.budget + ' €' : 'Non spécifié' }}</p>

        <p v-if="mission.deadline">
          <strong>Date limite :</strong>
          {{ formatDate(mission.deadline) }}
        </p>

        <p v-if="mission.required_skills?.length">
          <strong>Compétences requises :</strong>
          {{ mission.required_skills.join(', ') }}
        </p>

        <p><strong>Statut :</strong> {{ getStatusText(mission.status) }}</p>
        <p><strong>Créée le :</strong> {{ formatDate(mission.created_at) }}</p>
        <p v-if="mission.updated_at"><strong>Modifiée le :</strong> {{ formatDate(mission.updated_at) }}</p>
        
        <!-- Statistiques de candidatures -->
        <div v-if="mission.postulations_total !== undefined" class="stats">
          <p><strong>Candidatures :</strong> 
            <span class="total">{{ mission.postulations_total }} total</span> 
            <span v-if="mission.postulations_pending > 0" class="pending">
              ({{ mission.postulations_pending }} en attente)
            </span>
          </p>
        </div>
      </div>

      <!-- Actions pour le client -->
      <div class="action-section">
        <!-- Bouton pour gérer les candidatures -->
        <router-link 
          v-if="(mission.status === 'OPEN' || mission.status === 'IN_PROGRESS') && mission.postulations_total > 0"
          :to="`/missions/${mission.id}/applications`"
          class="btn-manage"
        >
          Gérer les candidatures ({{ mission.postulations_pending || 0 }} en attente)
        </router-link>

        <!-- Boutons d'action selon le statut -->
        <div class="action-buttons">
          <!-- Publier la mission (draft → open) -->
          <button 
            v-if="mission.status === 'DRAFT'"
            @click="publishMission"
            class="btn-publish"
            :disabled="loadingAction"
          >
            Publier la mission
          </button>

          <!-- Modifier la mission (draft seulement) -->
          <button 
            v-if="mission.status === 'DRAFT'"
            @click="editMission"
            class="btn-edit"
          >
            Modifier
          </button>

          <!-- Marquer comme complétée (in_progress seulement) -->
          <button 
            v-if="mission.status === 'IN_PROGRESS'"
            @click="completeMission"
            class="btn-complete"
            :disabled="loadingAction"
          >
            Marquer comme complétée
          </button>

          <!-- Bouton pour démarrer le chat avec le freelance -->
          <button 
            v-if="mission?.status === 'IN_PROGRESS' && hasAcceptedFreelance"
            @click="openMissionChat"
            class="btn-chat"
            :disabled="loadingAction"
          >
            <i class="fas fa-comments"></i>
            Démarrer le chat
          </button>

          <!-- Annuler la mission (tous statuts sauf completed et cancelled) -->
          <button 
            v-if="mission.status !== 'COMPLETED' && mission.status !== 'CANCELLED' && mission.status !== 'IN_PROGRESS'"
            @click="cancelMission"
            class="btn-cancel"
            :disabled="loadingAction"
          >
            Annuler la mission
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useMissionStore } from '@/stores/missions'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat';
import { useRoute, useRouter } from 'vue-router'

const missionsStore = useMissionStore()
const authStore = useAuthStore()
const chatStore = useChatStore();
const route = useRoute()
const router = useRouter()

const missionId = parseInt(route.params.id)
const applications = ref([])
const loading = ref(false)
const loadingAction = ref(false)
const error = ref(null)

// Mission courante
const mission = computed(() => missionsStore.missionDetails)

// Fonctions utilitaires
const formatDate = (dateString) => {
  if (!dateString) return 'Non spécifié'
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusText = (status) => {
  const statusMap = {
    'DRAFT': 'Brouillon',
    'OPEN': 'Publiée',
    'IN_PROGRESS': 'En cours',
    'COMPLETED': 'Terminée',
    'CANCELLED': 'Annulée'
  }
  return statusMap[status] || status
}

const getApplicationStatusText = (status) => {
  const statusMap = {
    'PENDING': 'En attente',
    'ACCEPTED': 'Acceptée',
    'REJECTED': 'Refusée',
    'CANCELLED': 'Annulée'
  }
  return statusMap[status] || status
}

// Vérifier si un freelance est déjà accepté
const isFreelanceAlreadyAccepted = computed(() => {
  return applications.value.some(app => app.status === 'ACCEPTED')
})

// Vérifier s'il y a un freelance accepté
const hasAcceptedFreelance = computed(() => {
  return applications.value.some(app => app.status === 'ACCEPTED');
});

// Trouver le freelance accepté
const acceptedFreelance = computed(() => {
  return applications.value.find(app => app.status === 'ACCEPTED');
});

// Chargement des données
const loadData = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log('🔍 Chargement des détails de la mission:', missionId)
    
    // 1. Charger les détails de la mission
    await missionsStore.fetchMissionDetails(missionId)
    
    // Vérifier si la mission existe
    if (!missionsStore.missionDetails) {
      router.push(`/missions/client`)
      error.value = 'Mission non trouvée'
      return
    }
    
    console.log('✅ Mission chargée:', missionsStore.missionDetails)
    
    // 2. Charger les candidatures uniquement si l'utilisateur est le client propriétaire
    const isOwner = authStore.user?.id === missionsStore.missionDetails.client_id
    if (isOwner) {
      console.log('🔍 Chargement des candidatures (utilisateur propriétaire)')
      const apps = await missionsStore.fetchMissionApplications(missionId)
      
      // Transformer les données
      applications.value = apps.map(app => {
        const profile = app.freelance?.profile || {}
        return {
          id: app.id,
          freelance_id: app.freelance_id,
          freelancer_name: app.freelance_name || profile.full_name || `Freelance #${app.freelance_id}`,
          status: app.status,
          bio: profile.bio || 'Aucune biographie disponible',
          skills: Array.isArray(profile.skills) ? profile.skills.join(', ') : 'Compétences non spécifiées',
          proposal: app.proposal || 'Aucune lettre de motivation',
          rating: profile.rating || 0.0,
          completed_missions: profile.completed_projects || 0,
          photo: profile.url_photo || `https://i.pravatar.cc/150?img=${app.freelance_id}`,
          portfolio: app.attachments || []
        }
      })
      
      console.log('✅ Candidatures transformées:', applications.value)
    } else {
      console.log('⚠️ L\'utilisateur n\'est pas propriétaire, pas de chargement des candidatures')
      applications.value = []
    }
    
  } catch (err) {
    console.error('❌ Erreur lors du chargement:', err)
    error.value = err.response?.data?.error || err.message || 'Erreur de chargement'
  } finally {
    loading.value = false
  }
}

// Ouvrir le chat de mission
const openMissionChat = async () => {
  if (!mission.value || !acceptedFreelance.value) {
    alert('Aucun freelance accepté pour cette mission.');
    return;
  }
  
  try {
    loadingAction.value = true;
    
    // Utiliser le store chat pour récupérer ou créer le chat
    const chat = await chatStore.getOrCreateMissionChat(mission.value.id);
    
    if (chat) {
      // Naviguer vers la page de chat avec l'ID du chat
      router.push(`/chat?chatId=${chat.id}`);
    } else {
      alert('Impossible de créer ou trouver le chat.');
    }
  } catch (error) {
    console.error('Erreur lors de l\'ouverture du chat:', error);
    alert('Impossible de démarrer le chat. Veuillez réessayer.');
  } finally {
    loadingAction.value = false;
  }
}

// Actions
const acceptApplication = async (applicationId) => {
  if (!confirm('Êtes-vous sûr de vouloir accepter cette candidature ?')) return
  
  loadingAction.value = true
  try {
    // Utiliser la nouvelle méthode avec missionId et applicationId
    await missionsStore.acceptApplication(missionId, applicationId)
    alert('Candidature acceptée avec succès !')
    await loadData() // Recharger les données
  } catch (err) {
    error.value = err.response?.data?.error || 'Erreur lors de l\'acceptation'
    alert('Erreur: ' + (err.response?.data?.error || err.message))
  } finally {
    loadingAction.value = false
  }
}

const rejectApplication = async (applicationId) => {
  if (!confirm('Êtes-vous sûr de vouloir refuser cette candidature ?')) return
  
  loadingAction.value = true
  try {
    // Utiliser la nouvelle méthode avec missionId et applicationId
    await missionsStore.rejectApplication(missionId, applicationId)
    alert('Candidature refusée')
    await loadData() // Recharger les données
  } catch (err) {
    error.value = err.response?.data?.error || 'Erreur lors du refus'
    alert('Erreur: ' + (err.response?.data?.error || err.message))
  } finally {
    loadingAction.value = false
  }
}

const publishMission = async () => {
  if (!confirm('Publier cette mission ? Elle sera visible par les freelances.')) return
  
  loadingAction.value = true
  try {
    await missionsStore.publishMission(missionId)
    alert('Mission publiée avec succès !')
    await loadData()
  } catch (err) {
    error.value = err.response?.data?.error || 'Erreur lors de la publication'
    alert('Erreur: ' + (err.response?.data?.error || err.message))
  } finally {
    loadingAction.value = false
  }
}

const completeMission = async () => {
  if (!confirm('Êtes-vous sûr de vouloir marquer cette mission comme complétée ?')) return
  
  loadingAction.value = true
  try {
    await missionsStore.completeMission(missionId)
    alert('Mission marquée comme complétée !')
    await loadData()
  } catch (err) {
    error.value = err.response?.data?.error || 'Erreur lors de la complétion'
    alert('Erreur: ' + (err.response?.data?.error || err.message))
  } finally {
    loadingAction.value = false
  }
}

const cancelMission = async () => {
  if (!confirm('Êtes-vous sûr de vouloir annuler cette mission ? Toutes les candidatures seront annulées.')) return
  
  loadingAction.value = true
  try {
    await missionsStore.cancelMission(missionId)
    alert('Mission annulée !')
    await loadData()
  } catch (err) {
    error.value = err.response?.data?.error || 'Erreur lors de l\'annulation'
    alert('Erreur: ' + (err.response?.data?.error || err.message))
  } finally {
    loadingAction.value = false
  }
}

const editMission = () => {
  router.push(`/missions/${missionId}/edit`)
}

const goToProfile = (freelanceId) => {
  router.push(`/profiles/${freelanceId}`)
}

const refreshData = () => {
  loadData()
}

// Chargement initial
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.client-mission-details-page {
  max-width: 1200px;
  margin: 100px auto 50px;
  padding: 0 20px;
  font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Titres */
h1 {
  font-size: 32px;
  margin-bottom: 30px;
  color: #111827;
  font-weight: 700;
  text-align: center;
}

h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #1f2937;
  font-weight: 700;
}

/* Carte mission */
.mission-card {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  margin-bottom: 40px;
  border: 1px solid #e5e7eb;
}

.mission-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.mission-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
}

.mission-status.draft {
  background-color: #f3f4f6;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.mission-status.open {
  background-color: #dbeafe;
  color: #1d4ed8;
  border: 1px solid #93c5fd;
}

.mission-status.in_progress {
  background-color: #fef3c7;
  color: #d97706;
  border: 1px solid #fcd34d;
}

.mission-status.completed {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.mission-status.cancelled {
  background-color: #fee2e2;
  color: #dc2626;
  border: 1px solid #fca5a5;
}

.description {
  color: #4b5563;
  line-height: 1.7;
  font-size: 16px;
  margin-bottom: 25px;
}

.info-block {
  background: #f9fafb;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  margin-bottom: 25px;
}

.info-block p {
  margin: 8px 0;
  color: #374151;
  font-size: 15px;
}

.info-block strong {
  color: #111827;
  margin-right: 8px;
}

.stats {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e5e7eb;
}

.stats .total {
  font-weight: 600;
  color: #3b82f6;
}

.stats .pending {
  color: #f59e0b;
  font-weight: 600;
}

/* Style pour le bouton chat */
.btn-chat {
  padding: 12px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-chat:hover:not(:disabled) {
  background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.btn-chat:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-chat i {
  font-size: 16px;
}

/* Section d'actions */
.action-section {
  margin-top: 30px;
  padding-top: 25px;
  border-top: 1px solid #e5e7eb;
}

.btn-manage {
  display: inline-block;
  padding: 12px 24px;
  background: #3b82f6;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 20px;
  transition: background-color 0.2s;
}

.btn-manage:hover {
  background: #2563eb;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 15px;
}

.btn-publish, .btn-edit, .btn-complete, .btn-cancel {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-publish {
  background: #10b981;
  color: white;
}

.btn-publish:hover:not(:disabled) {
  background: #059669;
}

.btn-publish:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-edit {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-edit:hover {
  background: #e5e7eb;
}

.btn-complete {
  background: #059669;
  color: white;
}

.btn-complete:hover:not(:disabled) {
  background: #047857;
}

.btn-complete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-cancel {
  background: #ef4444;
  color: white;
}

.btn-cancel:hover:not(:disabled) {
  background: #dc2626;
}

.btn-cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Messages d'état */
.loading {
  text-align: center;
  padding: 40px;
  color: #6b7280;
  font-size: 18px;
}

.error {
  background: #fee2e2;
  color: #dc2626;
  padding: 16px 20px;
  border-radius: 8px;
  margin: 20px 0;
  border: 1px solid #fca5a5;
  text-align: center;
}

.no-mission {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.back-btn {
  margin-top: 20px;
  padding: 12px 24px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.back-btn:hover {
  background: #2563eb;
}

/* Adaptation des boutons pour mobile */
@media (max-width: 768px) {
  .client-mission-details-page {
    margin-top: 80px;
    padding: 0 16px;
  }
  
  h1 {
    font-size: 28px;
  }
  
  .mission-card {
    padding: 20px;
  }
  
  .mission-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .btn-chat,
  .btn-publish, 
  .btn-edit, 
  .btn-complete, 
  .btn-cancel {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .client-mission-details-page {
    padding: 0 12px;
  }
  
  h1 {
    font-size: 24px;
  }
  
  .mission-card {
    padding: 16px;
  }
}
</style>