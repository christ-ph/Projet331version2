<template>
  <div class="home-page">
    
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
          <router-link to="/register" class="mobile-nav-link" @click="closeMobileMenu">
            <i class="fas fa-user-plus"></i> S'inscrire
          </router-link>
          <router-link to="/login" class="mobile-nav-link" @click="closeMobileMenu">
            <i class="fas fa-sign-in-alt"></i> Se connecter
          </router-link>
        </div>
      </div>
    </header>

    <!-- ==================== SECTION ACCUEIL ==================== -->
    <section class="hero-section">
      <!-- Background Slideshow -->
      <div class="slideshow">
        <div class="slide" :class="{ 'active': currentSlide === 0 }" 
             style="background-image: url('../../public/touriste.jpg');"></div>
        <div class="slide" :class="{ 'active': currentSlide === 1 }" 
             style="background-image: url('../../public/palais.avif');"></div>
        <div class="slide" :class="{ 'active': currentSlide === 2 }" 
             style="background-image: url('../../public/reunification.avif');"></div>
        <div class="slide" :class="{ 'active': currentSlide === 3 }" 
             style="background-image: url('../../public/jaime.jpg');"></div>
        
        <!-- Overlay sombre pour meilleure lisibilité -->
        <div class="slideshow-overlay"></div>
        
        <!-- Indicateurs de slides -->
        <div class="slide-indicators">
          <span v-for="i in 4" :key="i" 
                :class="{ 'active': currentSlide === i-1 }" 
                @click="goToSlide(i-1)"
                :aria-label="`Aller au slide ${i}`"
                role="button"
                tabindex="0"
                @keyup.enter="goToSlide(i-1)"></span>
        </div>
      </div>

      <!-- Contenu principal de la section hero -->
      <div class="hero-content">
        <!-- Titre principal -->
        <h1 class="hero-title">
          <span class="title-line">Plateforme N°1 des</span>
          <span class="title-line highlight">Freelances Camerounais</span>
        </h1>

        <!-- Message dynamique pour les Camerounais -->
        <div class="dynamic-message-container">
          <p class="dynamic-message">{{ dynamicMessages[currentMessageIndex] }}</p>
          <div class="flag-container">
            <i class="fas fa-flag flag-icon"></i>
            <span class="flag-text">Made in Cameroon</span>
          </div>
        </div>

        <!-- Bouton d'action principal -->
        <router-link to="/register" class="cta-button">
          <span>Commencer maintenant</span>
        </router-link>
      </div>
    </section>

    <!-- ==================== SECTION POURQUOI FREELANCECMR ==================== -->
    <section class="why-section">
      <div class="section-container">
        <!-- Titre de la section -->
        <div class="section-header">
          <h2 class="section-titles">
            Pourquoi choisir <span class="highlight-title">FreelanceCMR</span> ?
          </h2>
          <p class="section-subtitle">
            La plateforme conçue spécifiquement pour l'écosystème entrepreneurial camerounais
          </p>
        </div>

        <!-- Grille des raisons -->
        <div class="reasons-grid">
          <!-- Raison 1 -->
          <div class="reason-card" @mouseenter="hoverCard(0)" @mouseleave="resetCard(0)" 
               :style="{ transform: cardHover === 0 ? 'translateY(-10px)' : 'translateY(0)' }"
               @touchstart="hoverCard(0)"
               @touchend="resetCard()">
            <div class="reason-icon-wrapper">
              <div class="reason-icon">
                <i class="fas fa-globe-africa"></i>
              </div>
              <div class="icon-bg-animation"></div>
            </div>
            <h3 class="reason-title">100% Camerounais</h3>
            <p class="reason-description">
              Une plateforme créée par des Camerounais pour les Camerounais. 
              Nous comprenons les défis et opportunités du marché local.
            </p>
            <div class="reason-tag">
              <i class="fas fa-map-marker-alt"></i>
              <span>Adapté au contexte local</span>
            </div>
          </div>

          <!-- Raison 2 -->
          <div class="reason-card" @mouseenter="hoverCard(1)" @mouseleave="resetCard(1)"
               :style="{ transform: cardHover === 1 ? 'translateY(-10px)' : 'translateY(0)' }"
               @touchstart="hoverCard(1)"
               @touchend="resetCard()">
            <div class="reason-icon-wrapper">
              <div class="reason-icon">
                <i class="fas fa-money-bill-wave"></i>
              </div>
              <div class="icon-bg-animation"></div>
            </div>
            <h3 class="reason-title">Paiements en FCFA</h3>
            <p class="reason-description">
              Évitez les frais de change et recevez vos paiements directement 
              en Francs CFA via Mobile Money, virement bancaire ou espèces.
            </p>
            <div class="reason-tag">
              <i class="fas fa-shield-alt"></i>
              <span>Sécurisé & Rapide</span>
            </div>
          </div>

          <!-- Raison 3 -->
          <div class="reason-card" @mouseenter="hoverCard(2)" @mouseleave="resetCard(2)"
               :style="{ transform: cardHover === 2 ? 'translateY(-10px)' : 'translateY(0)' }"
               @touchstart="hoverCard(2)"
               @touchend="resetCard()">
            <div class="reason-icon-wrapper">
              <div class="reason-icon">
                <i class="fas fa-users"></i>
              </div>
              <div class="icon-bg-animation"></div>
            </div>
            <h3 class="reason-title">Communauté Active</h3>
            <p class="reason-description">
              Rejoignez une communauté grandissante de freelances et clients 
              camerounais. Échangez, collaborez et développez votre réseau.
            </p>
            <div class="reason-tag">
              <i class="fas fa-comments"></i>
              <span>Support en français</span>
            </div>
          </div>

          <!-- Raison 4 -->
          <div class="reason-card" @mouseenter="hoverCard(3)" @mouseleave="resetCard(3)"
               :style="{ transform: cardHover === 3 ? 'translateY(-10px)' : 'translateY(0)' }"
               @touchstart="hoverCard(3)"
               @touchend="resetCard()">
            <div class="reason-icon-wrapper">
              <div class="reason-icon">
                <i class="fas fa-bolt"></i>
              </div>
              <div class="icon-bg-animation"></div>
            </div>
            <h3 class="reason-title">Rapidité & Efficacité</h3>
            <p class="reason-description">
              Trouvez des freelances ou des projets en quelques minutes. 
              Notre interface est optimisée pour une expérience fluide.
            </p>
            <div class="reason-tag">
              <i class="fas fa-rocket"></i>
              <span>Lancement rapide</span>
            </div>
          </div>

          <!-- Raison 5 -->
          <div class="reason-card" @mouseenter="hoverCard(4)" @mouseleave="resetCard(4)"
               :style="{ transform: cardHover === 4 ? 'translateY(-10px)' : 'translateY(0)' }"
               @touchstart="hoverCard(4)"
               @touchend="resetCard()">
            <div class="reason-icon-wrapper">
              <div class="reason-icon">
                <i class="fas fa-chart-line"></i>
              </div>
              <div class="icon-bg-animation"></div>
            </div>
            <h3 class="reason-title">Croissance Garantie</h3>
            <p class="reason-description">
              Accédez à des outils et ressources pour développer vos compétences 
              et augmenter vos revenus sur le marché camerounais.
            </p>
            <div class="reason-tag">
              <i class="fas fa-graduation-cap"></i>
              <span>Formations gratuites</span>
            </div>
          </div>

          <!-- Raison 6 -->
          <div class="reason-card" @mouseenter="hoverCard(5)" @mouseleave="resetCard(5)"
               :style="{ transform: cardHover === 5 ? 'translateY(-10px)' : 'translateY(0)' }"
               @touchstart="hoverCard(5)"
               @touchend="resetCard()">
            <div class="reason-icon-wrapper">
              <div class="reason-icon">
                <i class="fas fa-handshake"></i>
              </div>
              <div class="icon-bg-animation"></div>
            </div>
            <h3 class="reason-title">Confiance & Fiabilité</h3>
            <p class="reason-description">
              Système de notation et d'avis transparent. Travaillez avec 
              des professionnels vérifiés et fiables.
            </p>
            <div class="reason-tag">
              <i class="fas fa-star"></i>
              <span>Profils vérifiés</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SECTION AVANTAGES POUR VISITEURS ==================== -->
    <section class="benefits-section">
      <div class="section-container">
        <div class="section-header">
          <h2 class="section-title">
            Avantages pour <span class="highlight-title">vos business</span>
          </h2>
          <p class="section-subtitle">
            Découvrez comment FreelanceCMR transforme l'entrepreneuriat au Cameroun
          </p>
        </div>

        <!-- Grille des avantages -->
        <div class="benefits-grid">
          <div class="benefit-card">
            <div class="benefit-icon">
              <i class="fas fa-money-bill-wave"></i>
            </div>
            <div class="benefit-content">
              <h3 class="benefit-title">Gagnez en FCFA</h3>
              <p class="benefit-desc">Recevez vos paiements directement en FCFA sans frais de conversion</p>
            </div>
          </div>

          <div class="benefit-card">
            <div class="benefit-icon">
              <i class="fas fa-users"></i>
            </div>
            <div class="benefit-content">
              <h3 class="benefit-title">Réseau local</h3>
              <p class="benefit-desc">Connectez-vous avec des clients et freelances de tout le Cameroun</p>
            </div>
          </div>

          <div class="benefit-card">
            <div class="benefit-icon">
              <i class="fas fa-bolt"></i>
            </div>
            <div class="benefit-content">
              <h3 class="benefit-title">Transactions rapides</h3>
              <p class="benefit-desc">Paiements instantanés via Mobile Money et autres moyens locaux</p>
            </div>
          </div>
        </div>

        <!-- Bouton CTA secondaire -->
        <div class="benefits-cta">
          <router-link to="/register" class="secondary-cta-button">
            <span>Rejoindre gratuitement</span>
          </router-link>
          <router-link to="/apropos" class="outline-cta-button">
            <span>Voir la démo</span>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ==================== SECTION COMMENT ÇA MARCHE ==================== -->
    <section class="how-it-works-section">
      <div class="section-container">
        <!-- En-tête de la section -->
        <div class="section-header">
          <h2 class="section-title">Comment ça marche ?</h2>
          <p class="section-subtitle">Rejoignez notre communauté en quelques étapes simples</p>
        </div>

        <!-- Navigation Client/Freelance -->
        <div class="role-navigation">
          <button class="role-btn" 
                  :class="{ 'active': activeRole === 'client' }" 
                  @click="setActiveRole('client')"
                  :aria-pressed="activeRole === 'client'">
            <i class="fas fa-briefcase"></i>
            <span>Je suis Client</span>
          </button>
          
          <button class="role-btn" 
                  :class="{ 'active': activeRole === 'freelance' }" 
                  @click="setActiveRole('freelance')"
                  :aria-pressed="activeRole === 'freelance'">
            <i class="fas fa-code"></i>
            <span>Je suis Freelance</span>
          </button>
        </div>

        <!-- Contenu pour Client -->
        <div class="process-content" v-if="activeRole === 'client'">
          <div class="process-steps">
            <div class="process-step">
              <div class="step-number">1</div>
              <div class="step-content">
                <h3 class="step-title">Créez votre compte</h3>
                <p class="step-description">Inscrivez-vous gratuitement en tant que client et complétez votre profil</p>
              </div>
            </div>

            <div class="process-step">
              <div class="step-number">2</div>
              <div class="step-content">
                <h3 class="step-title">Publiez votre projet</h3>
                <p class="step-description">Décrivez vos besoins et fixez un budget en FCFA</p>
              </div>
            </div>

            <div class="process-step">
              <div class="step-number">3</div>
              <div class="step-content">
                <h3 class="step-title">Choisissez un freelance</h3>
                <p class="step-description">Recevez des propositions et sélectionnez le meilleur profil</p>
              </div>
            </div>

            <div class="process-step">
              <div class="step-number">4</div>
              <div class="step-content">
                <h3 class="step-title">Collaborez et payez</h3>
                <p class="step-description">Suivez l'avancement et payez en toute sécurité</p>
              </div>
            </div>
          </div>

          <router-link to="/register?role=client" class="launch-btn">
            <i class="fas fa-rocket"></i>
            <span>Trouver un freelance</span>
          </router-link>
        </div>

        <!-- Contenu pour Freelance -->
        <div class="process-content" v-else>
          <div class="process-steps">
            <div class="process-step">
              <div class="step-number">1</div>
              <div class="step-content">
                <h3 class="step-title">Inscrivez-vous gratuitement</h3>
                <p class="step-description">Créez votre compte et remplissez votre profil professionnel</p>
              </div>
            </div>

            <div class="process-step">
              <div class="step-number">2</div>
              <div class="step-content">
                <h3 class="step-title">Montrez vos compétences</h3>
                <p class="step-description">Ajoutez vos réalisations, certifications et spécialités</p>
              </div>
            </div>

            <div class="process-step">
              <div class="step-number">3</div>
              <div class="step-content">
                <h3 class="step-title">Trouvez des projets</h3>
                <p class="step-description">Parcourez les projets et soumettez vos propositions</p>
              </div>
            </div>

            <div class="process-step">
              <div class="step-number">4</div>
              <div class="step-content">
                <h3 class="step-title">Travaillez et gagnez</h3>
                <p class="step-description">Réalisez les missions et recevez vos paiements en FCFA</p>
              </div>
            </div>
          </div>

          <router-link to="/register?role=freelance" class="launch-btn">
            <i class="fas fa-rocket"></i>
            <span>Devenir freelance</span>
          </router-link>
        </div>
      </div>
    </section>

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
            <!-- <li><router-link to="/apropos">À propos</router-link></li>
            <li><router-link to="/freelances">Freelances</router-link></li>
            <li><router-link to="/projets">Projets</router-link></li>
            <li><router-link to="/contact">Contact</router-link></li> -->
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

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// ==================== ÉTATS RÉACTIFS ====================
const mobileMenuOpen = ref(false)
const currentSlide = ref(0)
const currentMessageIndex = ref(0)
const activeRole = ref('client')
const cardHover = ref(-1)

