<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useProfileStore } from '@/stores/profile';
import { usePortfolioStore } from '@/stores/portfolio';

const authStore = useAuthStore();
const profileStore = useProfileStore();
const portfolioStore = usePortfolioStore();
const router = useRouter();

// ✅ States réactifs
const loading = ref(true);
const profile = ref({
  full_name: '',
  email: '',
  title: '',
  description: '',
  skills: [],
  hourly_rate: '',
  experience_years: '',
  availability: '',
  languages: [],
  url_photo: ''
});
const portfolio = ref([]);
const activeTab = ref('profile');

// ✅ Modals
const showEditProfileModal = ref(false);
const showPortfolioModal = ref(false);
const editingPortfolio = ref(null);

// ✅ Formulaires
const editForm = ref({});
const portfolioForm = ref({
  title: '',
  description: '',
  url: '',
  image_url: ''
});

// ✅ Computed
const isAuthenticated = computed(() => authStore.isAuthenticated);
const formattedSkills = computed(() => profile.value.skills?.join(', ') || '');
const formattedLanguages = computed(() => profile.value.languages?.join(', ') || '');

// ✅ Chargement des données
onMounted(async () => {
  if (!isAuthenticated.value) {
    authStore.logout();
    router.push('/login');
    return;
  }

  try {
    const profileData = await profileStore.getMyProfile();
    
    if (!profileData) {
      router.push('/dashboard');
      return;
    }

    profile.value = {
      ...profile.value,
      ...profileData
    };

    editForm.value = { ...profile.value };

    portfolio.value = await portfolioStore.fetchPortfolio() || [];

  } catch (error) {
    console.error('Erreur lors du chargement:', error);
  } finally {
    loading.value = false;
  }
});

// ✅ ACTIONS PROFILE
function openEditProfile() {
  editForm.value = { ...profile.value };
  showEditProfileModal.value = true;
}

function closeEditProfile() {
  showEditProfileModal.value = false;
}

async function saveProfile() {
  try {
    const updatedProfile = {
      ...editForm.value,
      skills: editForm.value.skills ? 
        (Array.isArray(editForm.value.skills) ? editForm.value.skills : editForm.value.skills.split(',').map(s => s.trim())) 
        : [],
      languages: editForm.value.languages ? 
        (Array.isArray(editForm.value.languages) ? editForm.value.languages : editForm.value.languages.split(',').map(s => s.trim())) 
        : []
    };

    await profileStore.updateProfile(updatedProfile);
    
    profile.value = { ...profile.value, ...updatedProfile };
    
    showNotification('Profil mis à jour avec succès !', 'success');
    closeEditProfile();
  } catch (error) {
    console.error('Erreur mise à jour profil:', error);
    showNotification('Erreur lors de la mise à jour du profil', 'error');
  }
}

// ✅ ACTIONS PORTFOLIO
function openAddPortfolio() {
  editingPortfolio.value = null;
  portfolioForm.value = { title: '', description: '', url: '', image_url: '' };
  showPortfolioModal.value = true;
}

function openEditPortfolio(item) {
  editingPortfolio.value = item;
  portfolioForm.value = { ...item };
  showPortfolioModal.value = true;
}

function closePortfolioModal() {
  showPortfolioModal.value = false;
  editingPortfolio.value = null;
}

async function savePortfolio() {
  try {
    if (editingPortfolio.value) {
      await portfolioStore.updatePortfolio(editingPortfolio.value.id, portfolioForm.value);
      showNotification('Portfolio mis à jour !', 'success');
    } else {
      await portfolioStore.addPortfolio(portfolioForm.value);
      showNotification('Portfolio ajouté !', 'success');
    }
    
    portfolio.value = await portfolioStore.fetchPortfolio() || [];
    closePortfolioModal();
    
  } catch (error) {
    console.error('Erreur portfolio:', error);
    showNotification('Erreur lors de l\'enregistrement', 'error');
  }
}

async function deletePortfolio(id) {
  if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) return;
  
  try {
    await portfolioStore.deletePortfolio(id);
    portfolio.value = await portfolioStore.fetchPortfolio() || [];
    showNotification('Portfolio supprimé !', 'success');
  } catch (error) {
    console.error('Erreur suppression:', error);
    showNotification('Erreur lors de la suppression', 'error');
  }
}

