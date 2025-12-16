<template>
  <div class="manage-applications">
    <h1>Gérer les candidatures</h1>
    
    <!-- Bouton retour -->
    <router-link :to="`/missions/${missionId}`" class="btn-back">
      ← Retour à la mission
    </router-link>
    
    <div v-if="loading" class="loading">
      Chargement des candidatures...
    </div>
    
    <div v-else-if="applications.length === 0" class="no-applications">
      Aucune candidature pour cette mission
    </div>
    
    <div v-else class="applications-list">
      <div v-for="app in applications" :key="app.id" class="application-card">
        <div class="application-header">
          <h3>{{ app.freelance_name || `Freelance #${app.freelance_id}` }}</h3>
          <span :class="['status-badge', app.status]">
            {{ getStatusLabel(app.status) }}
          </span>
        </div>
        
        <div class="application-info">
          <p><strong>Titre:</strong> {{ app.profile_title || 'Non spécifié' }}</p>
          <p><strong>Note:</strong> {{ app.rating || 0 }} / 5</p>
          <p><strong>Projets complétés:</strong> {{ app.completed_projects || 0 }}</p>
          <p><strong>Postulé le:</strong> {{ formatDate(app.created_at) }}</p>
        </div>
        
        <div v-if="app.status === 'pending'" class="action-buttons">
          <button 
            @click="acceptApplication(app.id)" 
            class="btn-accept"
            :disabled="actionLoading"
          >
            Accepter
          </button>
          <button 
            @click="rejectApplication(app.id)" 
            class="btn-reject"
            :disabled="actionLoading"
          >
            Refuser
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMissionStore } from '@/stores/missions'

const route = useRoute()
const missionStore = useMissionStore()

const missionId = route.params.id
const applications = ref([])
const loading = ref(false)
const actionLoading = ref(false)

onMounted(async () => {
  await loadApplications()
})

const loadApplications = async () => {
  loading.value = true
  try {
    // CORRECTION ICI : utiliser fetchMissionApplications au lieu de getMissionApplications
    applications.value = await missionStore.fetchMissionApplications(missionId)
  } catch (error) {
    console.error('Erreur:', error)
    alert('Erreur lors du chargement des candidatures')
  } finally {
    loading.value = false
  }
}

const acceptApplication = async (applicationId) => {
  if (confirm('Êtes-vous sûr de vouloir accepter cette candidature ?')) {
    actionLoading.value = true
    try {
      // Correction ici aussi : missionId vient de route.params.id
      await missionStore.acceptApplication(missionId, applicationId)
      alert('Candidature acceptée avec succès!')
      await loadApplications() // Recharger la liste
    } catch (error) {
      alert('Erreur: ' + (error.response?.data?.error || error.message))
    } finally {
      actionLoading.value = false
    }
  }
}

const rejectApplication = async (applicationId) => {
  if (confirm('Êtes-vous sûr de vouloir refuser cette candidature ?')) {
    actionLoading.value = true
    try {
      await missionStore.rejectApplication(missionId, applicationId)
      alert('Candidature refusée')
      await loadApplications() // Recharger la liste
    } catch (error) {
      alert('Erreur: ' + (error.response?.data?.error || error.message))
    } finally {
      actionLoading.value = false
    }
  }
}

const getStatusLabel = (status) => {
  const labels = {
    'pending': 'En attente',
    'accepted': 'Acceptée',
    'rejected': 'Refusée',
    'cancelled': 'Annulée'
  }
  return labels[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return 'Date inconnue'
  return new Date(dateString).toLocaleDateString('fr-FR')
}
</script>

<style scoped>
.manage-applications {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.application-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: #fff;
}

.application-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.status-badge {
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.pending {
  background: #ffd700;
  color: #000;
}

.status-badge.accepted {
  background: #4caf50;
  color: white;
}

.status-badge.rejected {
  background: #f44336;
  color: white;
}

.status-badge.cancelled {
  background: #9e9e9e;
  color: white;
}

.application-info p {
  margin: 5px 0;
}

.action-buttons {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.btn-accept, .btn-reject {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-accept {
  background: #4caf50;
  color: white;
}

.btn-accept:hover:not(:disabled) {
  background: #45a049;
}

.btn-accept:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-reject {
  background: #f44336;
  color: white;
}

.btn-reject:hover:not(:disabled) {
  background: #d32f2f;
}

.btn-reject:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading, .no-applications {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #666;
}

.btn-back {
  display: inline-block;
  margin-bottom: 20px;
  padding: 8px 16px;
  background: #f0f0f0;
  color: #333;
  text-decoration: none;
  border-radius: 4px;
}

.btn-back:hover {
  background: #e0e0e0;
}
</style>