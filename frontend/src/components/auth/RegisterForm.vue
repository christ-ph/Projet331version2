<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const form = ref({ email: '', password: '', confirm: '' });
const otp = ref('');
const showOtp = ref(false);
const mobileMenuOpen = ref(false); // AJOUTÉ

const errorMessage = ref('');
const successMessage = ref('');
const otpMessage = ref('');

const router = useRouter();
const authStore = useAuthStore();

// AJOUTÉ: Fonctions pour le menu mobile
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value;
};

const closeMobileMenu = () => {
  mobileMenuOpen.value = false;
};

const register = async () => {
  errorMessage.value = '';
  successMessage.value = '';
  otpMessage.value = '';

  if (form.value.password !== form.value.confirm) {
    errorMessage.value = "Les mots de passe ne correspondent pas.";
    return;
  }

  if (!form.value.email.includes("@")) {
    errorMessage.value = "Veuillez entrer un email valide.";
    return;
  }

  try {
    const result = await authStore.register({email:form.value.email, password:form.value.password});
    if(!result.success){
      const msg = result.message || "Erreur lors de l'inscription";
      errorMessage.value = msg;
      return;
    }
    successMessage.value = "Compte créé ! Un code de vérification vous a été envoyé.";
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

    otpMessage.value = "Email vérifié avec succès ! Redirection...";

    setTimeout(() => {
      router.push('/login');
    }, 1500);

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
    otpMessage.value = "Nouveau code envoyé ! Vérifiez votre boîte email.";
  } catch (error) {
    errorMessage.value = "Impossible d'envoyer un nouveau code.";
  }
};
</script>

