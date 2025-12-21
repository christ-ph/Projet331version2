<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useProfileStore } from '@/stores/profile';

const profileStore = useProfileStore();
const router = useRouter();

const step = ref(1);
const type = ref(null);
const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// Options pour les selects
const clientTypes = ref([
  { value: '', label: 'Sélectionner un type' },
  { value: 'entreprise', label: 'Entreprise' },
  { value: 'startup', label: 'Startup' },
  { value: 'association', label: 'Association' },
  { value: 'particulier', label: 'Particulier' },
  { value: 'autre', label: 'Autre' }
]);

const industries = ref([
  { value: '', label: 'Sélectionner un secteur' },
  { value: 'tech', label: 'Technologie' },
  { value: 'finance', label: 'Finance' },
  { value: 'sante', label: 'Santé' },
  { value: 'education', label: 'Éducation' },
  { value: 'ecommerce', label: 'E-commerce' },
  { value: 'marketing', label: 'Marketing' },
  { value: 'design', label: 'Design' },
  { value: 'autre', label: 'Autre' }
]);

const availabilityOptions = ref([
  { value: '', label: 'Sélectionner une disponibilité' },
  { value: 'full_time', label: 'Temps plein (40h/semaine)' },
  { value: 'part_time', label: 'Temps partiel (20h/semaine)' },
  { value: 'flexible', label: 'Flexible' },
  { value: 'project_basis', label: 'Par projet' },
  { value: 'on_demand', label: 'Sur demande' }
]);

// Formulaires
const freelanceForm = ref({
  full_name: '',
  title: '',
  description: '',
  skills: '',
  languages: '',
  hourly_rate: '',
  experience_years: '',
  availability: ''
});

const clientForm = ref({
  client_type: '',
  fullname: '',
  company_name: '',
  company_website: '',
  industry: ''
});

// Sélection du type
const selectType = (selected) => {
  type.value = selected;
  step.value = 2;
};

const goBack = () => {
  step.value = 1;
  type.value = null;
  errorMessage.value = '';
  successMessage.value = '';
};

// Validation
const validateForm = () => {
  if (type.value === 'freelance') {
    return freelanceForm.value.full_name &&
           freelanceForm.value.title &&
           freelanceForm.value.description &&
           freelanceForm.value.skills;
  } else {
    return clientForm.value.client_type &&
           clientForm.value.fullname &&
           clientForm.value.industry;
  }
};

