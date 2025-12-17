<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const form = ref({ email: '', password: '', confirm: '' });
const otp = ref('');
const showOtp = ref(false);

const errorMessage = ref('');
const successMessage = ref('');
const otpMessage = ref('');

// ✅ Toggle visibility des mots de passe
const showPassword = ref(false);
const showConfirm = ref(false);

const router = useRouter();
const authStore = useAuthStore();

// ✅ Validation du mot de passe en temps réel
const passwordValidation = computed(() => {
  const pwd = form.value.password;
  
  if (!pwd) return { valid: false, errors: [] };
  
  const errors = [];
  
  // Longueur minimale
  if (pwd.length < 8) {
    errors.push('Au moins 8 caractères');
  }
  
  // Espaces au début ou à la fin
  if (pwd !== pwd.trim()) {
    errors.push('Pas d\'espaces en début ou fin');
  }
  
  // Caractères interdits (emojis, symboles bizarres)
  const invalidChars = /[^\x20-\x7E]/g; // Accepte uniquement ASCII imprimable
  if (invalidChars.test(pwd)) {
    errors.push('Caractères invalides détectés');
  }
  
  // Scripts/balises HTML
  if (/<|>|script|&lt;|&gt;/i.test(pwd)) {
    errors.push('Caractères interdits (< > script)');
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
});

// ✅ Vérification si le mot de passe de confirmation correspond
const confirmPasswordMatch = computed(() => {
  if (!form.value.confirm) return null; // Pas encore rempli
  return form.value.password === form.value.confirm;
});

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};

const toggleConfirmVisibility = () => {
  showConfirm.value = !showConfirm.value;
};

const register = async () => {
  errorMessage.value = '';
  successMessage.value = '';
  otpMessage.value = '';

  // ✅ Validation mot de passe
  if (!passwordValidation.value.valid) {
    errorMessage.value = passwordValidation.value.errors.join(', ');
    return;
  }

  // ✅ Vérification confirmation
  if (form.value.password !== form.value.confirm) {
    errorMessage.value = "Les mots de passe ne correspondent pas.";
    return;
  }

  // ✅ Validation email
  if (!form.value.email.includes("@")) {
    errorMessage.value = "Veuillez entrer un email valide.";
    return;
  }

  try {
    await authStore.register(form.value.email, form.value.password);

    successMessage.value = "Compte créé ! Un code vous a été envoyé.";
    showOtp.value = true;

  } catch (error) {
    const msg = error.response?.data?.msg || "Erreur lors de l'inscription";
    errorMessage.value = msg;
  }
};

const verify = async () => {
  otpMessage.value = '';
  errorMessage.value = '';

  try {
    await authStore.verifyEmail(form.value.email, otp.value);

    otpMessage.value = "Email vérifié avec succès !";

    setTimeout(() => {
      router.push('/login');
    }, 800);

  } catch (error) {
    const msg = error.response?.data?.msg || "Code invalide";
    errorMessage.value = msg;
  }
};

const resend = async () => {
  otpMessage.value = '';
  errorMessage.value = '';

  try {
    await authStore.resendCode(form.value.email);
    otpMessage.value = "Nouveau code envoyé !";
  } catch (error) {
    errorMessage.value = "Impossible d'envoyer un nouveau code.";
  }
};
</script>