<template>
  <div class="register-page">
    <!-- ==================== HEADER ==================== -->
    <header class="header">
      <div class="header-container">
        <!-- Logo de l'application -->
        <div class="logo">
          <i class="fas fa-hands-helping logo-icon"></i>
          <span class="logo-text">Freelance<span class="logo-highlight">CMR</span></span>
        </div>

        <!-- Navigation Desktop -->
        <nav class="nav-desktop">
          <router-link to="/login" class="nav-link login-link">
            <i class="fas fa-sign-in-alt"></i> Se connecter
          </router-link>
        </nav>

        <!-- Menu Hamburger pour Mobile -->
        <button class="hamburger-btn" @click="toggleMobileMenu" aria-label="Menu mobile">
          <i class="fas fa-bars" v-if="!mobileMenuOpen">&#9776;</i>
          <i class="fas fa-times" v-else>X</i>
        </button>

        <!-- Menu Mobile -->
        <div class="mobile-menu" :class="{ 'active': mobileMenuOpen }" v-if="mobileMenuOpen">
          <router-link to="/login" class="mobile-nav-link" @click="closeMobileMenu">
            <i class="fas fa-sign-in-alt"></i> Se connecter
          </router-link>
        </div>
      </div>
    </header>

    <!-- ==================== SECTION PRINCIPALE ==================== -->
    <main class="main-content">
      <div class="register-section">
        <div class="section-container">
          <!-- Carte d'inscription -->
          <div class="register-card">
            <!-- En-tête de la carte -->
            <div class="card-header">
              <div class="header-icon">
                <i class="fas fa-user-plus"></i>
              </div>
              <h1 class="card-title">
                Rejoignez <span class="highlight">FreelanceCMR</span>
              </h1>
              <p class="card-subtitle">
                La première plateforme de freelancing 100% camerounaise
              </p>
            </div>

            <!-- Contenu de la carte -->
            <div class="card-content">
              <!-- Formulaire d'inscription -->
              <div v-if="!showOtp" class="register-form-container">
                <div class="form-intro">
                  <p class="intro-text">
                    <i class="fas fa-flag"></i>
                    Créez votre compte gratuitement et commencez à travailler avec des clients camerounais
                  </p>
                </div>

                <!-- Messages d'alerte -->
                <div v-if="errorMessage || successMessage" class="alerts-container">
                  <div v-if="errorMessage" class="alert error">
                    <i class="fas fa-exclamation-circle"></i>
                    {{ errorMessage }}
                  </div>
                  <div v-if="successMessage" class="alert success">
                    <i class="fas fa-check-circle"></i>
                    {{ successMessage }}
                  </div>
                </div>

                <!-- Formulaire -->
                <form @submit.prevent="register" class="register-form">
                  <div class="form-group">
                    <label for="email">
                      <i class="fas fa-envelope"></i>
                      Adresse Email *
                    </label>
                    <input
                      id="email"
                      v-model="form.email"
                      type="email"
                      placeholder="exemple@email.com"
                      required
                      class="form-input"
                    />
                    <div class="input-hint">
                      <i class="fas fa-info-circle"></i>
                      Utilisez une ademail valide pour recevoir le code de vérification
                    </div>
                  </div>

                  <div class="form-group">
                    <label for="password">
                      <i class="fas fa-lock"></i>
                      Mot de passe *
                    </label>
                    <input
                      id="password"
                      v-model="form.password"
                      type="password"
                      placeholder="••••••••"
                      required
                      class="form-input"
                    />
                    <div class="input-hint">
                      <i class="fas fa-shield-alt"></i>
                      Minimum 8 caractères avec chiffres et lettres
                    </div>
                  </div>

                  <div class="form-group">
                    <label for="confirm">
                      <i class="fas fa-lock"></i>
                      Confirmer le mot de passe *
                    </label>
                    <input
                      id="confirm"
                      v-model="form.confirm"
                      type="password"
                      placeholder="••••••••"
                      required
                      class="form-input"
                    />
                  </div>

                  <button 
                    type="submit" 
                    class="submit-btn" 
                    :disabled="authStore.isLoading"
                    :class="{ 'loading': authStore.isLoading }"
                  >
                    <span v-if="authStore.isLoading">
                      <i class="fas fa-spinner fa-spin"></i>
                      Inscription en cours...
                    </span>
                    <span v-else>
                      <i class="fas fa-rocket"></i>
                      Créer mon compte
                    </span>
                  </button>

                  <div class="form-footer">
                    <p class="agreement-text">
                      En vous inscrivant, vous acceptez nos
                      <router-link to="/conditions">Conditions d'utilisation</router-link>
                      et notre
                      <router-link to="/confidentialite">Politique de confidentialité</router-link>
                    </p>
                  </div>
                </form>

                <!-- Lien de connexion -->
                <div class="auth-switch">
                  <p class="switch-text">
                    Vous avez déjà un compte ?
                    <router-link to="/login" class="switch-link">
                      <i class="fas fa-sign-in-alt"></i>
                      Connectez-vous ici
                    </router-link>
                  </p>
                </div>
              </div>

              <!-- Formulaire de vérification OTP -->
              <div v-else class="otp-container">
                <div class="otp-header">
                  <div class="otp-icon">
                    <i class="fas fa-mail-bulk"></i>
                  </div>
                  <h2 class="otp-title">Vérification de l'email</h2>
                  <p class="otp-subtitle">
                    Sécurité garantie pour la communauté FreelanceCMR
                  </p>
                </div>

                <!-- Messages OTP -->
                <div v-if="errorMessage || otpMessage" class="alerts-container">
                  <div v-if="errorMessage" class="alert error">
                    <i class="fas fa-exclamation-circle"></i>
                    {{ errorMessage }}
                  </div>
                  <div v-if="otpMessage" class="alert success">
                    <i class="fas fa-check-circle"></i>
                    {{ otpMessage }}
                  </div>
                </div>

                <!-- Informations email -->
                <div class="email-info">
                  <div class="email-badge">
                    <i class="fas fa-envelope-open-text"></i>
                    <div class="email-details">
                      <span class="email-label">Code envoyé à :</span>
                      <span class="email-value">{{ form.email }}</span>
                    </div>
                  </div>
                  <p class="otp-instruction">
                    Entrez le code à 6 chiffres reçu dans votre boîte email.
                    Le code expirera dans 15 minutes.
                  </p>
                </div>

                <!-- Champ OTP -->
                <div class="otp-input-group">
                  <label for="otp">
                    <i class="fas fa-key"></i>
                    Code de vérification *
                  </label>
                  <input
                    id="otp"
                    v-model="otp"
                    type="text"
                    maxlength="6"
                    placeholder="123456"
                    class="otp-input"
                    autocomplete="one-time-code"
                  />
                  <div class="otp-hint">
                    <i class="fas fa-clock"></i>
                    Code valide pendant 15 minutes
                  </div>
                </div>

                <!-- Boutons OTP -->
                <div class="otp-actions">
                  <button 
                    @click="verify" 
                    class="verify-btn"
                    :disabled="authStore.isLoading || otp.length !== 6"
                    :class="{ 'loading': authStore.isLoading }"
                  >
                    <span v-if="authStore.isLoading">
                      <i class="fas fa-spinner fa-spin"></i>
                      Vérification...
                    </span>
                    <span v-else>
                      <i class="fas fa-check-double"></i>
                      Vérifier et continuer
                    </span>
                  </button>

                  <button 
                    @click="resend" 
                    class="resend-btn"
                    :disabled="authStore.isLoading"
                  >
                    <i class="fas fa-redo"></i>
                    Renvoyer le code
                  </button>

                  <button 
                    @click="showOtp = false" 
                    class="back-btn"
                    :disabled="authStore.isLoading"
                  >
                    <i class="fas fa-arrow-left"></i>
                    Retour à l'inscription
                  </button>
                </div>

                <!-- Note de sécurité -->
                <div class="security-note">
                  <i class="fas fa-shield-alt"></i>
                  <span>
                    Votre sécurité est notre priorité. Ce code permet de garantir
                    l'authenticité de votre compte sur notre plateforme camerounaise.
                  </span>
                </div>
              </div>

              <!-- Avantages FreelanceCMR -->
              <div class="benefits-sidebar">
                <h3 class="benefits-title">
                  <i class="fas fa-star"></i>
                  Pourquoi nous rejoindre ?
                </h3>
                <ul class="benefits-list">
                  <li class="benefit-item">
                    <i class="fas fa-check-circle"></i>
                    <span>Paiements en FCFA sécurisés</span>
                  </li>
                  <li class="benefit-item">
                    <i class="fas fa-check-circle"></i>
                    <span>Communauté 100% camerounaise</span>
                  </li>
                  <li class="benefit-item">
                    <i class="fas fa-check-circle"></i>
                    <span>Support en français local</span>
                  </li>
                  <li class="benefit-item">
                    <i class="fas fa-check-circle"></i>
                    <span>Accès aux projets locaux et internationaux</span>
                  </li>
                  <li class="benefit-item">
                    <i class="fas fa-check-circle"></i>
                    <span>Outils adaptés au marché camerounais</span>
                  </li>
                </ul>
                <div class="benefits-footer">
                  <i class="fas fa-flag"></i>
                  <span>Fait au Cameroun, pour les Camerounais</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- ==================== FOOTER ==================== -->
    <footer class="footer">
      <div class="footer-container">
        <!-- Colonne 1: Logo et description -->
        <div class="footer-column">
          <div class="footer-logo">
            <i class="fas fa-hands-helping"></i>
            <span>Freelance<span class="logo-highlight">CMR</span></span>
          </div>
          <p class="footer-description">
            La première plateforme de freelancing 100% camerounaise. 
            Connectons les talents locaux avec des opportunités de qualité.
          </p>
          <div class="social-links">
            <a href="#" class="social-link" aria-label="Facebook">
              <i class="fab fa-facebook-f"></i>
            </a>
            <a href="#" class="social-link" aria-label="Twitter">
              <i class="fab fa-twitter"></i>
            </a>
            <a href="#" class="social-link" aria-label="LinkedIn">
              <i class="fab fa-linkedin-in"></i>
            </a>
            <a href="#" class="social-link" aria-label="Instagram">
              <i class="fab fa-instagram"></i>
            </a>
          </div>
        </div>

        <!-- Colonne 2: Liens rapides -->
        <div class="footer-column">
          <h3 class="footer-title">Liens rapides</h3>
          <ul class="footer-links">
            <li><router-link to="/">Accueil</router-link></li>
            <li><router-link to="/register">Inscription</router-link></li>
            <li><router-link to="/login">Connexion</router-link></li>
          </ul>
        </div>

        <!-- Colonne 3: Catégories -->
        <div class="footer-column">
          <h3 class="footer-title">Catégories</h3>
          <ul class="footer-links">
            <li><a href="#">Développement Web</a></li>
            <li><a href="#">Design Graphique</a></li>
            <li><a href="#">Marketing Digital</a></li>
            <li><a href="#">Rédaction</a></li>
            <li><a href="#">Montage Vidéo</a></li>
          </ul>
        </div>

        <!-- Colonne 4: Contact Cameroon -->
        <div class="footer-column">
          <h3 class="footer-title">Contactez-nous</h3>
          <div class="contact-info">
            <div class="contact-item">
              <i class="fas fa-map-marker-alt"></i>
              <span>Yaoundé, Cameroun</span>
            </div>
            <div class="contact-item">
              <i class="fas fa-phone"></i>
              <span>+237 650536195</span>
            </div>
            <div class="contact-item">
              <i class="fas fa-envelope"></i>
              <span>tms-compagny.vercel.app</span>
            </div>
            <div class="contact-item">
              <i class="fas fa-clock"></i>
              <span>Lun - Ven: 8h - 18h</span>
            </div>
          </div>
          
          <!-- Payment methods specific to Cameroon -->
          <div class="payment-methods">
            <span class="payment-title">Paiements acceptés:</span>
            <div class="payment-icons">
              <i class="fas fa-mobile-alt" title="Mobile Money"></i>
              <i class="fas fa-university" title="Virement bancaire"></i>
              <i class="fab fa-cc-visa" title="Visa"></i>
              <i class="fas fa-money-bill-wave" title="Espèces"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- Barre du bas du footer -->
      <div class="footer-bottom">
        <p>&copy; 2023 FreelanceCMR. Tous droits réservés. | Conçu avec ❤️ au Cameroun</p>
        <div class="footer-bottom-links">
          <router-link to="/confidentialite">Politique de confidentialité</router-link>
          <router-link to="/conditions">Conditions d'utilisation</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<!-- Le style reste EXACTEMENT le même que dans la version précédente -->
