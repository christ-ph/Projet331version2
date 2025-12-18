<script setup>
// Le script reste identique à celui que vous avez fourni
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useProfileStore } from '@/stores/profile';

const authStore = useAuthStore();
const profileStore = useProfileStore();
const router = useRouter();

// Données réactives
const loading = ref(true);
const profile = ref({
  client_type: '',
  fullname: '',
  company_name: '',
  company_website: '',
  industry: '',
  email: ''
});
const activeTab = ref('profile');
const showEditModal = ref(false);

// Options pour les selects
const clientTypes = ref([
  { value: 'entreprise', label: 'Entreprise' },
  { value: 'startup', label: 'Startup' },
  { value: 'association', label: 'Association' },
  { value: 'particulier', label: 'Particulier' },
  { value: 'autre', label: 'Autre' }
]);

const industries = ref([
  { value: 'tech', label: 'Technologie' },
  { value: 'finance', label: 'Finance' },
  { value: 'sante', label: 'Santé' },
  { value: 'education', label: 'Éducation' },
  { value: 'ecommerce', label: 'E-commerce' },
  { value: 'marketing', label: 'Marketing' },
  { value: 'design', label: 'Design' },
  { value: 'immobilier', label: 'Immobilier' },
  { value: 'restauration', label: 'Restauration' },
  { value: 'autre', label: 'Autre' }
]);

// Données mockées pour les statistiques et projets
const stats = ref({
  totalProjects: 12,
  activeProjects: 3,
  completedProjects: 9,
  totalSpent: 1850000,
  favoriteFreelancers: 5
});

const recentProjects = ref([
  { id: 1, title: 'Site e-commerce', freelancer: 'Jean Dupont', status: 'en_cours', budget: 450000, deadline: '15 Mars 2024' },
  { id: 2, title: 'Application mobile', freelancer: 'Marie Nkono', status: 'termine', budget: 750000, deadline: '10 Mars 2024' },
  { id: 3, title: 'Logo design', freelancer: 'Paul Mboma', status: 'en_attente', budget: 120000, deadline: '20 Mars 2024' },
  { id: 4, title: 'Campagne SEO', freelancer: 'Sarah Tchoumi', status: 'en_cours', budget: 300000, deadline: '25 Mars 2024' }
]);

const favoriteFreelancers = ref([
  { id: 1, name: 'Jean Dupont', skills: ['Vue.js', 'Node.js'], rating: 4.8, projects: 3 },
  { id: 2, name: 'Marie Nkono', skills: ['React Native', 'Firebase'], rating: 4.9, projects: 2 },
  { id: 3, name: 'Paul Mboma', skills: ['Design UI/UX', 'Figma'], rating: 4.7, projects: 4 }
]);

// Formulaires
const editForm = ref({});

// Computed
const clientTypeLabel = computed(() => {
  const type = clientTypes.value.find(t => t.value === profile.value.client_type);
  return type ? type.label : profile.value.client_type;
});

const industryLabel = computed(() => {
  const industry = industries.value.find(i => i.value === profile.value.industry);
  return industry ? industry.label : profile.value.industry;
});

// Chargement des données
onMounted(async () => {
  try {
    const profileData = await profileStore.getMyProfile();
    
    if (!profileData || profileData.type !== "client") {
      router.push('/dashboard');
      return;
    }

    profile.value = {
      ...profile.value,
      ...profileData,
      email: authStore.user?.email || ''
    };

    editForm.value = { ...profile.value };

  } catch (error) {
    console.error('Erreur lors du chargement:', error);
  } finally {
    loading.value = false;
  }
});

// Modal functions
function openEditProfile() {
  editForm.value = { ...profile.value };
  showEditModal.value = true;
}

function closeEditProfile() {
  showEditModal.value = false;
}

async function saveProfile() {
  try {
    await profileStore.updateProfile({
      type: "client",
      ...editForm.value
    });
    
    profile.value = { ...profile.value, ...editForm.value };
    
    showNotification('Profil mis à jour avec succès !', 'success');
    closeEditProfile();
  } catch (error) {
    console.error('Erreur mise à jour profil:', error);
    showNotification('Erreur lors de la mise à jour du profil', 'error');
  }
}

function navigateTo(path) {
  router.push(path);
}

// Notification
const notification = ref({ show: false, message: '', type: '' });

function showNotification(message, type = 'success') {
  notification.value = { show: true, message, type };
  setTimeout(() => {
    notification.value.show = false;
  }, 3000);
}
</script>

