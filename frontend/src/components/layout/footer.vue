<!-- components/Footer.vue -->
<script setup>
// Pas besoin de logique spéciale pour le footer
</script>

<template>
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
          <li><router-link to="/apropos">À propos</router-link></li>
          <li><router-link to="/freelances">Freelances</router-link></li>
          <li><router-link to="/projets">Projets</router-link></li>
          <li><router-link to="/contact">Contact</router-link></li>
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
</template>

<style scoped>
/* ==================== FOOTER STYLES ==================== */
.footer {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  padding-top: 80px;
  margin-top: auto; /* Pour le push vers le bas si nécessaire */
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
  padding: 0;
  margin: 0;
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

/* ==================== RESPONSIVE ==================== */
@media (max-width: 1024px) {
  .footer-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 50px 30px;
  }
}

@media (max-width: 768px) {
  .footer {
    padding-top: 60px;
  }
  
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
  
  .footer-bottom-links {
    flex-direction: column;
    gap: 10px;
  }
  
  .footer-bottom p {
    font-size: 0.8rem;
    padding: 0 10px;
  }
}

@media (max-width: 480px) {
  .footer-logo {
    font-size: 1.5rem;
  }
  
  .footer-logo i {
    font-size: 1.8rem;
  }
}
</style>