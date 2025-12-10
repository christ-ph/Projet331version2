<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const form = ref({ email: '', password: '', confirm: '' });

const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();
const authStore = useAuthStore();

const register = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  // ✅ Vérification mot de passe
  if (form.value.password !== form.value.confirm) {
    errorMessage.value = "Les mots de passe ne correspondent pas.";
    return;
  }

  // ✅ Vérification format email simple
  if (!form.value.email.includes("@")) {
    errorMessage.value = "Veuillez entrer un email valide.";
    return;
  }

  try {
    await authStore.register(form.value.email, form.value.password);
    successMessage.value = "Compte créé avec succès !";

    setTimeout(() => {
      router.push('/login');
    }, 800);

  } catch (error) {
    const msg = error.response?.data?.msg || "Erreur lors de l'inscription";
    errorMessage.value = msg;
  }
};
</script>

<template>
  <div class="register-container">

    <div class="register-box">
      <h2 class="title">Créer un compte</h2>

      <form @submit.prevent="register" class="register-form">

        <!-- ✅ Messages -->
        <p v-if="errorMessage" class="alert error">{{ errorMessage }}</p>
        <p v-if="successMessage" class="alert success">{{ successMessage }}</p>

        <!-- ✅ Email -->
        <div class="form-group">
          <label>Email <span class="star">*</span></label>
          <input v-model="form.email" type="email" required placeholder="exemple@mail.com" />
        </div>

        <!-- ✅ Password -->
        <div class="form-group">
          <label>Mot de passe <span class="star">*</span></label>
          <input v-model="form.password" type="password" required placeholder="Votre mot de passe" />
        </div>

        <!-- ✅ Confirm Password -->
        <div class="form-group">
          <label>Confirmer le mot de passe <span class="star">*</span></label>
          <input v-model="form.confirm" type="password" required placeholder="Confirmez le mot de passe" />
        </div>

        <!-- ✅ Submit -->
        <button type="submit" class="btn" :disabled="authStore.isLoading">
          <span v-if="authStore.isLoading">Création...</span>
          <span v-else>S'inscrire</span>
        </button>
      </form>

      <p class="login-text">
        Vous avez déjà un compte ?
        <router-link to="/login">Se connecter</router-link>
      </p>
    </div>

  </div>
</template>

<style scoped>
/* ✅ Container global */
.register-container {
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #1f2937, #111827);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

/* ✅ Box centrale */
.register-box {
  background: #ffffff;
  width: 350px;
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
.register-form {
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
.form-group input {
  width: 100%;
  height: 40px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0 10px;
  font-size: 14px;
  transition: 0.2s;
}
.form-group input:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.2);
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

/* ✅ Lien login */
.login-text {
  margin-top: 15px;
  font-size: 14px;
}
.login-text a {
  color: #3b82f6;
  text-decoration: none;
}
.login-text a:hover {
  text-decoration: underline;
}

/* ✅ Étoile obligatoire */
.star {
  color: #f59e0b;
}
</style>