<style scoped>
/* ==================== STYLES GÉNÉRAUX ==================== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.register-page {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

/* ==================== HEADER STYLES ==================== */
.header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
  padding: 15px 0;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 2.2rem;
  color: #FF6B35;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-text {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2D3047;
}

.logo-highlight {
  color: #FF6B35;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Navigation Desktop */
.nav-desktop {
  display: flex;
  gap: 20px;
  align-items: center;
}

.nav-link {
  padding: 10px 25px;
  border-radius: 30px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.login-link {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border: 2px solid #FF6B35;
}

.login-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 107, 53, 0.3);
}

/* Bouton Hamburger (Mobile) */
.hamburger-btn {
  display: none;
  background-color: white;
  border: none;
  font-size: 1.8rem;
  color: #000000;
  cursor: pointer;
  padding: 5px;
  transition: transform 0.3s ease;
  z-index: 1001;
}

.hamburger-btn:hover {
  transform: scale(1.1);
}

/* Menu Mobile */
.mobile-menu {
  display: none;
  position: fixed;
  top: 70px;
  left: 0;
  right: 0;
  background: white;
  padding: 20px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  flex-direction: column;
  gap: 15px;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  z-index: 999;
}

.mobile-menu.active {
  display: flex;
  opacity: 1;
  visibility: visible;
}