<template>
  <div class="client-dashboard-page">
    <!-- Notification -->
    <div v-if="notification.show" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
      </div>
      <p>Chargement de votre profil...</p>
    </div>

    <!-- Contenu principal -->
    <div v-else class="dashboard-container">
      <!-- Navigation Tabs -->
      <div class="dashboard-tabs">
        <button 
          class="tab-btn" 
          :class="{ 'active': activeTab === 'profile' }"
          @click="activeTab = 'profile'"
        >
          <i class="fas fa-user-circle"></i>
          <span>Mon Profil</span>
        </button>
        <button 
          class="tab-btn" 
          :class="{ 'active': activeTab === 'projects' }"
          @click="activeTab = 'projects'"
        >
          <i class="fas fa-briefcase"></i>
          <span>Mes Projets</span>
          <span class="tab-badge">{{ stats.totalProjects }}</span>
        </button>
        <button 
          class="tab-btn" 
          :class="{ 'active': activeTab === 'freelancers' }"
          @click="activeTab = 'freelancers'"
        >
          <i class="fas fa-users"></i>
          <span>Freelances</span>
          <span class="tab-badge">{{ stats.favoriteFreelancers }}</span>
        </button>
        <button 
          class="tab-btn" 
          :class="{ 'active': activeTab === 'stats' }"
          @click="activeTab = 'stats'"
        >
          <i class="fas fa-chart-line"></i>
          <span>Statistiques</span>
        </button>
      </div>

      <!-- SECTION PROFIL -->
      <div v-if="activeTab === 'profile'" class="profile-section">
        <!-- En-tête du profil -->
        <div class="profile-header-card">
          <div class="profile-cover">
            <div class="profile-avatar-section">
              <div class="avatar-container">
                <div class="profile-avatar">
                  {{ profile.fullname?.charAt(0)?.toUpperCase() || 'C' }}
                </div>
                <div class="avatar-status"></div>
              </div>
              <div class="profile-main-info">
                <h1 class="profile-name">{{ profile.fullname || 'Client' }}</h1>
                <p class="profile-title">
                  <i class="fas fa-building"></i>
                  {{ profile.company_name || clientTypeLabel }}
                </p>
                <div class="profile-meta">
                  <span class="meta-item">
                    <i class="fas fa-envelope"></i>
                    {{ profile.email || 'Email non défini' }}
                  </span>
                  <span class="meta-item" v-if="profile.industry">
                    <i class="fas fa-industry"></i>
                    {{ industryLabel }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="profile-actions">
              <button class="action-btn primary-btn" @click="openEditProfile">
                <i class="fas fa-edit"></i>
                Modifier le profil
              </button>
              <button class="action-btn outline-btn" @click="navigateTo('/missions/create')">
                <i class="fas fa-plus"></i>
                Nouveau projet
              </button>
            </div>
          </div>

          <!-- Stats rapides -->
          <div class="profile-stats">
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-briefcase"></i>
              </div>
              <div class="stat-content">
                <h3 class="stat-value">{{ stats.totalProjects }}</h3>
                <p class="stat-label">Projets totaux</p>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-play-circle"></i>
              </div>
              <div class="stat-content">
                <h3 class="stat-value">{{ stats.activeProjects }}</h3>
                <p class="stat-label">Projets actifs</p>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-check-circle"></i>
              </div>
              <div class="stat-content">
                <h3 class="stat-value">{{ stats.completedProjects }}</h3>
                <p class="stat-label">Projets terminés</p>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-money-bill-wave"></i>
              </div>
              <div class="stat-content">
                <h3 class="stat-value">{{ stats.totalSpent.toLocaleString() }} FCFA</h3>
                <p class="stat-label">Total dépensé</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Détails du profil -->
        <div class="profile-details-grid">
          <!-- Informations entreprise -->
          <div class="detail-card company-card">
            <div class="card-header">
              <h3>
                <i class="fas fa-building"></i>
                Informations entreprise
              </h3>
              <button class="card-action-btn" @click="openEditProfile">
                <i class="fas fa-edit"></i>
              </button>
            </div>
            <div class="card-content">
              <div class="info-list">
                <div class="info-item">
                  <i class="fas fa-user-tie"></i>
                  <div>
                    <p class="info-label">Type de client</p>
                    <p class="info-value">{{ clientTypeLabel }}</p>
                  </div>
                </div>
                <div class="info-item" v-if="profile.company_name">
                  <i class="fas fa-landmark"></i>
                  <div>
                    <p class="info-label">Nom de l'entreprise</p>
                    <p class="info-value">{{ profile.company_name }}</p>
                  </div>
                </div>
                <div class="info-item" v-if="profile.industry">
                  <i class="fas fa-industry"></i>
                  <div>
                    <p class="info-label">Secteur d'activité</p>
                    <p class="info-value">{{ industryLabel }}</p>
                  </div>
                </div>
                <div class="info-item" v-if="profile.company_website">
                  <i class="fas fa-globe"></i>
                  <div>
                    <p class="info-label">Site web</p>
                    <a :href="profile.company_website" target="_blank" class="website-link">
                      {{ profile.company_website }}
                      <i class="fas fa-external-link-alt"></i>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Projets récents -->
          <div class="detail-card recent-projects-card">
            <div class="card-header">
              <h3>
                <i class="fas fa-clock"></i>
                Projets récents
              </h3>
              <button class="card-action-btn" @click="navigateTo('/client/missions')">
                <i class="fas fa-external-link-alt"></i>
              </button>
            </div>
            <div class="card-content">
              <div class="projects-list">
                <div v-for="project in recentProjects.slice(0, 3)" :key="project.id" class="project-item">
                  <div class="project-info">
                    <h4 class="project-title">{{ project.title }}</h4>
                    <p class="project-freelancer">
                      <i class="fas fa-user"></i>
                      {{ project.freelancer }}
                    </p>
                  </div>
                  <div class="project-meta">
                    <span class="project-budget">{{ project.budget.toLocaleString() }} FCFA</span>
                    <span class="project-status" :class="project.status">
                      {{ project.status === 'en_cours' ? 'En cours' : 
                         project.status === 'termine' ? 'Terminé' : 'En attente' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Freelances favoris -->
          <div class="detail-card favorites-card">
            <div class="card-header">
              <h3>
                <i class="fas fa-star"></i>
                Freelances favoris
              </h3>
              <button class="card-action-btn" @click="navigateTo('/freelances')">
                <i class="fas fa-external-link-alt"></i>
              </button>
            </div>
            <div class="card-content">
              <div class="freelancers-list">
                <div v-for="freelancer in favoriteFreelancers" :key="freelancer.id" class="freelancer-item">
                  <div class="freelancer-avatar">
                    {{ freelancer.name.charAt(0) }}
                  </div>
                  <div class="freelancer-info">
                    <h4 class="freelancer-name">{{ freelancer.name }}</h4>
                    <div class="freelancer-skills">
                      <span v-for="skill in freelancer.skills.slice(0, 2)" :key="skill" class="skill-tag">
                        {{ skill }}
                      </span>
                    </div>
                  </div>
                  <div class="freelancer-rating">
                    <i class="fas fa-star"></i>
                    <span>{{ freelancer.rating }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions rapides -->
          <div class="detail-card quick-actions-card">
            <div class="card-header">
              <h3>
                <i class="fas fa-bolt"></i>
                Actions rapides
              </h3>
            </div>
            <div class="card-content">
              <div class="actions-grid">
                <button class="action-card" @click="navigateTo('/missions/create')">
                  <div class="action-icon">
                    <i class="fas fa-plus-circle"></i>
                  </div>
                  <div class="action-content">
                    <h4>Nouveau projet</h4>
                    <p>Publiez une mission</p>
                  </div>
                </button>
                
                <button class="action-card" @click="navigateTo('/freelances')">
                  <div class="action-icon">
                    <i class="fas fa-search"></i>
                  </div>
                  <div class="action-content">
                    <h4>Trouver un freelance</h4>
                    <p>Recherchez des talents</p>
                  </div>
                </button>
                
                <button class="action-card" @click="navigateTo('/messages')">
                  <div class="action-icon">
                    <i class="fas fa-comments"></i>
                  </div>
                  <div class="action-content">
                    <h4>Messages</h4>
                    <p>Discutez avec les freelances</p>
                  </div>
                </button>
                
                <button class="action-card" @click="navigateTo('/client/missions')">
                  <div class="action-icon">
                    <i class="fas fa-list-check"></i>
                  </div>
                  <div class="action-content">
                    <h4>Mes projets</h4>
                    <p>Gérez vos missions</p>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- SECTION PROJETS -->
      <div v-else-if="activeTab === 'projects'" class="projects-section">
        <div class="section-header">
          <div>
            <h2 class="section-title">
              <i class="fas fa-briefcase"></i>
              Mes Projets
            </h2>
            <p class="section-subtitle">
              Gérez toutes vos missions et collaborations
            </p>
          </div>
          <button class="add-project-btn" @click="navigateTo('/missions/create')">
            <i class="fas fa-plus"></i>
            Nouveau projet
          </button>
        </div>

        <div class="projects-filters">
          <button class="filter-btn active">Tous ({{ recentProjects.length }})</button>
          <button class="filter-btn">En cours ({{ recentProjects.filter(p => p.status === 'en_cours').length }})</button>
          <button class="filter-btn">Terminés ({{ recentProjects.filter(p => p.status === 'termine').length }})</button>
          <button class="filter-btn">En attente ({{ recentProjects.filter(p => p.status === 'en_attente').length }})</button>
        </div>

        <div class="projects-grid">
          <div 
            v-for="project in recentProjects" 
            :key="project.id" 
            class="project-card"
            @click="navigateTo(`/project/${project.id}`)"
          >
            <div class="project-header">
              <div class="project-status-badge" :class="project.status">
                {{ project.status === 'en_cours' ? 'En cours' : 
                   project.status === 'termine' ? 'Terminé' : 'En attente' }}
              </div>
              <div class="project-actions">
                <button class="icon-btn">
                  <i class="fas fa-ellipsis-v"></i>
                </button>
              </div>
            </div>
            
            <h3 class="project-title">{{ project.title }}</h3>
            
            <div class="project-freelancer-info">
              <div class="freelancer-avatar small">
                {{ project.freelancer.charAt(0) }}
              </div>
              <div class="freelancer-details">
                <p class="freelancer-name">{{ project.freelancer }}</p>
                <p class="project-deadline">
                  <i class="far fa-calendar-alt"></i>
                  {{ project.deadline }}
                </p>
              </div>
            </div>
            
            <div class="project-meta">
              <div class="meta-item">
                <i class="fas fa-money-bill-wave"></i>
                <span>{{ project.budget.toLocaleString() }} FCFA</span>
              </div>
              <div class="meta-item">
                <i class="fas fa-clock"></i>
                <span>2 semaines</span>
              </div>
            </div>
            
            <div class="project-actions-footer">
              <button class="action-btn outline-btn small" @click.stop="navigateTo(`/project/${project.id}`)">
                <i class="fas fa-eye"></i>
                Voir détails
              </button>
              <button class="action-btn primary-btn small" @click.stop="navigateTo(`/messages?project=${project.id}`)">
                <i class="fas fa-comment"></i>
                Message
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- SECTION FREELANCES -->
      <div v-else-if="activeTab === 'freelancers'" class="freelancers-section">
        <div class="section-header">
          <div>
            <h2 class="section-title">
              <i class="fas fa-users"></i>
              Freelances
            </h2>
            <p class="section-subtitle">
              Découvrez les meilleurs talents pour vos projets
            </p>
          </div>
          <button class="add-project-btn" @click="navigateTo('/freelances')">
            <i class="fas fa-search"></i>
            Voir tous
          </button>
        </div>

        <div class="freelancers-grid">
          <div 
            v-for="freelancer in favoriteFreelancers" 
            :key="freelancer.id" 
            class="freelancer-card"
          >
            <div class="freelancer-header">
              <div class="freelancer-avatar large">
                {{ freelancer.name.charAt(0) }}
              </div>
              <div class="freelancer-rating-badge">
                <i class="fas fa-star"></i>
                {{ freelancer.rating }}
              </div>
            </div>
            
            <h3 class="freelancer-name">{{ freelancer.name }}</h3>
            
            <div class="freelancer-skills-list">
              <span v-for="skill in freelancer.skills" :key="skill" class="skill-tag">
                {{ skill }}
              </span>
            </div>
            
            <div class="freelancer-stats">
              <div class="stat">
                <span class="stat-number">{{ freelancer.projects }}</span>
                <span class="stat-label">projets</span>
              </div>
              <div class="stat">
                <span class="stat-number">95%</span>
                <span class="stat-label">satisfaction</span>
              </div>
              <div class="stat">
                <span class="stat-number">2</span>
                <span class="stat-label">semaines</span>
              </div>
            </div>
            
            <div class="freelancer-actions">
              <button class="action-btn outline-btn" @click="navigateTo(`/freelancer/${freelancer.id}`)">
                <i class="fas fa-eye"></i>
                Voir profil
              </button>
              <button class="action-btn primary-btn" @click="navigateTo(`/messages?freelancer=${freelancer.id}`)">
                <i class="fas fa-comment"></i>
                Contacter
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- SECTION STATISTIQUES -->
      <div v-else class="stats-section">
        <div class="section-header">
          <h2 class="section-title">
            <i class="fas fa-chart-line"></i>
            Mes Statistiques
          </h2>
        </div>
        
        <div class="stats-cards">
          <div class="stats-card main">
            <h3>Performance globale</h3>
            <div class="stats-metrics">
              <div class="metric">
                <span class="metric-value">{{ stats.totalProjects }}</span>
                <span class="metric-label">Projets</span>
              </div>
              <div class="metric">
                <span class="metric-value">{{ stats.totalSpent.toLocaleString() }} FCFA</span>
                <span class="metric-label">Investis</span>
              </div>
              <div class="metric">
                <span class="metric-value">4.7</span>
                <span class="metric-label">Note moyenne</span>
              </div>
            </div>
          </div>
          
          <div class="stats-card">
            <h3>Activité récente</h3>
            <div class="activity-list">
              <div class="activity-item">
                <i class="fas fa-file-contract info"></i>
                <div>
                  <p>Nouveau projet "Refonte site web"</p>
                  <span class="activity-time">Il y a 2 jours</span>
                </div>
              </div>
              <div class="activity-item">
                <i class="fas fa-money-bill-wave success"></i>
                <div>
                  <p>Paiement envoyé à Jean Dupont</p>
                  <span class="activity-time">Il y a 3 jours</span>
                </div>
              </div>
              <div class="activity-item">
                <i class="fas fa-comment warning"></i>
                <div>
                  <p>Nouveau message de Marie Nkono</p>
                  <span class="activity-time">Il y a 5 jours</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL EDIT PROFILE -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditProfile">
      <div class="modal">
        <div class="modal-header">
          <h2>
            <i class="fas fa-user-edit"></i>
            Modifier le profil client
          </h2>
          <button class="modal-close" @click="closeEditProfile">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group">
              <label for="client_type">
                <i class="fas fa-users"></i>
                Type de client *
              </label>
              <select id="client_type" v-model="editForm.client_type" required>
                <option value="">Sélectionner un type</option>
                <option v-for="type in clientTypes" :key="type.value" :value="type.value">
                  {{ type.label }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="fullname">
                <i class="fas fa-user-tie"></i>
                Nom complet *
              </label>
              <input 
                id="fullname" 
                v-model="editForm.fullname" 
                type="text" 
                placeholder="Votre nom complet"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="company_name">
                <i class="fas fa-landmark"></i>
                Nom de l'entreprise
              </label>
              <input 
                id="company_name" 
                v-model="editForm.company_name" 
                type="text" 
                placeholder="Ex: Tech Solutions SARL"
              />
            </div>
            
            <div class="form-group">
              <label for="industry">
                <i class="fas fa-industry"></i>
                Secteur d'activité *
              </label>
              <select id="industry" v-model="editForm.industry" required>
                <option value="">Sélectionner un secteur</option>
                <option v-for="industry in industries" :key="industry.value" :value="industry.value">
                  {{ industry.label }}
                </option>
              </select>
            </div>
            
            <div class="form-group full-width">
              <label for="company_website">
                <i class="fas fa-globe"></i>
                Site web
              </label>
              <div class="input-with-icon">
                <i class="fas fa-link input-prefix"></i>
                <input 
                  id="company_website" 
                  v-model="editForm.company_website" 
                  type="url" 
                  placeholder="https://votre-entreprise.com"
                />
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeEditProfile">
            Annuler
          </button>
          <button class="btn btn-primary" @click="saveProfile">
            <i class="fas fa-save"></i>
            Enregistrer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==================== STYLES GÉNÉRAUX ==================== */
.client-dashboard-page {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px;
}

/* ==================== NOTIFICATIONS ==================== */
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 25px;
  border-radius: 12px;
  color: white;
  font-weight: 600;
  z-index: 1000;
  animation: slideIn 0.3s ease;
  max-width: 400px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
}

.notification.success {
  background: linear-gradient(135deg, #10B981, #34D399);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.notification.error {
  background: linear-gradient(135deg, #EF4444, #F87171);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* ==================== LOADING ==================== */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  text-align: center;
}

.loading-spinner {
  font-size: 3rem;
  color: #FF6B35;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.loading-spinner i {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-container p {
  color: #2D3047;
  font-size: 1.2rem;
  font-weight: 500;
}

/* ==================== CONTAINER ==================== */
.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* ==================== TABS ==================== */
.dashboard-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  background: white;
  padding: 10px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  flex-wrap: wrap;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px 25px;
  border: none;
  background: transparent;
  color: #6c757d;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  white-space: nowrap;
}

.tab-btn:hover {
  background: rgba(255, 107, 53, 0.1);
  color: #FF6B35;
  transform: translateY(-2px);
}

.tab-btn.active {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  box-shadow: 0 5px 15px rgba(255, 107, 53, 0.3);
}

.tab-btn i {
  font-size: 1.1rem;
}

.tab-badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 0.85rem;
  min-width: 24px;
  height: 24px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  margin-left: 5px;
}

/* ==================== PROFILE SECTION ==================== */
.profile-header-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  position: relative;
  overflow: hidden;
}

.profile-header-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
}

.profile-cover {
  margin-bottom: 30px;
}

.profile-avatar-section {
  display: flex;
  align-items: center;
  gap: 25px;
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .profile-avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
}

.avatar-container {
  position: relative;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 2.5rem;
  border: 4px solid white;
  box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
  transition: transform 0.3s ease;
}

.profile-avatar:hover {
  transform: scale(1.05);
}

.avatar-status {
  position: absolute;
  bottom: 10px;
  right: 10px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #10B981;
  border: 3px solid white;
  box-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);
}

.profile-main-info {
  flex: 1;
}

.profile-name {
  font-size: 2.2rem;
  font-weight: 700;
  color: #2D3047;
  margin: 0 0 10px 0;
  line-height: 1.2;
}

.profile-title {
  font-size: 1.2rem;
  color: #6c757d;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 15px 0;
}

.profile-title i {
  color: #FF6B35;
}

.profile-meta {
  display: flex;
  gap: 25px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #6c757d;
  font-size: 0.95rem;
  padding: 8px 16px;
  background: #f8f9fa;
  border-radius: 10px;
  border: 1px solid #e9ecef;
}

.meta-item i {
  color: #FF6B35;
  font-size: 1rem;
}

.profile-actions {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 2px solid transparent;
}

.primary-btn {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
}

.primary-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(255, 107, 53, 0.3);
}