// Soumission
const submitProfile = async () => {
  if (!validateForm()) {
    errorMessage.value = 'Veuillez remplir tous les champs obligatoires (*)';
    return;
  }

  loading.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
    if (type.value === "freelance") {
      await profileStore.createFreelanceProfile({
        ...freelanceForm.value,
        skills: freelanceForm.value.skills.split(',').map(s => s.trim()),
        languages: freelanceForm.value.languages ? 
          freelanceForm.value.languages.split(',').map(s => s.trim()) 
          : []
      });
    } else {
      await profileStore.createClientProfile({
        ...clientForm.value
      });
    }

    successMessage.value = "🎉 Profil créé avec succès !";
    
    setTimeout(() => {
      router.push('/dashboard');
    }, 1500);

  } catch (e) {
    console.error('Erreur création profil:', e);
    errorMessage.value = e.response?.data?.msg || 
      "Une erreur est survenue. Veuillez réessayer.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="profile-setup-page">
    <!-- Header -->
    <div class="setup-header">
      <div class="logo" @click="router.push('/')">
        <i class="fas fa-hands-helping"></i>
        <span>Freelance<span class="logo-highlight">CMR</span></span>
      </div>
      <div class="setup-progress">
        <div class="progress-step" :class="{ 'active': step === 1 }">
          <div class="step-number">1</div>
          <span class="step-label">Type de compte</span>
        </div>
        <div class="progress-line"></div>
        <div class="progress-step" :class="{ 'active': step === 2 }">
          <div class="step-number">2</div>
          <span class="step-label">Informations</span>
        </div>
      </div>
    </div>

    <div class="setup-container">
      <!-- Étape 1 : Choix du type -->
      <div v-if="step === 1" class="type-selection">
        <div class="selection-header">
          <h1 class="selection-title">
            <i class="fas fa-user-plus"></i>
            Créer votre profil
          </h1>
          <p class="selection-subtitle">
            Choisissez le type de compte qui correspond à vos besoins
          </p>
        </div>

        <div class="type-cards">
          <!-- Carte Freelance -->
          <div 
            class="type-card" 
            :class="{ 'selected': type === 'freelance' }"
            @click="selectType('freelance')"
          >
            <div class="type-icon freelance">
              <i class="fas fa-laptop-code"></i>
            </div>
            <div class="type-content">
              <h3 class="type-title">Je suis Freelance</h3>
              <p class="type-description">
                Proposez vos services et trouvez des missions rémunératrices
              </p>
              <ul class="type-features">
                <li><i class="fas fa-check"></i> Trouvez des missions</li>
                <li><i class="fas fa-check"></i> Travaillez à distance</li>
                <li><i class="fas fa-check"></i> Recevez en FCFA</li>
              </ul>
            </div>
            <div class="type-arrow">
              <i class="fas fa-arrow-right"></i>
            </div>
          </div>

          <!-- Carte Client -->
          <div 
            class="type-card" 
            :class="{ 'selected': type === 'client' }"
            @click="selectType('client')"
          >
            <div class="type-icon client">
              <i class="fas fa-briefcase"></i>
            </div>
            <div class="type-content">
              <h3 class="type-title">Je suis Client</h3>
              <p class="type-description">
                Trouvez les meilleurs talents pour vos projets
              </p>
              <ul class="type-features">
                <li><i class="fas fa-check"></i> Trouvez des freelances</li>
                <li><i class="fas fa-check"></i> Gérez vos projets</li>
                <li><i class="fas fa-check"></i> Payez en FCFA</li>
              </ul>
            </div>
            <div class="type-arrow">
              <i class="fas fa-arrow-right"></i>
            </div>
          </div>
        </div>

        <div class="selection-footer">
          <p class="selection-note">
            <i class="fas fa-info-circle"></i>
            Vous pourrez modifier ces informations plus tard
          </p>
        </div>
      </div>

      <!-- Étape 2 : Formulaire -->
      <div v-else class="form-container">
        <!-- En-tête du formulaire -->
        <div class="form-header">
          <button class="back-btn" @click="goBack">
            <i class="fas fa-arrow-left"></i>
            Retour
          </button>
          <div class="form-header-content">
            <h1 class="form-title">
              <i :class="type === 'freelance' ? 'fas fa-laptop-code' : 'fas fa-briefcase'"></i>
              {{ type === 'freelance' ? 'Profil Freelance' : 'Profil Client' }}
            </h1>
            <p class="form-subtitle">
              Remplissez les informations nécessaires pour commencer
            </p>
          </div>
        </div>

        <!-- Messages -->
        <div v-if="errorMessage" class="alert error-alert">
          <i class="fas fa-exclamation-circle"></i>
          {{ errorMessage }}
        </div>
        
        <div v-if="successMessage" class="alert success-alert">
          <i class="fas fa-check-circle"></i>
          {{ successMessage }}
        </div>

        <!-- Formulaire Freelance -->
        <form 
          v-if="type === 'freelance'" 
          @submit.prevent="submitProfile" 
          class="profile-form"
        >
          <div class="form-section">
            <h3 class="section-title">
              <i class="fas fa-user"></i>
              Informations personnelles
            </h3>
            <div class="form-grid">
              <div class="form-group">
                <label for="full_name">
                  <i class="fas fa-user-tag"></i>
                  Nom complet *
                </label>
                <input 
                  id="full_name" 
                  v-model="freelanceForm.full_name" 
                  type="text" 
                  placeholder="Ex: Jean Dupont"
                  required
                />
                <span class="field-hint">Votre nom complet tel qu'il apparaîtra sur votre profil</span>
              </div>

              <div class="form-group">
                <label for="title">
                  <i class="fas fa-briefcase"></i>
                  Titre professionnel *
                </label>
                <input 
                  id="title" 
                  v-model="freelanceForm.title" 
                  type="text" 
                  placeholder="Ex: Développeur Fullstack"
                  required
                />
                <span class="field-hint">Votre spécialisation principale</span>
              </div>

              <div class="form-group full-width">
                <label for="description">
                  <i class="fas fa-file-alt"></i>
                  Description *
                </label>
                <textarea 
                  id="description" 
                  v-model="freelanceForm.description" 
                  placeholder="Décrivez votre expertise, expérience, et ce que vous pouvez offrir aux clients..."
                  rows="4"
                  required
                ></textarea>
                <span class="field-hint">Présentez-vous en quelques lignes</span>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3 class="section-title">
              <i class="fas fa-tools"></i>
              Compétences et expérience
            </h3>
            <div class="form-grid">
              <div class="form-group">
                <label for="skills">
                  <i class="fas fa-cogs"></i>
                  Compétences *
                </label>
                <input 
                  id="skills" 
                  v-model="freelanceForm.skills" 
                  type="text" 
                  placeholder="Ex: Vue.js, Node.js, MongoDB"
                  required
                />
                <span class="field-hint">Séparez par des virgules</span>
              </div>

              <div class="form-group">
                <label for="languages">
                  <i class="fas fa-language"></i>
                  Langues parlées
                </label>
                <input 
                  id="languages" 
                  v-model="freelanceForm.languages" 
                  type="text" 
                  placeholder="Ex: Français, Anglais"
                />
              </div>

              <div class="form-group">
                <label for="experience_years">
                  <i class="fas fa-calendar-alt"></i>
                  Années d'expérience *
                </label>
                <input 
                  id="experience_years" 
                  v-model="freelanceForm.experience_years" 
                  type="number" 
                  min="0" 
                  placeholder="Ex: 3"
                  required
                />
              </div>

              <div class="form-group">
                <label for="availability">
                  <i class="fas fa-clock"></i>
                  Disponibilité
                </label>
                <select id="availability" v-model="freelanceForm.availability">
                  <option 
                    v-for="option in availabilityOptions" 
                    :key="option.value" 
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3 class="section-title">
              <i class="fas fa-money-bill-wave"></i>
              Informations tarifaires
            </h3>
            <div class="form-grid">
              <div class="form-group">
                <label for="hourly_rate">
                  <i class="fas fa-coins"></i>
                  Taux horaire (FCFA) *
                </label>
                <div class="input-with-icon">
                  <input 
                    id="hourly_rate" 
                    v-model="freelanceForm.hourly_rate" 
                    type="number" 
                    min="0" 
                    placeholder="Ex: 5000"
                    required
                  />
                  <span class="input-suffix">FCFA/h</span>
                </div>
                <span class="field-hint">Votre tarif horaire moyen</span>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="goBack">
              <i class="fas fa-arrow-left"></i>
              Retour
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <template v-if="loading">
                <i class="fas fa-spinner fa-spin"></i>
                Création en cours...
              </template>
              <template v-else>
                <i class="fas fa-check"></i>
                Créer mon profil
              </template>
            </button>
          </div>
        </form>

        <!-- Formulaire Client -->
        <form 
          v-else 
          @submit.prevent="submitProfile" 
          class="profile-form"
        >
          <div class="form-section">
            <h3 class="section-title">
              <i class="fas fa-building"></i>
              Informations de l'entreprise
            </h3>
            <div class="form-grid">
              <div class="form-group">
                <label for="client_type">
                  <i class="fas fa-users"></i>
                  Type de client *
                </label>
                <select id="client_type" v-model="clientForm.client_type" required>
                  <option 
                    v-for="option in clientTypes" 
                    :key="option.value" 
                    :value="option.value"
                  >
                    {{ option.label }}
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
                  v-model="clientForm.fullname" 
                  type="text" 
                  placeholder="Ex: Marie Nkono"
                  required
                />
                <span class="field-hint">Votre nom de contact principal</span>
              </div>

              <div class="form-group">
                <label for="company_name">
                  <i class="fas fa-landmark"></i>
                  Nom de l'entreprise
                </label>
                <input 
                  id="company_name" 
                  v-model="clientForm.company_name" 
                  type="text" 
                  placeholder="Ex: Tech Solutions SARL"
                />
              </div>

              <div class="form-group">
                <label for="industry">
                  <i class="fas fa-industry"></i>
                  Secteur d'activité *
                </label>
                <select id="industry" v-model="clientForm.industry" required>
                  <option 
                    v-for="option in industries" 
                    :key="option.value" 
                    :value="option.value"
                  >
                    {{ option.label }}
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
                    v-model="clientForm.company_website" 
                    type="url" 
                    placeholder="https://votre-entreprise.com"
                  />
                </div>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3 class="section-title">
              <i class="fas fa-info-circle"></i>
              À propos de vos besoins
            </h3>
            <div class="info-card">
              <div class="info-icon">
                <i class="fas fa-lightbulb"></i>
              </div>
              <div class="info-content">
                <h4>Comment fonctionne FreelanceCMR pour les clients ?</h4>
                <p>Une fois votre profil créé, vous pourrez :</p>
                <ul>
                  <li>Publier vos projets et missions</li>
                  <li>Recevoir des propositions de freelances</li>
                  <li>Discuter directement avec les talents</li>
                  <li>Payer en toute sécurité en FCFA</li>
                </ul>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="goBack">
              <i class="fas fa-arrow-left"></i>
              Retour
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <template v-if="loading">
                <i class="fas fa-spinner fa-spin"></i>
                Création en cours...
              </template>
              <template v-else>
                <i class="fas fa-check"></i>
                Créer mon profil client
              </template>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==================== BASE STYLES ==================== */
.profile-setup-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* ==================== HEADER ==================== */
.setup-header {
  background: white;
  padding: 20px 40px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.8rem;
  font-weight: 700;
  color: #2D3047;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.logo i {
  color: #FF6B35;
  font-size: 2rem;
}

.logo-highlight {
  color: #FF6B35;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.setup-progress {
  display: flex;
  align-items: center;
  gap: 15px;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e5e7eb;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s ease;
}

.progress-step.active .step-number {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
}

.step-label {
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 500;
}

.progress-line {
  width: 80px;
  height: 3px;
  background: #e5e7eb;
  border-radius: 2px;
}

/* ==================== CONTAINER ==================== */
.setup-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
}