.mobile-nav-link {
  padding: 15px;
  text-decoration: none;
  color: #2D3047;
  font-weight: 600;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  width: 100%;
}

.mobile-nav-link:hover {
  background: #f8f9fa;
  color: #FF6B35;
}

/* ==================== SECTION INSCRIPTION ==================== */
.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.register-section {
  width: 100%;
  max-width: 1200px;
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Carte d'inscription */
.register-card {
  background: white;
  border-radius: 25px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border: 1px solid #f0f0f0;
  animation: fadeInUp 0.6s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* En-tête de la carte */
.card-header {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  padding: 40px;
  text-align: center;
  color: white;
  position: relative;
  overflow: hidden;
}

.card-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path fill="rgba(255,255,255,0.05)" d="M0,0L100,0L100,100L0,100Z"/></svg>');
  background-size: cover;
  opacity: 0.1;
}

.header-icon {
  font-size: 3rem;
  color: #FF6B35;
  margin-bottom: 20px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.card-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  line-height: 1.2;
}

.highlight {
  color: #FF6B35;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.card-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

/* Contenu de la carte */
.card-content {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 40px;
  padding: 50px;
}

@media (max-width: 1024px) {
  .card-content {
    grid-template-columns: 1fr;
    gap: 40px;
  }
}

/* Formulaire d'inscription */
.register-form-container {
  padding-right: 40px;
  border-right: 1px solid #f0f0f0;
}

@media (max-width: 1024px) {
  .register-form-container {
    padding-right: 0;
    border-right: none;
    border-bottom: 1px solid #f0f0f0;
    padding-bottom: 40px;
  }
}

.form-intro {
  background: rgba(255, 107, 53, 0.05);
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 30px;
  border-left: 4px solid #FF6B35;
}

.intro-text {
  display: flex;
  align-items: center;
  gap: 15px;
  color: #2D3047;
  font-size: 1.1rem;
  line-height: 1.6;
}

.intro-text i {
  color: #FF6B35;
  font-size: 1.5rem;
  flex-shrink: 0;
}

/* Alertes */
.alerts-container {
  margin-bottom: 30px;
}

.alert {
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 15px;
  display: flex;
  align-items: flex-start;
  gap: 15px;
  font-size: 1rem;
  line-height: 1.5;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.alert.error {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.1), rgba(220, 53, 69, 0.05));
  border: 1px solid rgba(220, 53, 69, 0.2);
  color: #dc3545;
}

.alert.success {
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.1), rgba(40, 167, 69, 0.05));
  border: 1px solid rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.alert i {
  font-size: 1.2rem;
  margin-top: 2px;
}