// ✅ QR Code Actions
function handleQrError(event) {
  event.target.src = '/icone/qr-placeholder.png';
}

function downloadQrCode() {
  const link = document.createElement('a');
  link.href = '/icone/Qr-code.png';
  link.download = `QR-${profile.value.full_name || 'profil'}.png`;
  link.click();
  showNotification('QR code téléchargé !', 'success');
}

function shareProfile() {
  if (navigator.share) {
    navigator.share({
      title: `Profil de ${profile.value.full_name}`,
      text: `Découvrez le profil de ${profile.value.full_name} sur FreelanceCMR`,
      url: window.location.href
    });
  } else {
    navigator.clipboard.writeText(window.location.href);
    showNotification('Lien copié dans le presse-papier !', 'success');
  }
}

// ✅ Notification
const notification = ref({ show: false, message: '', type: '' });

function showNotification(message, type = 'success') {
  notification.value = { show: true, message, type };
  setTimeout(() => {
    notification.value.show = false;
  }, 3000);
}
</script>

<template>
  <div class="freelance-profile-page">
    <!-- ✅ Notification -->
    <div v-if="notification.show" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>

    <!-- ✅ Loading -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
      </div>
      <p>Chargement de votre profil...</p>
    </div>

    <!-- ✅ Contenu principal -->
    <div v-else class="profile-container">
      <!-- ✅ Navigation Tabs -->
      <div class="profile-tabs">
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
          :class="{ 'active': activeTab === 'portfolio' }"
          @click="activeTab = 'portfolio'"
        >
          <i class="fas fa-briefcase"></i>
          <span>Portfolio</span>
          <span class="tab-badge">{{ portfolio.length }}</span>
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

      <!-- ✅ SECTION PROFIL -->
      <div v-if="activeTab === 'profile'" class="profile-section">
        <!-- En-tête du profil -->
        <div class="profile-header-card">
          <div class="profile-cover">
            <div class="profile-avatar-section">
              <div class="avatar-container">
                <img 
                  :src="profile.url_photo || '/icone/account.png'" 
                  alt="Photo de profil" 
                  class="profile-avatar"
                  @error="profile.url_photo = '/icone/account.png'"
                />
                <div class="avatar-status"></div>
              </div>
              <div class="profile-main-info">
                <h1 class="profile-name">{{ profile.full_name || 'Nom non défini' }}</h1>
                <p class="profile-title">
                  <i class="fas fa-briefcase"></i>
                  {{ profile.title || 'Titre non défini' }}
                </p>
                <div class="profile-meta">
                  <span class="meta-item">
                    <i class="fas fa-envelope"></i>
                    {{ profile.email || 'Email non défini' }}
                  </span>
                  <span class="meta-item" v-if="profile.experience_years">
                    <i class="fas fa-calendar-alt"></i>
                    {{ profile.experience_years }} ans d'expérience
                  </span>
                </div>
              </div>
            </div>
            
            <div class="profile-actions">
              <button class="action-btn primary-btn" @click="openEditProfile">
                <i class="fas fa-edit"></i>
                Modifier le profil
              </button>
              <button class="action-btn outline-btn" @click="shareProfile">
                <i class="fas fa-share-alt"></i>
                Partager
              </button>
            </div>
          </div>

          <!-- Stats rapides -->
          <div class="profile-stats">
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-money-bill-wave"></i>
              </div>
              <div class="stat-content">
                <h3 class="stat-value">{{ profile.hourly_rate || '0' }} FCFA</h3>
                <p class="stat-label">Taux horaire</p>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-star"></i>
              </div>
              <div class="stat-content">
                <h3 class="stat-value">4.8</h3>
                <p class="stat-label">Note moyenne</p>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-check-circle"></i>
              </div>
              <div class="stat-content">
                <h3 class="stat-value">24</h3>
                <p class="stat-label">Projets terminés</p>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-clock"></i>
              </div>
              <div class="stat-content">
                <h3 class="stat-value">{{ profile.availability || 'Disponible' }}</h3>
                <p class="stat-label">Disponibilité</p>
              </div>
            </div>
          </div>

          <!-- QR Code Section -->
          <div class="profile-qr-section">
            <div class="qr-card">
              <h3>
                <i class="fas fa-qrcode"></i>
                Mon QR Code
              </h3>
              <div class="qr-container">
                <img 
                  src="/icone/Qr-code.png" 
                  alt="QR Code Profil" 
                  class="qr-code"
                  @error="handleQrError"
                />
              </div>
              <p class="qr-hint">Scannez pour voir mon profil public</p>
              <div class="qr-actions">
                <button class="qr-action-btn" @click="downloadQrCode">
                  <i class="fas fa-download"></i>
                  Télécharger
                </button>
                <button class="qr-action-btn" @click="shareProfile">
                  <i class="fas fa-share-alt"></i>
                  Partager
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Détails du profil -->
        <div class="profile-details-grid">
          <!-- À propos -->
          <div class="detail-card about-card">
            <div class="card-header">
              <h3>
                <i class="fas fa-info-circle"></i>
                À propos
              </h3>
              <button class="card-action-btn" @click="openEditProfile">
                <i class="fas fa-edit"></i>
              </button>
            </div>
            <div class="card-content">
              <p class="description">{{ profile.description || 'Aucune description fournie' }}</p>
            </div>
          </div>

          <!-- Compétences -->
          <div class="detail-card skills-card">
            <div class="card-header">
              <h3>
                <i class="fas fa-tools"></i>
                Compétences
              </h3>
            </div>
            <div class="card-content">
              <div v-if="formattedSkills" class="skills-list">
                <span v-for="skill in profile.skills" :key="skill" class="skill-tag">
                  {{ skill.trim() }}
                </span>
              </div>
              <p v-else class="empty-text">Aucune compétence définie</p>
            </div>
          </div>

          <!-- Langues -->
          <div class="detail-card languages-card">
            <div class="card-header">
              <h3>
                <i class="fas fa-language"></i>
                Langues
              </h3>
            </div>
            <div class="card-content">
              <div v-if="formattedLanguages" class="languages-list">
                <div v-for="lang in profile.languages" :key="lang" class="language-item">
                  <span class="language-name">{{ lang.trim() }}</span>
                  <div class="language-level">
                    <span class="level-dot active"></span>
                    <span class="level-dot active"></span>
                    <span class="level-dot active"></span>
                    <span class="level-dot"></span>
                    <span class="level-dot"></span>
                  </div>
                </div>
              </div>
              <p v-else class="empty-text">Aucune langue définie</p>
            </div>
          </div>

          <!-- Informations supplémentaires -->
          <div class="detail-card info-card">
            <div class="card-header">
              <h3>
                <i class="fas fa-id-card"></i>
                Informations
              </h3>
            </div>
            <div class="card-content">
              <div class="info-list">
                <div class="info-item">
                  <i class="fas fa-map-marker-alt"></i>
                  <div>
                    <p class="info-label">Localisation</p>
                    <p class="info-value">Cameroun</p>
                  </div>
                </div>
                <div class="info-item" v-if="profile.experience_years">
                  <i class="fas fa-briefcase"></i>
                  <div>
                    <p class="info-label">Expérience</p>
                    <p class="info-value">{{ profile.experience_years }} ans</p>
                  </div>
                </div>
                <div class="info-item" v-if="profile.hourly_rate">
                  <i class="fas fa-money-bill-wave"></i>
                  <div>
                    <p class="info-label">Taux horaire</p>
                    <p class="info-value">{{ profile.hourly_rate }} FCFA</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ✅ SECTION PORTFOLIO -->
      <div v-else-if="activeTab === 'portfolio'" class="portfolio-section">
        <div class="section-header">
          <div>
            <h2 class="section-title">
              <i class="fas fa-briefcase"></i>
              Mon Portfolio
            </h2>
            <p class="section-subtitle">
              Présentez vos meilleurs projets et réalisations
            </p>
          </div>
          <button class="add-project-btn" @click="openAddPortfolio">
            <i class="fas fa-plus"></i>
            Nouveau projet
          </button>
        </div>

        <div v-if="portfolio.length > 0" class="portfolio-grid">
          <div 
            v-for="item in portfolio" 
            :key="item.id" 
            class="portfolio-item"
            @click="openEditPortfolio(item)"
          >
            <div class="portfolio-image-container">
              <img 
                :src="item.image_url || '/icone/project-placeholder.jpg'" 
                :alt="item.title" 
                class="portfolio-image"
                @error="item.image_url = '/icone/project-placeholder.jpg'"
              />
              <div class="portfolio-overlay">
                <button class="view-project-btn">
                  <i class="fas fa-eye"></i>
                  Voir
                </button>
              </div>
            </div>
            
            <div class="portfolio-content">
              <h3 class="portfolio-title">{{ item.title }}</h3>
              <p class="portfolio-description">{{ item.description }}</p>
              
              <div class="portfolio-actions">
                <a 
                  v-if="item.url" 
                  :href="item.url" 
                  target="_blank" 
                  class="project-link"
                  @click.stop
                >
                  <i class="fas fa-external-link-alt"></i>
                  Visiter le site
                </a>
                <div class="action-buttons">
                  <button class="icon-btn edit-btn" @click.stop="openEditPortfolio(item)">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="icon-btn delete-btn" @click.stop="deletePortfolio(item.id)">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-portfolio">
          <div class="empty-icon">
            <i class="fas fa-folder-open"></i>
          </div>
          <h3>Aucun projet dans votre portfolio</h3>
          <p>Commencez par ajouter vos réalisations pour impressionner les clients</p>
          <button class="empty-action-btn" @click="openAddPortfolio">
            <i class="fas fa-plus"></i>
            Ajouter mon premier projet
          </button>
        </div>
      </div>

      <!-- ✅ SECTION STATISTIQUES -->
      <div v-else class="stats-section">
        <div class="section-header">
          <h2 class="section-title">
            <i class="fas fa-chart-line"></i>
            Mes Statistiques
          </h2>
        </div>
        
        <div class="stats-cards">
          <div class="stats-card main">
            <h3>Performance générale</h3>
            <div class="stats-metrics">
              <div class="metric">
                <span class="metric-value">95%</span>
                <span class="metric-label">Taux de satisfaction</span>
              </div>
              <div class="metric">
                <span class="metric-value">4.8</span>
                <span class="metric-label">Note moyenne</span>
              </div>
              <div class="metric">
                <span class="metric-value">24</span>
                <span class="metric-label">Projets livrés</span>
              </div>
            </div>
          </div>
          
          <div class="stats-card">
            <h3>Activité récente</h3>
            <div class="activity-list">
              <div class="activity-item">
                <i class="fas fa-check-circle success"></i>
                <div>
                  <p>Projet "Site e-commerce" terminé</p>
                  <span class="activity-time">Il y a 2 jours</span>
                </div>
              </div>
              <div class="activity-item">
                <i class="fas fa-comment info"></i>
                <div>
                  <p>Nouveau message de Sarah M.</p>
                  <span class="activity-time">Il y a 3 jours</span>
                </div>
              </div>
              <div class="activity-item">
                <i class="fas fa-money-bill-wave warning"></i>
                <div>
                  <p>Paiement reçu: 150.000 FCFA</p>
                  <span class="activity-time">Il y a 5 jours</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ✅ MODAL EDIT PROFILE -->
    <div v-if="showEditProfileModal" class="modal-overlay" @click.self="closeEditProfile">
      <div class="modal">
        <div class="modal-header">
          <h2>
            <i class="fas fa-user-edit"></i>
            Modifier le profil
          </h2>
          <button class="modal-close" @click="closeEditProfile">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group">
              <label for="full_name">
                <i class="fas fa-user"></i>
                Nom complet *
              </label>
              <input 
                id="full_name" 
                v-model="editForm.full_name" 
                type="text" 
                placeholder="Votre nom complet"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="title">
                <i class="fas fa-briefcase"></i>
                Titre professionnel *
              </label>
              <input 
                id="title" 
                v-model="editForm.title" 
                type="text" 
                placeholder="Ex: Développeur Fullstack"
                required
              />
            </div>
            
            <div class="form-group full-width">
              <label for="description">
                <i class="fas fa-file-alt"></i>
                Description *
              </label>
              <textarea 
                id="description" 
                v-model="editForm.description" 
                placeholder="Décrivez votre expertise et expérience..."
                rows="4"
                required
              ></textarea>
            </div>
            
            <div class="form-group">
              <label for="hourly_rate">
                <i class="fas fa-money-bill-wave"></i>
                Taux horaire (FCFA)
              </label>
              <input 
                id="hourly_rate" 
                v-model="editForm.hourly_rate" 
                type="number" 
                placeholder="Ex: 5000"
              />
            </div>
            
            <div class="form-group">
              <label for="experience_years">
                <i class="fas fa-calendar-alt"></i>
                Années d'expérience
              </label>
              <input 
                id="experience_years" 
                v-model="editForm.experience_years" 
                type="number" 
                placeholder="Ex: 3"
              />
            </div>
            
            <div class="form-group full-width">
              <label for="skills">
                <i class="fas fa-tools"></i>
                Compétences (séparées par des virgules)
              </label>
              <input 
                id="skills" 
                v-model="editForm.skills" 
                type="text" 
                placeholder="Ex: Vue.js, Node.js, MongoDB, API REST"
              />
            </div>
            
            <div class="form-group full-width">
              <label for="languages">
                <i class="fas fa-language"></i>
                Langues (séparées par des virgules)
              </label>
              <input 
                id="languages" 
                v-model="editForm.languages" 
                type="text" 
                placeholder="Ex: Français, Anglais, Espagnol"
              />
            </div>
            
            <div class="form-group">
              <label for="availability">
                <i class="fas fa-clock"></i>
                Disponibilité
              </label>
              <select id="availability" v-model="editForm.availability">
                <option value="">Sélectionner</option>
                <option value="Disponible immédiatement">Disponible immédiatement</option>
                <option value="À temps partiel">À temps partiel</option>
                <option value="À temps plein">À temps plein</option>
                <option value="Sur demande">Sur demande</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="url_photo">
                <i class="fas fa-camera"></i>
                URL Photo
              </label>
              <input 
                id="url_photo" 
                v-model="editForm.url_photo" 
                type="url" 
                placeholder="https://exemple.com/photo.jpg"
              />
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeEditProfile">
            Annuler
          </button>
          <button class="btn btn-primary" @click="saveProfile">
            <i class="fas fa-save"></i>
            Enregistrer les modifications
          </button>
        </div>
      </div>
    </div>

    <!-- ✅ MODAL PORTFOLIO -->
    <div v-if="showPortfolioModal" class="modal-overlay" @click.self="closePortfolioModal">
      <div class="modal">
        <div class="modal-header">
          <h2>
            <i class="fas fa-briefcase"></i>
            {{ editingPortfolio ? 'Modifier' : 'Ajouter' }} un projet
          </h2>
          <button class="modal-close" @click="closePortfolioModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label for="portfolio-title">
              <i class="fas fa-heading"></i>
              Titre du projet *
            </label>
            <input 
              id="portfolio-title" 
              v-model="portfolioForm.title" 
              type="text" 
              placeholder="Ex: Application E-commerce"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="portfolio-description">
              <i class="fas fa-file-alt"></i>
              Description *
            </label>
            <textarea 
              id="portfolio-description" 
              v-model="portfolioForm.description" 
              placeholder="Décrivez le projet, vos responsabilités, les technologies utilisées..."
              rows="4"
              required
            ></textarea>
          </div>
          
          <div class="form-group">
            <label for="portfolio-url">
              <i class="fas fa-link"></i>
              URL du projet
            </label>
            <input 
              id="portfolio-url" 
              v-model="portfolioForm.url" 
              type="url" 
              placeholder="https://exemple.com"
            />
          </div>
          
          <div class="form-group">
            <label for="portfolio-image">
              <i class="fas fa-image"></i>
              URL de l'image
            </label>
            <input 
              id="portfolio-image" 
              v-model="portfolioForm.image_url" 
              type="url" 
              placeholder="https://exemple.com/image.jpg"
            />
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closePortfolioModal">
            Annuler
          </button>
          <button class="btn btn-primary" @click="savePortfolio">
            <i class="fas fa-save"></i>
            {{ editingPortfolio ? 'Mettre à jour' : 'Ajouter' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==================== BASE STYLES ==================== */
.freelance-profile-page {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px;
}

/* ==================== NOTIFICATION ==================== */
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 25px;
  border-radius: 12px;
  color: white;
  font-weight: 500;
  z-index: 1000;
  animation: slideIn 0.3s ease;
  max-width: 400px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.notification.success {
  background: linear-gradient(135deg, #10B981, #34D399);
}

.notification.error {
  background: linear-gradient(135deg, #EF4444, #F87171);
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
}

.loading-spinner i {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ==================== CONTAINER ==================== */
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* ==================== TABS ==================== */
.profile-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  background: white;
  padding: 10px;
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 25px;
  border: none;
  background: transparent;
  color: #6c757d;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.3s ease;
  position: relative;
}

.tab-btn:hover {
  background: rgba(255, 107, 53, 0.1);
  color: #FF6B35;
}

.tab-btn.active {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
}

.tab-btn i {
  font-size: 1.1rem;
}

.tab-badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 0.8rem;
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
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
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

.avatar-container {
  position: relative;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid white;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
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
  gap: 8px;
  color: #6c757d;
  font-size: 0.95rem;
}

.meta-item i {
  color: #FF6B35;
  font-size: 1rem;
}

.profile-actions {
  display: flex;
  gap: 15px;
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
  transition: all 0.3s ease;
  border: none;
}

.primary-btn {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
}

.primary-btn:hover {
  transform: translateY(-2px);
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
  transform: translateY(-2px);
}

/* Profile Stats */
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
  transition: all 0.3s ease;
}

.stat-card:hover {
  border-color: #FF6B35;
  transform: translateY(-3px);
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
}

.stat-content {
  flex: 1;
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

/* QR Code Section */
.profile-qr-section {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 2px solid #f1f5f9;
}

.qr-card {
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  border-radius: 15px;
  padding: 25px;
  text-align: center;
  border: 2px solid #e5e7eb;
  transition: all 0.3s ease;
  max-width: 400px;
  margin: 0 auto;
}

.qr-card:hover {
  border-color: #FF6B35;
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.qr-card h3 {
  font-size: 1.2rem;
  color: #2D3047;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.qr-card i {
  color: #FF6B35;
}

.qr-container {
  background: white;
  padding: 20px;
  border-radius: 10px;
  display: inline-block;
  margin-bottom: 15px;
  border: 2px solid #e5e7eb;
}

.qr-code {
  width: 180px;
  height: 180px;
  object-fit: contain;
}

.qr-hint {
  color: #6c757d;
  font-size: 0.9rem;
  margin: 0 0 20px 0;
}

.qr-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.qr-action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 500;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid #e5e7eb;
  background: white;
  color: #2D3047;
}

.qr-action-btn:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: translateY(-2px);
}

.qr-action-btn i {
  font-size: 1rem;
}

/* Profile Details Grid */
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
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  border: 2px solid #f1f5f9;
  transition: all 0.3s ease;
}

.detail-card:hover {
  border-color: #FF6B35;
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
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
  transition: all 0.3s ease;
}

.card-action-btn:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: rotate(15deg);
}

/* About Card */
.description {
  color: #4b5563;
  line-height: 1.6;
  font-size: 1rem;
  margin: 0;
}

/* Skills Card */
.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.skill-tag {
  padding: 8px 16px;
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  color: #0369a1;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.skill-tag:hover {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  transform: translateY(-2px);
}

/* Languages Card */
.languages-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.language-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.language-name {
  font-weight: 500;
  color: #2D3047;
}

.language-level {
  display: flex;
  gap: 5px;
}

.level-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e5e7eb;
}

