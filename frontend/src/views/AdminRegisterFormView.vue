<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'

const form = ref({
  email: '',
  password: '',
  confirmPassword: ''
})
const errorMessage = ref('')
const successMessage = ref('')
const loading = ref(false)
const showPassword = ref(false)

const router = useRouter()
const adminStore = useAdminStore()

// Validation du formulaire
const validateForm = () => {
  errorMessage.value = ''

  // Validation email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.value.email)) {
    errorMessage.value = 'Veuillez entrer un email valide'
    return false
  }

  // Validation mot de passe
  if (form.value.password.length < 8) {
    errorMessage.value = 'Le mot de passe doit contenir au moins 8 caractères'
    return false
  }

  // Confirmation mot de passe
  if (form.value.password !== form.value.confirmPassword) {
    errorMessage.value = 'Les mots de passe ne correspondent pas'
    return false
  }

  return true
}

// Inscription admin
const register = async () => {
  if (!validateForm()) return

  errorMessage.value = ''
  successMessage.value = ''
  loading.value = true

  try {
    const result = await adminStore.register(form.value.email, form.value.password)
    
    if (result.success) {
      successMessage.value = "Compte admin créé avec succès ! Vous allez être redirigé..."
      
      // Auto-connexion après inscription
      setTimeout(async () => {
        const loginResult = await adminStore.login(form.value.email, form.value.password)
        if (loginResult.success) {
          router.push('/admin/dashboard')
        }
      }, 2000)
    } else {
      errorMessage.value = result.message || "Erreur d'inscription"
    }
  } catch (error) {
    console.error("Erreur d'inscription admin:", error)
    errorMessage.value = "Une erreur technique est survenue. Veuillez réessayer."
  } finally {
    loading.value = false
  }
}

// Basculer la visibilité du mot de passe
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

// Retour au login
const goToLogin = () => {
  router.push('/admin/login')
}
</script>

<template>
  <div class="admin-register-page">
    <div class="admin-register-container">
      <div class="admin-register-header">
        <div class="admin-register-logo">
          <i class="fas fa-shield-alt"></i>
          <h1>Création de compte Admin</h1>
        </div>
        <p class="admin-register-subtitle">
          Créez un nouveau compte administrateur pour la plateforme
        </p>
      </div>

      <div class="admin-register-card">
        <!-- Messages d'alerte -->
        <div v-if="errorMessage || successMessage" class="admin-alerts-container">
          <div v-if="errorMessage" class="admin-alert error">
            <i class="fas fa-exclamation-circle"></i>
            {{ errorMessage }}
          </div>
          <div v-if="successMessage" class="admin-alert success">
            <i class="fas fa-check-circle"></i>
            {{ successMessage }}
          </div>
        </div>

        <!-- Formulaire d'inscription -->
        <form @submit.prevent="register" class="admin-register-form">
          <div class="admin-form-group">
            <label for="register-email">
              <i class="fas fa-envelope"></i>
              Email Administrateur
            </label>
            <input
              id="register-email"
              v-model="form.email"
              type="email"
              placeholder="admin@freelancecmr.com"
              required
              class="admin-form-input"
              :disabled="loading"
            />
            <div class="input-hint">
              <i class="fas fa-info-circle"></i>
              Cet email sera utilisé pour la connexion administrative
            </div>
          </div>

          <div class="admin-form-group">
            <label for="register-password">
              <i class="fas fa-key"></i>
              Mot de passe
            </label>
            <div class="password-input-container">
              <input
                id="register-password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                required
                class="admin-form-input"
                :disabled="loading"
              />
              <button
                type="button"
                class="password-toggle"
                @click="togglePasswordVisibility"
                :disabled="loading"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <div class="password-strength">
              <div class="strength-indicator" :class="{
                'weak': form.password.length > 0 && form.password.length < 4,
                'medium': form.password.length >= 4 && form.password.length < 8,
                'strong': form.password.length >= 8
              }"></div>
              <span class="strength-label">
                {{ form.password.length >= 8 ? 'Fort' : form.password.length >= 4 ? 'Moyen' : 'Faible' }}
              </span>
            </div>
            <div class="input-hint">
              <i class="fas fa-shield-alt"></i>
              Minimum 8 caractères
            </div>
          </div>

          <div class="admin-form-group">
            <label for="confirm-password">
              <i class="fas fa-check-circle"></i>
              Confirmer le mot de passe
            </label>
            <input
              id="confirm-password"
              v-model="form.confirmPassword"
              type="password"
              placeholder="••••••••"
              required
              class="admin-form-input"
              :disabled="loading"
            />
            <div v-if="form.password && form.confirmPassword" class="password-match">
              <i :class="form.password === form.confirmPassword ? 'fas fa-check success' : 'fas fa-times error'"></i>
              <span :class="form.password === form.confirmPassword ? 'success' : 'error'">
                {{ form.password === form.confirmPassword ? 'Les mots de passe correspondent' : 'Les mots de passe ne correspondent pas' }}
              </span>
            </div>
          </div>

          <div class="admin-terms">
            <input type="checkbox" id="terms" required />
            <label for="terms">
              J'accepte les conditions d'utilisation du panneau d'administration
            </label>
          </div>

          <div class="admin-form-actions">
            <button 
              type="submit" 
              class="admin-submit-btn" 
              :disabled="loading"
              :class="{ 'loading': loading }"
            >
              <span v-if="loading">
                <i class="fas fa-spinner fa-spin"></i>
                Création en cours...
              </span>
              <span v-else>
                <i class="fas fa-user-plus"></i>
                Créer le compte Admin
              </span>
            </button>

            <button 
              type="button" 
              class="admin-secondary-btn"
              @click="goToLogin"
              :disabled="loading"
            >
              <i class="fas fa-sign-in-alt"></i>
              Déjà un compte ? Se connecter
            </button>
          </div>
        </form>
      </div>

      <div class="admin-security-notice">
        <i class="fas fa-lock"></i>
        <p>
          <strong>Sécurité :</strong> Ce compte aura des privilèges d'administration complets.
          Assurez-vous de choisir un mot de passe fort et de le garder confidentiel.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.admin-register-container {
  width: 100%;
  max-width: 500px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

/* En-tête */
.admin-register-header {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  padding: 40px;
  text-align: center;
  color: white;
}

.admin-register-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 15px;
}