// ==================== DONNÉES ====================
const dynamicMessages = ref([
  "Vous êtes au bon endroit pour développer votre business au Cameroun !",
  "Boostez votre carrière freelance dans l'écosystème numérique camerounais",
  "Trouvez les meilleurs talents locaux pour vos projets professionnels",
  "Gagnez en FCFA avec des clients camerounais et internationaux",
  "Rejoignez la première communauté de freelances 100% camerounaise"
])

// ==================== MÉTHODES ====================
// Gestion du menu mobile
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

// Navigation des slides
const goToSlide = (index) => {
  currentSlide.value = index
}

// Changer de rôle (client/freelance)
const setActiveRole = (role) => {
  activeRole.value = role
}

// Gestion du hover sur les cartes
const hoverCard = (index) => {
  cardHover.value = index
}

const resetCard = () => {
  cardHover.value = -1
}

// ==================== LIFECYCLE HOOKS ====================
onMounted(() => {
  // Intervalle pour le slideshow (30 secondes)
  const slideInterval = setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % 4
  }, 30000)

  // Intervalle pour les messages dynamiques (10 secondes)
  const messageInterval = setInterval(() => {
    currentMessageIndex.value = (currentMessageIndex.value + 1) % dynamicMessages.value.length
  }, 10000)

  // Nettoyage des intervals à la destruction du composant
  onUnmounted(() => {
    clearInterval(slideInterval)
    clearInterval(messageInterval)
  })
})
</script>

