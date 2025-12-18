<template>
  <div class="client-profile-page">
    <!-- Header identique à la page d'accueil -->
    <header class="header">
      <div class="header-container">
        <div class="logo" @click="$router.push('/')">
          <i class="fas fa-hands-helping logo-icon"></i>
          <span class="logo-text">Freelance<span class="logo-highlight">CMR</span></span>
        </div>
        
        <nav class="nav-desktop">
          <router-link to="/dashboard" class="nav-link">
            <i class="fas fa-tachometer-alt"></i>
            Dashboard
          </router-link>
          <router-link to="/client-profile" class="nav-link active">
            <i class="fas fa-user"></i>
            Mon Profil
          </router-link>
          <router-link to="/missions/create" class="nav-link">
            <i class="fas fa-plus-circle"></i>
            Créer Mission
          </router-link>
          <button class="logout-btn" @click="authStore.logout(); $router.push('/')">
            <i class="fas fa-sign-out-alt"></i>
            Déconnexion
          </button>
        </nav>
      </div>
    </header>

    <!-- Modal d'édition -->
    <div v-if="showEditProfileModal" class="modal-overlay" @click.self="closeEditProfile">
      <div class="modal-content">
        <div class="modal-header">
          <h2><i class="fas fa-user-edit"></i> Modifier mon profil</h2>
          <button class="close-btn" @click="closeEditProfile">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label><i class="fas fa-user"></i> Nom complet</label>
            <input v-model="editForm.full_name" type="text" class="form-input" />
          </div>
          
          <div class="form-group">
            <label><i class="fas fa-building"></i> Nom entreprise</label>
            <input v-model="editForm.company_name" type="text" class="form-input" />
          </div>
          
          <div class="form-group">
            <label><i class="fas fa-globe"></i> Site web</label>
            <input v-model="editForm.company_website" type="url" class="form-input" placeholder="https://..." />
          </div>
          
          <div class="form-group">
            <label><i class="fas fa-industry"></i> Secteur d'activité</label>
            <select v-model="editForm.industry" class="form-input">
              <option value="">Sélectionnez...</option>
              <option v-for="industry in industries" :key="industry">{{ industry }}</option>
            </select>
          </div>
          
          <div class="form-group">
            <label><i class="fas fa-phone"></i> Téléphone</label>
            <input v-model="editForm.phone" type="tel" class="form-input" placeholder="+237 XXX XX XX XX" />
          </div>
          
          <div class="form-group">
            <label><i class="fas fa-map-marker-alt"></i> Ville</label>
            <input v-model="editForm.city" type="text" class="form-input" placeholder="Yaoundé, Douala..." />
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeEditProfile">Annuler</button>
          <button class="btn-primary" @click="saveProfile">
            <i class="fas fa-save"></i> Enregistrer
          </button>
        </div>
      </div>
    </div>

    <!-- Contenu principal -->
    <main class="profile-main">
      <div class="profile-container">
        <!-- En-tête Hero Style (comme home page) -->
        <section class="profile-hero">
          <div class="hero-content">
            <div class="profile-avatar-section">
              <div class="avatar-wrapper">
                <img 
                  :src="profile?.url_photo || '/icone/account.png'" 
                  alt="Profile" 
                  class="profile-avatar"
                  @error="profile.url_photo = '/icone/account.png'"
                />
                <div class="avatar-badge">
                  <i class="fas fa-user-tie"></i>
                </div>
              </div>
              <div class="profile-intro">
                <h1 class="profile-name">{{ profile?.full_name || userName }}</h1>
                <p class="profile-email">
                  <i class="fas fa-envelope"></i> {{ profile?.email || user?.email }}
                </p>
                <div class="profile-tags">
                  <span class="tag" v-if="profile?.client_type">
                    <i class="fas fa-tag"></i> {{ profile.client_type }}
                  </span>
                  <span class="tag" v-if="profile?.industry">
                    <i class="fas fa-industry"></i> {{ profile.industry }}
                  </span>
                  <span class="tag" v-if="profile?.city">
                    <i class="fas fa-map-marker-alt"></i> {{ profile.city }}, Cameroun
                  </span>
                </div>
              </div>
            </div>
            
            <div class="hero-actions">
              <button class="cta-button" @click="openEditProfile">
                <i class="fas fa-user-edit"></i> Modifier le profil
              </button>
              <div class="qr-section">
                <img src="/icone/Qr-code.png" alt="QR Code" class="qr-code" />
                <span class="qr-label">Mon QR Code</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Section statistiques (style comme home page) -->
        <section class="stats-section">
          <div class="section-container">
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-icon">
                  <i class="fas fa-briefcase"></i>
                </div>
                <div class="stat-content">
                  <h3>12</h3>
                  <p>Missions publiées</p>
                </div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon">
                  <i class="fas fa-users"></i>
                </div>
                <div class="stat-content">
                  <h3>45</h3>
                  <p>Freelances engagés</p>
                </div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon">
                  <i class="fas fa-check-circle"></i>
                </div>
                <div class="stat-content">
                  <h3>98%</h3>
                  <p>Taux de satisfaction</p>
                </div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon">
                  <i class="fas fa-money-bill-wave"></i>
                </div>
                <div class="stat-content">
                  <h3>2.5M FCFA</h3>
                  <p>Budget total</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Section détails profil -->
        <section class="details-section">
          <div class="section-container">
            <div class="section-header">
              <h2 class="section-title">
                <i class="fas fa-id-card"></i> Informations du profil
              </h2>
            </div>
            
            <div v-if="loading" class="loading-state">
              <i class="fas fa-spinner fa-spin"></i> Chargement...
            </div>
            
            <div v-else class="details-grid">
              <!-- Entreprise -->
              <div class="detail-card" v-if="profile?.company_name">
                <div class="detail-icon">
                  <i class="fas fa-building"></i>
                </div>
                <div class="detail-content">
                  <h3>Entreprise</h3>
                  <p>{{ profile.company_name }}</p>
                </div>
              </div>
              
              <!-- Site web -->
              <div class="detail-card" v-if="profile?.company_website">
                <div class="detail-icon">
                  <i class="fas fa-globe"></i>
                </div>
                <div class="detail-content">
                  <h3>Site web</h3>
                  <a :href="profile.company_website" target="_blank" class="website-link">
                    {{ profile.company_website.replace(/^https?:\/\//, '') }}
                    <i class="fas fa-external-link-alt"></i>
                  </a>
                </div>
              </div>
              
              <!-- Téléphone -->
              <div class="detail-card" v-if="profile?.phone">
                <div class="detail-icon">
                  <i class="fas fa-phone"></i>
                </div>
                <div class="detail-content">
                  <h3>Téléphone</h3>
                  <p>{{ profile.phone }}</p>
                </div>
              </div>
              
              <!-- Localisation -->
              <div class="detail-card" v-if="profile?.city || profile?.country">
                <div class="detail-icon">
                  <i class="fas fa-map-marker-alt"></i>
                </div>
                <div class="detail-content">
                  <h3>Localisation</h3>
                  <p>{{ profile.city }} {{ profile.country ? ', ' + profile.country : '' }}</p>
                </div>
              </div>
              
              <!-- Type client -->
              <div class="detail-card" v-if="profile?.client_type">
                <div class="detail-icon">
                  <i class="fas fa-user-tag"></i>
                </div>
                <div class="detail-content">
                  <h3>Type de client</h3>
                  <p>{{ profile.client_type }}</p>
                </div>
              </div>
              
              <!-- Secteur -->
              <div class="detail-card" v-if="profile?.industry">
                <div class="detail-icon">
                  <i class="fas fa-industry"></i>
                </div>
                <div class="detail-content">
                  <h3>Secteur d'activité</h3>
                  <p>{{ profile.industry }}</p>
                </div>
              </div>
            </div>
            
            <!-- Bio -->
            <div v-if="profile?.bio" class="bio-section">
              <h3 class="bio-title">
                <i class="fas fa-align-left"></i> À propos
              </h3>
              <p class="bio-content">{{ profile.bio }}</p>
            </div>
          </div>
        </section>

        <!-- Section actions rapides -->
        <section class="quick-actions-section">
          <div class="section-container">
            <div class="section-header">
              <h2 class="section-title">
                <i class="fas fa-bolt"></i> Actions rapides
              </h2>
            </div>
            
            <div class="actions-grid">
              <router-link to="/missions/create" class="action-card">
                <div class="action-icon">
                  <i class="fas fa-plus-circle"></i>
                </div>
                <h3>Créer une mission</h3>
                <p>Publiez votre projet pour trouver le freelance idéal</p>
              </router-link>
              
              <router-link to="/client/missions" class="action-card">
                <div class="action-icon">
                  <i class="fas fa-tasks"></i>
                </div>
                <h3>Mes missions</h3>
                <p>Gérez et suivez toutes vos missions en cours</p>
              </router-link>
              
              <router-link to="/freelancers" class="action-card">
                <div class="action-icon">
                  <i class="fas fa-users"></i>
                </div>
                <h3>Rechercher freelances</h3>
                <p>Trouvez des talents pour vos futurs projets</p>
              </router-link>
              
              <router-link to="/messages" class="action-card">
                <div class="action-icon">
                  <i class="fas fa-comments"></i>
                </div>
                <h3>Messages</h3>
                <p>Communiquez avec vos freelances</p>
              </router-link>
            </div>
          </div>
        </section>
      </div>
    </main>

    <!-- Footer identique à la page d'accueil -->
    <footer class="footer">
      <div class="footer-container">
        <div class="footer-column">
          <div class="footer-logo">
            <i class="fas fa-hands-helping"></i>
            <span>Freelance<span class="logo-highlight">CMR</span></span>
          </div>
          <p class="footer-description">
            La première plateforme de freelancing 100% camerounaise.
          </p>
          <div class="social-links">
            <a href="#" class="social-link"><i class="fab fa-facebook-f"></i></a>
            <a href="#" class="social-link"><i class="fab fa-twitter"></i></a>
            <a href="#" class="social-link"><i class="fab fa-linkedin-in"></i></a>
            <a href="#" class="social-link"><i class="fab fa-instagram"></i></a>
          </div>
        </div>

        <div class="footer-column">
          <h3 class="footer-title">Liens rapides</h3>
          <ul class="footer-links">
            <li><router-link to="/dashboard">Dashboard</router-link></li>
            <li><router-link to="/client-profile">Mon profil</router-link></li>
            <li><router-link to="/missions">Missions</router-link></li>
            <li><router-link to="/freelancers">Freelances</router-link></li>
          </ul>
        </div>

        <div class="footer-column">
          <h3 class="footer-title">Contact</h3>
          <div class="contact-info">
            <div class="contact-item">
              <i class="fas fa-map-marker-alt"></i>
              <span>Yaoundé, Cameroun</span>
            </div>
            <div class="contact-item">
              <i class="fas fa-phone"></i>
              <span>+237 650536195</span>
            </div>
            <div class="contact-item">
              <i class="fas fa-envelope"></i>
              <span>support@freelancecmr.cm</span>
            </div>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <p>&copy; 2024 FreelanceCMR. Tous droits réservés. | Conçu avec ❤️ au Cameroun</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useProfileStore } from '@/stores/profile';

const authStore = useAuthStore();
const profileStore = useProfileStore();
const router = useRouter();

// États
const loading = ref(true);
const profile = ref(null);
const showEditProfileModal = ref(false);

// Formulaires
const editForm = ref({
  full_name: '',
  company_name: '',
  company_website: '',
  industry: '',
  phone: '',
  city: '',
  bio: ''
});

// Données
const industries = [
  'Technologie & Digital', 'Finance & Banque', 'Santé & Médical',
  'Éducation & Formation', 'Commerce & Retail', 'Immobilier',
  'Tourisme & Hôtellerie', 'Agriculture & Agroalimentaire'
];

const user = computed(() => authStore.user);
const userName = computed(() => profile.value?.full_name || user.value?.email?.split('@')[0] || 'Client');

// Chargement
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }

  try {
    const profileData = await profileStore.getMyProfile();
    if (!profileData) {
      router.push('/dashboard');
      return;
    }
    profile.value = profileData;
    
    // Pré-remplir formulaire
    Object.assign(editForm.value, {
      full_name: profileData.full_name || '',
      company_name: profileData.company_name || '',
      company_website: profileData.company_website || '',
      industry: profileData.industry || '',
      phone: profileData.phone || '',
      city: profileData.city || '',
      bio: profileData.bio || ''
    });
  } catch (error) {
    console.error('Erreur:', error);
  } finally {
    loading.value = false;
  }
});

