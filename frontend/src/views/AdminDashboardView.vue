<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'

const adminStore = useAdminStore()
const router = useRouter()

// États
const activeTab = ref('complaints')
const complaintStatusFilter = ref('pending')
const isLoading = ref(false)
const selectedComplaint = ref(null)
const showRejectModal = ref(false)
const rejectNotes = ref('')
const showDeleteModal = ref(false)
const showUnblockModal = ref(false)
const unblockUserId = ref(null)
const unblockNotes = ref('')

// Données
const complaints = ref([])
const blockedAccounts = ref([])
const stats = ref({
  totalComplaints: 0,
  pendingComplaints: 0,
  blockedUsers: 0,
  approvedComplaints: 0,
  rejectedComplaints: 0
})

// Pagination
const complaintsPagination = ref({
  page: 1,
  perPage: 10,
  total: 0,
  pages: 1
})

const blockedPagination = ref({
  page: 1,
  perPage: 10,
  total: 0,
  pages: 1
})

// Filtrer les plaintes par statut
const filteredComplaints = computed(() => {
  if (complaintStatusFilter.value === 'all') {
    return complaints.value
  }
  return complaints.value.filter(c => c.status === complaintStatusFilter.value)
})

// Initialisation
onMounted(async () => {
  if (!adminStore.isAuthenticated) {
    router.push('/admin/login')
    return
  }

  await loadData()
})

// Charger les données
const loadData = async () => {
  isLoading.value = true
  
  try {
    // Charger les statistiques
    await adminStore.refreshStats()
    
    // Charger les plaintes
    await loadComplaints()
    
    // Charger les comptes bloqués
    await loadBlockedAccounts()
    
    // Mettre à jour les stats locales
    updateStats()
    
  } catch (error) {
    console.error('Erreur de chargement:', error)
  } finally {
    isLoading.value = false
  }
}

// Charger les plaintes
const loadComplaints = async (status = null) => {
  const result = await adminStore.fetchComplaints(
    status || complaintStatusFilter.value,
    complaintsPagination.value.page,
    complaintsPagination.value.perPage
  )
  
  if (result.success) {
    complaints.value = result.complaints
    complaintsPagination.value = result.pagination
  }
}

// Charger les comptes bloqués
const loadBlockedAccounts = async () => {
  const result = await adminStore.fetchBlockedAccounts(
    blockedPagination.value.page,
    blockedPagination.value.perPage
  )
  
  if (result.success) {
    blockedAccounts.value = result.accounts
    blockedPagination.value = result.pagination
  }
}

// Mettre à jour les statistiques
const updateStats = () => {
  stats.value = {
    totalComplaints: adminStore.stats.totalComplaints || 0,
    pendingComplaints: adminStore.stats.pendingComplaints || 0,
    blockedUsers: adminStore.stats.blockedUsers || 0,
    approvedComplaints: complaints.value.filter(c => c.status === 'approved').length,
    rejectedComplaints: complaints.value.filter(c => c.status === 'rejected').length
  }
}

// Approuver une plainte
const approveComplaint = async (complaintId) => {
  if (!confirm('Êtes-vous sûr de vouloir approuver cette plainte ? L\'utilisateur signalé sera bloqué.')) {
    return
  }

  isLoading.value = true
  const result = await adminStore.approveComplaint(complaintId)
  
  if (result.success) {
    alert(result.message)
    await loadData()
  } else {
    alert(result.message)
  }
  isLoading.value = false
}

// Ouvrir le modal de rejet
const openRejectModal = (complaint) => {
  selectedComplaint.value = complaint
  rejectNotes.value = ''
  showRejectModal.value = true
}

// Rejeter une plainte
const rejectComplaint = async () => {
  if (!selectedComplaint.value) return

  isLoading.value = true
  const result = await adminStore.rejectComplaint(
    selectedComplaint.value.id,
    rejectNotes.value || null
  )
  
  if (result.success) {
    alert(result.message)
    showRejectModal.value = false
    await loadData()
  } else {
    alert(result.message)
  }
  isLoading.value = false
}

// Ouvrir le modal de suppression
const openDeleteModal = (complaint) => {
  selectedComplaint.value = complaint
  showDeleteModal.value = true
}