<style scoped>
/* ==================== STYLES GÉNÉRAUX ==================== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.home-page {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
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

.register-link {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border: 2px solid #FF6B35;
}

.register-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 107, 53, 0.3);
}

.login-link {
  background: transparent;
  color: #2D3047;
  border: 2px solid #2D3047;
}

.login-link:hover {
  background: #2D3047;
  color: white;
  transform: translateY(-2px);
}

/* Bouton Hamburger (Mobile) */
.hamburger-btn {
  display: none;
  background-color:white;
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

/* ==================== SECTION HERO STYLES ==================== */
.hero-section {
  height: 90vh;
  min-height: 600px;
  max-height: 900px;
  position: relative;
  overflow: hidden;
}

/* Slideshow */
.slideshow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 0;
  transition: opacity 1s ease-in-out;
  z-index: 1;
}

.slide.active {
  opacity: 1;
  z-index: 2;
}

.slideshow-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(45, 48, 71, 0.8), rgba(255, 107, 53, 0.4));
  z-index: 3;
}

.slide-indicators {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  z-index: 4;
}

.slide-indicators span {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s ease;
}

.slide-indicators span.active {
  background: #FF6B35;
  transform: scale(1.2);
}

.slide-indicators span:hover {
  background: #FF8E53;
}

/* Contenu Hero */
.hero-content {
  position: relative;
  z-index: 4;
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: white;
}