.outline-btn {
  background: white;
  color: #2D3047;
  border: 2px solid #e5e7eb;
}

.outline-btn:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: translateY(-3px);
}

.action-btn.small {
  padding: 8px 16px;
  font-size: 0.9rem;
}

/* ==================== PROFILE STATS ==================== */
.profile-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  padding-top: 30px;
  border-top: 2px solid #f1f5f9;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 15px;
  border: 2px solid transparent;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease;
}

.stat-card:hover {
  border-color: #FF6B35;
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.stat-card:hover::before {
  transform: scaleX(1);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  position: relative;
  z-index: 2;
}

.stat-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 107, 53, 0.2), rgba(255, 142, 83, 0.2));
  border-radius: 12px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.stat-content {
  flex: 1;
  position: relative;
  z-index: 2;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2D3047;
  margin: 0 0 5px 0;
  line-height: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: #6c757d;
}

/* ==================== PROFILE DETAILS GRID ==================== */
.profile-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
}

.detail-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  border: 2px solid #f1f5f9;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.detail-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease;
}

.detail-card:hover {
  border-color: #FF6B35;
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
}

.detail-card:hover::before {
  transform: scaleX(1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f1f5f9;
}

.card-header h3 {
  font-size: 1.3rem;
  color: #2D3047;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-header i {
  color: #FF6B35;
  font-size: 1.2rem;
}

.card-action-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #e5e7eb;
  background: white;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.card-action-btn:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: rotate(15deg) scale(1.1);
  box-shadow: 0 5px 15px rgba(255, 107, 53, 0.2);
}