.admin-register-logo i {
  font-size: 2.5rem;
  color: #FF6B35;
}

.admin-register-logo h1 {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
}

.admin-register-subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
  margin: 0;
}

/* Carte d'inscription */
.admin-register-card {
  padding: 40px;
}

/* Alertes (même style que login) */
.admin-alerts-container {
  margin-bottom: 25px;
}

.admin-alert {
  padding: 18px;
  border-radius: 12px;
  margin-bottom: 12px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-size: 0.95rem;
  line-height: 1.5;
  animation: slideIn 0.3s ease;
  border-left: 4px solid;
}

.admin-alert.error {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.1), rgba(220, 53, 69, 0.05));
  border-left-color: #dc3545;
  color: #dc3545;
}

.admin-alert.success {
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.1), rgba(40, 167, 69, 0.05));
  border-left-color: #28a745;
  color: #28a745;
}

/* Formulaire d'inscription */
.admin-register-form {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.admin-form-group {
  position: relative;
}

.admin-form-group label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.95rem;
  font-weight: 600;
  color: #2D3047;
  margin-bottom: 10px;
}

.admin-form-group label i {
  color: #FF6B35;
  font-size: 1rem;
}

.admin-form-input {
  width: 100%;
  padding: 16px 18px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  font-size: 0.95rem;
  font-family: inherit;
  transition: all 0.3s ease;
  background: #f8f9fa;
  color: #2D3047;
}

.admin-form-input:focus {
  outline: none;
  border-color: #2D3047;
  background: white;
  box-shadow: 0 5px 15px rgba(45, 48, 71, 0.1);
}

/* Conteneur mot de passe avec bouton toggle */
.password-input-container {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 5px;
  transition: color 0.3s ease;
}

.password-toggle:hover:not(:disabled) {
  color: #2D3047;
}

.password-toggle:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Force du mot de passe */
.password-strength {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.strength-indicator {
  flex: 1;
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
  position: relative;
}

.strength-indicator::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 0;
  border-radius: 3px;
  transition: all 0.3s ease;
}

.strength-indicator.weak::after {
  width: 33%;
  background: #dc3545;
}

.strength-indicator.medium::after {
  width: 66%;
  background: #ffc107;
}

.strength-indicator.strong::after {
  width: 100%;
  background: #28a745;
}

.strength-label {
  font-size: 0.85rem;
  font-weight: 500;
  min-width: 50px;
}

/* Correspondance des mots de passe */
.password-match {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-size: 0.85rem;
}

.password-match i.success {
  color: #28a745;
}

.password-match i.error {
  color: #dc3545;
}

.password-match .success {
  color: #28a745;
}

.password-match .error {
  color: #dc3545;
}

/* Conditions */
.admin-terms {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin: 10px 0;
}

.admin-terms input[type="checkbox"] {
  margin-top: 4px;
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 2px solid #dee2e6;
  cursor: pointer;
  transition: all 0.2s ease;
}

.admin-terms input[type="checkbox"]:checked {
  background-color: #2D3047;
  border-color: #2D3047;
}

.admin-terms label {
  font-size: 0.9rem;
  color: #6c757d;
  line-height: 1.4;
  cursor: pointer;
  user-select: none;
}

/* Actions du formulaire */
.admin-form-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.admin-submit-btn {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  border: none;
  padding: 18px;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.admin-submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(45, 48, 71, 0.3);
}

.admin-submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.admin-submit-btn.loading::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  border-radius: 12px;
  animation: loadingPulse 1.5s infinite;
}

.admin-secondary-btn {
  background: #f8f9fa;
  color: #2D3047;
  border: 2px solid #dee2e6;
  padding: 16px;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.admin-secondary-btn:hover:not(:disabled) {
  background: #e9ecef;
  border-color: #2D3047;
}

.admin-secondary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Notice de sécurité */
.admin-security-notice {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 193, 7, 0.05));
  border-radius: 12px;
  padding: 20px;
  margin: 0 40px 40px;
  border-left: 4px solid #ffc107;
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.admin-security-notice i {
  color: #ffc107;
  font-size: 1.5rem;
  margin-top: 2px;
}

.admin-security-notice p {
  color: #2D3047;
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0;
}

.admin-security-notice strong {
  color: #2D3047;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-register-container {
    max-width: 100%;
  }
  
  .admin-register-header,
  .admin-register-card {
    padding: 30px 20px;
  }
  
  .admin-security-notice {
    margin: 0 20px 30px;
    padding: 15px;
  }
  
  .admin-register-logo {
    flex-direction: column;
    gap: 10px;
  }
  
  .admin-register-logo h1 {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .admin-register-page {
    padding: 10px;
  }
  
  .admin-form-actions {
    gap: 10px;
  }
  
  .admin-submit-btn,
  .admin-secondary-btn {
    padding: 14px;
    font-size: 1rem;
  }
  
  .admin-security-notice {
    flex-direction: column;
    text-align: center;
  }
}
</style>