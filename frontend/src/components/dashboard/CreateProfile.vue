<script setup>
import { ref } from 'vue';
import { useProfileStore } from '@/stores/profile';
import router from '@/router';

const profileStore = useProfileStore();

const step = ref(1); // 1 = choix du type, 2 = formulaire

const type = ref(null); // "freelance" ou "client"

const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

/* ✅ Formulaire Freelance */
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

/* ✅ Formulaire Client */
const clientForm = ref({
  client_type: '',
  fullname: '',
  company_name: '',
  company_website: '',
  industry: ''
});

/* ✅ Choix du type */
const selectType = (selected) => {
  type.value = selected;
  step.value = 2;
};

/* ✅ Soumission du profil */
const submitProfile = async () => {
  loading.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
    if (type.value === "freelance") {
      await profileStore.createFreelanceProfile({
        ...freelanceForm.value,
        skills: freelanceForm.value.skills.split(',').map(s => s.trim()),
        languages: freelanceForm.value.languages.split(',').map(s => s.trim())
      });
    } else {
      await profileStore.createClientProfile({
        ...clientForm.value
      });
    }

    successMessage.value = "Profil créé avec succès !";

    setTimeout(() => {
      router.push('/dashboard');
    }, 800);

  } catch (e) {
    errorMessage.value = "Erreur lors de la création du profil.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="profile-container">

    <div class="profile-box">

      <!-- ✅ ÉTAPE 1 : CHOIX DU TYPE -->
      <div v-if="step === 1" class="step-choose">
        <h2 class="title">Créer votre profil</h2>
        <p class="subtitle">Choisissez votre type de compte</p>

        <button class="btn btn-type" @click="selectType('freelance')">
          👨‍💻 Je suis Freelance
        </button>

        <button class="btn btn-type" @click="selectType('client')">
          🧑‍💼 Je suis Client
        </button>
      </div>

      <!-- ✅ ÉTAPE 2 : FORMULAIRE FREELANCE -->
      <form v-if="step === 2 && type === 'freelance'" @submit.prevent="submitProfile" class="profile-form">

        <h2 class="title">Profil Freelance</h2>

        <p v-if="errorMessage" class="alert error">{{ errorMessage }}</p>
        <p v-if="successMessage" class="alert success">{{ successMessage }}</p>

        <div class="form-group">
          <label>Nom complet *</label>
          <input v-model="freelanceForm.full_name" required />
        </div>

        <div class="form-group">
          <label>Titre *</label>
          <input v-model="freelanceForm.title" required placeholder="Ex: Développeur Fullstack" />
        </div>

        <div class="form-group">
          <label>Description *</label>
          <textarea v-model="freelanceForm.description" required></textarea>
        </div>

        <div class="form-group">
          <label>Compétences *</label>
          <input v-model="freelanceForm.skills" placeholder="Ex: Python, Vue.js" />
        </div>

        <div class="form-group">
          <label>Langues *</label>
          <input v-model="freelanceForm.languages" placeholder="Ex: Français, Anglais" />
        </div>

        <div class="form-group">
          <label>Taux horaire (€) *</label>
          <input type="number" v-model="freelanceForm.hourly_rate" required />
        </div>

        <div class="form-group">
          <label>Années d'expérience *</label>
          <input type="number" v-model="freelanceForm.experience_years" required />
        </div>

        <div class="form-group">
          <label>Disponibilité *</label>
          <input v-model="freelanceForm.availability" placeholder="Ex: 20h/semaine" />
        </div>

        <button class="btn" :disabled="loading">
          <span v-if="loading">Enregistrement...</span>
          <span v-else>Créer mon profil</span>
        </button>
      </form>

      <!-- ✅ ÉTAPE 2 : FORMULAIRE CLIENT -->
      <form v-if="step === 2 && type === 'client'" @submit.prevent="submitProfile" class="profile-form">

        <h2 class="title">Profil Client</h2>

        <p v-if="errorMessage" class="alert error">{{ errorMessage }}</p>
        <p v-if="successMessage" class="alert success">{{ successMessage }}</p>

        <div class="form-group">
          <label>Type de client *</label>
          <input v-model="clientForm.client_type" required placeholder="Ex: Entreprise, Particulier" />
        </div>

        <div class="form-group">
          <label>Nom complet *</label>
          <input v-model="clientForm.fullname" required />
        </div>

        <div class="form-group">
          <label>Nom de l'entreprise</label>
          <input v-model="clientForm.company_name" />
        </div>

        <div class="form-group">
          <label>Site web</label>
          <input v-model="clientForm.company_website" />
        </div>

        <div class="form-group">
          <label>Secteur d'activité *</label>
          <input v-model="clientForm.industry" required />
        </div>

        <button class="btn" :disabled="loading">
          <span v-if="loading">Enregistrement...</span>
          <span v-else>Créer mon profil</span>
        </button>
      </form>

    </div>

  </div>
</template>

<style scoped>
.profile-container {
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #1f2937, #111827);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.profile-box {
  background: #ffffff;
  width: 450px;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.25);
  text-align: center;
}

.title {
  margin-bottom: 10px;
  font-size: 24px;
  color: #1f2937;
}

.subtitle {
  margin-bottom: 20px;
  color: #6b7280;
}

.btn-type {
  width: 100%;
  margin-top: 10px;
  padding: 12px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
}
.btn-type:hover {
  background: #2563eb;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.alert {
  padding: 10px;
  border-radius: 6px;
  font-size: 14px;
}
.alert.error {
  background: #fee2e2;
  color: #b91c1c;
}
.alert.success {
  background: #dcfce7;
  color: #166534;
}

.form-group {
  text-align: left;
}
.form-group label {
  font-size: 14px;
  color: #374151;
  margin-bottom: 5px;
  display: block;
}
.form-group input,
.form-group textarea {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 10px;
  font-size: 14px;
}
.form-group textarea {
  height: 80px;
  resize: none;
}

.btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
}
.btn:hover {
  background: #2563eb;
}
.btn:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}
</style>