/* Info List */
.info-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.info-item:hover {
  border-color: #FF6B35;
  transform: translateX(5px);
}

.info-item i {
  color: #FF6B35;
  font-size: 1.2rem;
  margin-top: 3px;
}

.info-label {
  font-size: 0.85rem;
  color: #6c757d;
  margin: 0 0 5px 0;
  font-weight: 500;
}

.info-value {
  font-size: 1rem;
  font-weight: 600;
  color: #2D3047;
  margin: 0;
}

.website-link {
  color: #3B82F6;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.website-link:hover {
  color: #FF6B35;
}

.website-link i {
  font-size: 0.8rem;
}

/* Projects List */
.projects-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.project-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8fafc;
  border-radius: 10px;
  border: 2px solid #f1f5f9;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.project-item:hover {
  border-color: #FF6B35;
  transform: translateX(8px);
}

.project-info {
  flex: 1;
}

.project-title {
  font-size: 1rem;
  font-weight: 600;
  color: #2D3047;
  margin: 0 0 5px 0;
}

.project-freelancer {
  font-size: 0.9rem;
  color: #6c757d;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.project-freelancer i {
  color: #FF6B35;
  font-size: 0.8rem;
}

.project-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.project-budget {
  font-weight: 600;
  color: #10B981;
  font-size: 0.95rem;
}

