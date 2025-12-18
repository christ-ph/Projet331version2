<script setup>
import { ref } from 'vue';
import { useAdminStore } from '@/stores/admin';

const adminStore = useAdminStore();

const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const successMessage = ref('');
const errorMessage = ref('');
const isLoading = ref(false);

const handleRegisterAdmin = async () => {
  errorMessage.value = '';
  successMessage.value = '';
  
  // Validations
  if (!email.value || !password.value || !confirmPassword.value) {
    errorMessage.value = 'Veuillez remplir tous les champs';
    return;
  }

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Les mots de passe ne correspondent pas';
    return;
  }

  if (password.value.length < 6) {
    errorMessage.value = 'Le mot de passe doit contenir au moins 6 caractères';
    return;
  }

  isLoading.value = true;
  const result = await adminStore.registerAdmin(email.value, password.value);
  isLoading.value = false;

  if (result.success) {
    successMessage.value = result.message || 'Admin créé avec succès';
    // Réinitialiser le formulaire
    email.value = '';
    password.value = '';
    confirmPassword.value = '';
  } else {
    errorMessage.value = result.message;
  }
};
</script>

<template>
  <div class="register-admin-form">
    <div class="form-header">
      <h2>Créer un nouvel administrateur</h2>
      <p>Ajouter un compte administrateur au système</p>
    </div>

    <form @submit.prevent="handleRegisterAdmin">
      <div class="form-group">
        <label for="email">Email</label>
        <input
          id="email"
          v-model="email"
          type="email"
          placeholder="admin@example.com"
          required
        />
      </div>

      <div class="form-group">
        <label for="password">Mot de passe</label>
        <input
          id="password"
          v-model="password"
          type="password"
          placeholder="••••••••"
          required
        />
      </div>

      <div class="form-group">
        <label for="confirmPassword">Confirmer le mot de passe</label>
        <input
          id="confirmPassword"
          v-model="confirmPassword"
          type="password"
          placeholder="••••••••"
          required
        />
      </div>

      <div v-if="successMessage" class="success-message">
        ✓ {{ successMessage }}
      </div>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <button type="submit" class="submit-btn" :disabled="isLoading">
        <span v-if="isLoading">Création en cours...</span>
        <span v-else>Créer l'administrateur</span>
      </button>
    </form>
  </div>
</template>

<style scoped>
.register-admin-form {
  width: 100%;
  max-width: 500px;
  background: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
}

.form-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 8px;
}

.form-header p {
  font-size: 14px;
  color: #718096;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  font-size: 15px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s;
  outline: none;
}

.form-group input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.success-message {
  padding: 12px;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 8px;
  color: #155724;
  font-size: 14px;
  margin-bottom: 20px;
}

.error-message {
  padding: 12px;
  background-color: #fff5f5;
  border: 1px solid #fc8181;
  border-radius: 8px;
  color: #c53030;
  font-size: 14px;
  margin-bottom: 20px;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