/* Titre Hero */
.hero-title {
  font-size: 3.5rem;
  margin-bottom: 30px;
  line-height: 1.2;
}

.title-line {
  display: block;
}

.highlight {
  color: #FFD166;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  position: relative;
  display: inline-block;
}

.highlight::after {
  content: '';
  position: absolute;
  bottom: 5px;
  left: 0;
  width: 100%;
  height: 10px;
  background: rgba(255, 209, 102, 0.3);
  z-index: -1;
  border-radius: 5px;
}

/* Message dynamique */
.dynamic-message-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 40px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  max-width: 800px;
}

.dynamic-message {
  font-size: 1.4rem;
  margin-bottom: 15px;
  font-weight: 500;
  line-height: 1.6;
  animation: fadeIn 1s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.flag-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.flag-icon {
  color: #009A49;
  font-size: 1.2rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.flag-text {
  font-weight: 600;
  color: #FFD166;
}

/* Bouton CTA */
.cta-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  text-decoration: none;
  padding: 20px 40px;
  border-radius: 50px;
  font-size: 1.3rem;
  font-weight: 700;
  transition: all 0.3s ease;
  margin-bottom: 60px;
  max-width: 350px;
  box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.2);
  text-align: center;
}

.cta-button:hover {
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 15px 40px rgba(255, 107, 53, 0.5);
}