.project-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.project-status.en_cours {
  background: #DBEAFE;
  color: #1E40AF;
}

.project-status.termine {
  background: #D1FAE5;
  color: #065F46;
}

.project-status.en_attente {
  background: #FEF3C7;
  color: #92400E;
}

/* Freelancers List */
.freelancers-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.freelancer-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8fafc;
  border-radius: 10px;
  border: 2px solid #f1f5f9;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.freelancer-item:hover {
  border-color: #FF6B35;
  transform: translateX(8px);
}

.freelancer-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  flex-shrink: 0;
  border: 2px solid white;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.freelancer-avatar.small {
  width: 30px;
  height: 30px;
  font-size: 0.9rem;
}

.freelancer-avatar.large {
  width: 60px;
  height: 60px;
  font-size: 1.5rem;
}

.freelancer-info {
  flex: 1;
}

.freelancer-name {
  font-size: 1rem;
  font-weight: 600;
  color: #2D3047;
  margin: 0 0 5px 0;
}

.freelancer-skills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.skill-tag {
  padding: 4px 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 15px;
  font-size: 0.8rem;
  color: #6c757d;
  font-weight: 500;
  transition: all 0.3s ease;
}

.skill-tag:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: translateY(-1px);
}

.freelancer-rating {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #F59E0B;
  font-weight: 600;
  padding: 6px 12px;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 20px;
}