.level-dot.active {
  background: #FF6B35;
}

/* Info Card */
.info-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
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
}

.info-value {
  font-size: 1rem;
  font-weight: 500;
  color: #2D3047;
  margin: 0;
}

.empty-text {
  color: #9ca3af;
  font-style: italic;
  text-align: center;
  padding: 20px 0;
}

/* ==================== PORTFOLIO SECTION ==================== */
.portfolio-section {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
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
}

.section-subtitle {
  color: #6c757d;
  margin: 0;
  font-size: 1rem;
}

.add-project-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-project-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 107, 53, 0.3);
}

/* Portfolio Grid */
.portfolio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
}

.portfolio-item {
  background: white;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  border: 2px solid #f1f5f9;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.portfolio-item:hover {
  border-color: #FF6B35;
  transform: translateY(-8px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.1);
}

.portfolio-image-container {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.portfolio-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.portfolio-item:hover .portfolio-image {
  transform: scale(1.05);
}

.portfolio-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(45, 48, 71, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.portfolio-item:hover .portfolio-overlay {
  opacity: 1;
}

.view-project-btn {
  padding: 10px 20px;
  background: white;
  color: #2D3047;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.view-project-btn:hover {
  background: #FF6B35;
  color: white;
  transform: scale(1.1);
}

.portfolio-content {
  padding: 20px;
}

.portfolio-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2D3047;
  margin: 0 0 10px 0;
}

.portfolio-description {
  color: #6c757d;
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0 0 15px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.portfolio-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-link {
  color: #3B82F6;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: color 0.3s ease;
}

.project-link:hover {
  color: #FF6B35;
}

.action-buttons {
  display: flex;
  gap: 10px;
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
  transition: all 0.3s ease;
}

.icon-btn:hover {
  transform: scale(1.1);
}

.edit-btn:hover {
  border-color: #3B82F6;
  color: #3B82F6;
}

.delete-btn:hover {
  border-color: #EF4444;
  color: #EF4444;
}

/* Empty Portfolio */
.empty-portfolio {
  text-align: center;
  padding: 60px 40px;
  border: 2px dashed #e5e7eb;
  border-radius: 15px;
}

.empty-icon {
  font-size: 4rem;
  color: #9ca3af;
  margin-bottom: 20px;
}

.empty-portfolio h3 {
  font-size: 1.5rem;
  color: #2D3047;
  margin: 0 0 10px 0;
}

.empty-portfolio p {
  color: #6c757d;
  max-width: 400px;
  margin: 0 auto 30px;
  line-height: 1.5;
}

.empty-action-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 30px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 0 auto;
}

.empty-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 107, 53, 0.3);
}

