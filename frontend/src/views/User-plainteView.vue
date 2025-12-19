<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAdminStore } from '@/stores/admin'

const authStore = useAuthStore()
const adminStore = useAdminStore()
const router = useRouter()

// États
const activeTab = ref('new')
const isLoading = ref(false)
const complaints = ref([])
const filteredComplaints = computed(() => {
  return complaints.value
})
const stats = ref({
  total: 0,
  pending: 0,
  approved: 0,
  rejected: 0
})

// Formulaire
const form = ref({
  reported_email: '',
  reason: ''
})
const errors = ref({})
const successMessage = ref('')

// Pagination
const pagination = ref({
  page: 1,
  perPage: 10,
  total: 0,
  pages: 1
})

// Initialisation
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  await loadComplaints()
})

// Charger les plaintes
const loadComplaints = async () => {
  isLoading.value = true
  try {
    const result = await adminStore.fetchMyComplaints()
    if (result.success) {
      complaints.value = result.complaints
      pagination.value.total = result.total
      
      // Calculer les statistiques
      updateStats()
    }
  } catch (error) {
    console.error('Erreur de chargement:', error)
  } finally {
    isLoading.value = false
  }
}

// Mettre à jour les statistiques
const updateStats = () => {
  stats.value = {
    total: complaints.value.length,
    pending: complaints.value.filter(c => c.status === 'pending').length,
    approved: complaints.value.filter(c => c.status === 'approved').length,
    rejected: complaints.value.filter(c => c.status === 'rejected').length
  }
}

// Valider le formulaire
const validateForm = () => {
  errors.value = {}
  let isValid = true

  // Validation email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!form.value.reported_email) {
    errors.value.reported_email = 'L\'email est requis'
    isValid = false
  } else if (!emailRegex.test(form.value.reported_email)) {
    errors.value.reported_email = 'Format d\'email invalide'
    isValid = false
  } else if (form.value.reported_email === authStore.user?.email) {
    errors.value.reported_email = 'Vous ne pouvez pas vous signaler vous-même'
    isValid = false
  }

  // Validation motif
  if (!form.value.reason) {
    errors.value.reason = 'Le motif est requis'
    isValid = false
  } else if (form.value.reason.length < 10) {
    errors.value.reason = 'Le motif doit contenir au moins 10 caractères'
    isValid = false
  } else if (form.value.reason.length > 1000) {
    errors.value.reason = 'Le motif ne doit pas dépasser 1000 caractères'
    isValid = false
  }

  return isValid
}

// Soumettre une plainte
const submitComplaint = async () => {
  if (!validateForm()) return

  isLoading.value = true
  successMessage.value = ''

  try {
    const result = await adminStore.createComplaint(
      form.value.reported_email,
      form.value.reason
    )

    if (result.success) {
      successMessage.value = result.message
      
      // Réinitialiser le formulaire
      form.value = {
        reported_email: '',
        reason: ''
      }
      errors.value = {}
      
      // Recharger les plaintes
      await loadComplaints()
      
      // Basculer vers l'onglet historique
      activeTab.value = 'history'
    } else {
      errors.value.submit = result.message
    }
  } catch (error) {
    console.error('Erreur de soumission:', error)
    errors.value.submit = 'Une erreur est survenue. Veuillez réessayer.'
  } finally {
    isLoading.value = false
  }
}

// Obtenir le texte du statut
const getStatusText = (status) => {
  switch (status) {
    case 'pending': return 'En attente'
    case 'approved': return 'Approuvée'
    case 'rejected': return 'Rejetée'
    default: return status
  }
}

// Obtenir la classe du statut
const getStatusClass = (status) => {
  switch (status) {
    case 'pending': return 'status-pending'
    case 'approved': return 'status-approved'
    case 'rejected': return 'status-rejected'
    default: return ''
  }
}

// Obtenir l'icône du statut
const getStatusIcon = (status) => {
  switch (status) {
    case 'pending': return 'fas fa-clock'
    case 'approved': return 'fas fa-check-circle'
    case 'rejected': return 'fas fa-times-circle'
    default: return 'fas fa-info-circle'
  }
}