.freelancer-rating-badge {
  padding: 6px 12px;
  background: #FEF3C7;
  color: #92400E;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
}

/* Actions Grid */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.action-card {
  background: #f8fafc;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  text-align: left;
  display: flex;
  align-items: center;
  gap: 15px;
}

.action-card:hover {
  border-color: #FF6B35;
  transform: translateY(-8px);
  box-shadow: 0 15px 40px rgba(255, 107, 53, 0.15);
}

.action-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  position: relative;
  overflow: hidden;
}

.action-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 107, 53, 0.2), rgba(255, 142, 83, 0.2));
  animation: pulse 2s infinite;
}

.action-content h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #2D3047;
  margin: 0 0 5px 0;
}

.action-content p {
  font-size: 0.85rem;
  color: #6c757d;
  margin: 0;
}

/* ==================== SECTIONS COMMUNES ==================== */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
}

.section-header > div {
  flex: 1;
}

.section-title {
  font-size: 1.8rem;
  color: #2D3047;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  gap: 15px;
}

.section-title i {
  color: #FF6B35;
  font-size: 1.5rem;
}

.section-subtitle {
  color: #6c757d;
  margin: 0;
  font-size: 1rem;
  line-height: 1.6;
}

.add-project-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 2px solid transparent;
}

.add-project-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
  border-color: rgba(255, 255, 255, 0.2);
}

