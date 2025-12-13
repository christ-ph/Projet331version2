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
  client_type: '',
  fullname: '',
  company_name: '',
  company_website: '',
  industry: ''
});

onMounted(async () => {
  loading.value = true;

  try {
    const profile = await profileStore.getMyProfile();

    if (!profile || profile.type !== "client") {
      router.push('/dashboard');
      return;
    }

    // ✅ Pré-remplir le formulaire
    form.value.client_type = profile.client_type;
    form.value.fullname = profile.fullname;
    form.value.company_name = profile.company_name;
    form.value.company_website = profile.company_website;
    form.value.industry = profile.industry;

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
      type: "client",
      client_type: form.value.client_type,
      fullname: form.value.fullname,
      company_name: form.value.company_name,
      company_website: form.value.company_website,
      industry: form.value.industry
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

      <h2 class="title">Mon Profil Client</h2>

      <div v-if="loading" class="loading">Chargement...</div>

      <form v-else @submit.prevent="saveProfile" class="profile-form">

        <p v-if="errorMessage" class="alert error">{{ errorMessage }}</p>
        <p v-if="successMessage" class="alert success">{{ successMessage }}</p>

        <div class="form-group">
          <label>Type de client *</label>
          <input v-model="form.client_type" required placeholder="Ex: Entreprise, Particulier" />
        </div>

        <div class="form-group">
          <label>Nom complet *</label>
          <input v-model="form.fullname" required />
        </div>

        <div class="form-group">
          <label>Nom de l'entreprise</label>
          <input v-model="form.company_name" />
        </div>

        <div class="form-group">
          <label>Site web</label>
          <input v-model="form.company_website" placeholder="https://..." />
        </div>

        <div class="form-group">
          <label>Secteur d'activité *</label>
          <input v-model="form.industry" required placeholder="Ex: Technologie, Santé..." />
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
.form-group input {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 10px;
  font-size: 14px;
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