// Actions
const openEditProfile = () => {
  showEditProfileModal.value = true;
};

const closeEditProfile = () => {
  showEditProfileModal.value = false;
};

const saveProfile = async () => {
  try {
    await profileStore.updateProfile(editForm.value);
    alert('Profil mis à jour !');
    closeEditProfile();
    // Recharger
    const profileData = await profileStore.getMyProfile();
    profile.value = profileData;
  } catch (error) {
    console.error('Erreur:', error);
    alert('Erreur lors de la mise à jour');
  }
};
</script>

<style scoped>
/* ==================== STYLES IDENTIQUES À LA HOME PAGE ==================== */

/* Header */
.header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
  padding: 15px 0;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 2.2rem;
  color: #FF6B35;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-text {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2D3047;
}

.logo-highlight {
  color: #FF6B35;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-desktop {
  display: flex;
  gap: 20px;
  align-items: center;
}

.nav-link {
  padding: 10px 25px;
  border-radius: 30px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  color: #2D3047;
  border: 2px solid transparent;
}

.nav-link:hover {
  color: #FF6B35;
  border-color: #FF6B35;
}

.nav-link.active {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border-color: #FF6B35;
}

.logout-btn {
  padding: 10px 25px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 30px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.logout-btn:hover {
  background: #dc2626;
  transform: translateY(-2px);
}

/* Main Content */
.profile-main {
  min-height: calc(100vh - 140px);
}

.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Hero Section */
.profile-hero {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  border-radius: 20px;
  padding: 40px;
  margin: 30px 0;
  color: white;
  box-shadow: 0 10px 30px rgba(45, 48, 71, 0.15);
}

.hero-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 30px;
}