/* ==================== PROJECTS SECTION ==================== */
.projects-filters {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 12px 24px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  color: #6c757d;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.filter-btn:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: translateY(-2px);
}

.filter-btn.active {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border-color: #FF6B35;
  box-shadow: 0 5px 15px rgba(255, 107, 53, 0.3);
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
}

.project-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  border: 2px solid #f1f5f9;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.project-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease;
}

.project-card:hover {
  border-color: #FF6B35;
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
}

.project-card:hover::before {
  transform: scaleX(1);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.project-status-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.project-status-badge.en_cours {
  background: #DBEAFE;
  color: #1E40AF;
}

.project-status-badge.termine {
  background: #D1FAE5;
  color: #065F46;
}

.project-status-badge.en_attente {
  background: #FEF3C7;
  color: #92400E;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #e5e7eb;
  background: white;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.icon-btn:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: rotate(90deg) scale(1.1);
}

.project-freelancer-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin: 20px 0;
  padding: 15px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #e9ecef;
}

.freelancer-details .freelancer-name {
  font-weight: 600;
  color: #2D3047;
  margin: 0 0 5px 0;
}

.project-deadline {
  font-size: 0.9rem;
  color: #6c757d;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.project-deadline i {
  color: #FF6B35;
}

.project-meta {
  display: flex;
  gap: 20px;
  margin: 20px 0;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6c757d;
  font-size: 0.9rem;
  padding: 8px 16px;
  background: #f8f9fa;
  border-radius: 10px;
  border: 1px solid #e9ecef;
}

.meta-item i {
  color: #FF6B35;
}

.project-actions-footer {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

/* ==================== FREELANCERS SECTION ==================== */
.freelancers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.freelancer-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  text-align: center;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  border: 2px solid #f1f5f9;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.freelancer-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease;
}

.freelancer-card:hover {
  border-color: #FF6B35;
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
}

.freelancer-card:hover::before {
  transform: scaleX(1);
}

.freelancer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.freelancer-skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin: 15px 0;
}

.freelancer-stats {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
  padding: 15px 0;
  border-top: 2px solid #f1f5f9;
  border-bottom: 2px solid #f1f5f9;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 1.2rem;
  font-weight: 700;
  color: #2D3047;
}

.stat-label {
  font-size: 0.8rem;
  color: #6c757d;
  margin-top: 5px;
}

.freelancer-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

/* ==================== STATS SECTION ==================== */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
}

.stats-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  border: 2px solid #f1f5f9;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.stats-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease;
}

.stats-card:hover::before {
  transform: scaleX(1);
}

.stats-card.main {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  border: none;
}

.stats-card h3 {
  font-size: 1.3rem;
  margin: 0 0 25px 0;
  color: #2D3047;
  position: relative;
  padding-bottom: 15px;
}

.stats-card h3::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: #FF6B35;
  border-radius: 2px;
}

.stats-card.main h3 {
  color: white;
}

.stats-card.main h3::after {
  background: #FFD166;
}

.stats-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  transition: all 0.3s ease;
}

.metric:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-5px);
}

.metric-value {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 5px;
  line-height: 1;
}

.stats-card.main .metric-value {
  color: #FFD166;
}

.metric-label {
  font-size: 0.9rem;
  color: #6c757d;
  font-weight: 500;
}

