<template>
  <div class="not-found-page">
    <!-- Background Animation -->
    <div class="background-animation">
      <div class="floating-shape shape-1"></div>
      <div class="floating-shape shape-2"></div>
      <div class="floating-shape shape-3"></div>
      <div class="floating-shape shape-4"></div>
    </div>

    <!-- Main Content -->
    <div class="not-found-container">
      <!-- Error Code -->
      <div class="error-code">
        <span class="number">4</span>
        <div class="zero">
          <div class="zero-inner">
            <i class="fas fa-question-circle"></i>
          </div>
        </div>
        <span class="number">4</span>
      </div>

      <!-- Message -->
      <div class="error-content">
        <h1 class="error-title">Oups ! Page introuvable</h1>
        <p class="error-message">
          La page que vous recherchez semble avoir disparu dans le cyberespace.
          Elle a peut-être été déplacée, supprimée ou n'a jamais existé.
        </p>
        
        <!-- Suggestions -->
        <div class="suggestions">
          <h3>Suggestions :</h3>
          <ul class="suggestions-list">
            <li><i class="fas fa-check-circle"></i> Vérifiez l'URL dans la barre d'adresse</li>
            <li><i class="fas fa-check-circle"></i> Retournez à la page précédente</li>
            <li><i class="fas fa-check-circle"></i> Utilisez la recherche pour trouver ce que vous cherchez</li>
            <li><i class="fas fa-check-circle"></i> Consultez notre page d'accueil</li>
          </ul>
        </div>

        <!-- Actions -->
        <div class="action-buttons">
          <button class="btn-primary" @click="$router.push('/')">
            <i class="fas fa-home"></i>
            <span>Retour à l'accueil</span>
          </button>
          <button class="btn-secondary" @click="$router.go(-1)">
            <i class="fas fa-arrow-left"></i>
            <span>Page précédente</span>
          </button>
          <button class="btn-outline" @click="$router.push('/dashboard')">
            <i class="fas fa-tachometer-alt"></i>
            <span>Mon Dashboard</span>
          </button>
        </div>

        <!-- Search -->
        <div class="search-box">
          <div class="search-input-wrapper">
            <i class="fas fa-search search-icon"></i>
            <input 
              type="text" 
              placeholder="Rechercher sur FreelanceCMR..."
              class="search-input"
              v-model="searchQuery"
              @keyup.enter="performSearch"
            />
            <button class="search-btn" @click="performSearch">
              <i class="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>

        <!-- Stats -->
        <div class="stats">
          <div class="stat-item">
            <i class="fas fa-users"></i>
            <div class="stat-content">
              <span class="stat-number">1,500+</span>
              <span class="stat-label">Freelances actifs</span>
            </div>
          </div>
          <div class="stat-item">
            <i class="fas fa-briefcase"></i>
            <div class="stat-content">
              <span class="stat-number">350+</span>
              <span class="stat-label">Projets disponibles</span>
            </div>
          </div>
          <div class="stat-item">
            <i class="fas fa-check-circle"></i>
            <div class="stat-content">
              <span class="stat-number">98%</span>
              <span class="stat-label">Taux de satisfaction</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Note -->
    <div class="footer-note">
      <p>
        <i class="fas fa-info-circle"></i>
        Vous avez besoin d'aide ? 
        <router-link to="/contact" class="contact-link">Contactez notre support</router-link>
        ou appelez-nous au <strong>+237 650 536 195</strong>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')