.profile-avatar-section {
  display: flex;
  align-items: center;
  gap: 30px;
}

.avatar-wrapper {
  position: relative;
  width: 150px;
  height: 150px;
}

.profile-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.avatar-badge {
  position: absolute;
  bottom: 10px;
  right: 10px;
  width: 40px;
  height: 40px;
  background: #FF6B35;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  border: 3px solid white;
}

.profile-intro {
  flex: 1;
}

.profile-name {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  line-height: 1.2;
}

.profile-email {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.profile-tags {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.tag {
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.hero-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.cta-button {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 50px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 5px 20px rgba(255, 107, 53, 0.3);
}

.cta-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(255, 107, 53, 0.4);
}

.qr-code {
  width: 100px;
  height: 100px;
  border-radius: 10px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  padding: 5px;
  background: white;
}

.qr-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 8px;
}

/* Section Container (comme home page) */
.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Stats Section */
.stats-section {
  padding: 50px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 25px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.stat-content h3 {
  font-size: 2.2rem;
  font-weight: 700;
  color: #2D3047;
  margin-bottom: 5px;
  line-height: 1;
}

.stat-content p {
  color: #6c757d;
  font-size: 0.95rem;
}

/* Details Section */
.details-section {
  padding: 50px 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 20px;
  margin: 30px 0;
}

.section-header {
  text-align: center;
  margin-bottom: 40px;
}

.section-title {
  font-size: 2.5rem;
  color: #2D3047;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.section-title i {
  color: #FF6B35;
}

.loading-state {
  text-align: center;
  padding: 40px;
  font-size: 1.2rem;
  color: #6c757d;
}

.loading-state i {
  margin-right: 10px;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
}

.detail-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
}

.detail-card:hover {
  border-color: #FF6B35;
  transform: translateY(-3px);
}

.detail-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(255, 142, 83, 0.1));
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #FF6B35;
}

