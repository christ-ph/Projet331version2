<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAdminStore } from '@/stores/admin';

const adminStore = useAdminStore();
const router = useRouter();

const activeTab = ref('pending');
const selectedComplaint = ref(null);
const showRejectModal = ref(false);
const rejectNotes = ref('');
const successMessage = ref('');
const errorMessage = ref('');

// ✅ Vérifier authentification au chargement
onMounted(async () => {
  if (!adminStore.isAdminAuthenticated) {
    router.push('/admin/login');
    return;
  }
  
  await loadComplaints();
});

const loadComplaints = async () => {
  const status = activeTab.value === 'all' ? null : activeTab.value;
  await adminStore.fetchComplaints(status);
};

const filteredComplaints = computed(() => {
  if (activeTab.value === 'all') return adminStore.complaints;
  if (activeTab.value === 'pending') return adminStore.pendingComplaints;
  if (activeTab.value === 'approved') return adminStore.approvedComplaints;
  if (activeTab.value === 'rejected') return adminStore.rejectedComplaints;
  return [];
});

const handleApprove = async (complaintId) => {
  if (!confirm('Êtes-vous sûr de vouloir approuver cette plainte ? L\'utilisateur sera bloqué.')) {
    return;
  }

  const result = await adminStore.approveComplaint(complaintId);
  
  if (result.success) {
    successMessage.value = result.message;
    setTimeout(() => successMessage.value = '', 5000);
    await loadComplaints();
  } else {
    errorMessage.value = result.message;
    setTimeout(() => errorMessage.value = '', 5000);
  }
};

const openRejectModal = (complaint) => {
  selectedComplaint.value = complaint;
  showRejectModal.value = true;
  rejectNotes.value = '';
};

const handleReject = async () => {
  if (!selectedComplaint.value) return;

  const result = await adminStore.rejectComplaint(
    selectedComplaint.value.id, 
    rejectNotes.value
  );
  
  if (result.success) {
    successMessage.value = result.message;
    setTimeout(() => successMessage.value = '', 5000);
    showRejectModal.value = false;
    selectedComplaint.value = null;
    await loadComplaints();
  } else {
    errorMessage.value = result.message;
    setTimeout(() => errorMessage.value = '', 5000);
  }
};

const handleDelete = async (complaintId) => {
  if (!confirm('Êtes-vous sûr de vouloir supprimer définitivement cette plainte ?')) {
    return;
  }

  const result = await adminStore.deleteComplaint(complaintId);
  
  if (result.success) {
    successMessage.value = result.message;
    setTimeout(() => successMessage.value = '', 5000);
    await loadComplaints();
  } else {
    errorMessage.value = result.message;
    setTimeout(() => errorMessage.value = '', 5000);
  }
};

const handleLogout = () => {
  if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
    adminStore.adminLogout();
  }
};

const goToChat = () => {
  router.push('/admin/chat');
};

const goToBlockedAccounts = () => {
  router.push('/admin/blocked-accounts');
};

const goToActions = () => {
  router.push('/admin/actions');
};

