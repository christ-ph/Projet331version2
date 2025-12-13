<script setup>
import { ref, onMounted } from 'vue';
import { useProfileStore } from '@/stores/profile';
import router from '@/router';

const profileStore = useProfileStore();

const loading = ref(true);
const saving = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

const form = ref({
  full_name: '',
  title: '',
  description: '',
  skills: '',
  languages: '',
  hourly_rate: '',
  experience_years: '',
  availability: ''
});

onMounted(async () => {
  loading.value = true;

  try {
    const profile = await profileStore.getMyProfile();

    if (!profile || profile.type !== "freelance") {
      router.push('/dashboard');
      return;
    }

    // ✅ Pré-remplir le formulaire
    form.value.full_name = profile.full_name;
    form.value.title = profile.title;
    form.value.description = profile.description;
    form.value.skills = profile.skills?.join(', ') || '';
    form.value.languages = profile.languages?.join(', ') || '';
    form.value.hourly_rate = profile.hourly_rate;
    form.value.experience_years = profile.experience_years;
    form.value.availability = profile.availability;

  } catch (e) {
    errorMessage.value = "Impossible de charger votre profil.";
  }

  loading.value = false;
});

const saveProfile = async () => {
  saving.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
    await profileStore.updateProfile({
      type: "freelance",
      full_name: form.value.full_name,
      title: form.value.title,
      description: form.value.description,
      skills: form.value.skills.split(',').map(s => s.trim()),
      languages: form.value.languages.split(',').map(s => s.trim()),
      hourly_rate: form.value.hourly_rate,
      experience_years: form.value.experience_years,
      availability: form.value.availability
    });

    successMessage.value = "Profil mis à jour avec succès !";

  } catch (e) {
    errorMessage.value = "Erreur lors de la mise à jour du profil.";
  }

  saving.value = false;
};
</script>

<template>
  <div class="profile-container">

    <div class="profile-box">

      <h2 class="title">Mon Profil Freelance</h2>

      <div v-if="loading" class="loading">Chargement...</div>

      <form v-else @submit.prevent="saveProfile" class="profile-form">

        <p v-if="errorMessage" class="alert error">{{ errorMessage }}</p>
        <p v-if="successMessage" class="alert success">{{ successMessage }}</p>

        <div class="form-group">
          <label>Nom complet *</label>
          <input v-model="form.full_name" required />
        </div>

        <div class="form-group">
          <label>Titre *</label>
          <input v-model="form.title" required placeholder="Ex: Développeur Fullstack" />
        </div>

        <div class="form-group">
          <label>Description *</label>
          <textarea v-model="form.description" required></textarea>
        </div>

        <div class="form-group">
          <label>Compétences *</label>
          <input v-model="form.skills" placeholder="Ex: Python, Vue.js" />
        </div>

        <div class="form-group">
          <label>Langues *</label>
          <input v-model="form.languages" placeholder="Ex: Français, Anglais" />
        </div>

        <div class="form-group">
          <label>Taux horaire (€) *</label>
          <input type="number" v-model="form.hourly_rate" required />
        </div>

        <div class="form-group">
          <label>Années d'expérience *</label>
          <input type="number" v-model="form.experience_years" required />
        </div>

        <div class="form-group">
          <label>Disponibilité *</label>
          <input v-model="form.availability" placeholder="Ex: 20h/semaine" />
        </div>

        <button class="btn" :disabled="saving">
          <span v-if="saving">Enregistrement...</span>
          <span v-else>Mettre à jour</span>
        </button>

      </form>

    </div>

  </div>
</template>

<style scoped>
.profile-container {
  width: 100%;
  min-height: 100vh;
  background: #f3f4f6;
  display: flex;
  justify-content: center;
  padding: 40px 20px;
}

.profile-box {
  background: #ffffff;
  width: 600px;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.title {
  margin-bottom: 20px;
  font-size: 26px;
  color: #1f2937;
  text-align: center;
}

.loading {
  text-align: center;
  padding: 20px;
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