/* ==================== SECTION POURQUOI FREELANCECMR STYLES ==================== */
.why-section {
  padding: 100px 0;
  background: linear-gradient(135deg, #2d2e2e 0%, #201d1d 100%);
  position: relative;
  overflow: hidden;
}

.why-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23FF6B35' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
  opacity: 0.3;
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

/* En-tête de section */
.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-title {
  font-size: 3rem;
  color: #e4e4e4;
  margin-bottom: 15px;
  font-weight: 700;
  line-height: 1.2;
}

.section-titles {
  font-size: 3rem;
  color: #ffffff;
  margin-bottom: 15px;
  font-weight: 700;
  line-height: 1.2;
}

.highlight-title {
  color: #FF6B35;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
}

.highlight-title::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  border-radius: 2px;
}

.section-subtitle {
  font-size: 1.3rem;
  color: #6c757d;
  max-width: 700px;
  margin: 0 auto;
  line-height: 1.6;
}

/* Grille des raisons */
.reasons-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  margin-bottom: 80px;
}

.reason-card {
  background: white;
  border-radius: 20px;
  padding: 40px 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 1px solid #f0f0f0;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.reason-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease;
}

.reason-card:hover::before {
  transform: scaleX(1);
}

.reason-card:hover {
  box-shadow: 0 20px 60px rgba(255, 107, 53, 0.15);
}