<template>
  <div class="register-container">
    <div class="register-box">
      <h2 class="title">Créer un compte</h2>

      <!-- FORMULAIRE REGISTER -->
      <form v-if="!showOtp" @submit.prevent="register" class="register-form">
        <p v-if="errorMessage" class="alert error">{{ errorMessage }}</p>
        <p v-if="successMessage" class="alert success">{{ successMessage }}</p>

        <!-- Email -->
        <div class="form-group">
          <label>Email *</label>
          <input v-model="form.email" type="email" required />
        </div>

        <!-- Mot de passe avec toggle -->
        <div class="form-group">
          <label>Mot de passe *</label>
          <div class="password-wrapper">
            <input 
              v-model="form.password" 
              :type="showPassword ? 'text' : 'password'" 
              required 
            />
            <button 
              type="button" 
              class="toggle-password" 
              @click="togglePasswordVisibility"
              tabindex="-1"
            >
              <img 
                :src="showPassword ? '/icone/eye-close.png' : '/icone/eye-open.png'" 
                alt="Toggle"
              />
            </button>
          </div>
          
          <!-- ✅ Affichage des erreurs de validation -->
          <div v-if="form.password && !passwordValidation.valid" class="validation-errors">
            <p v-for="error in passwordValidation.errors" :key="error" class="error-text">
              ⚠️ {{ error }}
            </p>
          </div>
        </div>

        <!-- Confirmation mot de passe avec toggle -->
        <div class="form-group">
          <label>Confirmer le mot de passe *</label>
          <div class="password-wrapper">
            <input 
              v-model="form.confirm" 
              :type="showConfirm ? 'text' : 'password'" 
              required 
              :class="{ 
                'input-error': confirmPasswordMatch === false,
                'input-success': confirmPasswordMatch === true 
              }"
            />
            <button 
              type="button" 
              class="toggle-password" 
              @click="toggleConfirmVisibility"
              tabindex="-1"
            >
              <img 
                :src="showConfirm ? '/icone/eye-close.png' : '/icone/eye-open.png'" 
                alt="Toggle"
              />
            </button>
          </div>
          
          <!-- ✅ Message si les mots de passe ne correspondent pas -->
          <p v-if="confirmPasswordMatch === false" class="error-text">
            ❌ Les mots de passe ne correspondent pas
          </p>
          <p v-if="confirmPasswordMatch === true" class="success-text">
            ✅ Les mots de passe correspondent
          </p>
        </div>

        <button 
          type="submit" 
          class="btn" 
          :disabled="authStore.isLoading || !passwordValidation.valid"
        >
          <span v-if="authStore.isLoading">Inscription...</span>
          <span v-else>S'inscrire</span>
        </button>
      </form>

      <!-- FORMULAIRE OTP -->
      <div v-else class="otp-box">
        <p v-if="errorMessage" class="alert error">{{ errorMessage }}</p>
        <p v-if="otpMessage" class="alert success">{{ otpMessage }}</p>

        <h3>Vérification de l'email</h3>
        <p class="info">Un code a été envoyé à <strong>{{ form.email }}</strong></p>

        <input
          v-model="otp"
          maxlength="6"
          class="otp-input"
          placeholder="Entrez le code"
        />

        <button class="btn" @click="verify" :disabled="authStore.isLoading">
          <span v-if="authStore.isLoading">Vérification...</span>
          <span v-else>Valider</span>
        </button>

        <button class="btn resend" @click="resend" :disabled="authStore.isLoading">
          Renvoyer le code
        </button>
      </div>

      <p class="login-text" v-if="!showOtp">
        Déjà un compte ?
        <router-link to="/login">Se connecter</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.otp-box {
  margin-top: 20px;
  text-align: center;
}

.otp-box h3 {
  font-size: 18px;
  margin-bottom: 10px;
}

.info {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 15px;
}

.otp-input {
  width: 100%;
  height: 45px;
  font-size: 20px;
  text-align: center;
  letter-spacing: 5px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  margin-bottom: 15px;
}

.resend {
  background: #6b7280;
  margin-top: 10px;
}
.resend:hover {
  background: #4b5563;
}

.register-container {
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #1f2937, #111827);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.register-box {
  background: #ffffff;
  width: 380px;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.25);
  text-align: center;
}

.title {
  margin-bottom: 20px;
  font-size: 24px;
  color: #1f2937;
}

.register-form {
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

/* ✅ Wrapper password */
.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.form-group input {
  width: 100%;
  height: 40px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0 40px 0 10px;
  font-size: 14px;
  transition: 0.2s;
}

.form-group input:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.2);
}

/* ✅ Bordures pour confirmation password */
.input-error {
  border-color: #ef4444 !important;
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2) !important;
}

.input-success {
  border-color: #10b981 !important;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
}

/* ✅ Toggle password button */
.toggle-password {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-password img {
  width: 20px;
  height: 20px;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.toggle-password:hover img {
  opacity: 1;
}

/* ✅ Messages de validation */
.validation-errors {
  margin-top: 5px;
}

.error-text {
  font-size: 12px;
  color: #ef4444;
  margin: 3px 0;
}

.success-text {
  font-size: 12px;
  color: #10b981;
  margin-top: 5px;
}

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
</style>