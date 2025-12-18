<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const form = ref({ email: '', password: '' });
const errorMessage = ref('');
const successMessage = ref('');
const mobileMenuOpen = ref(false); // AJOUTÉ
const router = useRouter();
const authStore = useAuthStore();

// AJOUTÉ: Fonctions pour le menu mobile
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value;
};

const closeMobileMenu = () => {
  mobileMenuOpen.value = false;
};

const login = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (authStore.isLoading) return;

  try {
    const result = await authStore.login(form.value.email, form.value.password);

  if(result.success){
    successMessage.value = "Connexion réussie ! Redirection...";

    setTimeout(() => {
      router.push('/dashboard');
    }, 1500);
  }
  else
   {
    const msg = result.message || "Erreur de connexion";
    errorMessage.value = msg;
    
   }
  } catch (error) {
    // ✅ Cas spécial : email non vérifié
    if (error.type === 'unverified') {
      router.push({
        path: '/verify-email',
        query: { email: form.value.email }
      });
      return;
    }

    const msg = error.response?.data?.msg || "Erreur de connexion";
    errorMessage.value = msg;
  }
};
</script>

<template>
  <div class="login-page">
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
          <router-link to="/register" class="nav-link register-link">
            <i class="fas fa-user-plus"></i> S'inscrire
          </router-link>
        </nav>

        <!-- Menu Hamburger pour Mobile -->
        <button class="hamburger-btn" @click="toggleMobileMenu" aria-label="Menu mobile">
          <i class="fas fa-bars" v-if="!mobileMenuOpen">&#9776;</i>
          <i class="fas fa-times" v-else>X</i>
        </button>

        <!-- Menu Mobile -->
        <div class="mobile-menu" :class="{ 'active': mobileMenuOpen }" v-if="mobileMenuOpen">
          <router-link to="/register" class="mobile-nav-link" @click="closeMobileMenu">
            <i class="fas fa-user-plus"></i> S'inscrire
          </router-link>
        </div>
      </div>
    </header>

    <!-- ==================== SECTION PRINCIPALE ==================== -->
    <main class="main-content">
      <div class="login-section">
        <div class="section-container">
          <div class="login-grid">
            <!-- Colonne gauche : Message de bienvenue -->
            <div class="welcome-column">
              <div class="welcome-content">
                <div class="welcome-icon">
                  <i class="fas fa-sign-in-alt"></i>
                </div>
                <h1 class="welcome-title">
                  Re-bienvenue sur <span class="highlight">FreelanceCMR</span>
                </h1>
                <p class="welcome-subtitle">
                  Accédez à votre espace personnel et découvrez de nouvelles opportunités
                </p>
                
                <div class="features-list">
                  <div class="feature-item">
                    <i class="fas fa-bolt"></i>
                    <div class="feature-content">
                      <h4>Accès rapide</h4>
                      <p>Retrouvez tous vos projets en cours</p>
                    </div>
                  </div>
                  <div class="feature-item">
                    <i class="fas fa-chart-line"></i>
                    <div class="feature-content">
                      <h4>Suivi en temps réel</h4>
                      <p>Visualisez votre activité et vos revenus</p>
                    </div>
                  </div>
                  <div class="feature-item">
                    <i class="fas fa-bell"></i>
                    <div class="feature-content">
                      <h4>Notifications</h4>
                      <p>Soyez informé des nouvelles opportunités</p>
                    </div>
                  </div>
                </div>

                <div class="community-stats">
                  <div class="stat-item">
                    <i class="fas fa-users"></i>
                    <div class="stat-content">
                      <span class="stat-number">500+</span>
                      <span class="stat-label">Freelances actifs</span>
                    </div>
                  </div>
                  <div class="stat-item">
                    <i class="fas fa-briefcase"></i>
                    <div class="stat-content">
                      <span class="stat-number">1200+</span>
                      <span class="stat-label">Projets réalisés</span>
                    </div>
                  </div>
                </div>

                <div class="flag-badge">
                  <i class="fas fa-flag"></i>
                  <span>Connectez-vous à la communauté camerounaise</span>
                </div>
              </div>
            </div>

            <!-- Colonne droite : Formulaire de connexion -->
            <div class="form-column">
              <div class="login-card">
                <div class="card-header">
                  <h2 class="card-title">
                    <i class="fas fa-lock"></i>
                    Connexion à votre compte
                  </h2>
                  <p class="card-subtitle">
                    Entrez vos identifiants pour accéder à votre espace
                  </p>
                </div>

                <div class="card-content">
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

                  <!-- Formulaire de connexion -->
                  <form @submit.prevent="login" class="login-form">
                    <div class="form-group">
                      <label for="email">
                        <i class="fas fa-envelope"></i>
                        Adresse Email
                      </label>
                      <input
                        id="email"
                        v-model="form.email"
                        type="email"
                        placeholder="exemple@email.com"
                        required
                        class="form-input"
                        :disabled="authStore.isLoading"
                      />
                    </div>

                    <div class="form-group">
                      <label for="password">
                        <i class="fas fa-lock"></i>
                        Mot de passe
                      </label>
                      <input
                        id="password"
                        v-model="form.password"
                        type="password"
                        placeholder="••••••••"
                        required
                        class="form-input"
                        :disabled="authStore.isLoading"
                      />
                      <div class="password-actions">
                        <router-link to="/forgot-password" class="forgot-link">
                          <i class="fas fa-key"></i>
                          Mot de passe oublié ?
                        </router-link>
                      </div>
                    </div>

                    <button 
                      type="submit" 
                      class="submit-btn" 
                      :disabled="authStore.isLoading"
                      :class="{ 'loading': authStore.isLoading }"
                    >
                      <span v-if="authStore.isLoading">
                        <i class="fas fa-spinner fa-spin"></i>
                        Connexion en cours...
                      </span>
                      <span v-else>
                        <i class="fas fa-sign-in-alt"></i>
                        Se connecter
                      </span>
                    </button>

                    <div class="divider">
                      <span>Ou connectez-vous avec</span>
                    </div>

                    <div class="social-login">
                      <button type="button" class="social-btn google">
                        <i class="fab fa-google"></i>
                        <span>Google</span>
                      </button>
                      <button type="button" class="social-btn facebook">
                        <i class="fab fa-facebook-f"></i>
                        <span>Facebook</span>
                      </button>
                    </div>

                    <div class="form-footer">
                      <p class="register-text">
                        Pas encore de compte ?
                        <router-link to="/register" class="register-link">
                          <i class="fas fa-user-plus"></i>
                          Créer un compte gratuit
                        </router-link>
                      </p>
                    </div>
                  </form>
                </div>

                <div class="security-notice">
                  <i class="fas fa-shield-alt"></i>
                  <span>
                    Votre connexion est sécurisée avec un chiffrement SSL 256-bit.
                    Vos données sont protégées conformément à notre politique de confidentialité.
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- ==================== FOOTER (identique à home) ==================== -->
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
            <li><router-link to="/login">Connexion</router-link></li>
            <li><router-link to="/register">Inscription</router-link></li>
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

