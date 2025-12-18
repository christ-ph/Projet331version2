<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'

const form = ref({ 
  email: '', 
  password: '' 
})
const errorMessage = ref('')
const successMessage = ref('')
const loading = ref(false)
const rememberMe = ref(false)
const lastLoginTime = ref('Non disponible')
const currentTime = ref('')

const router = useRouter()
const adminStore = useAdminStore()

// Obtenir l'heure actuelle formatée
const getCurrentTime = () => {
  const now = new Date()
  return now.toLocaleTimeString('fr-FR', { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit'
  })
}

// Récupérer la dernière connexion admin
const getLastLoginTime = () => {
  const lastLogin = localStorage.getItem('admin_last_login')
  if (lastLogin) {
    const date = new Date(lastLogin)
    lastLoginTime.value = date.toLocaleString('fr-FR')
  } else {
    lastLoginTime.value = 'Première connexion'
  }
}

onMounted(() => {
  // Initialiser l'heure
  currentTime.value = getCurrentTime()
  
  // Mettre à jour l'heure toutes les secondes
  setInterval(() => {
    currentTime.value = getCurrentTime()
  }, 1000)
  
  // Récupérer la dernière connexion
  getLastLoginTime()
  
  // Charger l'email mémorisé si existant
  const rememberedEmail = localStorage.getItem('admin_remembered_email')
  if (rememberedEmail) {
    form.value.email = rememberedEmail
    rememberMe.value = true
  }
})