.stats-card.main .metric-label {
  color: rgba(255, 255, 255, 0.8);
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.activity-item {
  display: flex;
  gap: 15px;
  align-items: flex-start;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.activity-item:hover {
  transform: translateX(5px);
}

.activity-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.activity-item i {
  font-size: 1.2rem;
  margin-top: 3px;
  flex-shrink: 0;
}

.activity-item i.success {
  color: #10B981;
}

.activity-item i.info {
  color: #3B82F6;
}

.activity-item i.warning {
  color: #F59E0B;
}

.activity-item p {
  margin: 0 0 5px 0;
  color: #2D3047;
  font-weight: 500;
}

.activity-time {
  font-size: 0.85rem;
  color: #6c757d;
}

/* ==================== MODALS ==================== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(45, 48, 71, 0.8);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  border: 1px solid #f0f0f0;
  animation: modalSlideIn 0.3s ease;
  position: relative;
}

@keyframes modalSlideIn {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  padding: 25px 30px;
  border-bottom: 2px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  background: white;
  z-index: 1;
  border-radius: 20px 20px 0 0;
}

.modal-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #2D3047;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-header i {
  color: #FF6B35;
}

.modal-close {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #e5e7eb;
  background: white;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.modal-close:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: rotate(90deg) scale(1.1);
  box-shadow: 0 5px 15px rgba(255, 107, 53, 0.2);
}

.modal-body {
  padding: 30px;
}

.modal-footer {
  padding: 25px 30px;
  border-top: 2px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  position: sticky;
  bottom: 0;
  background: white;
  border-radius: 0 0 20px 20px;
}

/* ==================== FORM STYLES ==================== */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #2D3047;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-group i {
  color: #FF6B35;
}

.form-group input,
.form-group textarea,
.form-group select {
  padding: 14px 15px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.95rem;
  font-family: inherit;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  background: white;
  color: #2D3047;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #FF6B35;
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
  transform: translateY(-2px);
}

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-prefix {
  position: absolute;
  left: 16px;
  color: #6c757d;
  font-size: 1rem;
}

.input-with-icon .input-prefix + input {
  padding-left: 45px;
}

/* ==================== BUTTONS ==================== */
.btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 2px solid transparent;
  font-family: inherit;
}

.btn-primary {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
  border-color: rgba(255, 255, 255, 0.2);
}

.btn-secondary {
  background: white;
  color: #2D3047;
  border: 2px solid #e5e7eb;
}

.btn-secondary:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: translateY(-3px);
}

/* ==================== RESPONSIVE DESIGN ==================== */

/* Tablette en mode paysage et petits ordinateurs portables */
@media (max-width: 1200px) {
  .dashboard-container {
    padding: 0 20px;
  }
  
  .profile-details-grid {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .stats-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Tablette en mode portrait */
@media (max-width: 1024px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .profile-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .projects-grid,
  .freelancers-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Tablette petite et grands téléphones */
@media (max-width: 768px) {
  .client-dashboard-page {
    padding: 15px;
  }
  
  /* Tabs */
  .dashboard-tabs {
    flex-direction: column;
  }
  
  .tab-btn {
    width: 100%;
    justify-content: flex-start;
  }
  
  /* Profile Header */
  .profile-avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .profile-meta {
    justify-content: center;
  }
  
  .profile-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .action-btn {
    width: 100%;
    justify-content: center;
  }
  
  /* Profile Stats */
  .profile-stats {
    grid-template-columns: 1fr;
  }
  
  /* Section Header */
  .section-header {
    flex-direction: column;
    gap: 20px;
    align-items: stretch;
  }
  
  .add-project-btn {
    width: 100%;
    justify-content: center;
  }
  
  /* Projects Grid */
  .projects-grid,
  .freelancers-grid {
    grid-template-columns: 1fr;
  }
  
  /* Modal */
  .modal {
    max-width: 95%;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  /* Forms */
  .form-group {
    margin-bottom: 20px;
  }
}

/* Téléphones petits */
@media (max-width: 480px) {
  .profile-name {
    font-size: 1.8rem;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
  
  .profile-details-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-metrics {
    grid-template-columns: 1fr;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .modal-header,
  .modal-footer {
    padding: 20px;
  }
  
  .projects-filters {
    flex-direction: column;
  }
  
  .filter-btn {
    width: 100%;
  }
}

/* Support tactile amélioré */
@media (hover: none) and (pointer: coarse) {
  .project-card:hover,
  .freelancer-card:hover,
  .action-btn:hover,
  .icon-btn:hover,
  .card-action-btn:hover,
  .modal-close:hover,
  .stat-card:hover,
  .detail-card:hover,
  .info-item:hover,
  .project-item:hover,
  .freelancer-item:hover,
  .action-card:hover {
    transform: none;
  }
  
  .project-card:active,
  .freelancer-card:active,
  .detail-card:active {
    transform: scale(0.98);
  }
}

/* Support pour les modes sombre */
@media (prefers-color-scheme: dark) {
  .client-dashboard-page {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  }
  
  .detail-card,
  .profile-header-card,
  .section-header,
  .project-card,
  .freelancer-card,
  .stats-card,
  .modal {
    background: #2d2d2d;
    border-color: #404040;
    color: #e4e4e4;
  }
  
  .stat-card,
  .info-item,
  .project-item,
  .freelancer-item,
  .action-card,
  .project-freelancer-info,
  .meta-item {
    background: #363636;
    border-color: #404040;
  }
  
  .profile-name,
  .section-title,
  .card-header h3,
  .info-value,
  .project-title,
  .freelancer-name,
  .stat-value,
  .metric-value {
    color: #e4e4e4;
  }
  
  .profile-title,
  .section-subtitle,
  .info-label,
  .project-freelancer,
  .stat-label,
  .metric-label,
  .activity-time {
    color: #a0a0a0;
  }
}
</style>