// Formater la date
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Obtenir la description du statut
const getStatusDescription = (status) => {
  switch (status) {
    case 'pending':
      return 'Votre plainte est en cours d\'examen par notre équipe. Nous vous répondrons sous 24-48 heures.'
    case 'approved':
      return 'Votre plainte a été validée. L\'utilisateur signalé a été sanctionné selon nos conditions d\'utilisation.'
    case 'rejected':
      return 'Votre plainte a été rejetée. Si vous pensez qu\'il s\'agit d\'une erreur, vous pouvez contacter notre support.'
    default:
      return ''
  }
}

// Naviguer vers le tableau de bord
const goToDashboard = () => {
  router.push('/dashboard')
}

// Rafraîchir les plaintes
const refreshComplaints = () => {
  loadComplaints()
}
</script>

<template>
  <div class="complaints-page">
    <!-- Header -->
    <header class="complaints-header">
      <div class="header-container">
        <div class="header-left">
          <button class="back-btn" @click="goToDashboard">
            <i class="fas fa-arrow-left"></i>
            Retour
          </button>
          <h1>
            <i class="fas fa-flag"></i>
            Signalements et plaintes
          </h1>
        </div>
        <div class="header-right">
          <button class="refresh-btn" @click="refreshComplaints" :disabled="isLoading">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            <span>Rafraîchir</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Statistiques -->
    <section class="complaints-stats">
      <div class="stats-container">
        <div class="stat-card total">
          <div class="stat-icon">
            <i class="fas fa-flag"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ stats.total }}</h3>
            <p class="stat-label">Plaintes totales</p>
          </div>
        </div>
        
        <div class="stat-card pending">
          <div class="stat-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ stats.pending }}</h3>
            <p class="stat-label">En attente</p>
          </div>
        </div>
        
        <div class="stat-card approved">
          <div class="stat-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ stats.approved }}</h3>
            <p class="stat-label">Approuvées</p>
          </div>
        </div>
        
        <div class="stat-card rejected">
          <div class="stat-icon">
            <i class="fas fa-times-circle"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ stats.rejected }}</h3>
            <p class="stat-label">Rejetées</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Navigation par onglets -->
    <nav class="complaints-tabs">
      <div class="tabs-container">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'new' }"
          @click="activeTab = 'new'"
        >
          <i class="fas fa-plus-circle"></i>
          Nouvelle plainte
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'history' }"
          @click="activeTab = 'history'"
        >
          <i class="fas fa-history"></i>
          Historique
          <span class="tab-badge">{{ stats.total }}</span>
        </button>
      </div>
    </nav>

    <!-- Contenu principal -->
    <main class="complaints-main">
      <!-- Onglet Nouvelle plainte -->
      <div v-if="activeTab === 'new'" class="tab-content new-complaint">
        <div class="complaint-form-container">
          <div class="form-header">
            <h2>
              <i class="fas fa-exclamation-triangle"></i>
              Signaler un utilisateur
            </h2>
            <p class="form-subtitle">
              Aidez-nous à maintenir une communauté saine en signalant les comportements inappropriés.
            </p>
          </div>

          <!-- Message de succès -->
          <div v-if="successMessage" class="success-message">
            <i class="fas fa-check-circle"></i>
            {{ successMessage }}
          </div>

          <!-- Message d'erreur général -->
          <div v-if="errors.submit" class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            {{ errors.submit }}
          </div>

          <!-- Formulaire -->
          <form @submit.prevent="submitComplaint" class="complaint-form">
            <!-- Informations sur la procédure -->
            <div class="info-box">
              <div class="info-header">
                <i class="fas fa-info-circle"></i>
                <h4>À propos du signalement</h4>
              </div>
              <div class="info-content">
                <p>Votre signalement sera traité de manière confidentielle par notre équipe de modération.</p>
                <ul>
                  <li>Les signalements abusifs peuvent entraîner la suspension de votre compte</li>
                  <li>Nous vous répondrons sous 24-48 heures</li>
                  <li>L'utilisateur signalé ne sera pas informé de votre identité</li>
                </ul>
              </div>
            </div>

            <!-- Champ email -->
            <div class="form-group">
              <label for="reported_email">
                <i class="fas fa-envelope"></i>
                Email de l'utilisateur à signaler
                <span class="required">*</span>
              </label>
              <input
                id="reported_email"
                v-model="form.reported_email"
                type="email"
                placeholder="exemple@email.com"
                :disabled="isLoading"
                class="form-input"
                :class="{ 'error': errors.reported_email }"
              />
              <div v-if="errors.reported_email" class="error-text">
                <i class="fas fa-exclamation-circle"></i>
                {{ errors.reported_email }}
              </div>
              <div class="input-hint">
                <i class="fas fa-lightbulb"></i>
                Assurez-vous d'avoir la bonne adresse email
              </div>
            </div>

            <!-- Champ motif -->
            <div class="form-group">
              <label for="reason">
                <i class="fas fa-comment-alt"></i>
                Motif du signalement
                <span class="required">*</span>
              </label>
              <div class="character-count">
                <span>{{ form.reason.length }}/1000 caractères</span>
              </div>
              <textarea
                id="reason"
                v-model="form.reason"
                placeholder="Décrivez en détail le comportement inapproprié..."
                rows="6"
                :disabled="isLoading"
                class="form-textarea"
                :class="{ 'error': errors.reason }"
                maxlength="1000"
              ></textarea>
              <div v-if="errors.reason" class="error-text">
                <i class="fas fa-exclamation-circle"></i>
                {{ errors.reason }}
              </div>
              <div class="input-hint">
                <i class="fas fa-lightbulb"></i>
                Soyez précis et fournissez des détails concrets si possible
              </div>
            </div>

            <!-- Conseils pour un bon signalement -->
            <div class="tips-box">
              <div class="tips-header">
                <i class="fas fa-lightbulb"></i>
                <h4>Conseils pour un signalement efficace</h4>
              </div>
              <div class="tips-content">
                <div class="tip-item">
                  <i class="fas fa-check"></i>
                  <div>
                    <strong>Soyez précis :</strong> Mentionnez des dates, heures et échanges spécifiques
                  </div>
                </div>
                <div class="tip-item">
                  <i class="fas fa-check"></i>
                  <div>
                    <strong>Restez objectif :</strong> Décrivez les faits sans émotion excessive
                  </div>
                </div>
                <div class="tip-item">
                  <i class="fas fa-check"></i>
                  <div>
                    <strong>Fournissez des preuves :</strong> Capture d'écran, messages, etc. (sauvegardez-les localement)
                  </div>
                </div>
              </div>
            </div>

            <!-- Confidentialité -->
            <div class="privacy-box">
              <div class="privacy-header">
                <i class="fas fa-shield-alt"></i>
                <h4>Confidentialité et sécurité</h4>
              </div>
              <div class="privacy-content">
                <p>
                  <i class="fas fa-lock"></i>
                  Votre identité reste strictement confidentielle. L'utilisateur signalé ne recevra jamais votre nom ou email.
                </p>
                <div class="privacy-checkbox">
                  <input type="checkbox" id="privacy" required />
                  <label for="privacy">
                    Je comprends que mon signalement sera traité de manière confidentielle et que les fausses déclarations peuvent entraîner la suspension de mon compte.
                  </label>
                </div>
              </div>
            </div>

            <!-- Boutons de soumission -->
            <div class="form-actions">
              <button 
                type="button" 
                class="cancel-btn" 
                @click="form = { reported_email: '', reason: '' }"
                :disabled="isLoading"
              >
                <i class="fas fa-times"></i>
                Effacer le formulaire
              </button>
              <button 
                type="submit" 
                class="submit-btn" 
                :disabled="isLoading"
                :class="{ 'loading': isLoading }"
              >
                <span v-if="isLoading">
                  <i class="fas fa-spinner fa-spin"></i>
                  Envoi en cours...
                </span>
                <span v-else>
                  <i class="fas fa-paper-plane"></i>
                  Envoyer le signalement
                </span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Onglet Historique -->
      <div v-if="activeTab === 'history'" class="tab-content complaints-history">
        <div class="history-header">
          <h2>
            <i class="fas fa-history"></i>
            Historique de vos signalements
          </h2>
          <p class="history-subtitle">
            Suivez l'état de traitement de vos signalements
          </p>
        </div>

        <!-- Message vide -->
        <div v-if="complaints.length === 0 && !isLoading" class="empty-history">
          <div class="empty-icon">
            <i class="fas fa-inbox"></i>
          </div>
          <h3>Aucun signalement</h3>
          <p>Vous n'avez pas encore effectué de signalement.</p>
          <button class="new-complaint-btn" @click="activeTab = 'new'">
            <i class="fas fa-plus-circle"></i>
            Faire un premier signalement
          </button>
        </div>

        <!-- Liste des plaintes -->
        <div v-else class="complaints-list">
          <!-- Indicateur de chargement -->
          <div v-if="isLoading" class="loading-overlay">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Chargement de vos signalements...</p>
          </div>

          <!-- Cartes des plaintes -->
          <div class="complaint-cards">
            <div 
              v-for="complaint in filteredComplaints" 
              :key="complaint.id" 
              class="complaint-card"
              :class="getStatusClass(complaint.status)"
            >
              <div class="card-header">
                <div class="complaint-id">
                  <i class="fas fa-hashtag"></i>
                  Signalement #{{ complaint.id }}
                </div>
                <div class="complaint-date">
                  <i class="fas fa-calendar"></i>
                  {{ formatDate(complaint.created_at) }}
                </div>
              </div>
              
              <div class="card-content">
                <!-- Utilisateur signalé -->
                <div class="complaint-target">
                  <div class="target-label">
                    <i class="fas fa-user-times"></i>
                    Utilisateur signalé
                  </div>
                  <div class="target-email">
                    {{ complaint.reported_email }}
                  </div>
                </div>

                <!-- Motif -->
                <div class="complaint-reason">
                  <div class="reason-label">
                    <i class="fas fa-comment-alt"></i>
                    Motif
                  </div>
                  <div class="reason-text">
                    {{ complaint.reason }}
                  </div>
                </div>

                <!-- Statut -->
                <div class="complaint-status">
                  <div class="status-label">
                    <i class="fas fa-info-circle"></i>
                    État du signalement
                  </div>
                  <div class="status-info">
                    <div class="status-badge" :class="getStatusClass(complaint.status)">
                      <i :class="getStatusIcon(complaint.status)"></i>
                      {{ getStatusText(complaint.status) }}
                    </div>
                    <div class="status-description">
                      {{ getStatusDescription(complaint.status) }}
                    </div>
                  </div>
                </div>

                <!-- Dates de traitement -->
                <div v-if="complaint.reviewed_at" class="complaint-dates">
                  <div class="dates-grid">
                    <div class="date-item">
                      <div class="date-label">
                        <i class="fas fa-paper-plane"></i>
                        Envoyé le
                      </div>
                      <div class="date-value">
                        {{ formatDate(complaint.created_at) }}
                      </div>
                    </div>
                    <div class="date-item">
                      <div class="date-label">
                        <i class="fas fa-check-double"></i>
                        Traité le
                      </div>
                      <div class="date-value">
                        {{ formatDate(complaint.reviewed_at) }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Actions possibles -->
                <div v-if="complaint.status === 'rejected'" class="complaint-actions">
                  <div class="actions-note">
                    <i class="fas fa-exclamation-circle"></i>
                    Vous pouvez contacter notre support si vous pensez qu'il s'agit d'une erreur.
                  </div>
                </div>
              </div>

              <div class="card-footer">
                <div class="footer-actions">
                  <button class="view-details-btn" @click="activeTab = 'new'">
                    <i class="fas fa-plus-circle"></i>
                    Nouveau signalement
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Informations importantes -->
    <section class="complaints-info">
      <div class="info-container">
        <div class="info-card">
          <div class="info-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="info-content">
            <h4>Temps de traitement</h4>
            <p>Nos modérateurs examinent généralement les signalements sous 24 à 48 heures ouvrables.</p>
          </div>
        </div>
        
        <div class="info-card">
          <div class="info-icon">
            <i class="fas fa-shield-alt"></i>
          </div>
          <div class="info-content">
            <h4>Confidentialité garantie</h4>
            <p>Votre identité est protégée. L'utilisateur signalé ne connaîtra jamais votre nom.</p>
          </div>
        </div>
        
        <div class="info-card">
          <div class="info-icon">
            <i class="fas fa-balance-scale"></i>
          </div>
          <div class="info-content">
            <h4>Justice équitable</h4>
            <p>Tous les signalements sont examinés impartialement selon nos conditions d'utilisation.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="complaints-footer">
      <div class="footer-container">
        <div class="footer-content">
          <div class="footer-left">
            <h4>
              <i class="fas fa-headset"></i>
              Besoin d'aide ?
            </h4>
            <p>Pour toute question concernant les signalements, contactez notre support.</p>
            <div class="support-contact">
              <i class="fas fa-envelope"></i>
              <span>support@freelancecmr.com</span>
            </div>
          </div>
          
          <div class="footer-right">
            <div class="urgent-alert">
              <i class="fas fa-exclamation-triangle"></i>
              <div class="urgent-content">
                <h5>Urgence ?</h5>
                <p>Pour des cas urgents (harcèlement grave, menaces), contactez immédiatement notre support d'urgence.</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="footer-bottom">
          <p>
            <i class="fas fa-info-circle"></i>
            En utilisant ce système de signalement, vous acceptez nos conditions d'utilisation et notre politique de confidentialité.
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Styles généraux */
.complaints-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

/* Header */
.complaints-header {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  padding: 20px 0;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.header-left h1 {
  margin: 0;
  font-size: 1.6rem;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h1 i {
  color: #FF6B35;
}

.header-right {
  display: flex;
  gap: 10px;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Statistiques */
.complaints-stats {
  padding: 30px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 25px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.total .stat-icon {
  background: linear-gradient(135deg, #4dabf7, #339af0);
  color: white;
}

.pending .stat-icon {
  background: linear-gradient(135deg, #ffc107, #e6a800);
  color: white;
}

.approved .stat-icon {
  background: linear-gradient(135deg, #51cf66, #37b24d);
  color: white;
}

.rejected .stat-icon {
  background: linear-gradient(135deg, #ff6b6b, #fa5252);
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 5px 0;
  color: #2D3047;
}

.stat-label {
  font-size: 0.9rem;
  color: #6c757d;
  margin: 0;
}

/* Navigation par onglets */
.complaints-tabs {
  max-width: 1200px;
  margin: 0 auto 30px;
  padding: 0 20px;
}

.tabs-container {
  display: flex;
  gap: 10px;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 5px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 25px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 1rem;
  font-weight: 600;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.tab-btn:hover {
  color: #2D3047;
}

.tab-btn.active {
  color: #2D3047;
  border-bottom-color: #2D3047;
}

.tab-btn i {
  font-size: 1.1rem;
}

.tab-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #dc3545;
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

/* Contenu principal */
.complaints-main {
  max-width: 1200px;
  margin: 0 auto 40px;
  padding: 0 20px;
}

.tab-content {
  background: white;
  border-radius: 20px;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* Onglet Nouvelle plainte */
.new-complaint {
  padding: 40px;
}

.form-header {
  margin-bottom: 30px;
  text-align: center;
}

.form-header h2 {
  font-size: 1.8rem;
  color: #2D3047;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.form-header h2 i {
  color: #FF6B35;
}

.form-subtitle {
  color: #6c757d;
  font-size: 1rem;
  line-height: 1.6;
  max-width: 600px;
  margin: 0 auto;
}

/* Messages */
.success-message {
  background: linear-gradient(135deg, #d4edda, #c3e6cb);
  border: 1px solid #c3e6cb;
  border-left: 4px solid #28a745;
  color: #155724;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 12px;
  animation: slideIn 0.3s ease;
}

.error-message {
  background: linear-gradient(135deg, #f8d7da, #f5c6cb);
  border: 1px solid #f5c6cb;
  border-left: 4px solid #dc3545;
  color: #721c24;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 12px;
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

/* Formulaire */
.complaint-form {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* Box d'information */
.info-box, .tips-box, .privacy-box {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 25px;
  border-left: 4px solid #FF6B35;
}

.info-header, .tips-header, .privacy-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 15px;
}

.info-header i, .tips-header i, .privacy-header i {
  color: #FF6B35;
  font-size: 1.2rem;
}

.info-header h4, .tips-header h4, .privacy-header h4 {
  margin: 0;
  color: #2D3047;
  font-size: 1.1rem;
}

.info-content p {
  margin: 0 0 10px 0;
  color: #6c757d;
  line-height: 1.6;
}

.info-content ul {
  margin: 15px 0 0 0;
  padding-left: 20px;
}

.info-content li {
  color: #6c757d;
  margin-bottom: 8px;
  line-height: 1.5;
}

/* Champs du formulaire */
.form-group {
  position: relative;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-weight: 600;
  color: #2D3047;
  font-size: 0.95rem;
}

.required {
  color: #dc3545;
  font-weight: 700;
}

.character-count {
  text-align: right;
  font-size: 0.85rem;
  color: #6c757d;
  margin-bottom: 5px;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 16px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-family: inherit;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #f8f9fa;
  color: #2D3047;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: #2D3047;
  background: white;
  box-shadow: 0 0 0 3px rgba(45, 48, 71, 0.1);
}

.form-input.error, .form-textarea.error {
  border-color: #dc3545;
  background: #fff8f8;
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
}

.error-text {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #dc3545;
  font-size: 0.85rem;
  margin-top: 8px;
}

.input-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-size: 0.85rem;
  color: #6c757d;
}

/* Conseils */
.tips-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.tip-item i {
  color: #28a745;
  margin-top: 2px;
  flex-shrink: 0;
}

/* Confidentialité */
.privacy-content p {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: #6c757d;
  line-height: 1.6;
  margin-bottom: 20px;
}

.privacy-checkbox {
  display: flex;
  gap: 12px;
}

.privacy-checkbox input[type="checkbox"] {
  margin-top: 4px;
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 2px solid #dee2e6;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.privacy-checkbox input[type="checkbox"]:checked {
  background-color: #2D3047;
  border-color: #2D3047;
}

.privacy-checkbox label {
  font-size: 0.9rem;
  color: #6c757d;
  line-height: 1.5;
  cursor: pointer;
  font-weight: normal;
}

/* Boutons */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 20px;
}

.cancel-btn, .submit-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 30px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: #6c757d;
  color: white;
}

.cancel-btn:hover:not(:disabled) {
  background: #5a6268;
}

.submit-btn {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  position: relative;
  overflow: hidden;
}

.submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.submit-btn:hover:not(:disabled)::before {
  left: 100%;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(45, 48, 71, 0.3);
}

.submit-btn:disabled, .cancel-btn:disabled {
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
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  border-radius: 10px;
  animation: loadingPulse 1.5s infinite;
}

@keyframes loadingPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

/* Onglet Historique */
.complaints-history {
  padding: 40px;
}

.history-header {
  margin-bottom: 30px;
  text-align: center;
}

.history-header h2 {
  font-size: 1.8rem;
  color: #2D3047;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.history-subtitle {
  color: #6c757d;
  font-size: 1rem;
}

/* Historique vide */
.empty-history {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 4rem;
  color: #dee2e6;
  margin-bottom: 20px;
}

.empty-history h3 {
  color: #2D3047;
  margin: 0 0 10px 0;
}

.empty-history p {
  color: #6c757d;
  margin-bottom: 30px;
}

.new-complaint-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 15px 30px;
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.new-complaint-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(45, 48, 71, 0.3);
}

/* Liste des plaintes */
.loading-overlay {
  text-align: center;
  padding: 40px;
}

.loading-overlay i {
  font-size: 2rem;
  color: #2D3047;
  margin-bottom: 15px;
}

.loading-overlay p {
  color: #6c757d;
  margin: 0;
}

.complaint-cards {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.complaint-card {
  background: white;
  border-radius: 15px;
  border: 1px solid #e9ecef;
  overflow: hidden;
  transition: all 0.3s ease;
}

.complaint-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.complaint-card.status-pending {
  border-left: 4px solid #ffc107;
}

.complaint-card.status-approved {
  border-left: 4px solid #28a745;
}

.complaint-card.status-rejected {
  border-left: 4px solid #dc3545;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.complaint-id, .complaint-date {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #6c757d;
}

.card-content {
  padding: 25px;
}

/* Sections de la carte */
.complaint-target,
.complaint-reason,
.complaint-status,
.complaint-dates,
.complaint-actions {
  margin-bottom: 20px;
}

.complaint-target:last-child,
.complaint-reason:last-child,
.complaint-status:last-child,
.complaint-dates:last-child,
.complaint-actions:last-child {
  margin-bottom: 0;
}

.target-label,
.reason-label,
.status-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 8px;
  font-weight: 500;
}

.target-email {
  font-weight: 600;
  color: #2D3047;
  font-size: 1.1rem;
}

.reason-text {
  color: #495057;
  line-height: 1.6;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

/* Statut */
.status-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
  width: fit-content;
}

.status-badge.status-pending {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.status-badge.status-approved {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.status-badge.status-rejected {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.status-description {
  color: #6c757d;
  font-size: 0.9rem;
  line-height: 1.5;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #dee2e6;
}

/* Dates */
.dates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.date-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.date-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #6c757d;
}

.date-value {
  font-weight: 600;
  color: #2D3047;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

/* Actions */
.actions-note {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 15px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  color: #856404;
  font-size: 0.9rem;
}

/* Footer de la carte */
.card-footer {
  padding: 20px;
  border-top: 1px solid #e9ecef;
  background: #f8f9fa;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
}

.view-details-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #2D3047;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-details-btn:hover {
  background: #1A1C2E;
  transform: translateY(-2px);
}

/* Informations importantes */
.complaints-info {
  max-width: 1200px;
  margin: 0 auto 40px;
  padding: 0 20px;
}

.info-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.info-card {
  background: white;
  border-radius: 15px;
  padding: 25px;
  display: flex;
  align-items: flex-start;
  gap: 20px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease;
}

.info-card:hover {
  transform: translateY(-5px);
}

.info-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2D3047, #1A1C2E);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.info-icon i {
  color: white;
  font-size: 1.3rem;
}

.info-content h4 {
  margin: 0 0 10px 0;
  color: #2D3047;
  font-size: 1.1rem;
}

.info-content p {
  margin: 0;
  color: #6c757d;
  line-height: 1.6;
  font-size: 0.9rem;
}

/* Footer */
.complaints-footer {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  padding: 40px 0 20px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 40px;
  margin-bottom: 30px;
}

.footer-left h4 {
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
}

.footer-left p {
  margin: 0 0 20px 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

.support-contact {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.urgent-alert {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 20px;
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 12px;
}

.urgent-alert i {
  color: #ffc107;
  font-size: 1.5rem;
  margin-top: 2px;
}

.urgent-content h5 {
  margin: 0 0 10px 0;
  color: #ffc107;
  font-size: 1.1rem;
}

.urgent-content p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  font-size: 0.9rem;
}

.footer-bottom {
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.footer-bottom p {
  margin: 0;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* Responsive */
@media (max-width: 992px) {
  .header-container {
    flex-direction: column;
    text-align: center;
  }
  
  .header-left {
    flex-direction: column;
    gap: 15px;
  }
  
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .cancel-btn, .submit-btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .tabs-container {
    flex-direction: column;
    border-bottom: none;
  }
  
  .tab-btn {
    border: 1px solid #e9ecef;
    border-radius: 10px;
    margin-bottom: 10px;
  }
  
  .tab-btn.active {
    border-color: #2D3047;
  }
  
  .new-complaint,
  .complaints-history {
    padding: 25px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .dates-grid {
    grid-template-columns: 1fr;
  }
  
  .info-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 576px) {
  .stats-container {
    grid-template-columns: 1fr;
  }
  
  .complaint-form-container,
  .complaints-history {
    padding: 20px;
  }
  
  .form-header h2 {
    font-size: 1.5rem;
    flex-direction: column;
    gap: 8px;
  }
  
  .footer-content {
    grid-template-columns: 1fr;
    gap: 30px;
  }
}
</style>