// Connexion admin
const login = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  loading.value = true

  try {
    const result = await adminStore.login(form.value.email, form.value.password)
    
    if (result.success) {
      // Sauvegarder la dernière connexion admin
      localStorage.setItem('admin_last_login', new Date().toISOString())
      
      // Sauvegarder l'email si "Se souvenir de moi"
      if (rememberMe.value) {
        localStorage.setItem('admin_remembered_email', form.value.email)
      } else {
        localStorage.removeItem('admin_remembered_email')
      }
      
      successMessage.value = "Authentification admin réussie ! Redirection..."
      
      setTimeout(() => {
        router.push('/admin/dashboard')
      }, 1500)
    } else {
      errorMessage.value = result.message || "Erreur de connexion admin"
    }
  } catch (error) {
    console.error("Erreur de connexion admin:", error)
    errorMessage.value = "Une erreur technique est survenue. Veuillez réessayer."
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="admin-login-form">
    <!-- Logo et titre Admin -->
    <div class="admin-logo">
      <i class="fas fa-shield-alt admin-icon"></i>
      <span class="admin-title">Admin<span class="logo-highlight">FreelanceCMR</span></span>
    </div>

    <div class="admin-card">
      <div class="admin-card-header">
        <h2 class="admin-card-title">
          <i class="fas fa-user-shield"></i>
          Portail Administrateur
        </h2>
        <p class="admin-card-subtitle">
          Accès sécurisé au panneau d'administration
        </p>
      </div>

      <div class="admin-card-content">
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

        <!-- Formulaire de connexion -->
        <form @submit.prevent="login" class="admin-login-form-main">
          <div class="admin-form-group">
            <label for="admin-email">
              <i class="fas fa-envelope"></i>
              Email Administrateur
            </label>
            <input
              id="admin-email"
              v-model="form.email"
              type="email"
              placeholder="admin@freelancecmr.com"
              required
              class="admin-form-input"
              :disabled="loading"
              autocomplete="username"
            />
            <div class="input-hint">
              <i class="fas fa-info-circle"></i>
              Utilisez vos identifiants d'administration
            </div>
          </div>

          <div class="admin-form-group">
            <label for="admin-password">
              <i class="fas fa-key"></i>
              Mot de passe Admin
            </label>
            <input
              id="admin-password"
              v-model="form.password"
              type="password"
              placeholder="••••••••"
              required
              class="admin-form-input"
              :disabled="loading"
              autocomplete="current-password"
            />
            <div class="input-hint">
              <i class="fas fa-lock"></i>
              Mot de passe sensible, gardez-le confidentiel
            </div>
          </div>

          <div class="admin-form-actions">
            <div class="remember-me">
              <input 
                type="checkbox" 
                id="remember" 
                v-model="rememberMe"
                :disabled="loading"
              />
              <label for="remember">Se souvenir de moi sur cet appareil</label>
            </div>
          </div>

          <button 
            type="submit" 
            class="admin-submit-btn" 
            :disabled="loading"
            :class="{ 'loading': loading }"
          >
            <span v-if="loading">
              <i class="fas fa-spinner fa-spin"></i>
              Vérification d'accès...
            </span>
            <span v-else>
              <i class="fas fa-sign-in-alt"></i>
              Accéder au panneau Admin
            </span>
          </button>

          <div class="admin-security-info">
            <div class="security-level">
              <div class="security-indicator">
                <span class="security-dot active"></span>
                <span class="security-dot active"></span>
                <span class="security-dot active"></span>
                <span class="security-dot"></span>
                <span class="security-dot"></span>
              </div>
              <span class="security-label">Haute sécurité requise</span>
            </div>
          </div>

          <div class="admin-divider">
            <span>Restrictions d'accès</span>
          </div>

          <div class="admin-warning">
            <i class="fas fa-exclamation-triangle"></i>
            <div class="warning-content">
              <h4>Accès restreint</h4>
              <p>Cette interface est réservée aux administrateurs autorisés. Toute tentative non autorisée sera journalisée.</p>
            </div>
          </div>
        </form>
      </div>

      <div class="admin-card-footer">
        <div class="admin-access-info">
          <i class="fas fa-clock"></i>
          <span>Dernière connexion : {{ lastLoginTime }}</span>
        </div>
        <div class="admin-back-link">
          <router-link to="/" class="back-link">
            <i class="fas fa-arrow-left"></i>
            Retour à l'accueil
          </router-link>
        </div>
      </div>
    </div>

    <!-- Bandeau de sécurité -->
    <div class="security-banner">
      <i class="fas fa-shield-check"></i>
      <span>Session chiffrée AES-256 | Horodatage: {{ currentTime }}</span>
    </div>
  </div>
</template>

<style scoped>
/* Le même CSS que dans la réponse précédente */
.admin-login-form {
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Logo Admin */
.admin-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 30px;
  padding: 20px 0;
}

.admin-icon {
  font-size: 2.8rem;
  color: #2D3047;
  background: linear-gradient(135deg, #2D3047, #1A1C2E);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  padding: 10px;
  border-radius: 50%;
  border: 3px solid #2D3047;
}

.admin-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2D3047;
}

.logo-highlight {
  color: #FF6B35;
  margin-left: 5px;
}

/* Carte Admin */
.admin-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  border: 1px solid #f0f0f0;
  margin-bottom: 25px;
}

/* En-tête de la carte */
.admin-card-header {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  padding: 35px;
  text-align: center;
  color: white;
  position: relative;
  overflow: hidden;
}

.admin-card-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.05) 50%, transparent 70%);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.admin-card-title {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  line-height: 1.3;
  position: relative;
  z-index: 1;
}

.admin-card-title i {
  font-size: 1.8rem;
  color: #FF6B35;
}

.admin-card-subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
  position: relative;
  z-index: 1;
}

/* Contenu de la carte */
.admin-card-content {
  padding: 35px;
}

/* Alertes Admin */
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

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

.admin-alert i {
  font-size: 1.1rem;
  margin-top: 2px;
  flex-shrink: 0;
}

/* Formulaire Admin */
.admin-login-form-main {
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

.admin-form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.admin-form-input::placeholder {
  color: #adb5bd;
}

.input-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-size: 0.85rem;
  color: #6c757d;
}

.input-hint i {
  font-size: 0.8rem;
  color: #6c757d;
}

/* Actions du formulaire */
.admin-form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px 0;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
}

