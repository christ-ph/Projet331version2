<script setup>
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

const activeTab = ref('projects');
const showEditModal = ref(false);

// Données réelles
const stats = ref({
  totalProjects: 0,
  activeProjects: 0,
  completedProjects: 0,
  totalSpent: 0
});

const projects = ref([]);
const freelancers = ref([]);

// Options pour les selects (gardées pour le formulaire d'édition)
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

// Filtres
const projectFilter = ref('all');
const freelancerFilter = ref('all');

// Fonctions pour charger les données réelles
async function loadProfile() {
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
    console.error('Erreur lors du chargement du profil:', error);
  }
}

async function loadProjects() {
  try {
    // Ici, vous devriez appeler votre API pour récupérer les projets
    // Exemple: const response = await api.get('/projects');
    // projects.value = response.data;
    
    // Pour l'instant, on laisse un tableau vide qui sera rempli par votre API
    projects.value = [];
    
    // Calculer les statistiques
    stats.value.totalProjects = projects.value.length;
    stats.value.activeProjects = projects.value.filter(p => p.status === 'en_cours').length;
    stats.value.completedProjects = projects.value.filter(p => p.status === 'termine').length;
    stats.value.totalSpent = projects.value
      .filter(p => p.status === 'termine')
      .reduce((sum, p) => sum + (p.budget || 0), 0);
      
  } catch (error) {
    console.error('Erreur lors du chargement des projets:', error);
  }
}

async function loadFreelancers() {
  try {
    // Ici, vous devriez appeler votre API pour récupérer les freelances
    // Exemple: const response = await api.get('/freelancers');
    // freelancers.value = response.data;
    
    // Pour l'instant, on laisse un tableau vide qui sera rempli par votre API
    freelancers.value = [];
    
  } catch (error) {
    console.error('Erreur lors du chargement des freelances:', error);
  }
}

// Chargement des données
onMounted(async () => {
  try {
    loading.value = true;
    await Promise.all([
      loadProfile(),
      loadProjects(),
      loadFreelancers()
    ]);
  } catch (error) {
    console.error('Erreur lors du chargement:', error);
  } finally {
    loading.value = false;
  }
});

// Fonctions de filtrage
const filteredProjects = computed(() => {
  if (projectFilter.value === 'all') return projects.value;
  return projects.value.filter(project => {
    if (projectFilter.value === 'en_cours') return project.status === 'en_cours';
    if (projectFilter.value === 'termine') return project.status === 'termine';
    if (projectFilter.value === 'en_attente') return project.status === 'en_attente';
    return true;
  });
});