const changeTab = async (tab) => {
  activeTab.value = tab;
  await loadComplaints();
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getStatusBadge = (status) => {
  const badges = {
    pending: { text: 'En attente', class: 'badge-pending' },
    approved: { text: 'Approuvée', class: 'badge-approved' },
    rejected: { text: 'Rejetée', class: 'badge-rejected' }
  };
  return badges[status] || { text: status, class: 'badge-default' };
};
</script>

<template>
  <div class="admin-dashboard">
    <!-- Header -->
    <header class="dashboard-header">
      <div class="header-content">
        <div>
          <h1>Panneau d'Administration</h1>
          <p>Bienvenue, {{ adminStore.adminEmail }}</p>
        </div>
        <div class="header-actions">
          <button @click="goToChat" class="btn-chat">
            💬 Chat Support
          </button>
          <button @click="goToBlockedAccounts" class="btn-secondary">
            🚫 Comptes Bloqués
          </button>
          <button @click="goToActions" class="btn-secondary">
            📋 Historique
          </button>
          <button @click="handleLogout" class="btn-logout">
            🚪 Déconnexion
          </button>
        </div>
      </div>
    </header>

    <!-- Stats -->
    <div class="stats-container">
      <div class="stat-card">
        <div class="stat-icon pending">⏳</div>
        <div class="stat-info">
          <h3>{{ adminStore.pendingComplaints.length }}</h3>
          <p>Plaintes en attente</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon approved">✅</div>
        <div class="stat-info">
          <h3>{{ adminStore.approvedComplaints.length }}</h3>
          <p>Plaintes approuvées</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon rejected">❌</div>
        <div class="stat-info">
          <h3>{{ adminStore.rejectedComplaints.length }}</h3>
          <p>Plaintes rejetées</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon total">📊</div>
        <div class="stat-info">
          <h3>{{ adminStore.totalComplaints }}</h3>
          <p>Total plaintes</p>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>
    <div v-if="errorMessage" class="alert alert-error">
      {{ errorMessage }}
    </div>

    <!-- Tabs -->
    <div class="tabs-container">
      <button 
        @click="changeTab('pending')" 
        :class="['tab', { active: activeTab === 'pending' }]"
      >
        En attente ({{ adminStore.pendingComplaints.length }})
      </button>
      <button 
        @click="changeTab('approved')" 
        :class="['tab', { active: activeTab === 'approved' }]"
      >
        Approuvées ({{ adminStore.approvedComplaints.length }})
      </button>
      <button 
        @click="changeTab('rejected')" 
        :class="['tab', { active: activeTab === 'rejected' }]"
      >
        Rejetées ({{ adminStore.rejectedComplaints.length }})
      </button>
      <button 
        @click="changeTab('all')" 
        :class="['tab', { active: activeTab === 'all' }]"
      >
        Toutes ({{ adminStore.complaints.length }})
      </button>
    </div>

    <!-- Complaints List -->
    <div class="complaints-container">
      <div v-if="adminStore.isLoading" class="loading">
        Chargement...
      </div>

      <div v-else-if="filteredComplaints.length === 0" class="empty-state">
        <p>Aucune plainte pour le moment</p>
      </div>

      <div v-else class="complaints-list">
        <div 
          v-for="complaint in filteredComplaints" 
          :key="complaint.id" 
          class="complaint-card"
        >
          <div class="complaint-header">
            <div>
              <span :class="['status-badge', getStatusBadge(complaint.status).class]">
                {{ getStatusBadge(complaint.status).text }}
              </span>
              <span class="complaint-id">#{{ complaint.id }}</span>
            </div>
            <span class="complaint-date">{{ formatDate(complaint.created_at) }}</span>
          </div>

          <div class="complaint-body">
            <div class="complaint-row">
              <strong>Plaignant :</strong> 
              <span>{{ complaint.plaintiff_email || 'N/A' }}</span>
            </div>
            <div class="complaint-row">
              <strong>Utilisateur signalé :</strong> 
              <span class="reported-email">{{ complaint.reported_email }}</span>
            </div>
            <div class="complaint-row">
              <strong>Motif :</strong>
              <p class="reason">{{ complaint.reason }}</p>
            </div>
            <div v-if="complaint.reviewed_at" class="complaint-row">
              <strong>Examinée le :</strong> 
              <span>{{ formatDate(complaint.reviewed_at) }}</span>
            </div>
          </div>

          <div v-if="complaint.status === 'pending'" class="complaint-actions">
            <button @click="handleApprove(complaint.id)" class="btn-approve">
              ✓ Approuver & Bloquer
            </button>
            <button @click="openRejectModal(complaint)" class="btn-reject">
              ✗ Rejeter
            </button>
            <button @click="handleDelete(complaint.id)" class="btn-delete">
              🗑️ Supprimer
            </button>
          </div>

          <div v-else class="complaint-actions">
            <button @click="handleDelete(complaint.id)" class="btn-delete">
              🗑️ Supprimer
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Reject -->
    <div v-if="showRejectModal" class="modal-overlay" @click.self="showRejectModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>Rejeter la plainte</h2>
          <button @click="showRejectModal = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <p><strong>Plainte #{{ selectedComplaint?.id }}</strong></p>
          <p>Utilisateur signalé : {{ selectedComplaint?.reported_email }}</p>
          
          <label for="reject-notes">Notes (optionnel) :</label>
          <textarea 
            id="reject-notes"
            v-model="rejectNotes" 
            placeholder="Raison du rejet..."
            rows="4"
          ></textarea>
        </div>
        <div class="modal-footer">
          <button @click="showRejectModal = false" class="btn-cancel">
            Annuler
          </button>
          <button @click="handleReject" class="btn-confirm">
            Confirmer le rejet
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background: #f7fafc;
  padding: 20px;
}