.detail-content h3 {
  font-size: 1rem;
  color: #6c757d;
  margin-bottom: 8px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-content p {
  font-size: 1.2rem;
  color: #2D3047;
  font-weight: 600;
  margin: 0;
}

.website-link {
  color: #FF6B35;
  text-decoration: none;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.website-link:hover {
  color: #FF8E53;
  text-decoration: underline;
}

.bio-section {
  background: white;
  border-radius: 20px;
  padding: 40px;
  margin-top: 40px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
}

.bio-title {
  font-size: 1.8rem;
  color: #2D3047;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.bio-content {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #6c757d;
}

/* Quick Actions */
.quick-actions-section {
  padding: 50px 0;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
}

.action-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(255, 107, 53, 0.1);
  border-color: #FF6B35;
}

.action-icon {
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
  margin-bottom: 20px;
}

.action-card h3 {
  font-size: 1.3rem;
  color: #2D3047;
  margin-bottom: 10px;
}

.action-card p {
  color: #6c757d;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Modal (même style que votre code) */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  width: 90%;
  max-width: 600px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 25px 30px;
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  gap: 12px;
}

.close-btn {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  font-size: 1.5rem;
  color: white;
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: rotate(90deg);
}

.modal-body {
  padding: 30px;
  max-height: 60vh;
  overflow-y: auto;
}

.modal-footer {
  padding: 20px 30px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  background: #f9fafb;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #374151;
}

.form-group label i {
  color: #FF6B35;
  width: 20px;
}

.form-input {
  width: 100%;
  padding: 15px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #FF6B35;
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.btn-primary, .btn-secondary {
  padding: 12px 30px;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  border: none;
  font-size: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(255, 107, 53, 0.3);
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
  transform: translateY(-2px);
}

/* Footer (identique à home page) */
.footer {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  padding-top: 60px;
  margin-top: 50px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 50px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
}

.footer-column {
  display: flex;
  flex-direction: column;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 20px;
  color: white;
}

.footer-logo i {
  color: #FF6B35;
  font-size: 2rem;
}

.footer-description {
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  margin-bottom: 30px;
  font-size: 0.95rem;
}

.social-links {
  display: flex;
  gap: 15px;
}

.social-link {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  text-decoration: none;
  transition: all 0.3s ease;
}

.social-link:hover {
  background: #FF6B35;
  transform: translateY(-3px);
}

.footer-title {
  font-size: 1.3rem;
  margin-bottom: 25px;
  color: white;
  position: relative;
  padding-bottom: 10px;
}

.footer-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: #FF6B35;
}

.footer-links {
  list-style: none;
  padding: 0;
}

.footer-links li {
  margin-bottom: 15px;
}

.footer-links a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.footer-links a:hover {
  color: #FF6B35;
  padding-left: 5px;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.contact-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
  line-height: 1.4;
}

.contact-item i {
  color: #FF6B35;
  width: 20px;
  margin-top: 2px;
}

.footer-bottom {
  background: rgba(0, 0, 0, 0.2);
  padding: 25px 0;
  text-align: center;
}

.footer-bottom p {
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  font-size: 0.9rem;
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 1024px) {
  .stats-grid,
  .details-grid,
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .footer-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .header-container {
    flex-direction: column;
    gap: 15px;
  }
  
  .nav-desktop {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .hero-content {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-avatar-section {
    flex-direction: column;
  }
  
  .stats-grid,
  .details-grid,
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .footer-container {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .contact-item {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .profile-hero,
  .detail-card,
  .stat-card,
  .action-card {
    padding: 20px;
  }
  
  .profile-name {
    font-size: 2rem;
  }
  
  .cta-button {
    width: 100%;
    justify-content: center;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .modal-footer button {
    width: 100%;
  }
}
</style>