/* ==================== STATS SECTION ==================== */
.stats-section {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
}

.stats-card {
  background: #f8fafc;
  border-radius: 15px;
  padding: 25px;
  border: 2px solid #f1f5f9;
}

.stats-card.main {
  background: linear-gradient(135deg, #2D3047, #1A1C2E);
  color: white;
  border: none;
}

.stats-card h3 {
  font-size: 1.3rem;
  margin: 0 0 25px 0;
  color: inherit;
}

.stats-card.main h3 {
  color: white;
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
}

.metric-value {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 5px;
}

.stats-card.main .metric-value {
  color: #FFD166;
}

.metric-label {
  font-size: 0.9rem;
  color: #6c757d;
}

.stats-card.main .metric-label {
  color: rgba(255, 255, 255, 0.8);
}

/* Activity List */
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
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  animation: modalSlideIn 0.3s ease;
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
  transition: all 0.3s ease;
}

.modal-close:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: rotate(90deg);
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

/* Form Styles */
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
  font-weight: 500;
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
  padding: 12px 15px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.95rem;
  font-family: inherit;
  transition: all 0.3s ease;
  background: white;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #FF6B35;
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

/* Buttons */
.btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  font-family: inherit;
}

.btn-primary {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 107, 53, 0.3);
}

.btn-secondary {
  background: white;
  color: #2D3047;
  border: 2px solid #e5e7eb;
}