/* Formulaire */
.register-form {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.form-group {
  position: relative;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1rem;
  font-weight: 600;
  color: #2D3047;
  margin-bottom: 10px;
}

.form-group label i {
  color: #FF6B35;
  font-size: 1.1rem;
}

.form-input {
  width: 100%;
  padding: 18px 20px;
  border: 2px solid #e9ecef;
  border-radius: 15px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.form-input:focus {
  outline: none;
  border-color: #FF6B35;
  background: white;
  box-shadow: 0 5px 20px rgba(255, 107, 53, 0.1);
}

.form-input::placeholder {
  color: #adb5bd;
}

.input-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #6c757d;
  margin-top: 8px;
  padding-left: 5px;
}

.input-hint i {
  color: #FF6B35;
  font-size: 0.9rem;
}

/* Bouton de soumission */
.submit-btn {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border: none;
  padding: 20px;
  border-radius: 15px;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 10px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-btn.loading {
  position: relative;
}

.submit-btn.loading::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  border-radius: 15px;
  animation: loadingPulse 1.5s infinite;
}

@keyframes loadingPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Pied de formulaire */
.form-footer {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.agreement-text {
  font-size: 0.9rem;
  color: #6c757d;
  text-align: center;
  line-height: 1.6;
}

.agreement-text a {
  color: #FF6B35;
  text-decoration: none;
  font-weight: 500;
}

.agreement-text a:hover {
  text-decoration: underline;
}

/* Switch d'authentification */
.auth-switch {
  margin-top: 30px;
  padding: 25px;
  background: #f8f9fa;
  border-radius: 15px;
  text-align: center;
}

.switch-text {
  font-size: 1rem;
  color: #2D3047;
}

.switch-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #FF6B35;
  text-decoration: none;
  font-weight: 600;
  margin-top: 10px;
  padding: 10px 20px;
  border-radius: 25px;
  background: white;
  border: 2px solid #FF6B35;
  transition: all 0.3s ease;
}

.switch-link:hover {
  background: #FF6B35;
  color: white;
  transform: translateY(-2px);
}

/* Container OTP */
.otp-container {
  padding-right: 40px;
}

@media (max-width: 1024px) {
  .otp-container {
    padding-right: 0;
  }
}

/* En-tête OTP */
.otp-header {
  text-align: center;
  margin-bottom: 30px;
}

.otp-icon {
  font-size: 3rem;
  color: #FF6B35;
  margin-bottom: 15px;
}

.otp-title {
  font-size: 2rem;
  color: #2D3047;
  margin-bottom: 10px;
  font-weight: 700;
}

.otp-subtitle {
  color: #6c757d;
  font-size: 1.1rem;
  line-height: 1.6;
}

/* Informations email */
.email-info {
  background: rgba(255, 107, 53, 0.05);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 30px;
  border: 1px solid rgba(255, 107, 53, 0.1);
}

.email-badge {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.email-badge i {
  font-size: 2rem;
  color: #FF6B35;
}

.email-details {
  flex: 1;
}

.email-label {
  display: block;
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 5px;
}

.email-value {
  display: block;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2D3047;
  word-break: break-all;
}

.otp-instruction {
  color: #6c757d;
  font-size: 0.95rem;
  line-height: 1.6;
  text-align: center;
}

/* Champ OTP */
.otp-input-group {
  margin-bottom: 30px;
}

.otp-input-group label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1rem;
  font-weight: 600;
  color: #2D3047;
  margin-bottom: 15px;
}

.otp-input-group label i {
  color: #FF6B35;
}

.otp-input {
  width: 100%;
  padding: 25px;
  font-size: 2rem;
  text-align: center;
  letter-spacing: 10px;
  border: 2px solid #e9ecef;
  border-radius: 15px;
  background: #f8f9fa;
  font-family: 'Courier New', monospace;
  font-weight: 600;
  transition: all 0.3s ease;
}

.otp-input:focus {
  outline: none;
  border-color: #FF6B35;
  background: white;
  box-shadow: 0 5px 20px rgba(255, 107, 53, 0.1);
}

.otp-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #FF6B35;
  margin-top: 10px;
  justify-content: center;
}

