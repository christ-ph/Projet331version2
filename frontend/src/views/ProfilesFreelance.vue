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
const profile = ref(null);
const portfolio = ref([]);

// ✅ Modal edit profile
const showEditProfileModal = ref(false);

// ✅ Modal portfolio (add/edit)
const showPortfolioModal = ref(false);
const editingPortfolio = ref(null); // null = add, sinon = edit
const portfolioForm = ref({
  title: '',
  description: '',
  url: '',
  image_url: ''
});

// ✅ Computed
const isAuthenticated = computed(() => authStore.isAuthenticated);

// ✅ Chargement des données
onMounted(async () => {
  if (!isAuthenticated.value) {
    authStore.logout();
    router.push('/login');
    return;
  }

  try {
    profile.value = await profileStore.getMyProfile();
    
    if (!profile.value) {
      router.push('/dashboard');
      return;
    }

    portfolio.value = await portfolioStore.fetchPortfolio();
    
    console.log("Profile data:", profile.value);
    console.log("Portfolio data:", portfolio.value);

  } catch (error) {
    console.error('Erreur lors du chargement:', error);
  } finally {
    loading.value = false;
  }
});

// ✅ ACTIONS PROFILE
function openEditProfile() {
  showEditProfileModal.value = true;
}

function closeEditProfile() {
  showEditProfileModal.value = false;
}

async function saveProfile() {
  try {
    await profileStore.updateProfile(profile.value);
    alert('Profil mis à jour avec succès !');
    closeEditProfile();
  } catch (error) {
    console.error('Erreur mise à jour profil:', error);
    alert('Erreur lors de la mise à jour du profil');
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
      // Modifier
      await portfolioStore.updatePortfolio(editingPortfolio.value.id, portfolioForm.value);
      alert('Portfolio mis à jour !');
    } else {
      // Ajouter
      await portfolioStore.addPortfolio(portfolioForm.value);
      alert('Portfolio ajouté !');
    }
    
    // Recharger le portfolio
    portfolio.value = await portfolioStore.fetchPortfolio();
    closePortfolioModal();
    
  } catch (error) {
    console.error('Erreur portfolio:', error);
    alert('Erreur lors de l\'enregistrement');
  }
}

async function deletePortfolio(id) {
  if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) return;
  
  try {
    await portfolioStore.deletePortfolio(id);
    portfolio.value = await portfolioStore.fetchPortfolio();
    alert('Portfolio supprimé !');
  } catch (error) {
    console.error('Erreur suppression:', error);
    alert('Erreur lors de la suppression');
  }
}
</script>