// Supprimer une plainte
const deleteComplaint = async () => {
  if (!selectedComplaint.value) return

  isLoading.value = true
  const result = await adminStore.deleteComplaint(selectedComplaint.value.id)
  
  if (result.success) {
    alert(result.message)
    showDeleteModal.value = false
    await loadData()
  } else {
    alert(result.message)
  }
  isLoading.value = false
}

// Ouvrir le modal de déblocage
const openUnblockModal = (userId) => {
  unblockUserId.value = userId
  unblockNotes.value = ''
  showUnblockModal.value = true
}

// Débloquer un compte
const unblockUser = async () => {
  if (!unblockUserId.value) return

  isLoading.value = true
  const result = await adminStore.unblockUser(unblockUserId.value, unblockNotes.value || null)
  
  if (result.success) {
    alert(result.message)
    showUnblockModal.value = false
    await loadData()
  } else {
    alert(result.message)
  }
  isLoading.value = false
}

// Changer de page (plaintes)
const changeComplaintsPage = (page) => {
  complaintsPagination.value.page = page
  loadComplaints()
}

// Changer de page (comptes bloqués)
const changeBlockedPage = (page) => {
  blockedPagination.value.page = page
  loadBlockedAccounts()
}

// Changer le filtre de statut
const changeStatusFilter = (status) => {
  complaintStatusFilter.value = status
  complaintsPagination.value.page = 1
  loadComplaints(status)
}

// Formater la date
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Obtenir la classe de badge selon le statut
const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'pending': return 'status-badge pending'
    case 'approved': return 'status-badge approved'
    case 'rejected': return 'status-badge rejected'
    default: return 'status-badge'
  }
}

// Obtenir le texte du statut
const getStatusText = (status) => {
  switch (status) {
    case 'pending': return 'En attente'
    case 'approved': return 'Approuvée'
    case 'rejected': return 'Rejetée'
    default: return status
  }
}

// Déconnexion
const logout = () => {
  if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
    adminStore.logout()
  }
}

// Rafraîchir les données
const refreshData = () => {
  loadData()
}