const filteredFreelancers = computed(() => {
  return freelancers.value;
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
      <p>Chargement de votre dashboard...</p>
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
          <span>Projets</span>
          <span class="tab-badge">{{ stats.totalProjects }}</span>
        </button>
        <button 
          class="tab-btn" 
          :class="{ 'active': activeTab === 'freelancers' }"
          @click="activeTab = 'freelancers'"
        >
          <i class="fas fa-users"></i>
          <span>Freelances</span>
          <span class="tab-badge">{{ freelancers.length }}</span>
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
                
                <button class="action-card" @click="activeTab = 'projects'">
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
              Tous les Projets
            </h2>
            <p class="section-subtitle">
              {{ projects.length }} projet{{ projects.length !== 1 ? 's' : '' }} disponible{{ projects.length !== 1 ? 's' : '' }}
            </p>
          </div>
          <button class="add-project-btn" @click="navigateTo('/missions/create')">
            <i class="fas fa-plus"></i>
            Nouveau projet
          </button>
        </div>

        <div v-if="projects.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-briefcase"></i>
          </div>
          <h3>Aucun projet disponible</h3>
          <p>Commencez par créer votre premier projet pour trouver des freelances talentueux</p>
          <button class="action-btn primary-btn" @click="navigateTo('/missions/create')">
            <i class="fas fa-plus"></i>
            Créer un projet
          </button>
        </div>

        <div v-else>
          <div class="projects-filters">
            <button 
              class="filter-btn" 
              :class="{ 'active': projectFilter === 'all' }"
              @click="projectFilter = 'all'"
            >
              Tous ({{ projects.length }})
            </button>
            <button 
              class="filter-btn" 
              :class="{ 'active': projectFilter === 'en_cours' }"
              @click="projectFilter = 'en_cours'"
            >
              En cours ({{ projects.filter(p => p.status === 'en_cours').length }})
            </button>
            <button 
              class="filter-btn" 
              :class="{ 'active': projectFilter === 'termine' }"
              @click="projectFilter = 'termine'"
            >
              Terminés ({{ projects.filter(p => p.status === 'termine').length }})
            </button>
            <button 
              class="filter-btn" 
              :class="{ 'active': projectFilter === 'en_attente' }"
              @click="projectFilter = 'en_attente'"
            >
              En attente ({{ projects.filter(p => p.status === 'en_attente').length }})
            </button>
          </div>

          <div class="projects-grid">
            <div 
              v-for="project in filteredProjects" 
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
              
              <div class="project-freelancer-info" v-if="project.freelancer">
                <div class="freelancer-avatar small">
                  {{ project.freelancer.name?.charAt(0) || 'F' }}
                </div>
                <div class="freelancer-details">
                  <p class="freelancer-name">{{ project.freelancer.name || 'Freelance' }}</p>
                  <p class="project-deadline" v-if="project.deadline">
                    <i class="far fa-calendar-alt"></i>
                    {{ project.deadline }}
                  </p>
                </div>
              </div>
              
              <div class="project-meta">
                <div class="meta-item" v-if="project.budget">
                  <i class="fas fa-money-bill-wave"></i>
                  <span>{{ project.budget.toLocaleString() }} FCFA</span>
                </div>
                <div class="meta-item" v-if="project.created_at">
                  <i class="fas fa-clock"></i>
                  <span>{{ project.created_at }}</span>
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
      </div>

      <!-- SECTION FREELANCES -->
      <div v-else-if="activeTab === 'freelancers'" class="freelancers-section">
        <div class="section-header">
          <div>
            <h2 class="section-title">
              <i class="fas fa-users"></i>
              Tous les Freelances
            </h2>
            <p class="section-subtitle">
              {{ freelancers.length }} freelance{{ freelancers.length !== 1 ? 's' : '' }} disponible{{ freelancers.length !== 1 ? 's' : '' }}
            </p>
          </div>
          <button class="add-project-btn" @click="navigateTo('/freelances')">
            <i class="fas fa-search"></i>
            Voir tous
          </button>
        </div>

        <div v-if="freelancers.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-users"></i>
          </div>
          <h3>Aucun freelance disponible</h3>
          <p>Les freelances s'afficheront ici une fois inscrits sur la plateforme</p>
        </div>

        <div v-else class="freelancers-grid">
          <div 
            v-for="freelancer in filteredFreelancers" 
            :key="freelancer.id" 
            class="freelancer-card"
          >
            <div class="freelancer-header">
              <div class="freelancer-avatar large">
                {{ freelancer.name?.charAt(0)?.toUpperCase() || 'F' }}
              </div>
              <div class="freelancer-rating-badge" v-if="freelancer.rating">
                <i class="fas fa-star"></i>
                {{ freelancer.rating }}
              </div>
            </div>
            
            <h3 class="freelancer-name">{{ freelancer.name || 'Freelance' }}</h3>
            
            <div class="freelancer-skills-list" v-if="freelancer.skills && freelancer.skills.length > 0">
              <span v-for="skill in freelancer.skills.slice(0, 3)" :key="skill" class="skill-tag">
                {{ skill }}
              </span>
              <span v-if="freelancer.skills.length > 3" class="skill-tag more">
                +{{ freelancer.skills.length - 3 }}
              </span>
            </div>
            
            <div class="freelancer-stats">
              <div class="stat" v-if="freelancer.projects_count">
                <span class="stat-number">{{ freelancer.projects_count }}</span>
                <span class="stat-label">projets</span>
              </div>
              <div class="stat" v-if="freelancer.success_rate">
                <span class="stat-number">{{ freelancer.success_rate }}%</span>
                <span class="stat-label">réussite</span>
              </div>
              <div class="stat" v-if="freelancer.experience">
                <span class="stat-number">{{ freelancer.experience }}</span>
                <span class="stat-label">ans</span>
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
  padding: 40px;
  margin-top: 70px;
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

/* ==================== EMPTY STATE ==================== */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  border: 2px solid #f1f5f9;
}

.empty-icon {
  font-size: 4rem;
  color: #FF6B35;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.empty-state h3 {
  font-size: 1.8rem;
  color: #2D3047;
  margin: 0 0 10px 0;
}

.empty-state p {
  color: #6c757d;
  font-size: 1.1rem;
  margin-bottom: 30px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
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
  .modal {
    background: #2d2d2d;
    border-color: #404040;
    color: #e4e4e4;
  }
  
  .stat-card,
  .info-item,
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
  .stat-value {
    color: #e4e4e4;
  }
  
  .profile-title,
  .section-subtitle,
  .info-label,
  .project-deadline,
  .stat-label {
    color: #a0a0a0;
  }
}
</style>