.otp-hint i {
  animation: pulse 2s infinite;
}

/* Actions OTP */
.otp-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}

.verify-btn {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  padding: 20px;
  border-radius: 15px;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.verify-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(40, 167, 69, 0.3);
}

.verify-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.resend-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 18px;
  border-radius: 15px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.resend-btn:hover:not(:disabled) {
  background: #545b62;
  transform: translateY(-2px);
}

.back-btn {
  background: transparent;
  color: #6c757d;
  border: 2px solid #e9ecef;
  padding: 18px;
  border-radius: 15px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.back-btn:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #FF6B35;
  color: #FF6B35;
}

/* Note de sécurité */
.security-note {
  background: linear-gradient(135deg, rgba(13, 110, 253, 0.05), rgba(13, 110, 253, 0.02));
  border-radius: 15px;
  padding: 20px;
  border-left: 4px solid #0d6efd;
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.security-note i {
  color: #0d6efd;
  font-size: 1.5rem;
  margin-top: 2px;
}

.security-note span {
  color: #2D3047;
  font-size: 0.95rem;
  line-height: 1.6;
}

/* Sidebar des avantages */
.benefits-sidebar {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  border-radius: 20px;
  padding: 40px 30px;
  color: white;
  position: relative;
  overflow: hidden;
}

.benefits-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path fill="rgba(255,255,255,0.05)" d="M0,0L100,0L100,100L0,100Z"/></svg>');
  background-size: cover;
  opacity: 0.1;
}