// Exporter les données
const exportData = () => {
  const data = {
    complaints: complaints.value,
    blockedAccounts: blockedAccounts.value,
    stats: stats.value,
    exportedAt: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `admin-data-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  
  alert('Données exportées avec succès !')
}
</script>

<template>
  <div class="admin-dashboard">
    <!-- Header Admin -->
    <header class="admin-header">
      <div class="admin-header-container">
        <div class="admin-header-left">
          <div class="admin-logo">
            <i class="fas fa-shield-alt"></i>
            <h1>Dashboard Admin</h1>
          </div>
          <div class="admin-user-info">
            <i class="fas fa-user-circle"></i>
            <div class="user-details">
              <span class="user-name">{{ adminStore.displayName }}</span>
              <span class="user-email">{{ adminStore.adminEmail }}</span>
            </div>
          </div>
        </div>
        
        <div class="admin-header-right">
          <button class="header-btn refresh-btn" @click="refreshData" :disabled="isLoading">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            <span>Rafraîchir</span>
          </button>
          <button class="header-btn export-btn" @click="exportData">
            <i class="fas fa-download"></i>
            <span>Exporter</span>
          </button>
          <button class="header-btn logout-btn" @click="logout">
            <i class="fas fa-sign-out-alt"></i>
            <span>Déconnexion</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Statistiques -->
    <section class="admin-stats">
      <div class="stats-container">
        <div class="stat-card total-complaints">
          <div class="stat-icon">
            <i class="fas fa-flag"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ stats.totalComplaints }}</h3>
            <p class="stat-label">Plaintes totales</p>
          </div>
        </div>
        
        <div class="stat-card pending-complaints">
          <div class="stat-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ stats.pendingComplaints }}</h3>
            <p class="stat-label">En attente</p>
          </div>
        </div>
        
        <div class="stat-card blocked-users">
          <div class="stat-icon">
            <i class="fas fa-user-slash"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ stats.blockedUsers }}</h3>
            <p class="stat-label">Comptes bloqués</p>
          </div>
        </div>
        
        <div class="stat-card actions-today">
          <div class="stat-icon">
            <i class="fas fa-tasks"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ stats.approvedComplaints + stats.rejectedComplaints }}</h3>
            <p class="stat-label">Actions aujourd'hui</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Navigation par onglets -->
    <nav class="admin-tabs">
      <div class="tabs-container">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'complaints' }"
          @click="activeTab = 'complaints'"
        >
          <i class="fas fa-flag"></i>
          Gestion des plaintes
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'blocked' }"
          @click="activeTab = 'blocked'"
        >
          <i class="fas fa-user-slash"></i>
          Comptes bloqués
        </button>
      </div>
    </nav>

    <!-- Contenu principal -->
    <main class="admin-main">
      <!-- Onglet Plaintes -->
      <div v-if="activeTab === 'complaints'" class="tab-content">
        <div class="complaints-header">
          <h2>
            <i class="fas fa-flag"></i>
            Gestion des plaintes
          </h2>
          
          <div class="filters">
            <button 
              class="filter-btn" 
              :class="{ active: complaintStatusFilter === 'all' }"
              @click="changeStatusFilter('all')"
            >
              Toutes ({{ stats.totalComplaints }})
            </button>
            <button 
              class="filter-btn" 
              :class="{ active: complaintStatusFilter === 'pending' }"
              @click="changeStatusFilter('pending')"
            >
              En attente ({{ stats.pendingComplaints }})
            </button>
            <button 
              class="filter-btn" 
              :class="{ active: complaintStatusFilter === 'approved' }"
              @click="changeStatusFilter('approved')"
            >
              Approuvées ({{ stats.approvedComplaints }})
            </button>
            <button 
              class="filter-btn" 
              :class="{ active: complaintStatusFilter === 'rejected' }"
              @click="changeStatusFilter('rejected')"
            >
              Rejetées ({{ stats.rejectedComplaints }})
            </button>
          </div>
        </div>

        <!-- Tableau des plaintes -->
        <div class="table-container">
          <div v-if="isLoading" class="loading-overlay">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Chargement des plaintes...</p>
          </div>
          
          <table class="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Plaignant</th>
                <th>Signalé</th>
                <th>Motif</th>
                <th>Date</th>
                <th>Statut</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="complaint in filteredComplaints" :key="complaint.id">
                <td class="complaint-id">#{{ complaint.id }}</td>
                <td>
                  <div class="user-cell">
                    <i class="fas fa-user"></i>
                    <span>{{ complaint.plaintiff_email || 'Utilisateur' }}</span>
                  </div>
                </td>
                <td>
                  <div class="user-cell">
                    <i class="fas fa-user-times"></i>
                    <span>{{ complaint.reported_email }}</span>
                  </div>
                </td>
                <td>
                  <div class="reason-cell" :title="complaint.reason">
                    {{ complaint.reason.length > 50 ? complaint.reason.substring(0, 50) + '...' : complaint.reason }}
                  </div>
                </td>
                <td>{{ formatDate(complaint.created_at) }}</td>
                <td>
                  <span :class="getStatusBadgeClass(complaint.status)">
                    {{ getStatusText(complaint.status) }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <!-- Actions pour plaintes en attente -->
                    <template v-if="complaint.status === 'pending'">
                      <button 
                        class="action-btn approve-btn" 
                        @click="approveComplaint(complaint.id)"
                        :disabled="isLoading"
                        title="Approuver la plainte"
                      >
                        <i class="fas fa-check"></i>
                        Valider
                      </button>
                      <button 
                        class="action-btn reject-btn" 
                        @click="openRejectModal(complaint)"
                        :disabled="isLoading"
                        title="Rejeter la plainte"
                      >
                        <i class="fas fa-times"></i>
                        Rejeter
                      </button>
                    </template>
                    
                    <!-- Actions pour toutes les plaintes -->
                    <button 
                      class="action-btn delete-btn" 
                      @click="openDeleteModal(complaint)"
                      :disabled="isLoading"
                      title="Supprimer la plainte"
                    >
                      <i class="fas fa-trash"></i>
                      Supprimer
                    </button>
                    
                    <button 
                      class="action-btn view-btn" 
                      @click="selectedComplaint = complaint"
                      :disabled="isLoading"
                      title="Voir les détails"
                    >
                      <i class="fas fa-eye"></i>
                      Détails
                    </button>
                  </div>
                </td>
              </tr>
              
              <!-- Message vide -->
              <tr v-if="filteredComplaints.length === 0 && !isLoading">
                <td colspan="7" class="empty-message">
                  <i class="fas fa-inbox"></i>
                  <p>Aucune plainte trouvée</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination des plaintes -->
        <div v-if="complaintsPagination.pages > 1" class="pagination">
          <button 
            class="pagination-btn" 
            @click="changeComplaintsPage(complaintsPagination.page - 1)"
            :disabled="complaintsPagination.page === 1 || isLoading"
          >
            <i class="fas fa-chevron-left"></i>
            Précédent
          </button>
          
          <div class="pagination-info">
            Page {{ complaintsPagination.page }} sur {{ complaintsPagination.pages }}
          </div>
          
          <button 
            class="pagination-btn" 
            @click="changeComplaintsPage(complaintsPagination.page + 1)"
            :disabled="complaintsPagination.page === complaintsPagination.pages || isLoading"
          >
            Suivant
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>

      <!-- Onglet Comptes bloqués -->
      <div v-if="activeTab === 'blocked'" class="tab-content">
        <div class="blocked-header">
          <h2>
            <i class="fas fa-user-slash"></i>
            Comptes bloqués ({{ stats.blockedUsers }})
          </h2>
        </div>

        <!-- Tableau des comptes bloqués -->
        <div class="table-container">
          <div v-if="isLoading" class="loading-overlay">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Chargement des comptes bloqués...</p>
          </div>
          
          <table class="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Rôle</th>
                <th>Date d'inscription</th>
                <th>Bloqué depuis</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="account in blockedAccounts" :key="account.id">
                <td class="account-id">#{{ account.id }}</td>
                <td>
                  <div class="user-cell">
                    <i class="fas fa-envelope"></i>
                    <span>{{ account.email }}</span>
                  </div>
                </td>
                <td>
                  <span class="role-badge" :class="account.role.toLowerCase()">
                    {{ account.role }}
                  </span>
                </td>
                <td>{{ formatDate(account.created_at) }}</td>
                <td>
                  <span class="blocked-since">
                    <i class="fas fa-clock"></i>
                    {{ formatDate(account.created_at) }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button 
                      class="action-btn unblock-btn" 
                      @click="openUnblockModal(account.id)"
                      :disabled="isLoading"
                      title="Débloquer le compte"
                    >
                      <i class="fas fa-unlock"></i>
                      Débloquer
                    </button>
                  </div>
                </td>
              </tr>
              
              <!-- Message vide -->
              <tr v-if="blockedAccounts.length === 0 && !isLoading">
                <td colspan="6" class="empty-message">
                  <i class="fas fa-user-check"></i>
                  <p>Aucun compte bloqué</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination des comptes bloqués -->
        <div v-if="blockedPagination.pages > 1" class="pagination">
          <button 
            class="pagination-btn" 
            @click="changeBlockedPage(blockedPagination.page - 1)"
            :disabled="blockedPagination.page === 1 || isLoading"
          >
            <i class="fas fa-chevron-left"></i>
            Précédent
          </button>
          
          <div class="pagination-info">
            Page {{ blockedPagination.page }} sur {{ blockedPagination.pages }}
          </div>
          
          <button 
            class="pagination-btn" 
            @click="changeBlockedPage(blockedPagination.page + 1)"
            :disabled="blockedPagination.page === blockedPagination.pages || isLoading"
          >
            Suivant
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </main>

    <!-- Détails de la plainte -->
    <div v-if="selectedComplaint" class="modal-overlay" @click.self="selectedComplaint = null">
      <div class="modal-content complaint-details">
        <div class="modal-header">
          <h3>
            <i class="fas fa-flag"></i>
            Détails de la plainte #{{ selectedComplaint.id }}
          </h3>
          <button class="modal-close" @click="selectedComplaint = null">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="detail-section">
            <h4>Informations</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">Plaignant:</span>
                <span class="detail-value">{{ selectedComplaint.plaintiff_email || 'N/A' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Utilisateur signalé:</span>
                <span class="detail-value">{{ selectedComplaint.reported_email }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Statut:</span>
                <span :class="getStatusBadgeClass(selectedComplaint.status)">
                  {{ getStatusText(selectedComplaint.status) }}
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Date de création:</span>
                <span class="detail-value">{{ formatDate(selectedComplaint.created_at) }}</span>
              </div>
              <div v-if="selectedComplaint.reviewed_at" class="detail-item">
                <span class="detail-label">Traité le:</span>
                <span class="detail-value">{{ formatDate(selectedComplaint.reviewed_at) }}</span>
              </div>
              <div v-if="selectedComplaint.reviewed_by" class="detail-item">
                <span class="detail-label">Traité par:</span>
                <span class="detail-value">Admin #{{ selectedComplaint.reviewed_by }}</span>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <h4>Motif de la plainte</h4>
            <div class="reason-box">
              {{ selectedComplaint.reason }}
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="modal-btn secondary" @click="selectedComplaint = null">
            <i class="fas fa-times"></i>
            Fermer
          </button>
          
          <div v-if="selectedComplaint.status === 'pending'" class="modal-actions">
            <button class="modal-btn success" @click="approveComplaint(selectedComplaint.id)">
              <i class="fas fa-check"></i>
              Approuver
            </button>
            <button class="modal-btn danger" @click="openRejectModal(selectedComplaint)">
              <i class="fas fa-times"></i>
              Rejeter
            </button>
          </div>
          
          <button class="modal-btn danger" @click="openDeleteModal(selectedComplaint)">
            <i class="fas fa-trash"></i>
            Supprimer
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de rejet -->
    <div v-if="showRejectModal" class="modal-overlay" @click.self="showRejectModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>
            <i class="fas fa-times-circle"></i>
            Rejeter la plainte
          </h3>
          <button class="modal-close" @click="showRejectModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <p>Êtes-vous sûr de vouloir rejeter cette plainte ?</p>
          <p class="modal-warning">
            <i class="fas fa-exclamation-triangle"></i>
            Cette action ne peut pas être annulée.
          </p>
          
          <div class="form-group">
            <label for="reject-notes">
              <i class="fas fa-comment"></i>
              Notes (optionnel)
            </label>
            <textarea 
              id="reject-notes"
              v-model="rejectNotes"
              placeholder="Raison du rejet..."
              rows="4"
            ></textarea>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="modal-btn secondary" @click="showRejectModal = false">
            <i class="fas fa-times"></i>
            Annuler
          </button>
          <button class="modal-btn danger" @click="rejectComplaint" :disabled="isLoading">
            <i class="fas fa-times"></i>
            Rejeter la plainte
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de suppression -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>
            <i class="fas fa-trash-alt"></i>
            Supprimer la plainte
          </h3>
          <button class="modal-close" @click="showDeleteModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <p>Êtes-vous sûr de vouloir supprimer cette plainte ?</p>
          <p class="modal-warning">
            <i class="fas fa-exclamation-triangle"></i>
            Cette action est irréversible. Toutes les données associées seront perdues.
          </p>
        </div>
        
        <div class="modal-footer">
          <button class="modal-btn secondary" @click="showDeleteModal = false">
            <i class="fas fa-times"></i>
            Annuler
          </button>
          <button class="modal-btn danger" @click="deleteComplaint" :disabled="isLoading">
            <i class="fas fa-trash"></i>
            Supprimer définitivement
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de déblocage -->
    <div v-if="showUnblockModal" class="modal-overlay" @click.self="showUnblockModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>
            <i class="fas fa-unlock"></i>
            Débloquer le compte
          </h3>
          <button class="modal-close" @click="showUnblockModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <p>Êtes-vous sûr de vouloir débloquer ce compte utilisateur ?</p>
          <p class="modal-info">
            <i class="fas fa-info-circle"></i>
            L'utilisateur pourra à nouveau se connecter et utiliser la plateforme.
          </p>
          
          <div class="form-group">
            <label for="unblock-notes">
              <i class="fas fa-comment"></i>
              Notes (optionnel)
            </label>
            <textarea 
              id="unblock-notes"
              v-model="unblockNotes"
              placeholder="Raison du déblocage..."
              rows="4"
            ></textarea>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="modal-btn secondary" @click="showUnblockModal = false">
            <i class="fas fa-times"></i>
            Annuler
          </button>
          <button class="modal-btn success" @click="unblockUser" :disabled="isLoading">
            <i class="fas fa-unlock"></i>
            Débloquer le compte
          </button>
        </div>
      </div>
    </div>

    <!-- Footer Admin -->
    <footer class="admin-footer">
      <div class="footer-container">
        <div class="footer-left">
          <p>
            <i class="fas fa-shield-alt"></i>
            Système d'administration FreelanceCMR
          </p>
          <p class="footer-info">
            Connecté en tant que: {{ adminStore.adminEmail }} | 
            Dernière mise à jour: {{ new Date().toLocaleTimeString('fr-FR') }}
          </p>
        </div>
        <div class="footer-right">
          <span class="footer-stats">
            <i class="fas fa-server"></i>
            {{ stats.pendingComplaints }} plaintes en attente
          </span>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Styles généraux */
.admin-dashboard {
  min-height: 100vh;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
}

/* Header */
.admin-header {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  padding: 15px 0;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.admin-header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.admin-header-left {
  display: flex;
  align-items: center;
  gap: 30px;
}

.admin-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-logo i {
  font-size: 2rem;
  color: #FF6B35;
}

.admin-logo h1 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.admin-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.admin-user-info i {
  font-size: 2rem;
  color: #FF6B35;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  font-size: 0.95rem;
}

.user-email {
  font-size: 0.85rem;
  opacity: 0.8;
}

.admin-header-right {
  display: flex;
  gap: 10px;
}

.header-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.export-btn {
  background: #28a745;
  color: white;
}

.export-btn:hover:not(:disabled) {
  background: #218838;
}

.logout-btn {
  background: #dc3545;
  color: white;
}

.logout-btn:hover:not(:disabled) {
  background: #c82333;
}

.header-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Statistiques */
.admin-stats {
  padding: 30px 20px;
  background: white;
  margin: 20px auto;
  max-width: 1400px;
  width: 100%;
  border-radius: 15px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 25px;
  border-radius: 12px;
  background: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.total-complaints .stat-icon {
  background: linear-gradient(135deg, #4dabf7, #339af0);
  color: white;
}

.pending-complaints .stat-icon {
  background: linear-gradient(135deg, #ffc107, #e6a800);
  color: white;
}

.blocked-users .stat-icon {
  background: linear-gradient(135deg, #ff6b6b, #fa5252);
  color: white;
}

.actions-today .stat-icon {
  background: linear-gradient(135deg, #51cf66, #37b24d);
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 5px 0;
  color: #2D3047;
}

.stat-label {
  font-size: 0.9rem;
  color: #6c757d;
  margin: 0;
}

/* Navigation par onglets */
.admin-tabs {
  max-width: 1400px;
  margin: 0 auto 20px;
  padding: 0 20px;
  width: 100%;
}

.tabs-container {
  display: flex;
  gap: 10px;
  border-bottom: 2px solid #e9ecef;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 25px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 1rem;
  font-weight: 600;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  color: #2D3047;
}

.tab-btn.active {
  color: #2D3047;
  border-bottom-color: #2D3047;
}

.tab-btn i {
  font-size: 1.1rem;
}

/* Contenu principal */
.admin-main {
  flex: 1;
  max-width: 1400px;
  margin: 0 auto 30px;
  padding: 0 20px;
  width: 100%;
}

.tab-content {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
}

/* En-tête des plaintes */
.complaints-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.complaints-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #2D3047;
  display: flex;
  align-items: center;
  gap: 10px;
}

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 8px 16px;
  border: 2px solid #e9ecef;
  background: white;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  border-color: #2D3047;
  color: #2D3047;
}

.filter-btn.active {
  background: #2D3047;
  border-color: #2D3047;
  color: white;
}

/* Tableaux */
.table-container {
  position: relative;
  overflow-x: auto;
  border-radius: 10px;
  border: 1px solid #e9ecef;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 15px;
  z-index: 10;
}

.loading-overlay i {
  font-size: 2rem;
  color: #2D3047;
}

.loading-overlay p {
  margin: 0;
  color: #6c757d;
  font-weight: 500;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1000px;
}

.admin-table thead {
  background: #f8f9fa;
  border-bottom: 2px solid #e9ecef;
}

.admin-table th {
  padding: 15px;
  text-align: left;
  font-weight: 600;
  color: #2D3047;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.admin-table tbody tr {
  border-bottom: 1px solid #e9ecef;
  transition: background-color 0.2s ease;
}

.admin-table tbody tr:hover {
  background-color: #f8f9fa;
}

.admin-table td {
  padding: 15px;
  vertical-align: middle;
}

/* Cellules spécifiques */
.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-cell i {
  color: #6c757d;
}

.complaint-id, .account-id {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #6c757d;
}

.reason-cell {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: help;
}

/* Badges de statut */
.status-badge {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.status-badge.approved {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.status-badge.rejected {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.role-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.role-badge.admin {
  background: #e3f2fd;
  color: #1565c0;
}

.role-badge.client {
  background: #f3e5f5;
  color: #7b1fa2;
}

.role-badge.freelance {
  background: #e8f5e8;
  color: #2e7d32;
}

.blocked-since {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #dc3545;
  font-size: 0.9rem;
}

/* Boutons d'action */
.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.approve-btn {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.approve-btn:hover:not(:disabled) {
  background: #c3e6cb;
}

.reject-btn {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.reject-btn:hover:not(:disabled) {
  background: #f5c6cb;
}

.delete-btn {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.delete-btn:hover:not(:disabled) {
  background: #f5c6cb;
}

.view-btn {
  background: #e3f2fd;
  color: #1565c0;
  border: 1px solid #bbdefb;
}

.view-btn:hover:not(:disabled) {
  background: #bbdefb;
}

.unblock-btn {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.unblock-btn:hover:not(:disabled) {
  background: #c3e6cb;
}

/* Message vide */
.empty-message {
  text-align: center;
  padding: 40px !important;
  color: #6c757d;
}

.empty-message i {
  font-size: 3rem;
  margin-bottom: 15px;
  color: #dee2e6;
}

.empty-message p {
  margin: 0;
  font-size: 1rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 25px;
  padding: 20px 0;
  border-top: 1px solid #e9ecef;
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-weight: 600;
  color: #2D3047;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  border-color: #2D3047;
  background: #f8f9fa;
}

.pagination-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 0.9rem;
  color: #6c757d;
  font-weight: 500;
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
  border-radius: 15px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
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
  padding: 25px;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
  color: #2D3047;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #6c757d;
  cursor: pointer;
  padding: 5px;
  transition: color 0.3s ease;
}

.modal-close:hover {
  color: #2D3047;
}

.modal-body {
  padding: 25px;
}

.modal-warning, .modal-info {
  padding: 15px;
  border-radius: 8px;
  margin: 15px 0;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.modal-warning {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  color: #856404;
}

.modal-info {
  background: #d1ecf1;
  border: 1px solid #bee5eb;
  color: #0c5460;
}

.form-group {
  margin-top: 20px;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2D3047;
}

.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.95rem;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.form-group textarea:focus {
  outline: none;
  border-color: #2D3047;
}

.modal-footer {
  padding: 25px;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.modal-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 25px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-btn.secondary {
  background: #6c757d;
  color: white;
}

.modal-btn.secondary:hover:not(:disabled) {
  background: #5a6268;
}

.modal-btn.success {
  background: #28a745;
  color: white;
}

.modal-btn.success:hover:not(:disabled) {
  background: #218838;
}

.modal-btn.danger {
  background: #dc3545;
  color: white;
}

.modal-btn.danger:hover:not(:disabled) {
  background: #c82333;
}

/* Détails de la plainte */
.complaint-details {
  max-width: 800px;
}

.detail-section {
  margin-bottom: 30px;
}

.detail-section h4 {
  margin: 0 0 15px 0;
  color: #2D3047;
  font-size: 1.1rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-label {
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 500;
}

.detail-value {
  font-weight: 600;
  color: #2D3047;
}

.reason-box {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  line-height: 1.6;
  white-space: pre-wrap;
}

/* Footer */
.admin-footer {
  background: #2D3047;
  color: white;
  padding: 20px 0;
  margin-top: auto;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.footer-left p {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.footer-left .footer-info {
  font-size: 0.85rem;
  opacity: 0.8;
  margin-top: 5px;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.footer-stats {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  padding: 8px 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

/* Responsive */
@media (max-width: 1200px) {
  .admin-header-container,
  .admin-stats,
  .admin-tabs,
  .admin-main {
    max-width: 100%;
  }
}

@media (max-width: 992px) {
  .admin-header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .admin-header-container {
    flex-direction: column;
    gap: 20px;
  }
  
  .admin-header-right {
    width: 100%;
    justify-content: center;
  }
  
  .complaints-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filters {
    width: 100%;
    overflow-x: auto;
    padding-bottom: 10px;
  }
  
  .stats-container {
    grid-template-columns: 1fr;
  }
  
  .tabs-container {
    overflow-x: auto;
    padding-bottom: 10px;
  }
  
  .modal-content {
    margin: 20px;
  }
}

@media (max-width: 576px) {
  .tab-content {
    padding: 20px;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-btn {
    justify-content: center;
  }
  
  .footer-container {
    flex-direction: column;
    text-align: center;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .modal-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>