const performSearch = () => {
  if (searchQuery.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchQuery.value)}`)
  }
}
</script>

<style scoped>
/* ==================== VARIABLES ==================== */
:root {
  --color-primary: #FF6B35;
  --color-primary-light: #FF8E53;
  --color-dark: #2D3047;
  --color-dark-light: #3A3D5F;
  --color-light: #F8FAFC;
  --color-gray: #64748B;
  --color-gray-light: #E2E8F0;
  --color-success: #10B981;
  --color-danger: #EF4444;
  --color-info: #3B82F6;
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-secondary: 'SF Pro Display', -apple-system, sans-serif;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 40px rgba(0, 0, 0, 0.15);
  --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ==================== PAGE STYLES ==================== */
.not-found-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1c2e 0%, #0f111f 100%);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  font-family: var(--font-primary);
  position: relative;
  overflow: hidden;
}

/* Background Animation */
.background-animation {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 1;
}

.floating-shape {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 107, 53, 0.15), transparent);
  animation: float 20s infinite linear;
}

.shape-1 {
  width: 300px;
  height: 300px;
  top: 10%;
  left: 5%;
  animation-delay: 0s;
}

.shape-2 {
  width: 200px;
  height: 200px;
  bottom: 15%;
  right: 10%;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.1), transparent);
  animation-delay: 5s;
}

.shape-3 {
  width: 150px;
  height: 150px;
  top: 40%;
  right: 20%;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.1), transparent);
  animation-delay: 10s;
}

.shape-4 {
  width: 250px;
  height: 250px;
  bottom: 30%;
  left: 15%;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.1), transparent);
  animation-delay: 15s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  25% {
    transform: translate(20px, 20px) rotate(90deg);
  }
  50% {
    transform: translate(0, 40px) rotate(180deg);
  }
  75% {
    transform: translate(-20px, 20px) rotate(270deg);
  }
}

/* ==================== MAIN CONTAINER ==================== */
.not-found-container {
  position: relative;
  z-index: 2;
  text-align: center;
  max-width: 800px;
  width: 100%;
  background: rgba(45, 48, 71, 0.7);
  backdrop-filter: blur(20px);
  border-radius: var(--radius-xl);
  padding: 50px 40px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: var(--shadow-xl);
}

/* ==================== ERROR CODE ==================== */
.error-code {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 30px;
  margin-bottom: 40px;
  position: relative;
}

.number {
  font-size: 10rem;
  font-weight: 900;
  color: var(--color-primary);
  text-shadow: 0 10px 30px rgba(255, 107, 53, 0.4);
  font-family: var(--font-secondary);
  line-height: 1;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.8;
  }
}

.zero {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.zero::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border: 8px solid var(--color-primary);
  border-radius: 50%;
  box-shadow: 0 0 40px rgba(255, 107, 53, 0.5);
  animation: rotate 10s infinite linear;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.zero-inner {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.3);
}

.zero-inner i {
  font-size: 3.5rem;
  color: white;
}

/* ==================== ERROR CONTENT ==================== */
.error-content {
  margin-top: 30px;
}

.error-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #ffffff, #a5b4fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: var(--font-secondary);
  line-height: 1.2;
}

.error-message {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin-bottom: 40px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

/* ==================== SUGGESTIONS ==================== */
.suggestions {
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-lg);
  padding: 25px;
  margin-bottom: 40px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: left;
  backdrop-filter: blur(10px);
}

.suggestions h3 {
  font-size: 1.3rem;
  margin-bottom: 20px;
  color: white;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.suggestions h3::before {
  content: '💡';
  font-size: 1.2rem;
}

.suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.suggestions-list li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.95rem;
  line-height: 1.5;
}

.suggestions-list li i {
  color: var(--color-success);
  font-size: 0.9rem;
  margin-top: 3px;
  flex-shrink: 0;
}

/* ==================== ACTION BUTTONS ==================== */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin: 40px 0;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary,
.btn-outline {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px 32px;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  border: none;
  min-width: 200px;
  font-family: var(--font-primary);
}

.btn-primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  color: white;
  box-shadow: 0 5px 20px rgba(255, 107, 53, 0.3);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(255, 107, 53, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-3px);
}

.btn-outline {
  background: transparent;
  color: white;
  border: 2px solid var(--color-info);
}

.btn-outline:hover {
  background: rgba(59, 130, 246, 0.1);
  transform: translateY(-3px);
}

/* ==================== SEARCH BOX ==================== */
.search-box {
  max-width: 500px;
  margin: 40px auto;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
  border: 2px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
  transition: var(--transition);
}

.search-input-wrapper:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.search-icon {
  position: absolute;
  left: 20px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 1.1rem;
}

.search-input {
  flex: 1;
  padding: 18px 60px 18px 55px;
  background: transparent;
  border: none;
  color: white;
  font-size: 1rem;
  font-family: var(--font-primary);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.search-input:focus {
  outline: none;
}

.search-btn {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  color: white;
  border: none;
  padding: 0 25px;
  height: 100%;
  cursor: pointer;
  transition: var(--transition);
  font-size: 1.1rem;
}

.search-btn:hover {
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-primary));
  padding: 0 30px;
}

/* ==================== STATS ==================== */
.stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 50px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(255, 255, 255, 0.05);
  padding: 20px;
  border-radius: var(--radius-lg);
  border: 1px solid rgba(255, 255, 255, 0.1);
  min-width: 200px;
  backdrop-filter: blur(10px);
  transition: var(--transition);
}

.stat-item:hover {
  border-color: var(--color-primary);
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.1);
}

.stat-item i {
  font-size: 2.5rem;
  color: var(--color-primary);
  background: rgba(255, 255, 255, 0.1);
  width: 60px;
  height: 60px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-content {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
  color: white;
  line-height: 1;
  margin-bottom: 5px;
  font-family: var(--font-secondary);
}

.stat-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

/* ==================== FOOTER NOTE ==================== */
.footer-note {
  margin-top: 40px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  max-width: 800px;
  width: 100%;
}

.footer-note p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}

.footer-note i {
  color: var(--color-primary);
}

.contact-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 600;
  transition: var(--transition);
}

.contact-link:hover {
  color: var(--color-primary-light);
  text-decoration: underline;
}

.footer-note strong {
  color: white;
  font-weight: 600;
}

/* ==================== RESPONSIVE DESIGN ==================== */
@media (max-width: 1024px) {
  .number {
    font-size: 8rem;
  }
  
  .zero {
    width: 120px;
    height: 120px;
  }
  
  .zero-inner {
    width: 80px;
    height: 80px;
  }
  
  .error-title {
    font-size: 2.2rem;
  }
}

@media (max-width: 768px) {
  .not-found-container {
    padding: 40px 25px;
  }
  
  .error-code {
    gap: 20px;
  }
  
  .number {
    font-size: 6rem;
  }
  
  .zero {
    width: 100px;
    height: 100px;
  }
  
  .zero-inner {
    width: 70px;
    height: 70px;
  }
  
  .zero-inner i {
    font-size: 2.5rem;
  }
  
  .error-title {
    font-size: 1.8rem;
  }
  
  .error-message {
    font-size: 1.1rem;
  }
  
  .suggestions-list {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .btn-primary,
  .btn-secondary,
  .btn-outline {
    width: 100%;
    max-width: 300px;
  }
  
  .stats {
    gap: 20px;
  }
  
  .stat-item {
    min-width: 160px;
  }
}

@media (max-width: 480px) {
  .not-found-page {
    padding: 20px 15px;
  }
  
  .not-found-container {
    padding: 30px 20px;
  }
  
  .error-code {
    gap: 15px;
  }
  
  .number {
    font-size: 4.5rem;
  }
  
  .zero {
    width: 80px;
    height: 80px;
  }
  
  .zero-inner {
    width: 55px;
    height: 55px;
  }
  
  .zero-inner i {
    font-size: 1.8rem;
  }
  
  .error-title {
    font-size: 1.5rem;
  }
  
  .error-message {
    font-size: 1rem;
  }
  
  .stats {
    flex-direction: column;
    align-items: center;
  }
  
  .stat-item {
    width: 100%;
    max-width: 300px;
  }
  
  .footer-note p {
    flex-direction: column;
    text-align: center;
    gap: 5px;
  }
}

/* Support tactile amélioré */
@media (hover: none) and (pointer: coarse) {
  .btn-primary:hover,
  .btn-secondary:hover,
  .btn-outline:hover,
  .stat-item:hover,
  .search-btn:hover {
    transform: none;
  }
  
  .btn-primary:active,
  .btn-secondary:active,
  .btn-outline:active {
    transform: scale(0.98);
  }
}
</style>