.btn-secondary:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: translateY(-2px);
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 1024px) {
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

@media (max-width: 768px) {
  .freelance-profile-page {
    padding: 15px;
  }
  
  .profile-tabs {
    flex-direction: column;
  }
  
  .tab-btn {
    width: 100%;
    justify-content: center;
  }
  
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
  
  .profile-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .section-header {
    flex-direction: column;
    gap: 20px;
    align-items: stretch;
  }
  
  .add-project-btn {
    width: 100%;
    justify-content: center;
  }
  
  .qr-code {
    width: 150px;
    height: 150px;
  }
  
  .qr-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .qr-action-btn {
    width: 100%;
    justify-content: center;
  }
  
  .modal {
    max-width: 95%;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .profile-stats {
    grid-template-columns: 1fr;
  }
  
  .profile-details-grid {
    grid-template-columns: 1fr;
  }
  
  .portfolio-grid {
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
}

/* Support tactile */
@media (hover: none) and (pointer: coarse) {
  .portfolio-item:hover {
    transform: none;
  }
  
  .action-btn:hover,
  .icon-btn:hover,
  .card-action-btn:hover,
  .modal-close:hover,
  .qr-action-btn:hover {
    transform: none;
  }
  
  .portfolio-item:active {
    transform: scale(0.98);
  }
}
</style>