.remember-me input[type="checkbox"] {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 2px solid #dee2e6;
  cursor: pointer;
  transition: all 0.2s ease;
}

.remember-me input[type="checkbox"]:checked {
  background-color: #2D3047;
  border-color: #2D3047;
}

.remember-me label {
  font-size: 0.9rem;
  color: #6c757d;
  cursor: pointer;
  user-select: none;
}

.remember-me input[type="checkbox"]:disabled + label {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Bouton de soumission */
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
  margin-top: 15px;
  position: relative;
  overflow: hidden;
}

.admin-submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.admin-submit-btn:hover:not(:disabled)::before {
  left: 100%;
}

.admin-submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(45, 48, 71, 0.3);
}

.admin-submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.admin-submit-btn.loading {
  position: relative;
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

@keyframes loadingPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

/* Information de sécurité */
.admin-security-info {
  margin: 15px 0;
}

.security-level {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  padding: 15px;
  background: linear-gradient(135deg, rgba(13, 110, 253, 0.05), rgba(13, 110, 253, 0.02));
  border-radius: 10px;
  border: 1px solid rgba(13, 110, 253, 0.1);
}

.security-indicator {
  display: flex;
  gap: 6px;
}

.security-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #e9ecef;
}

.security-dot.active {
  background-color: #28a745;
  animation: pulseDot 1.5s infinite;
}

.security-dot:nth-child(1).active { animation-delay: 0s; }
.security-dot:nth-child(2).active { animation-delay: 0.3s; }
.security-dot:nth-child(3).active { animation-delay: 0.6s; }

@keyframes pulseDot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.security-label {
  font-size: 0.9rem;
  color: #28a745;
  font-weight: 600;
}

/* Diviseur */
.admin-divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 20px 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.admin-divider::before,
.admin-divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e9ecef;
}

.admin-divider span {
  padding: 0 15px;
  background: white;
  font-weight: 500;
}

/* Avertissement */
.admin-warning {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 18px;
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 193, 7, 0.05));
  border-radius: 12px;
  border: 1px solid rgba(255, 193, 7, 0.2);
}

.admin-warning i {
  font-size: 1.3rem;
  color: #ffc107;
  margin-top: 2px;
}

.warning-content h4 {
  font-size: 1rem;
  color: #2D3047;
  margin-bottom: 5px;
  font-weight: 600;
}

.warning-content p {
  font-size: 0.9rem;
  color: #6c757d;
  line-height: 1.5;
}

/* Pied de carte */
.admin-card-footer {
  padding: 25px 35px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.admin-access-info {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  color: #6c757d;
}

.admin-access-info i {
  color: #6c757d;
}

.back-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2D3047;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  padding: 8px 15px;
  border-radius: 8px;
  background: white;
  border: 1px solid #dee2e6;
  transition: all 0.3s ease;
}

.back-link:hover {
  background: #2D3047;
  color: white;
  border-color: #2D3047;
  gap: 12px;
}

/* Bandeau de sécurité */
.security-banner {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  padding: 15px 20px;
  border-radius: 12px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  animation: slideUp 0.5s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.security-banner i {
  font-size: 1rem;
  color: #28a745;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-login-form {
    max-width: 100%;
    padding: 0 20px;
  }
  
  .admin-logo {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
  
  .admin-icon {
    font-size: 2.2rem;
  }
  
  .admin-title {
    font-size: 1.5rem;
  }
  
  .admin-card-header {
    padding: 25px 20px;
  }
  
  .admin-card-content {
    padding: 25px 20px;
  }
  
  .admin-card-footer {
    padding: 20px;
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .admin-card-title {
    font-size: 1.4rem;
    flex-direction: column;
    gap: 10px;
  }
  
  .security-banner {
    flex-direction: column;
    text-align: center;
    gap: 8px;
    padding: 12px 15px;
  }
}

@media (max-width: 480px) {
  .admin-form-actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .admin-warning {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .back-link {
    width: 100%;
    justify-content: center;
  }
}
</style>