.reason-icon-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  margin-bottom: 25px;
}

.reason-icon {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  color: white;
  position: relative;
  z-index: 2;
  transition: transform 0.3s ease;
}

.reason-card:hover .reason-icon {
  transform: rotate(10deg) scale(1.1);
}

.icon-bg-animation {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255, 107, 53, 0.2), rgba(255, 142, 83, 0.2));
  border-radius: 20px;
  animation: pulseBackground 2s infinite;
}

@keyframes pulseBackground {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.05); }
}

.reason-title {
  font-size: 1.5rem;
  color: #2D3047;
  margin-bottom: 15px;
  font-weight: 600;
  line-height: 1.3;
}

.reason-description {
  color: #6c757d;
  line-height: 1.6;
  margin-bottom: 20px;
  font-size: 1rem;
}

.reason-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 107, 53, 0.1);
  color: #FF6B35;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.reason-tag i {
  font-size: 0.8rem;
}

/* ==================== SECTION AVANTAGES STYLES ==================== */
.benefits-section {
  padding: 100px 0;
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
}

.benefits-section .section-title {
  color: white;
}

.benefits-section .section-subtitle {
  color: rgba(255, 255, 255, 0.8);
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
  margin: 60px 0;
}

.benefit-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px 30px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 25px;
}

.benefit-card:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-10px);
  border-color: #FF6B35;
}

.benefit-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  color: white;
  flex-shrink: 0;
}

.benefit-content {
  flex: 1;
}

.benefit-title {
  font-size: 1.5rem;
  margin-bottom: 10px;
  color: white;
  line-height: 1.3;
}

.benefit-desc {
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  font-size: 1rem;
}

.benefits-cta {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 50px;
  flex-wrap: wrap;
}

.secondary-cta-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  text-decoration: none;
  padding: 18px 40px;
  border-radius: 50px;
  font-size: 1.2rem;
  font-weight: 600;
  transition: all 0.3s ease;
  text-align: center;
  min-width: 200px;
}

.secondary-cta-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(255, 107, 53, 0.4);
}

.outline-cta-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: transparent;
  color: white;
  text-decoration: none;
  padding: 18px 40px;
  border-radius: 50px;
  font-size: 1.2rem;
  font-weight: 600;
  border: 2px solid white;
  transition: all 0.3s ease;
  text-align: center;
  min-width: 200px;
}

.outline-cta-button:hover {
  background: white;
  color: #2D3047;
  transform: translateY(-3px);
}

/* ==================== SECTION COMMENT ÇA MARCHE STYLES ==================== */
.how-it-works-section {
  background: linear-gradient(135deg, #11041f 0%, #050e1d 100%);
  padding: 100px 0;
  position: relative;
  overflow: hidden;
}

.how-it-works-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><path fill="rgba(255,255,255,0.05)" d="M0,0L1000,0L1000,1000L0,1000Z"/></svg>');
  background-size: cover;
  opacity: 0.1;
}

/* Navigation des rôles */
.role-navigation {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 60px;
  flex-wrap: wrap;
}

.role-btn {
  padding: 20px 40px;
  border: none;
  border-radius: 50px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  min-width: 200px;
  text-align: center;
}

.role-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-3px);
}

.role-btn.active {
  background: white;
  color: #6A11CB;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.role-btn.active:hover {
  background: #f8f9fa;
}

.role-btn i {
  font-size: 1.5rem;
}