<style scoped>
/* ==================== STYLES GÉNÉRAUX ==================== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-page {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

/* ==================== HEADER STYLES (identique à home) ==================== */
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

.register-link {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border: 2px solid #FF6B35;
}

.register-link:hover {
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

/* ==================== SECTION CONNEXION ==================== */
.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.login-section {
  width: 100%;
  max-width: 1200px;
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Grille de connexion */
.login-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

@media (max-width: 1024px) {
  .login-grid {
    grid-template-columns: 1fr;
    gap: 40px;
  }
}

/* Colonne de bienvenue */
.welcome-column {
  padding-right: 40px;
}

@media (max-width: 1024px) {
  .welcome-column {
    padding-right: 0;
    text-align: center;
  }
}

.welcome-content {
  animation: fadeInLeft 0.6s ease;
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.welcome-icon {
  font-size: 4rem;
  color: #FF6B35;
  margin-bottom: 25px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.welcome-title {
  font-size: 2.5rem;
  color: #2D3047;
  margin-bottom: 15px;
  font-weight: 700;
  line-height: 1.2;
}

.highlight {
  color: #FF6B35;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  font-size: 1.2rem;
  color: #6c757d;
  margin-bottom: 40px;
  line-height: 1.6;
}

/* Liste des fonctionnalités */
.features-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
  margin-bottom: 40px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.feature-item i {
  font-size: 1.8rem;
  color: #FF6B35;
  background: rgba(255, 107, 53, 0.1);
  width: 60px;
  height: 60px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-content h4 {
  font-size: 1.2rem;
  color: #2D3047;
  margin-bottom: 5px;
  font-weight: 600;
}

.feature-content p {
  color: #6c757d;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Statistiques communauté */
.community-stats {
  display: flex;
  gap: 30px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-item i {
  font-size: 2rem;
  color: #FF6B35;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2D3047;
  line-height: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: #6c757d;
  margin-top: 5px;
}

/* Badge drapeau */
.flag-badge {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(255, 142, 83, 0.05));
  color: #2D3047;
  padding: 15px 25px;
  border-radius: 50px;
  font-weight: 500;
  border: 2px solid rgba(255, 107, 53, 0.2);
}

.flag-badge i {
  color: #FF6B35;
  font-size: 1.2rem;
  animation: flagWave 3s infinite;
}

@keyframes flagWave {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-5deg); }
  75% { transform: rotate(5deg); }
}

/* Colonne formulaire */
.form-column {
  animation: fadeInRight 0.6s ease;
}

@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Carte de connexion */
.login-card {
  background: white;
  border-radius: 25px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border: 1px solid #f0f0f0;
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

.card-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  line-height: 1.2;
}

.card-title i {
  font-size: 2rem;
  color: #FF6B35;
}

.card-subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

/* Contenu de la carte */
.card-content {
  padding: 40px;
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
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
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

/* Formulaire de connexion */
.login-form {
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

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-input::placeholder {
  color: #adb5bd;
}

.password-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.forgot-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #FF6B35;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.forgot-link:hover {
  gap: 12px;
}

.forgot-link i {
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

/* Diviseur */
.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 20px 0;
  color: #6c757d;
  font-size: 0.95rem;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e9ecef;
}

.divider span {
  padding: 0 20px;
}

/* Connexion sociale */
.social-login {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.social-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 18px;
  border-radius: 15px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid #e9ecef;
  background: white;
  color: #2D3047;
}

.social-btn.google:hover {
  background: #4285F4;
  border-color: #4285F4;
  color: white;
}

.social-btn.facebook:hover {
  background: #3b5998;
  border-color: #3b5998;
  color: white;
}

.social-btn i {
  font-size: 1.2rem;
}

/* Pied de formulaire */
.form-footer {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.register-text {
  font-size: 1rem;
  color: #6c757d;
  text-align: center;
  line-height: 1.6;
}

.register-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #FF6B35;
  text-decoration: none;
  font-weight: 600;
  margin-top: 10px;
  padding: 10px 20px;
  border-radius: 25px;
  background: rgba(255, 107, 53, 0.1);
  transition: all 0.3s ease;
}

.register-link:hover {
  background: #FF6B35;
  color: white;
  transform: translateY(-2px);
  gap: 12px;
}

.register-link i {
  font-size: 0.9rem;
}

/* Note de sécurité */
.security-notice {
  background: linear-gradient(135deg, rgba(13, 110, 253, 0.05), rgba(13, 110, 253, 0.02));
  border-radius: 15px;
  padding: 20px;
  margin: 0 40px 40px;
  border-left: 4px solid #0d6efd;
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.security-notice i {
  color: #0d6efd;
  font-size: 1.5rem;
  margin-top: 2px;
}

.security-notice span {
  color: #2D3047;
  font-size: 0.9rem;
  line-height: 1.6;
}

/* ==================== FOOTER STYLES (identique à home) ==================== */
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
  .login-grid {
    grid-template-columns: 1fr;
    gap: 40px;
  }
  
  .welcome-column {
    padding-right: 0;
    text-align: center;
  }
  
  .feature-item {
    justify-content: center;
  }
  
  .community-stats {
    justify-content: center;
  }
  
  .footer-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 50px 30px;
  }
  
  .welcome-title {
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
  
  /* Section connexion */
  .main-content {
    padding: 30px 20px;
  }
  
  .welcome-title {
    font-size: 1.8rem;
  }
  
  .welcome-subtitle {
    font-size: 1rem;
  }
  
  .welcome-icon {
    font-size: 3rem;
  }
  
  .feature-item {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 15px;
  }
  
  .stat-item {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
  
  /* Carte de connexion */
  .card-header {
    padding: 30px 20px;
  }
  
  .card-content {
    padding: 30px 20px;
  }
  
  .card-title {
    font-size: 1.5rem;
    flex-direction: column;
    gap: 10px;
  }
  
  .card-subtitle {
    font-size: 1rem;
  }
  
  /* Formulaire */
  .form-input {
    padding: 16px;
  }
  
  /* Boutons */
  .submit-btn {
    padding: 18px;
    font-size: 1.1rem;
  }
  
  .social-login {
    flex-direction: column;
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
  
  .security-notice {
    margin: 0 20px 30px;
    padding: 15px;
  }
}

/* Téléphones petits */
@media (max-width: 480px) {
  .header-container,
  .section-container,
  .footer-container {
    padding: 0 15px;
  }
  
  .welcome-title {
    font-size: 1.6rem;
  }
  
  .card-header {
    padding: 25px 15px;
  }
  
  .card-content {
    padding: 25px 15px;
  }
  
  .card-title {
    font-size: 1.3rem;
  }
  
  .form-input {
    padding: 14px;
  }
  
  /* Boutons */
  .submit-btn,
  .social-btn {
    padding: 16px;
    font-size: 1rem;
  }
  
  /* Alertes */
  .alert {
    padding: 15px;
    font-size: 0.95rem;
  }
  
  .register-link {
    padding: 8px 16px;
    font-size: 0.95rem;
  }
  
  .security-notice {
    margin: 0 15px 25px;
    padding: 15px;
  }
  
  .security-notice span {
    font-size: 0.85rem;
  }
  
  .flag-badge {
    padding: 12px 20px;
    font-size: 0.9rem;
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
  .social-btn:hover,
  .register-link:hover,
  .forgot-link:hover,
  .social-link:hover,
  .footer-links a:hover {
    transform: none;
  }
  
  .submit-btn:active,
  .social-btn:active {
    transform: scale(0.98);
  }
  
  .nav-link:hover,
  .mobile-nav-link:hover {
    transform: none;
  }
}

/* Support pour les modes sombre */
@media (prefers-color-scheme: dark) {
  .login-page {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  }
  
  .login-card {
    background: #2d2d2d;
    border-color: #404040;
  }
  
  .card-header {
    background: linear-gradient(135deg, #1A1C2E 0%, #0d0f1a 100%);
  }
  
  .welcome-title,
  .feature-content h4,
  .stat-number {
    color: #e4e4e4;
  }
  
  .welcome-subtitle,
  .feature-content p,
  .stat-label {
    color: #a0a0a0;
  }
  
  .form-input {
    background: #3d3d3d;
    border-color: #505050;
    color: #e4e4e4;
  }
  
  .form-input:focus {
    background: #404040;
    border-color: #FF6B35;
  }
  
  .form-group label {
    color: #e4e4e4;
  }
  
  .security-notice {
    background: linear-gradient(135deg, rgba(13, 110, 253, 0.1), rgba(13, 110, 253, 0.05));
  }
  
  .security-notice span {
    color: #e4e4e4;
  }
  
  .social-btn {
    background: #3d3d3d;
    border-color: #505050;
    color: #e4e4e4;
  }
  
  .flag-badge {
    background: linear-gradient(135deg, rgba(255, 107, 53, 0.2), rgba(255, 142, 83, 0.1));
    border-color: rgba(255, 107, 53, 0.3);
    color: #e4e4e4;
  }
}
</style>