/* ==================== ÉTAPE 1 : SELECTION ==================== */
.type-selection {
  animation: fadeIn 0.5s ease;
}

.selection-header {
  text-align: center;
  margin-bottom: 50px;
}

.selection-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2D3047;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.selection-title i {
  color: #FF6B35;
}

.selection-subtitle {
  font-size: 1.1rem;
  color: #6c757d;
  max-width: 500px;
  margin: 0 auto;
  line-height: 1.5;
}

.type-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.type-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  display: flex;
  align-items: center;
  gap: 25px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 3px solid transparent;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
}

.type-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

.type-card.selected {
  border-color: #FF6B35;
  background: linear-gradient(135deg, rgba(255, 107, 53, 0.05), rgba(255, 142, 83, 0.05));
}

.type-card.selected::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
}

.type-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  flex-shrink: 0;
}

.type-icon.freelance {
  background: linear-gradient(135deg, #3B82F6, #60A5FA);
  color: white;
}

.type-icon.client {
  background: linear-gradient(135deg, #10B981, #34D399);
  color: white;
}

.type-content {
  flex: 1;
}

.type-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2D3047;
  margin-bottom: 10px;
}

.type-description {
  color: #6c757d;
  line-height: 1.5;
  margin-bottom: 15px;
  font-size: 1rem;
}

.type-features {
  list-style: none;
  padding: 0;
  margin: 0;
}

.type-features li {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4b5563;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.type-features i {
  color: #10B981;
  font-size: 0.8rem;
}

.type-arrow {
  color: #6c757d;
  font-size: 1.5rem;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
}

.type-card:hover .type-arrow {
  opacity: 1;
  transform: translateX(0);
}

.selection-footer {
  text-align: center;
  padding-top: 30px;
  border-top: 2px solid #f1f5f9;
}

.selection-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #6c757d;
  font-size: 0.95rem;
}

.selection-note i {
  color: #FF6B35;
}

/* ==================== ÉTAPE 2 : FORMULAIRE ==================== */
.form-container {
  animation: slideUp 0.5s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-header {
  display: flex;
  align-items: flex-start;
  gap: 30px;
  margin-bottom: 40px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  color: #6c757d;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.back-btn:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: translateX(-5px);
}

.form-header-content {
  flex: 1;
}

.form-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2D3047;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.form-title i {
  color: #FF6B35;
}

.form-subtitle {
  font-size: 1.1rem;
  color: #6c757d;
  line-height: 1.5;
}

/* Alertes */
.alert {
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  display: flex;
  align-items: flex-start;
  gap: 15px;
  animation: fadeIn 0.3s ease;
}

.error-alert {
  background: linear-gradient(135deg, #FEF2F2, #FEE2E2);
  color: #B91C1C;
  border: 2px solid #FCA5A5;
}

.success-alert {
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
  color: #166534;
  border: 2px solid #86EFAC;
}

.alert i {
  font-size: 1.2rem;
  margin-top: 2px;
}

/* Sections du formulaire */
.profile-form {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.08);
}

.form-section {
  margin-bottom: 40px;
  padding-bottom: 40px;
  border-bottom: 2px solid #f1f5f9;
}

.form-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.section-title {
  font-size: 1.4rem;
  color: #2D3047;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title i {
  color: #FF6B35;
  font-size: 1.2rem;
}

/* Grille du formulaire */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
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
  font-size: 0.95rem;
  font-weight: 600;
  color: #2D3047;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-group i {
  color: #FF6B35;
  font-size: 1rem;
}

.form-group input,
.form-group textarea,
.form-group select {
  padding: 14px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1rem;
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
  min-height: 120px;
}

.field-hint {
  font-size: 0.85rem;
  color: #6c757d;
  margin-top: 5px;
}

/* Input avec icône/suffixe */
.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-with-icon input {
  flex: 1;
  padding-right: 60px;
}

.input-suffix {
  position: absolute;
  right: 16px;
  color: #6c757d;
  font-weight: 500;
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

/* Carte d'information */
.info-card {
  display: flex;
  gap: 25px;
  padding: 30px;
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border-radius: 15px;
  border: 2px solid #BAE6FD;
}

.info-icon {
  width: 60px;
  height: 60px;
  border-radius: 15px;
  background: linear-gradient(135deg, #3B82F6, #60A5FA);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  flex-shrink: 0;
}

.info-content h4 {
  font-size: 1.2rem;
  color: #2D3047;
  margin-bottom: 10px;
}

.info-content p {
  color: #4b5563;
  margin-bottom: 15px;
  line-height: 1.5;
}

.info-content ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.info-content li {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #4b5563;
  margin-bottom: 8px;
  font-size: 0.95rem;
}

.info-content li::before {
  content: '✓';
  color: #3B82F6;
  font-weight: bold;
}

/* Actions du formulaire */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 40px;
  padding-top: 30px;
  border-top: 2px solid #f1f5f9;
}

.btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 32px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  font-family: inherit;
}

.btn-primary {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(255, 107, 53, 0.3);
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

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 768px) {
  .setup-header {
    flex-direction: column;
    gap: 20px;
    padding: 20px;
    text-align: center;
  }
  
  .setup-progress {
    width: 100%;
    justify-content: center;
  }
  
  .progress-line {
    width: 40px;
  }
  
  .selection-title {
    font-size: 2rem;
    flex-direction: column;
    gap: 10px;
  }
  
  .type-cards {
    grid-template-columns: 1fr;
  }
  
  .form-header {
    flex-direction: column;
    gap: 20px;
  }
  
  .back-btn {
    align-self: flex-start;
  }
  
  .form-title {
    font-size: 1.6rem;
  }
  
  .profile-form {
    padding: 25px;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 15px;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .type-card {
    flex-direction: column;
    text-align: center;
    padding: 25px;
  }
  
  .type-icon {
    width: 70px;
    height: 70px;
    font-size: 2rem;
  }
  
  .form-section {
    padding-bottom: 30px;
    margin-bottom: 30px;
  }
  
  .info-card {
    flex-direction: column;
    text-align: center;
  }
  
  .info-icon {
    align-self: center;
  }
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Support tactile */
@media (hover: none) and (pointer: coarse) {
  .type-card:hover,
  .back-btn:hover,
  .btn:hover {
    transform: none;
  }
  
  .type-card:active {
    transform: scale(0.98);
  }
}
</style>