.benefits-title {
  font-size: 1.5rem;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
}

.benefits-title i {
  color: #FFD166;
}

.benefits-list {
  list-style: none;
  margin-bottom: 30px;
}

.benefit-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 18px;
  font-size: 1rem;
  line-height: 1.5;
}

.benefit-item i {
  color: #FF6B35;
  margin-top: 3px;
  flex-shrink: 0;
}

.benefit-item span {
  color: rgba(255, 255, 255, 0.9);
}

.benefits-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  color: #FFD166;
  font-weight: 500;
}

.benefits-footer i {
  font-size: 1.2rem;
}

/* ==================== FOOTER STYLES ==================== */
.footer {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  padding-top: 80px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 60px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 40px;
}

/* Colonnes du footer */
.footer-column {
  display: flex;
  flex-direction: column;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 20px;
  color: white;
}

.footer-logo i {
  color: #FF6B35;
  font-size: 2rem;
}

.footer-description {
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  margin-bottom: 30px;
  font-size: 0.95rem;
}

/* Liens sociaux */
.social-links {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.social-link {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  text-decoration: none;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.social-link:hover {
  background: #FF6B35;
  transform: translateY(-3px);
}

/* Titres des colonnes */
.footer-title {
  font-size: 1.3rem;
  margin-bottom: 25px;
  color: white;
  position: relative;
  padding-bottom: 10px;
}

.footer-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: #FF6B35;
}

/* Listes de liens */
.footer-links {
  list-style: none;
}

.footer-links li {
  margin-bottom: 15px;
}

.footer-links a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 0.95rem;
  display: inline-block;
}

.footer-links a:hover {
  color: #FF6B35;
  padding-left: 5px;
}

/* Informations de contact */
.contact-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.contact-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
  line-height: 1.4;
}

