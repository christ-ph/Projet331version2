<script setup>
import { ref } from 'vue';
import axios from 'axios';
import router from '@/router';

const form = ref({
  first_name: '',
  last_name: '',
  bio: '',
  skills: '',
  is_freelancer: false
});

const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

const submitProfile = async () => {
  loading.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
    await axios.post('/api/profiles/', form.value);
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
      <h2 class="title">Créer votre profil</h2>

      <form @submit.prevent="submitProfile" class="profile-form">

        <!-- ✅ Messages -->
        <p v-if="errorMessage" class="alert error">{{ errorMessage }}</p>
        <p v-if="successMessage" class="alert success">{{ successMessage }}</p>

        <!-- ✅ Prénom -->
        <div class="form-group">
          <label>Prénom <span class="star">*</span></label>
          <input v-model="form.first_name" required placeholder="Votre prénom" />
        </div>

        <!-- ✅ Nom -->
        <div class="form-group">
          <label>Nom <span class="star">*</span></label>
          <input v-model="form.last_name" required placeholder="Votre nom" />
        </div>

        <!-- ✅ Bio -->
        <div class="form-group">
          <label>Bio</label>
          <textarea v-model="form.bio" placeholder="Décrivez-vous en quelques lignes"></textarea>
        </div>

        <!-- ✅ Compétences -->
        <div class="form-group">
          <label>Compétences</label>
          <input v-model="form.skills" placeholder="Ex: Python, Vue.js, DevOps" />
        </div>

        <!-- ✅ Freelance ? -->
        <div class="checkbox-group">
          <input type="checkbox" v-model="form.is_freelancer" id="freelance-check" />
          <label for="freelance-check">Je suis freelance</label>
        </div>

        <!-- ✅ Submit -->
        <button type="submit" class="btn" :disabled="loading">
          <span v-if="loading">Enregistrement...</span>
          <span v-else>Créer mon profil</span>
        </button>
      </form>
    </div>

  </div>
</template>

<style scoped>
/* ✅ Container global */
.profile-container {
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #1f2937, #111827);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

/* ✅ Box centrale */
.profile-box {
  background: #ffffff;
  width: 400px;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.25);
  text-align: center;
}

/* ✅ Titre */
.title {
  margin-bottom: 20px;
  font-size: 24px;
  color: #1f2937;
}

/* ✅ Formulaire */
.profile-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* ✅ Messages */
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

/* ✅ Inputs */
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
  transition: 0.2s;
}
.form-group textarea {
  height: 80px;
  resize: none;
}
.form-group input:focus,
.form-group textarea:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.2);
}

/* ✅ Checkbox */
.checkbox-group {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #374151;
}

/* ✅ Bouton */
.btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 15px;
  transition: 0.2s;
}
.btn:hover {
  background: #2563eb;
}
.btn:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

/* ✅ Étoile obligatoire */
.star {
  color: #f59e0b;
}
</style>