/* Contenu du processus */
.process-content {
  background: white;
  border-radius: 25px;
  padding: 60px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
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

.process-steps {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 40px;
  margin-bottom: 50px;
}

.process-step {
  display: flex;
  gap: 25px;
  align-items: flex-start;
}

.step-number {
  background: linear-gradient(135deg, #6A11CB, #2575FC);
  color: white;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 5px 15px rgba(106, 17, 203, 0.3);
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 1.4rem;
  color: #2D3047;
  margin-bottom: 10px;
  font-weight: 600;
  line-height: 1.3;
}

.step-description {
  color: #6c757d;
  line-height: 1.6;
}

/* Bouton "Je me lance" */
.launch-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  text-decoration: none;
  padding: 20px 50px;
  border-radius: 50px;
  font-size: 1.3rem;
  font-weight: 700;
  transition: all 0.3s ease;
  margin: 0 auto;
  width: fit-content;
  box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
  text-align: center;
}

.launch-btn:hover {
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 15px 40px rgba(255, 107, 53, 0.5);
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

/* ==================== RESPONSIVE DESIGN AMÉLIORÉ ==================== */

/* Tablette en mode paysage et petits ordinateurs portables */
@media (max-width: 1200px) {
  .header-container,
  .section-container,
  .footer-container {
    padding: 0 30px;
  }
  
  .hero-title {
    font-size: 3rem;
  }
  
  .section-title,
  .section-titles {
    font-size: 2.5rem;
  }
}

/* Tablette en mode portrait */
@media (max-width: 1024px) {
  .hero-title {
    font-size: 2.8rem;
  }
  
  .reasons-grid,
  .benefits-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 30px;
  }
  
  .process-steps {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  
  .footer-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 50px 30px;
  }
  
  .dynamic-message {
    font-size: 1.2rem;
  }
  
  .section-subtitle {
    font-size: 1.1rem;
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
  
  /* Hero Section Responsive */
  .hero-section {
    height: 85vh;
    min-height: 500px;
  }
  
  .hero-content {
    padding: 60px 20px;
    justify-content: flex-end;
    padding-bottom: 80px;
  }
  
  .hero-title {
    font-size: 2.2rem;
    margin-bottom: 20px;
  }
  
  .dynamic-message-container {
    padding: 20px;
    margin-bottom: 30px;
  }
  
  .dynamic-message {
    font-size: 1.1rem;
    margin-bottom: 10px;
  }
  
  .cta-button {
    padding: 16px 30px;
    font-size: 1.1rem;
    max-width: 100%;
    margin-bottom: 40px;
  }
  
  .slide-indicators {
    bottom: 20px;
  }
  
  /* Sections Responsive */
  .why-section,
  .benefits-section,
  .how-it-works-section {
    padding: 70px 0;
  }
  
  .reasons-grid,
  .benefits-grid {
    grid-template-columns: 1fr;
    gap: 25px;
    margin-bottom: 50px;
  }
  
  .section-header {
    margin-bottom: 40px;
  }
  
  .section-title,
  .section-titles {
    font-size: 2rem;
    margin-bottom: 10px;
  }
  
  .section-subtitle {
    font-size: 1rem;
    padding: 0 10px;
  }
  
  .reason-card,
  .benefit-card {
    padding: 30px 25px;
  }
  
  .reason-icon-wrapper {
    width: 70px;
    height: 70px;
    margin-bottom: 20px;
  }
  
  .reason-icon {
    font-size: 2rem;
  }
  
  .reason-title,
  .benefit-title {
    font-size: 1.3rem;
  }
  
  .reason-description,
  .benefit-desc {
    font-size: 0.95rem;
  }
  
  /* Comment ça marche Responsive */
  .role-navigation {
    flex-direction: column;
    align-items: center;
    gap: 15px;
    margin-bottom: 40px;
  }
  
  .role-btn {
    width: 100%;
    max-width: 300px;
    padding: 18px 30px;
    font-size: 1.1rem;
  }
  
  .process-content {
    padding: 35px 25px;
  }
  
  .process-step {
    gap: 20px;
  }
  
  .step-number {
    width: 45px;
    height: 45px;
    font-size: 1.3rem;
  }
  
  .step-title {
    font-size: 1.2rem;
  }
  
  .step-description {
    font-size: 0.95rem;
  }
  
  .launch-btn {
    padding: 18px 40px;
    font-size: 1.1rem;
    width: 100%;
    max-width: 300px;
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
  
  .benefits-cta {
    flex-direction: column;
    align-items: center;
    gap: 15px;
  }
  
  .secondary-cta-button,
  .outline-cta-button {
    width: 100%;
    max-width: 300px;
    padding: 16px 30px;
    font-size: 1.1rem;
  }
}

/* Téléphones petits */
@media (max-width: 480px) {
  .header-container,
  .section-container,
  .footer-container {
    padding: 0 20px;
  }
  
  .hero-section {
    height: 80vh;
    min-height: 450px;
  }
  
  .hero-title {
    font-size: 1.8rem;
  }
  
  .title-line {
    display: inline;
  }
  
  .title-line:first-child::after {
    content: " ";
  }
  
  .dynamic-message {
    font-size: 1rem;
  }
  
  .flag-text {
    font-size: 0.9rem;
  }
  
  .cta-button {
    padding: 14px 25px;
    font-size: 1rem;
  }
  
  .section-title,
  .section-titles {
    font-size: 1.8rem;
  }
  
  .section-subtitle {
    font-size: 0.95rem;
  }
  
  .why-section,
  .benefits-section,
  .how-it-works-section {
    padding: 50px 0;
  }
  
  .reason-card,
  .benefit-card {
    padding: 25px 10px;
  }
  
  .reason-icon-wrapper {
    width: 60px;
    height: 60px;
  }
  
  .reason-icon {
    font-size: 1.8rem;
  }
  
  .reason-title,
  .benefit-title {
    font-size: 1.2rem;
  }
  
  .process-content {
    padding: 25px 20px;
  }
  
  .process-step {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 15px;
  }
  
  .step-content {
    text-align: center;
  }
  
  .footer-bottom-links {
    flex-direction: column;
    gap: 10px;
  }
  
  .footer-bottom p {
    font-size: 0.8rem;
    padding: 0 10px;
  }
  
  /* Optimisation pour les très petits écrans */
  @media (max-width: 360px) {
    .hero-title {
      font-size: 1.6rem;
    }
    
    .cta-button {
      padding: 12px 20px;
      font-size: 0.95rem;
    }
    
    .role-btn {
      padding: 16px 25px;
      font-size: 1rem;
    }
    
    .nav-link {
      padding: 8px 15px;
      font-size: 0.9rem;
    }
    
    .logo-text {
      font-size: 1.3rem;
    }
  }
}

/* Support tactile amélioré */
@media (hover: none) and (pointer: coarse) {
  .reason-card:hover,
  .benefit-card:hover,
  .role-btn:hover,
  .cta-button:hover,
  .launch-btn:hover,
  .secondary-cta-button:hover,
  .outline-cta-button:hover,
  .social-link:hover,
  .footer-links a:hover {
    transform: none;
  }
  
  .reason-card:active,
  .benefit-card:active {
    transform: scale(0.98);
  }
  
  .reason-card:hover .reason-icon {
    transform: none;
  }
  
  .reason-card:active .reason-icon {
    transform: rotate(10deg) scale(1.1);
  }
}

/* Support pour les modes sombre */
@media (prefers-color-scheme: dark) {
  .reason-card,
  .process-content {
    background: #2d2d2d;
    border-color: #404040;
  }
  
  .reason-title,
  .step-title {
    color: #e4e4e4;
  }
  
  .reason-description,
  .step-description {
    color: #a0a0a0;
  }
}
</style>