/* Header */
.dashboard-header {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.dashboard-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 4px;
}

.dashboard-header p {
  font-size: 14px;
  color: #718096;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-chat {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-chat:hover {
  transform: translateY(-2px);
}

.btn-secondary {
  padding: 10px 20px;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-secondary:hover {
  transform: translateY(-2px);
}

.btn-logout {
  padding: 10px 20px;
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-logout:hover {
  transform: translateY(-2px);
}

/* Stats */
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 40px;
  width: 70px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.stat-icon.pending { background: #fef5e7; }
.stat-icon.approved { background: #e8f5e9; }
.stat-icon.rejected { background: #ffebee; }
.stat-icon.total { background: #e3f2fd; }

.stat-info h3 {
  font-size: 32px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 4px;
}

.stat-info p {
  font-size: 14px;
  color: #718096;
}

/* Alerts */
.alert {
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-weight: 500;
}

.alert-success {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.alert-error {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

/* Tabs */
.tabs-container {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.tab {
  padding: 12px 24px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-weight: 600;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.tab:hover {
  border-color: #cbd5e0;
}

.tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

/* Complaints */
.complaints-container {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading {
  text-align: center;
  padding: 40px;
  color: #718096;
  font-size: 18px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #a0aec0;
  font-size: 16px;
}

.complaints-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.complaint-card {
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  transition: border-color 0.2s;
}

.complaint-card:hover {
  border-color: #cbd5e0;
}

.complaint-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.badge-pending {
  background: #fef5e7;
  color: #f39c12;
}

.badge-approved {
  background: #e8f5e9;
  color: #27ae60;
}

.badge-rejected {
  background: #ffebee;
  color: #e74c3c;
}

.complaint-id {
  margin-left: 12px;
  color: #718096;
  font-size: 14px;
}

.complaint-date {
  color: #a0aec0;
  font-size: 14px;
}

.complaint-body {
  margin-bottom: 16px;
}

.complaint-row {
  margin-bottom: 12px;
}

.complaint-row strong {
  color: #2d3748;
  margin-right: 8px;
}

.reported-email {
  color: #e53e3e;
  font-weight: 600;
}

.reason {
  margin-top: 8px;
  padding: 12px;
  background: #f7fafc;
  border-radius: 6px;
  color: #4a5568;
  line-height: 1.6;
}

.complaint-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-approve {
  padding: 10px 20px;
  background: #48bb78;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-approve:hover {
  background: #38a169;
}

.btn-reject {
  padding: 10px 20px;
  background: #ed8936;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-reject:hover {
  background: #dd6b20;
}

.btn-delete {
  padding: 10px 20px;
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-delete:hover {
  background: #c53030;
}

/* Modal */
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

.modal {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1a202c;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #a0aec0;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
}

.close-btn:hover {
  color: #718096;
}

.modal-body {
  padding: 24px;
}

.modal-body p {
  margin-bottom: 16px;
  color: #4a5568;
}

.modal-body label {
  display: block;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 8px;
}

.modal-body textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  outline: none;
}

.modal-body textarea:focus {
  border-color: #667eea;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel {
  padding: 10px 20px;
  background: #e2e8f0;
  color: #4a5568;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #cbd5e0;
}

.btn-confirm {
  padding: 10px 20px;
  background: #ed8936;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-confirm:hover {
  background: #dd6b20;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .stats-container {
    grid-template-columns: 1fr;
  }

  .complaint-actions {
    flex-direction: column;
  }

  .complaint-actions button {
    width: 100%;
  }
}
</style>