<template>
  <!-- ✅ MODAL EDIT PROFILE -->
  <div v-if="showEditProfileModal" class="modal-overlay" @click.self="closeEditProfile">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Modifier le profil</h2>
        <button class="close-btn" @click="closeEditProfile">✕</button>
      </div>
      
      <div class="modal-body">
        <div class="form-group">
          <label>Nom complet</label>
          <input v-model="profile.full_name" type="text" />
        </div>
        
        <div class="form-group">
          <label>Titre</label>
          <input v-model="profile.title" type="text" />
        </div>
        
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="profile.description"></textarea>
        </div>
        
        <div class="form-group">
          <label>Taux horaire (FCFA/h)</label>
          <input v-model="profile.hourly_rate" type="number" />
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="closeEditProfile">Annuler</button>
        <button class="btn btn-primary" @click="saveProfile">Enregistrer</button>
      </div>
    </div>
  </div>

  <!-- ✅ MODAL PORTFOLIO (ADD/EDIT) -->
  <div v-if="showPortfolioModal" class="modal-overlay" @click.self="closePortfolioModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>{{ editingPortfolio ? 'Modifier' : 'Ajouter' }} un projet</h2>
        <button class="close-btn" @click="closePortfolioModal">✕</button>
      </div>
      
      <div class="modal-body">
        <div class="form-group">
          <label>Titre *</label>
          <input v-model="portfolioForm.title" type="text" required />
        </div>
        
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="portfolioForm.description"></textarea>
        </div>
        
        <div class="form-group">
          <label>URL du projet</label>
          <input v-model="portfolioForm.url" type="url" />
        </div>
        
        <div class="form-group">
          <label>URL de l'image</label>
          <input v-model="portfolioForm.image_url" type="url" />
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="closePortfolioModal">Annuler</button>
        <button class="btn btn-primary" @click="savePortfolio">Enregistrer</button>
      </div>
    </div>
  </div>

  <!-- ✅ CONTENU PRINCIPAL -->
  <div class="content-profile">
    <div v-if="loading" class="loading">
      Chargement du profil...
    </div>

    <template v-else>
      <!-- ✅ SECTION PROFILE -->
      <section id="profile">
        <div class="profile-header">
          <img 
            :src="profile.url_photo || '/icone/account.png'" 
            alt="Profile" 
            class="profile-image"
          />
          
          <div class="profile-info-header">
            <h1>{{ profile.full_name }}</h1>
            <p class="email">{{ profile.email }}</p>
            <button class="btn-edit" @click="openEditProfile">
              <img src="/icone/edit.png" alt="Edit" />
              Modifier le profil
            </button>
          </div>
          
          <div class="qr-section">
            <img src="/icone/Qr-code.png" alt="QR Code" class="qr-code" />
          </div>
        </div>
        
        <div class="profile-details">
          <div class="detail-item">
            <strong>Titre :</strong> {{ profile.title }}
          </div>
          <div class="detail-item">
            <strong>Description :</strong> {{ profile.description }}
          </div>
          <div class="detail-item">
            <strong>Compétences :</strong> {{ profile.skills?.join(', ') }}
          </div>
          <div class="detail-item">
            <strong>Taux horaire :</strong> {{ profile.hourly_rate }} FCFA/h
          </div>
          <div class="detail-item">
            <strong>Années d'expérience :</strong> {{ profile.experience_years }} ans
          </div>
        </div>
      </section>

      <!-- ✅ SECTION PORTFOLIO -->
      <section id="portfolio">
        <div class="portfolio-header">
          <h2>Portfolio</h2>
          <button class="btn btn-primary" @click="openAddPortfolio">
            + Ajouter un projet
          </button>
        </div>
        
        <div v-if="portfolio.length > 0" class="portfolio-grid">
          <div v-for="item in portfolio" :key="item.id" class="portfolio-item">
            <img 
              v-if="item.image_url" 
              :src="item.image_url" 
              alt="Project" 
              class="portfolio-image"
            />
            
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
            
            <a v-if="item.url" :href="item.url" target="_blank" class="project-link">
              Voir le projet →
            </a>
            
            <div class="portfolio-actions">
              <button class="btn-small btn-secondary" @click="openEditPortfolio(item)">
                Modifier
              </button>
              <button class="btn-small btn-danger" @click="deletePortfolio(item.id)">
                Supprimer
              </button>
            </div>
          </div>
        </div>
        
        <p v-else class="empty">
          Aucun projet dans votre portfolio. Ajoutez-en un !
        </p>
      </section>
    </template>
  </div>
</template>

<style scoped>
/* ✅ MODAL */
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
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
}

.modal-body {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* ✅ FORM */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 5px;
  color: #374151;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

/* ✅ BUTTONS */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-small {
  padding: 6px 12px;
  font-size: 13px;
}

.btn-edit {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 10px;
}

.btn-edit img {
  width: 20px;
  height: 20px;
}

.btn-edit:hover {
  background: #059669;
}

/* ✅ CONTENT */
.content-profile {
  margin-top: 100px;
  padding: 20px;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

.loading {
  text-align: center;
  font-size: 18px;
  padding: 40px;
}

/* ✅ PROFILE SECTION */
#profile {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 30px;
  min-width: 600px;
}

.profile-header {
  display: flex;
  gap: 30px;
  align-items: flex-start;
  margin-bottom: 30px;
  position: relative;
}

.profile-image {
  width: 120px;
  height: 120px;
  border-radius: 60px;
  object-fit: cover;
  border: 3px solid #e5e7eb;
}

.profile-info-header {
  flex: 1;
}

.profile-info-header h1 {
  font-size: 28px;
  color: #1f2937;
  margin: 0 0 5px 0;
}

.email {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 10px;
}

.qr-section {
  position: absolute;
  top: 0;
  right: 0;
}

.qr-code {
  width: 120px;
  height: 120px;
}

.profile-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.detail-item {
  padding: 15px;
  background: #f9fafb;
  border-radius: 8px;
  font-size: 15px;
  color: #374151;
}

.detail-item strong {
  color: #1f2937;
}

/* ✅ PORTFOLIO SECTION */
#portfolio {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.portfolio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.portfolio-header h2 {
  font-size: 24px;
  color: #1f2937;
  margin: 0;
}

.portfolio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.portfolio-item {
  background: #f9fafb;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.portfolio-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 6px;
  margin-bottom: 10px;
}

.portfolio-item h3 {
  font-size: 18px;
  color: #1f2937;
  margin: 0;
}

.portfolio-item p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
  flex: 1;
}

.project-link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.project-link:hover {
  text-decoration: underline;
}

.portfolio-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.empty {
  text-align: center;
  color: #9ca3af;
  font-size: 16px;
  padding: 40px;
}
</style>