.contact-item i {
  color: #FF6B35;
  width: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

/* Méthodes de paiement */
.payment-methods {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.payment-title {
  display: block;
  margin-bottom: 15px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.payment-icons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.payment-icons i {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.6);
  transition: color 0.3s ease;
}

.payment-icons i:hover {
  color: #FF6B35;
}

/* Barre du bas du footer */
.footer-bottom {
  background: rgba(0, 0, 0, 0.2);
  padding: 25px 0;
  text-align: center;
}

.footer-bottom p {
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 15px;
  font-size: 0.9rem;
  line-height: 1.5;
}

.footer-bottom-links {
  display: flex;
  justify-content: center;
  gap: 30px;
  flex-wrap: wrap;
}

.footer-bottom-links a {
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.footer-bottom-links a:hover {
  color: #FF6B35;
}

/* ==================== RESPONSIVE DESIGN ==================== */

/* Tablette en mode portrait */
@media (max-width: 1024px) {
  .card-content {
    grid-template-columns: 1fr;
    padding: 40px 30px;
  }
  
  .register-form-container,
  .otp-container {
    padding-right: 0;
    border-right: none;
    border-bottom: 1px solid #f0f0f0;
    padding-bottom: 40px;
  }
  
  .footer-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 50px 30px;
  }
  
  .card-title {
    font-size: 2.2rem;
  }
}

/* Tablette petite et grands téléphones */
@media (max-width: 768px) {
  /* Header Responsive */
  .nav-desktop {
    display: none;
  }
  
  .hamburger-btn {
    display: block;
  }
  
  .logo-text {
    font-size: 1.5rem;
  }
  
  .logo-icon {
    font-size: 1.8rem;
  }
  
  /* Carte d'inscription */
  .card-header {
    padding: 30px 20px;
  }
  
  .card-content {
    padding: 30px 20px;
    gap: 30px;
  }
  
  .card-title {
    font-size: 1.8rem;
  }
  
  .card-subtitle {
    font-size: 1rem;
  }
  
  .header-icon,
  .otp-icon {
    font-size: 2.5rem;
  }
  
  /* Formulaire */
  .form-input,
  .otp-input {
    padding: 16px;
  }
  
  .otp-input {
    font-size: 1.8rem;
    padding: 20px;
  }
  
  /* Boutons */
  .submit-btn,
  .verify-btn {
    padding: 18px;
    font-size: 1.1rem;
  }
  
  .resend-btn,
  .back-btn {
    padding: 16px;
  }
  
  /* Footer Responsive */
  .footer-container {
    grid-template-columns: 1fr;
    gap: 40px;
  }
  
  .footer-column {
    text-align: center;
    align-items: center;
  }
  
  .footer-title::after {
    left: 50%;
    transform: translateX(-50%);
  }
  
  .contact-item {
    justify-content: center;
  }
  
  .payment-icons {
    justify-content: center;
  }
}

/* Téléphones petits */
@media (max-width: 480px) {
  .header-container,
  .section-container,
  .footer-container {
    padding: 0 15px;
  }
  
  .card-header {
    padding: 25px 15px;
  }
  
  .card-content {
    padding: 25px 15px;
  }
  
  .card-title {
    font-size: 1.6rem;
  }
  
  .otp-title {
    font-size: 1.6rem;
  }
  
  .form-input,
  .otp-input {
    padding: 14px;
  }
  
  .otp-input {
    font-size: 1.5rem;
    letter-spacing: 8px;
    padding: 18px;
  }
  
  /* Boutons */
  .submit-btn,
  .verify-btn,
  .resend-btn,
  .back-btn {
    padding: 14px;
    font-size: 1rem;
  }
  
  /* Alertes */
  .alert {
    padding: 15px;
    font-size: 0.95rem;
  }
  
  .intro-text {
    font-size: 1rem;
  }
  
  .benefits-title {
    font-size: 1.3rem;
  }
  
  .benefit-item {
    font-size: 0.95rem;
  }
  
  .footer-bottom-links {
    flex-direction: column;
    gap: 10px;
  }
  
  .footer-bottom p {
    font-size: 0.8rem;
    padding: 0 10px;
  }
}

/* Support tactile amélioré */
@media (hover: none) and (pointer: coarse) {
  .submit-btn:hover,
  .verify-btn:hover,
  .resend-btn:hover,
  .back-btn:hover,
  .social-link:hover,
  .footer-links a:hover,
  .switch-link:hover {
    transform: none;
  }
  
  .submit-btn:active,
  .verify-btn:active,
  .resend-btn:active,
  .back-btn:active {
    transform: scale(0.98);
  }
  
  .nav-link:hover,
  .mobile-nav-link:hover {
    transform: none;
  }
}

/* Support pour les modes sombre */
@media (prefers-color-scheme: dark) {
  .register-page {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  }
  
  .register-card {
    background: #2d2d2d;
    border-color: #404040;
  }
  
  .card-header {
    background: linear-gradient(135deg, #1A1C2E 0%, #0d0f1a 100%);
  }
  
  .form-input,
  .otp-input {
    background: #3d3d3d;
    border-color: #505050;
    color: #e4e4e4;
  }
  
  .form-input:focus,
  .otp-input:focus {
    background: #404040;
    border-color: #FF6B35;
  }
  
  .form-group label,
  .otp-title,
  .email-value {
    color: #e4e4e4;
  }
  
  .input-hint,
  .otp-subtitle,
  .otp-instruction,
  .agreement-text,
  .switch-text {
    color: #a0a0a0;
  }
  
  .auth-switch {
    background: #3d3d3d;
  }
  
  .switch-link {
    background: #404040;
    color: #FF6B35;
    border-color: #FF6B35;
  }
  
  .security-note {
    background: linear-gradient(135deg, rgba(13, 110, 253, 0.1), rgba(13, 110, 253, 0.05));
  }
  
  .security-note span {
    color: #e4e4e4;
  }
}
</style>