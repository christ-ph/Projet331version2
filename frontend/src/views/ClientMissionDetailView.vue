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

          <!-- Annuler la mission (tous statuts sauf completed et cancelled) -->
          <button 
            v-if="mission.status !== 'COMPLETED' && mission.status !== 'CANCELLED'"
            @click="cancelMission"
            class="btn-cancel"
            :disabled="loadingAction"
          >
            Annuler la mission
          </button>
        </div>
      </div>
    </div>

    <!-- Candidatures -->
    <div v-if="applications.length > 0" class="applications-section">
      <h2>Candidatures reçues ({{ applications.length }})</h2>

      <div class="applications-grid">
        <div v-for="app in applications" :key="app.id" class="application-card">
          <div class="application-header">
            <div class="freelancer-info">
              <div class="avatar-container">
                <img :src="app.photo" class="avatar" alt="Avatar" />
              </div>
              <div class="freelancer-details">
                <h3>{{ app.freelancer_name }}</h3>
                <p class="rating">
                  ⭐ {{ app.rating }} / 5
                  <span class="missions-count">
                    ({{ app.completed_missions }} missions)
                  </span>
                </p>
                <p class="skills" v-if="app.skills">{{ app.skills }}</p>
              </div>
            </div>

            <span class="badge" :class="app.status.toLowerCase()">
              {{ getApplicationStatusText(app.status) }}
            </span>
          </div>

          <div class="application-content">
            <p class="bio" v-if="app.bio">{{ app.bio }}</p>
            
            <div class="proposal-section" v-if="app.proposal">
              <h4>Lettre de motivation</h4>
              <p class="proposal">{{ app.proposal }}</p>
            </div>

            <div class="portfolio-section" v-if="app.portfolio?.length">
              <h4>Portfolio ({{ app.portfolio.length }} projets)</h4>
              <ul class="portfolio-list">
                <li v-for="item in app.portfolio" :key="item.id">
                  {{ item.title }}
                </li>
              </ul>
            </div>
          </div>

          <div class="application-actions">
            <button class="profile-btn" @click="goToProfile(app.freelance_id)">
              Voir profil complet
            </button>

            <!-- Boutons accepter/refuser uniquement si la mission est OPEN et candidature en attente -->
            <div class="decision-buttons" v-if="mission?.status === 'OPEN' && app.status === 'PENDING'">
              <button 
                class="accept-btn" 
                @click="acceptApplication(app.id)" 
                :disabled="loadingAction || isFreelanceAlreadyAccepted"
              >
                Accepter
              </button>
              <button 
                class="reject-btn" 
                @click="rejectApplication(app.id)" 
                :disabled="loadingAction"
              >
                Refuser
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Aucune candidature -->
    <div v-if="applications.length === 0 && mission && mission.status === 'OPEN'" class="no-applications">
      <div class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>Aucune candidature reçue</h3>
        <p>Cette mission est publiée mais n'a pas encore reçu de candidatures.</p>
        <button class="refresh-btn" @click="refreshData">
          Rafraîchir
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useMissionStore } from '@/stores/missions'
import { useAuthStore } from '@/stores/auth'
import { useRoute, useRouter } from 'vue-router'

const missionsStore = useMissionStore()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const missionId = parseInt(route.params.id)
const applications = ref([])
const loading = ref(false)
const loadingAction = ref(false)
const error = ref(null)

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

// Chargement des données
const loadData = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log('🔍 Chargement des détails de la mission:', missionId)
    
    // 1. Charger les détails de la mission
    await missionsStore.fetchMissionDetails(missionId)
    
    if (!missionsStore.missionDetails) {
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

// Mission courante
const mission = computed(() => missionsStore.missionDetails)

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

/* Section candidatures */
.applications-section {
  margin-top: 40px;
}

/* Grille des candidatures */
.applications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
}

/* Carte candidature */
.application-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  transition: transform 0.2s, box-shadow 0.2s;
}

.application-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.application-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.freelancer-info {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.avatar-container {
  flex-shrink: 0;
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e5e7eb;
}

.freelancer-details h3 {
  font-size: 18px;
  color: #111827;
  margin: 0 0 6px 0;
  font-weight: 600;
}

.rating {
  color: #f59e0b;
  font-weight: 600;
  margin: 0 0 6px 0;
}

.missions-count {
  color: #6b7280;
  font-weight: normal;
}

.skills {
  color: #4b5563;
  font-size: 14px;
  margin: 0;
}

/* Badges */
.badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.pending {
  background-color: #fef3c7;
  color: #d97706;
  border: 1px solid #fcd34d;
}

.badge.accepted {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.badge.rejected {
  background-color: #fee2e2;
  color: #dc2626;
  border: 1px solid #fca5a5;
}

.badge.cancelled {
  background-color: #f3f4f6;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

/* Contenu de la candidature */
.application-content {
  margin-bottom: 20px;
}

.bio, .proposal {
  color: #4b5563;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 16px;
}

.proposal-section h4, .portfolio-section h4 {
  font-size: 15px;
  color: #111827;
  margin-bottom: 8px;
  font-weight: 600;
}

.portfolio-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.portfolio-list li {
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
  color: #4b5563;
  font-size: 14px;
}

.portfolio-list li:last-child {
  border-bottom: none;
}

/* Boutons d'action de candidature */
.application-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.profile-btn {
  padding: 10px 16px;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: background-color 0.2s;
  text-align: center;
}

.profile-btn:hover {
  background: #e5e7eb;
}

.decision-buttons {
  display: flex;
  gap: 12px;
}

.accept-btn, .reject-btn {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: background-color 0.2s;
}

.accept-btn {
  background: #10b981;
  color: white;
}

.accept-btn:hover:not(:disabled) {
  background: #059669;
}

.accept-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.reject-btn {
  background: #ef4444;
  color: white;
}

.reject-btn:hover:not(:disabled) {
  background: #dc2626;
}

.reject-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* État vide */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: #f9fafb;
  border-radius: 12px;
  border: 2px dashed #d1d5db;
}

.empty-icon {
  font-size: 60px;
  margin-bottom: 20px;
  color: #9ca3af;
}

.empty-state h3 {
  color: #111827;
  margin-bottom: 12px;
}

.empty-state p {
  color: #6b7280;
  margin-bottom: 24px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.refresh-btn {
  padding: 12px 24px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
}

.refresh-btn:hover {
  background: #2563eb;
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

.no-mission, .no-applications {
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

/* Responsive */
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
  
  .applications-grid {
    grid-template-columns: 1fr;
  }
  
  .application-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .action-buttons, .decision-buttons {
    flex-direction: column;
  }
  
  .btn-publish, .btn-edit, .btn-complete, .btn-cancel,
  .accept-btn, .reject-btn {
    width: 100%;
  }
}
</style>