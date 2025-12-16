<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useProfileStore } from '@/stores/profile';

const authStore = useAuthStore();
const profileStore = useProfileStore();
const router = useRouter();

// ✅ States réactifs
const loading = ref(true);
const profile = ref(null);

// ✅ Modal edit profile
const showEditProfileModal = ref(false);

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

    console.log("Profile data:", profile.value);

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
          <input v-model="profile.fullname" type="text" />
        </div>
        
        <div class="form-group">
          <label>Type de client</label>
          <input v-model="profile.client_type" type="text" placeholder="Entreprise, Particulier, etc." />
        </div>
        
        <div class="form-group">
          <label>Nom de l'entreprise</label>
          <input v-model="profile.company_name" type="text" />
        </div>
        
        <div class="form-group">
          <label>Site web</label>
          <input v-model="profile.company_website" type="url" placeholder="https://..." />
        </div>
        
        <div class="form-group">
          <label>Secteur d'activité</label>
          <input v-model="profile.industry" type="text" placeholder="Tech, Finance, etc." />
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="closeEditProfile">Annuler</button>
        <button class="btn btn-primary" @click="saveProfile">Enregistrer</button>
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
            <h1>{{ profile.fullname || profile.email }}</h1>
            <p class="email">{{ profile.email }}</p>
            <p class="client-badge">👤 Client {{ profile.client_type }}</p>
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
            <strong>Type de client :</strong> {{ profile.client_type || 'Non renseigné' }}
          </div>
          
          <div class="detail-item" v-if="profile.company_name">
            <strong>Entreprise :</strong> {{ profile.company_name }}
          </div>
          
          <div class="detail-item" v-if="profile.company_website">
            <strong>Site web :</strong> 
            <a :href="profile.company_website" target="_blank" class="website-link">
              {{ profile.company_website }}
            </a>
          </div>
          
          <div class="detail-item">
            <strong>Secteur d'activité :</strong> {{ profile.industry || 'Non renseigné' }}
          </div>
          
          <div class="detail-item" v-if="profile.phone">
            <strong>Téléphone :</strong> {{ profile.phone }}
          </div>
          
          <div class="detail-item" v-if="profile.country">
            <strong>Pays :</strong> {{ profile.country }}
          </div>
          
          <div class="detail-item" v-if="profile.city">
            <strong>Ville :</strong> {{ profile.city }}
          </div>
        </div>

        <!-- ✅ Section Bio (si renseignée) -->
        <div v-if="profile.bio" class="bio-section">
          <h3>À propos</h3>
          <p>{{ profile.bio }}</p>
        </div>
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

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
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
  margin-bottom: 5px;
}

.client-badge {
  display: inline-block;
  background: #dbeafe;
  color: #1e40af;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
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
  margin-bottom: 20px;
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

.website-link {
  color: #3b82f6;
  text-decoration: none;
}

.website-link:hover {
  text-decoration: underline;
}

/* ✅ BIO SECTION */
.bio-section {
  margin-top: 20px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.bio-section h3 {
  font-size: 18px;
  color: #1f2937;
  margin: 0 0 10px 0;
}

.bio-section p {
  font-size: 15px;
  color: #374151;
  line-height: 1.6;
  margin: 0;
}
</style>