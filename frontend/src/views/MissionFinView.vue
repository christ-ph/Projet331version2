<template>
  <div class="mission-completion-page">
    <div class="completion-header">
      <h1>Mission complétée avec succès ! 🎉</h1>
      <p class="subtitle">Merci d'avoir utilisé notre plateforme</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Chargement des données...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button class="btn-retry" @click="loadCompletionData">
        <i class="fas fa-redo"></i> Réessayer
      </button>
    </div>

    <div v-else>
      <!-- Section d'export -->
      <div class="export-section">
        <div class="export-card">
          <div class="export-content">
            <i class="fas fa-file-export export-icon"></i>
            <div>
              <h4>Exporter cette mission</h4>
              <p>Téléchargez un rapport complet incluant tous les détails, livrables et évaluations</p>
            </div>
          </div>
          <div class="export-actions">
            <button class="btn-export-pdf" @click="exportMission('pdf')" :disabled="exporting">
              <i class="fas fa-file-pdf"></i> PDF
            </button>
            <button class="btn-export-csv" @click="exportMission('csv')" :disabled="exporting">
              <i class="fas fa-file-csv"></i> CSV
            </button>
            <button class="btn-export-excel" @click="exportMission('excel')" :disabled="exporting">
              <i class="fas fa-file-excel"></i> Excel
            </button>
          </div>
        </div>
      </div>

      <!-- Résumé de la mission -->
      <div class="summary-section">
        <div class="mission-card-completed">
          <div class="mission-header">
            <h2>{{ mission.title || 'Mission' }}</h2>
            <div class="status-badge completed">
              <i class="fas fa-check-circle"></i> Terminée
            </div>
          </div>
          
          <div class="mission-meta">
            <div class="meta-item">
              <i class="far fa-calendar"></i>
              <span>Créée le: {{ formatDate(mission.created_at) }}</span>
            </div>
            <div class="meta-item" v-if="mission.client_name">
              <i class="fas fa-user-tie"></i>
              <span>Client: {{ mission.client_name }}</span>
            </div>
          </div>

          <div class="mission-details-grid">
            <div class="detail-item">
              <i class="far fa-calendar-alt"></i>
              <div>
                <div class="label">Durée</div>
                <div class="value">{{ calculateDuration(mission.created_at, mission.updated_at) }} jours</div>
              </div>
            </div>
            <div class="detail-item">
              <i class="fas fa-euro-sign"></i>
              <div>
                <div class="label">Budget</div>
                <div class="value">{{ formatCurrency(mission.budget) }}</div>
              </div>
            </div>
            <div class="detail-item">
              <i class="far fa-clock"></i>
              <div>
                <div class="label">Terminée le</div>
                <div class="value">{{ formatDate(mission.updated_at) }}</div>
              </div>
            </div>
            <div class="detail-item">
              <i class="fas fa-tasks"></i>
              <div>
                <div class="label">Livrables</div>
                <div class="value">{{ deliverables.length }}</div>
              </div>
            </div>
          </div>

          <div v-if="mission.description" class="mission-description">
            <h4>Description de la mission</h4>
            <p>{{ mission.description }}</p>
          </div>

          <div v-if="mission.required_skills?.length" class="skills-section">
            <h4>Compétences requises</h4>
            <div class="skills-tags">
              <span v-for="skill in mission.required_skills" :key="skill" class="skill-tag">
                {{ skill }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Section freelance -->
      <div class="freelance-section" v-if="freelance && freelance.id">
        <div class="section-header">
          <h3>Freelance ayant travaillé sur cette mission</h3>
          <button v-if="freelance.id" class="btn-view-profile" @click="viewFreelanceProfile">
            <i class="fas fa-external-link-alt"></i> Voir le profil complet
          </button>
        </div>
        
        <div class="freelance-card-completion">
          <div class="freelance-main-info">
            <div class="freelance-avatar-large" :style="avatarStyle">
              {{ freelanceInitials }}
            </div>
            <div class="freelance-info-large">
              <h4>{{ freelance.full_name || freelance.name || 'Freelance' }}</h4>
              <p class="freelance-title">{{ freelance.title || 'Freelance' }}</p>
              <div class="freelance-location" v-if="freelance.location">
                <i class="fas fa-map-marker-alt"></i> {{ freelance.location }}
              </div>
              
              <div class="freelance-rating" v-if="freelance.rating !== undefined">
                <div class="stars">
                  <span v-for="i in 5" :key="i" class="star">
                    {{ i <= Math.round(freelance.rating || 0) ? '★' : '☆' }}
                  </span>
                </div>
                <span class="rating-value">{{ freelance.rating?.toFixed(1) || '0.0' }}</span>
                <span class="rating-count" v-if="freelance.completed_projects">
                  ({{ freelance.completed_projects }} projets)
                </span>
              </div>
            </div>
          </div>

          <div class="freelance-details">
            <div v-if="freelance.description" class="freelance-description">
              <h5>À propos</h5>
              <p>{{ freelance.description }}</p>
            </div>

            <div class="freelance-stats-grid">
              <div class="stat-card">
                <div class="stat-icon">
                  <i class="fas fa-briefcase"></i>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ freelance.completed_projects || 0 }}</div>
                  <div class="stat-label">Projets réalisés</div>
                </div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon">
                  <i class="fas fa-user-check"></i>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ freelance.rating?.toFixed(1) || '0.0' }}/5</div>
                  <div class="stat-label">Note moyenne</div>
                </div>
              </div>
              
              <div class="stat-card" v-if="freelance.experience_years">
                <div class="stat-icon">
                  <i class="fas fa-calendar-alt"></i>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ freelance.experience_years }}+</div>
                  <div class="stat-label">Années d'expérience</div>
                </div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon">
                  <i class="fas fa-star"></i>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ freelance.review_count || freelance.rating_count || 0 }}</div>
                  <div class="stat-label">Avis clients</div>
                </div>
              </div>
            </div>

            <div class="freelance-skills" v-if="freelance.skills?.length || freelance.expertise_areas?.length">
              <h5>Compétences & Expertises</h5>
              <div class="skills-list">
                <span v-for="skill in (freelance.skills || freelance.expertise_areas || []).slice(0, 8)" 
                      :key="skill.id || skill" class="skill-badge">
                  {{ skill.name || skill }}
                </span>
                <span v-if="(freelance.skills || freelance.expertise_areas || []).length > 8" 
                      class="skill-badge more">
                  +{{ (freelance.skills || freelance.expertise_areas || []).length - 8 }}
                </span>
              </div>
            </div>

            <div class="freelance-contact-info" v-if="freelance.email || freelance.phone">
              <h5>Coordonnées</h5>
              <div class="contact-list">
                <div v-if="freelance.email" class="contact-item">
                  <i class="fas fa-envelope"></i>
                  <span>{{ freelance.email }}</span>
                </div>
                <div v-if="freelance.phone" class="contact-item">
                  <i class="fas fa-phone"></i>
                  <span>{{ freelance.phone }}</span>
                </div>
                <div v-if="freelance.website" class="contact-item">
                  <i class="fas fa-globe"></i>
                  <a :href="freelance.website" target="_blank">{{ freelance.website }}</a>
                </div>
              </div>
            </div>
          </div>

          <div class="freelance-actions">
            <button class="btn-rehire" @click="rehireFreelance">
              <i class="fas fa-redo"></i> Réembaucher
            </button>
            <button class="btn-message" @click="messageFreelance">
              <i class="fas fa-envelope"></i> Envoyer un message
            </button>
            <button class="btn-rate" @click="rateFreelance" v-if="!mission.rating">
              <i class="fas fa-star"></i> Évaluer
            </button>
          </div>
        </div>
      </div>

      <!-- Section livrables -->
      <div class="deliverables-section" v-if="deliverables.length > 0">
        <div class="section-header">
          <h3>Livrables acceptés ({{ deliverables.length }})</h3>
          <div class="deliverables-summary">
            <span class="summary-item">
              <i class="fas fa-file"></i> {{ deliverables.length }} fichier(s)
            </span>
            <button class="btn-download-all" @click="downloadAllDeliverables" :disabled="deliverables.length === 0">
              <i class="fas fa-download"></i> Tout télécharger
            </button>
          </div>
        </div>
        
        <div class="deliverables-grid">
          <div v-for="(deliverable, index) in deliverables" :key="deliverable.id || index" 
               class="deliverable-card">
            <div class="deliverable-header">
              <div class="deliverable-icon">
                <i :class="getFileIcon(deliverable.file_type || deliverable.file_url)"></i>
              </div>
              <div class="deliverable-title-section">
                <h5>{{ deliverable.title || `Livrable ${index + 1}` }}</h5>
                <span class="deliverable-index">#{{ index + 1 }}</span>
              </div>
              <div class="deliverable-status accepted">
                <i class="fas fa-check-circle"></i> Accepté
              </div>
            </div>
            
            <div class="deliverable-content">
              <div v-if="deliverable.description" class="deliverable-description">
                <p>{{ deliverable.description }}</p>
              </div>
              
              <div class="deliverable-meta-grid">
                <div class="meta-item" v-if="deliverable.created_at">
                  <i class="far fa-calendar-plus"></i>
                  <div>
                    <div class="label">Créé le</div>
                    <div class="value">{{ formatDate(deliverable.created_at) }}</div>
                  </div>
                </div>
                
                <div class="meta-item" v-if="deliverable.accepted_at">
                  <i class="far fa-calendar-check"></i>
                  <div>
                    <div class="label">Accepté le</div>
                    <div class="value">{{ formatDate(deliverable.accepted_at) }}</div>
                  </div>
                </div>
                
                <div class="meta-item" v-if="deliverable.file_size">
                  <i class="fas fa-weight"></i>
                  <div>
                    <div class="label">Taille</div>
                    <div class="value">{{ getFileSize(deliverable.file_size) }}</div>
                  </div>
                </div>
                
                <div class="meta-item" v-if="deliverable.file_type">
                  <i class="fas fa-file-alt"></i>
                  <div>
                    <div class="label">Type</div>
                    <div class="value">{{ deliverable.file_type }}</div>
                  </div>
                </div>
              </div>
              
              <div class="deliverable-preview" v-if="hasPreview(deliverable)">
                <img v-if="isImage(deliverable.file_type || deliverable.file_url)" 
                     :src="deliverable.preview_url || deliverable.file_url" 
                     alt="Prévisualisation"
                     @click="openPreview(deliverable)"
                     class="preview-image">
                <div v-else-if="deliverable.thumbnail_url" 
                     class="thumbnail"
                     @click="openPreview(deliverable)"
                     :style="{ backgroundImage: `url(${deliverable.thumbnail_url})` }">
                  <div class="thumbnail-overlay">
                    <i class="fas fa-expand"></i>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="deliverable-footer">
              <div class="deliverable-actions">
                <button class="btn-download" @click="downloadDeliverable(deliverable)"
                        :title="`Télécharger ${deliverable.title}`">
                  <i class="fas fa-download"></i> Télécharger
                </button>
                <button class="btn-preview" v-if="hasPreview(deliverable)" 
                        @click="openPreview(deliverable)">
                  <i class="fas fa-eye"></i> Prévisualiser
                </button>
                <button class="btn-share" v-if="deliverable.file_url" 
                        @click="shareDeliverable(deliverable)">
                  <i class="fas fa-share-alt"></i> Partager
                </button>
              </div>
              <div class="deliverable-info">
                <span v-if="deliverable.download_count !== undefined" class="download-count">
                  <i class="fas fa-download"></i> {{ deliverable.download_count || 0 }}
                </span>
                <span v-if="deliverable.version" class="version">
                  v{{ deliverable.version }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section livrables vide -->
      <div class="no-deliverables-section" v-else>
        <div class="empty-state">
          <i class="fas fa-file-export empty-icon"></i>
          <h4>Aucun livrable disponible</h4>
          <p>Cette mission ne contient pas encore de livrables acceptés.</p>
        </div>
      </div>

      <!-- Section évaluation -->
      <div class="evaluation-section">
        <div class="section-header">
          <h3>Évaluation de la mission</h3>
          <button class="btn-add-review" @click="leaveReview" v-if="!mission.rating">
            <i class="fas fa-star"></i> Ajouter une évaluation
          </button>
        </div>
        
        <div v-if="mission.rating || mission.feedback" class="evaluation-card">
          <div class="evaluation-header">
            <div class="rating-display">
              <div class="stars-large">
                <span v-for="i in 5" :key="i" class="star-large">
                  {{ i <= (mission.rating || 0) ? '★' : '☆' }}
                </span>
              </div>
              <div class="rating-text">{{ (mission.rating || 0).toFixed(1) }}/5</div>
            </div>
            <div v-if="mission.evaluated_at" class="evaluation-date">
              Évalué le {{ formatDate(mission.evaluated_at) }}
            </div>
          </div>
          
          <div v-if="mission.feedback" class="feedback-box">
            <div class="feedback-header">
              <i class="fas fa-quote-left"></i>
              <h5>Votre avis</h5>
            </div>
            <p class="feedback-content">{{ mission.feedback }}</p>
          </div>
          
          <div v-if="freelance && mission.rating" class="evaluation-impact">
            <h5>Impact sur le profil du freelance</h5>
            <div class="impact-stats">
              <div class="impact-item">
                <div class="impact-label">Nouvelle note moyenne</div>
                <div class="impact-value">{{ freelance.rating?.toFixed(1) || '0.0' }}/5</div>
              </div>
              <div class="impact-item">
                <div class="impact-label">Projets réalisés</div>
                <div class="impact-value">{{ freelance.completed_projects || 0 }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="no-evaluation-card">
          <div class="no-evaluation-content">
            <i class="fas fa-star-half-alt"></i>
            <h4>Aucune évaluation n'a été laissée</h4>
            <p>Votre feedback aide les autres clients et améliore la qualité des services.</p>
            <button class="btn-review" @click="leaveReview">
              <i class="fas fa-star"></i> Laisser une évaluation
            </button>
          </div>
        </div>
      </div>

      <!-- Section statistiques -->
      <div class="stats-section">
        <h3>Statistiques de la mission</h3>
        <div class="stats-grid">
          <div class="stat-card-large">
            <div class="stat-icon-large">
              <i class="fas fa-chart-line"></i>
            </div>
            <div class="stat-content-large">
              <div class="stat-value-large">{{ calculateDuration(mission.created_at, mission.updated_at) }}</div>
              <div class="stat-label-large">Jours de travail</div>
            </div>
          </div>
          
          <div class="stat-card-large">
            <div class="stat-icon-large">
              <i class="fas fa-file-contract"></i>
            </div>
            <div class="stat-content-large">
              <div class="stat-value-large">{{ deliverables.length }}</div>
              <div class="stat-label-large">Livrables</div>
            </div>
          </div>
          
          <div class="stat-card-large">
            <div class="stat-icon-large">
              <i class="fas fa-euro-sign"></i>
            </div>
            <div class="stat-content-large">
              <div class="stat-value-large">{{ formatCurrency(mission.budget).replace('€', '') }}</div>
              <div class="stat-label-large">Budget total</div>
            </div>
          </div>
          
          <div class="stat-card-large">
            <div class="stat-icon-large">
              <i class="fas fa-calendar-check"></i>
            </div>
            <div class="stat-content-large">
              <div class="stat-value-large">{{ formatDate(mission.updated_at, true) }}</div>
              <div class="stat-label-large">Date de complétion</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="actions-section">
        <h3>Que souhaitez-vous faire maintenant ?</h3>
        <div class="actions-grid">
          <div class="action-card" @click="createSimilarMission">
            <div class="action-icon">
              <i class="fas fa-copy"></i>
            </div>
            <h4>Créer une mission similaire</h4>
            <p>Dupliquez cette mission pour un nouveau projet</p>
          </div>
          
          <div class="action-card" @click="rehireFreelance" v-if="freelance">
            <div class="action-icon">
              <i class="fas fa-user-plus"></i>
            </div>
            <h4>Retravailler avec {{ freelance.full_name?.split(' ')[0] || 'ce freelance' }}</h4>
            <p>Créez une nouvelle mission pour le même freelance</p>
          </div>

          <div class="action-card" @click="exportMissionReport">
            <div class="action-icon">
              <i class="fas fa-file-contract"></i>
            </div>
            <h4>Générer un rapport complet</h4>
            <p>PDF détaillé avec statistiques et livrables</p>
          </div>

          <div class="action-card" @click="viewAllMissions">
            <div class="action-icon">
              <i class="fas fa-list-ul"></i>
            </div>
            <h4>Voir toutes mes missions</h4>
            <p>Retour à la liste de vos missions</p>
          </div>
        </div>
      </div>

      <div class="completion-footer">
        <div class="footer-content">
          <div class="footer-message">
            <i class="fas fa-check-circle"></i>
            <div>
              <h4>Mission terminée avec succès !</h4>
              <p>Merci d'avoir utilisé notre plateforme pour votre projet.</p>
            </div>
          </div>
          <div class="footer-actions">
            <button class="btn-primary" @click="viewAllMissions">
              <i class="fas fa-arrow-left"></i> Retour aux missions
            </button>
            <button class="btn-secondary" @click="contactSupport">
              <i class="fas fa-headset"></i> Support
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMissionStore } from '@/stores/missions'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const missionStore = useMissionStore()
const authStore = useAuthStore()

const missionId = route.params.missionId

const mission = ref({})
const freelance = ref(null)
const deliverables = ref([])
const loading = ref(true)
const error = ref('')
const exporting = ref(false)

const freelanceInitials = computed(() => {
  if (!freelance.value) return 'F'
  
  const name = freelance.value.full_name || freelance.value.name || 'Freelance'
  return name
    .split(' ')
    .map(name => name[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const avatarStyle = computed(() => {
  if (!freelance.value) return {}
  
  if (freelance.value.avatar_url) {
    return {
      backgroundImage: `url(${freelance.value.avatar_url})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  
  // Générer une couleur basée sur l'ID du freelance
  const colors = [
    'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
    'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
    'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
  ]
  
  const id = freelance.value.id || 0
  const colorIndex = id % colors.length
  
  return {
    background: colors[colorIndex]
  }
})

onMounted(async () => {
  if (!missionId) {
    error.value = "ID de mission manquant"
    loading.value = false
    return
  }
  await loadCompletionData()
})

const loadCompletionData = async () => {
  try {
    loading.value = true
    error.value = ''
    
    // 1. Charger les détails de base de la mission
    await missionStore.fetchMissionDetails(missionId)
    mission.value = missionStore.currentMission || {}
    
    // 2. Charger les détails de complétion (freelance + livrables)
    try {
      const completionData = await missionStore.fetchMissionCompletionDetails(missionId)
      
      if (completionData) {
        // Gestion du freelance
        freelance.value = completionData.freelance || completionData.accepted_freelance || null
        
        // Gestion des livrables
        if (completionData.deliverables && Array.isArray(completionData.deliverables)) {
          deliverables.value = completionData.deliverables.map(d => ({
            id: d.id,
            title: d.title || `Livrable ${d.id}`,
            description: d.description,
            file_url: d.file_url,
            file_type: d.file_type || getFileTypeFromUrl(d.file_url),
            created_at: d.created_at,
            accepted_at: d.accepted_at,
            file_size: d.file_size,
            download_count: d.download_count,
            version: d.version
          }))
        }
        
        // Si le freelance n'est pas dans completionData, chercher dans la mission
        if (!freelance.value && mission.value.accepted_freelance) {
          freelance.value = mission.value.accepted_freelance
        }
      }
    } catch (completionError) {
      console.log('API completion non disponible, utilisation des données alternatives:', completionError)
      
      // Fallback: chercher le freelance via l'API des candidatures acceptées
      try {
        const acceptedApplication = await missionStore.fetchAcceptedFreelance(missionId)
        if (acceptedApplication) {
          freelance.value = acceptedApplication.freelance || acceptedApplication
        }
      } catch (freelanceError) {
        console.log('Erreur chargement freelance:', freelanceError)
      }
      
      // Fallback pour les livrables
      deliverables.value = mission.value.deliverables || []
    }
    
    // 3. Si toujours pas de freelance, essayer de trouver dans les postulations
    if (!freelance.value) {
      try {
        const applications = await missionStore.fetchMissionApplications(missionId)
        const acceptedApp = applications.find(app => app.status === 'accepted')
        if (acceptedApp && acceptedApp.freelance_id) {
          freelance.value = {
            id: acceptedApp.freelance_id,
            full_name: acceptedApp.freelance_name || 'Freelance',
            title: acceptedApp.profile_title || 'Freelance',
            rating: acceptedApp.rating || 0,
            completed_projects: acceptedApp.completed_projects || 0
          }
        }
      } catch (appError) {
        console.log('Erreur chargement candidatures:', appError)
      }
    }
    
    // 4. Données par défaut pour le débogage
    if (Object.keys(mission.value).length === 0) {
      mission.value = {
        id: missionId,
        title: 'Mission complétée',
        description: 'Mission terminée avec succès',
        budget: 1000,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        status: 'completed',
        required_skills: ['Design', 'Développement']
      }
    }
    
  } catch (err) {
    console.error('Erreur lors du chargement des données:', err)
    error.value = "Impossible de charger les données de la mission"
    
    // Données de secours pour le débogage
    mission.value = {
      title: 'Mission de test',
      budget: 1500,
      created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date().toISOString(),
      description: 'Description de test pour la mission complétée',
      required_skills: ['Vue.js', 'Node.js', 'UI/UX Design']
    }
    
    freelance.value = {
      id: 1,
      full_name: 'Jean Dupont',
      title: 'Développeur Full Stack',
      rating: 4.5,
      completed_projects: 12,
      description: 'Développeur expérimenté avec 5 ans d\'expérience',
      skills: ['JavaScript', 'Vue.js', 'Node.js', 'API Design']
    }
    
    deliverables.value = [
      {
        id: 1,
        title: 'Documentation technique',
        description: 'Documentation complète du projet',
        file_url: '#',
        file_type: 'pdf',
        created_at: new Date().toISOString(),
        accepted_at: new Date().toISOString(),
        file_size: 2048000
      },
      {
        id: 2,
        title: 'Code source final',
        description: 'Archive contenant tous les fichiers sources',
        file_url: '#',
        file_type: 'zip',
        created_at: new Date().toISOString(),
        accepted_at: new Date().toISOString(),
        file_size: 5120000
      }
    ]
  } finally {
    loading.value = false
  }
}

const getFileTypeFromUrl = (url) => {
  if (!url) return 'unknown'
  const extension = url.split('.').pop().toLowerCase()
  const typeMap = {
    'pdf': 'PDF Document',
    'doc': 'Word Document',
    'docx': 'Word Document',
    'xls': 'Excel Document',
    'xlsx': 'Excel Document',
    'zip': 'Archive ZIP',
    'rar': 'Archive RAR',
    'jpg': 'Image JPEG',
    'jpeg': 'Image JPEG',
    'png': 'Image PNG',
    'gif': 'Image GIF',
    'mp4': 'Vidéo MP4',
    'mov': 'Vidéo MOV',
    'avi': 'Vidéo AVI'
  }
  return typeMap[extension] || 'Fichier'
}

const formatDate = (dateString, short = false) => {
  if (!dateString) return 'Non spécifié'
  try {
    const date = new Date(dateString)
    if (short) {
      return date.toLocaleDateString('fr-FR')
    }
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return 'Date invalide'
  }
}

const formatCurrency = (amount) => {
  if (!amount && amount !== 0) return 'Non spécifié'
  try {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(amount)
  } catch (e) {
    return `${amount} €`
  }
}

const calculateDuration = (start, end) => {
  if (!start || !end) return 0
  try {
    const startDate = new Date(start)
    const endDate = new Date(end)
    const diffTime = Math.abs(endDate - startDate)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  } catch (e) {
    return 0
  }
}

const getFileIcon = (fileType) => {
  if (!fileType) return 'fas fa-file'
  
  const icons = {
    'pdf': 'fas fa-file-pdf',
    'doc': 'fas fa-file-word',
    'docx': 'fas fa-file-word',
    'xls': 'fas fa-file-excel',
    'xlsx': 'fas fa-file-excel',
    'zip': 'fas fa-file-archive',
    'rar': 'fas fa-file-archive',
    'jpg': 'fas fa-file-image',
    'jpeg': 'fas fa-file-image',
    'png': 'fas fa-file-image',
    'gif': 'fas fa-file-image',
    'mp4': 'fas fa-file-video',
    'mov': 'fas fa-file-video',
    'avi': 'fas fa-file-video'
  }
  
  if (typeof fileType === 'string') {
    const extension = fileType.split('.').pop().toLowerCase()
    return icons[extension] || 'fas fa-file'
  }
  
  return 'fas fa-file'
}

const getFileSize = (bytes) => {
  if (!bytes) return 'Taille inconnue'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

const isImage = (fileType) => {
  if (!fileType) return false
  const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']
  const extension = fileType.split('.').pop().toLowerCase()
  return imageTypes.includes(extension)
}

const hasPreview = (deliverable) => {
  return isImage(deliverable.file_type) || 
         deliverable.preview_url || 
         deliverable.thumbnail_url ||
         deliverable.file_type?.includes('pdf')
}

// Actions principales
const exportMission = async (format) => {
  try {
    exporting.value = true
    await missionStore.exportMissions(format, { mission_id: missionId })
  } catch (err) {
    console.error('Erreur export:', err)
    error.value = 'Erreur lors de l\'export de la mission'
    
    // Fallback
    const token = authStore.token || localStorage.getItem('token')
    const exportUrl = `/api/missions/${missionId}/export?format=${format}`
    if (token) {
      window.open(`${exportUrl}&token=${token}`, '_blank')
    }
  } finally {
    exporting.value = false
  }
}

const exportMissionReport = () => {
  exportMission('pdf')
}

const viewFreelanceProfile = () => {
  if (freelance.value?.id) {
    router.push(`/freelances/${freelance.value.id}`)
  }
}

const rehireFreelance = () => {
  if (freelance.value?.id) {
    router.push({
      name: 'create-mission',
      query: { 
        freelance_id: freelance.value.id,
        duplicate_from: missionId 
      }
    })
  }
}

const messageFreelance = () => {
  if (freelance.value?.id) {
    router.push({
      name: 'messages',
      query: { 
        user_id: freelance.value.user_id || freelance.value.id,
        mission_id: missionId 
      }
    })
  }
}

const rateFreelance = () => {
  leaveReview()
}

const downloadDeliverable = async (deliverable) => {
  try {
    if (deliverable.file_url) {
      window.open(deliverable.file_url, '_blank')
    } else {
      console.log('Aucun URL de fichier disponible')
    }
  } catch (err) {
    console.error('Erreur téléchargement livrable:', err)
    error.value = 'Erreur lors du téléchargement'
  }
}

const downloadAllDeliverables = async () => {
  try {
    const token = authStore.token || localStorage.getItem('token')
    const downloadUrl = `/api/missions/${missionId}/deliverables/archive`
    
    if (token) {
      window.open(`${downloadUrl}?token=${token}`, '_blank')
    }
  } catch (err) {
    console.error('Erreur téléchargement archive:', err)
    error.value = 'Erreur lors du téléchargement de l\'archive'
  }
}

const openPreview = (deliverable) => {
  if (deliverable.preview_url) {
    window.open(deliverable.preview_url, '_blank')
  } else if (deliverable.file_url) {
    window.open(deliverable.file_url, '_blank')
  }
}

const shareDeliverable = async (deliverable) => {
  try {
    if (navigator.share && deliverable.file_url) {
      await navigator.share({
        title: deliverable.title,
        text: `Livrable de la mission ${mission.value.title}`,
        url: deliverable.file_url
      })
    } else {
      // Copier le lien dans le presse-papier
      await navigator.clipboard.writeText(deliverable.file_url)
      alert('Lien copié dans le presse-papier !')
    }
  } catch (err) {
    console.error('Erreur partage:', err)
  }
}

const createSimilarMission = () => {
  router.push({
    path: '/missions/create',
    query: { duplicate_from: missionId }
  })
}

const viewAllMissions = () => {
  router.push('/client/missions')
}

const contactSupport = () => {
  router.push('/support')
}

const leaveReview = () => {
  router.push({
    name: 'mission-review',
    params: { missionId: missionId }
  })
}
</script>

<style scoped>
.mission-completion-page {
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 30px 20px;
  min-height: calc(100vh - 80px);
  background: #f8fafc;
}

.completion-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 30px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.completion-header h1 {
  font-size: 32px;
  color: #1e293b;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: #64748b;
  font-size: 18px;
}

/* États */
.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e2e8f0;
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.error-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.error-state i {
  font-size: 48px;
  color: #ef4444;
  margin-bottom: 20px;
}

.error-state p {
  color: #64748b;
  margin-bottom: 20px;
}

.btn-retry {
  background: #3b82f6;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: background 0.3s ease;
}

.btn-retry:hover {
  background: #2563eb;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Export Section */
.export-section {
  margin-bottom: 30px;
}

.export-card {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 16px;
  padding: 24px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.export-content {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.export-icon {
  font-size: 48px;
  color: #60a5fa;
}

.export-content h4 {
  font-size: 20px;
  margin: 0 0 8px;
  color: white;
}

.export-content p {
  color: #cbd5e1;
  margin: 0;
  font-size: 14px;
}

.export-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-export-pdf,
.btn-export-csv,
.btn-export-excel {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-export-pdf {
  background: #ef4444;
  color: white;
}

.btn-export-csv {
  background: #10b981;
  color: white;
}

.btn-export-excel {
  background: #059669;
  color: white;
}

.btn-export-pdf:hover:not(:disabled),
.btn-export-csv:hover:not(:disabled),
.btn-export-excel:hover:not(:disabled) {
  transform: translateY(-2px);
  opacity: 0.9;
}

.btn-export-pdf:disabled,
.btn-export-csv:disabled,
.btn-export-excel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Mission Card */
.mission-card-completed {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 2px solid #10b981;
  margin-bottom: 30px;
}

.mission-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.mission-header h2 {
  font-size: 24px;
  color: #1e293b;
  margin: 0;
}

.status-badge.completed {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.mission-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8fafc;
  border-radius: 12px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 14px;
}

.mission-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8fafc;
  border-radius: 12px;
}

.detail-item i {
  font-size: 20px;
  color: #64748b;
}

.detail-item .label {
  font-size: 12px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-item .value {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

.mission-description,
.skills-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.mission-description h4,
.skills-section h4 {
  font-size: 16px;
  color: #475569;
  margin-bottom: 10px;
}

.mission-description p {
  color: #475569;
  line-height: 1.6;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag {
  background: #dbeafe;
  color: #1e40af;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

/* Section Headers */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.section-header h3 {
  font-size: 20px;
  color: #1e293b;
  margin: 0;
}

/* Boutons génériques */
.btn-view-profile,
.btn-download-all,
.btn-add-review {
  background: #3b82f6;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-view-profile:hover,
.btn-download-all:hover,
.btn-add-review:hover {
  background: #2563eb;
  transform: translateY(-2px);
}

/* Freelance Card */
.freelance-card-completion {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.freelance-main-info {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 24px;
}

.freelance-avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 24px;
  flex-shrink: 0;
}

.freelance-info-large {
  flex: 1;
}

.freelance-info-large h4 {
  font-size: 20px;
  color: #1e293b;
  margin: 0 0 5px;
}

.freelance-title {
  color: #64748b;
  margin: 0 0 10px;
  font-size: 14px;
}

.freelance-location {
  color: #94a3b8;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 10px;
}

.freelance-rating {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stars {
  display: flex;
  gap: 2px;
}

.star {
  font-size: 16px;
  color: #ffd700;
}

.rating-value {
  font-weight: 600;
  color: #1e293b;
}

.rating-count {
  color: #64748b;
  font-size: 14px;
}

/* Freelance Details */
.freelance-details {
  margin: 24px 0;
}

.freelance-description {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.freelance-description h5 {
  font-size: 16px;
  color: #475569;
  margin-bottom: 8px;
}

.freelance-description p {
  color: #64748b;
  line-height: 1.6;
  margin: 0;
}

.freelance-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin: 24px 0;
}

.stat-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: #cbd5e1;
}

.stat-icon {
  font-size: 24px;
  color: #3b82f6;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 2px;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Freelance Skills */
.freelance-skills {
  margin: 20px 0;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
}

.freelance-skills h5 {
  font-size: 16px;
  color: #475569;
  margin-bottom: 12px;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-badge {
  background: white;
  color: #475569;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.skill-badge:hover {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.skill-badge.more {
  background: #e2e8f0;
  color: #64748b;
}

/* Freelance Contact */
.freelance-contact-info {
  margin: 20px 0;
  padding: 20px;
  background: #f1f5f9;
  border-radius: 12px;
}

.freelance-contact-info h5 {
  font-size: 16px;
  color: #475569;
  margin-bottom: 12px;
}

.contact-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #64748b;
  font-size: 14px;
}

.contact-item i {
  color: #3b82f6;
  width: 20px;
}

.contact-item a {
  color: #3b82f6;
  text-decoration: none;
}

.contact-item a:hover {
  text-decoration: underline;
}

/* Freelance Actions */
.freelance-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 20px;
}

.btn-rehire,
.btn-message,
.btn-rate {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-rehire {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.btn-message {
  background: white;
  color: #475569;
  border: 2px solid #e2e8f0;
}

.btn-rate {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.btn-rehire:hover,
.btn-message:hover,
.btn-rate:hover {
  transform: translateY(-2px);
}

.btn-message:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
}

/* Deliverables Section */
.deliverables-summary {
  display: flex;
  align-items: center;
  gap: 16px;
}

.summary-item {
  color: #64748b;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.deliverables-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.deliverable-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.deliverable-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border-color: #cbd5e1;
}

.deliverable-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.deliverable-icon {
  font-size: 32px;
  color: #3b82f6;
  flex-shrink: 0;
}

.deliverable-title-section {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.deliverable-title-section h5 {
  font-size: 18px;
  color: #1e293b;
  margin: 0;
}

.deliverable-index {
  background: #e2e8f0;
  color: #64748b;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
}

.deliverable-status.accepted {
  background: #10b981;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.deliverable-content {
  margin: 16px 0;
}

.deliverable-description {
  color: #64748b;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 20px;
}

.deliverable-meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin: 20px 0;
}

.deliverable-meta-grid .meta-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
}

.deliverable-meta-grid .meta-item i {
  font-size: 18px;
  color: #64748b;
}

.deliverable-meta-grid .label {
  font-size: 11px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.deliverable-meta-grid .value {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}

/* Preview */
.deliverable-preview {
  margin: 20px 0;
}

.preview-image {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.preview-image:hover {
  transform: scale(1.02);
}

.thumbnail {
  width: 100%;
  height: 150px;
  border-radius: 8px;
  background-size: cover;
  background-position: center;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.thumbnail-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.thumbnail:hover .thumbnail-overlay {
  opacity: 1;
}

/* Deliverable Footer */
.deliverable-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
  flex-wrap: wrap;
  gap: 16px;
}

.deliverable-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-download,
.btn-preview,
.btn-share {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-download {
  background: #10b981;
  color: white;
}

.btn-download:hover {
  background: #059669;
}

.btn-preview {
  background: #8b5cf6;
  color: white;
}

.btn-preview:hover {
  background: #7c3aed;
}

.btn-share {
  background: #f59e0b;
  color: white;
}

.btn-share:hover {
  background: #d97706;
}

.deliverable-info {
  display: flex;
  gap: 16px;
  color: #94a3b8;
  font-size: 12px;
}

.download-count,
.version {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* No Deliverables */
.no-deliverables-section {
  background: white;
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.empty-state .empty-icon {
  font-size: 48px;
  color: #cbd5e1;
  margin-bottom: 16px;
}

.empty-state h4 {
  color: #64748b;
  margin-bottom: 8px;
}

.empty-state p {
  color: #94a3b8;
  margin: 0;
}

/* Evaluation Section */
.evaluation-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.evaluation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.rating-display {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stars-large {
  display: flex;
  gap: 4px;
}

.star-large {
  font-size: 28px;
  color: #ffd700;
}

.rating-text {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.evaluation-date {
  color: #64748b;
  font-size: 14px;
}

.feedback-box {
  background: #f8fafc;
  padding: 20px;
  border-radius: 12px;
  border-left: 4px solid #10b981;
  margin: 20px 0;
}

.feedback-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.feedback-header i {
  color: #10b981;
  font-size: 20px;
}

.feedback-header h5 {
  font-size: 16px;
  color: #475569;
  margin: 0;
}

.feedback-content {
  color: #475569;
  line-height: 1.6;
  margin: 0;
  font-style: italic;
}

.evaluation-impact {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}

.evaluation-impact h5 {
  font-size: 16px;
  color: #475569;
  margin-bottom: 16px;
}

.impact-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.impact-item {
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.impact-label {
  font-size: 12px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.impact-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

/* No Evaluation */
.no-evaluation-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.no-evaluation-content i {
  font-size: 48px;
  color: #f59e0b;
  margin-bottom: 16px;
}

.no-evaluation-content h4 {
  color: #475569;
  margin-bottom: 8px;
}

.no-evaluation-content p {
  color: #94a3b8;
  margin-bottom: 20px;
}

.btn-review {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

/* Stats Section */
.stats-section {
  margin: 40px 0;
}

.stats-section h3 {
  font-size: 20px;
  color: #1e293b;
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.stat-card-large {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.3s ease;
}

.stat-card-large:hover {
  transform: translateY(-4px);
}

.stat-icon-large {
  font-size: 36px;
  color: #3b82f6;
}

.stat-content-large {
  flex: 1;
}

.stat-value-large {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.stat-label-large {
  font-size: 14px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Actions Section */
.actions-section {
  margin: 40px 0;
}

.actions-section h3 {
  font-size: 20px;
  color: #1e293b;
  margin-bottom: 24px;
  text-align: center;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.action-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.action-card:hover {
  transform: translateY(-4px);
  border-color: #10b981;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.action-icon {
  font-size: 36px;
  color: #3b82f6;
  margin-bottom: 16px;
}

.action-card h4 {
  font-size: 18px;
  color: #1e293b;
  margin: 0 0 8px;
  line-height: 1.4;
}

.action-card p {
  color: #64748b;
  font-size: 14px;
  margin: 0;
  line-height: 1.5;
}

/* Completion Footer */
.completion-footer {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-top: 40px;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 30px;
}

.footer-message {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.footer-message i {
  font-size: 48px;
  color: #10b981;
}

.footer-message h4 {
  font-size: 20px;
  color: #1e293b;
  margin: 0 0 8px;
}

.footer-message p {
  color: #64748b;
  margin: 0;
}

.footer-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary {
  padding: 12px 28px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-2px);
}

.btn-secondary {
  background: white;
  color: #475569;
  border: 2px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  transform: translateY(-2px);
}

/* Responsive */
@media (max-width: 768px) {
  .mission-completion-page {
    margin-top: 60px;
    padding: 20px 15px;
  }
  
  .completion-header h1 {
    font-size: 24px;
  }
  
  .export-card {
    flex-direction: column;
    text-align: center;
  }
  
  .export-content {
    flex-direction: column;
    text-align: center;
  }
  
  .mission-details-grid {
    grid-template-columns: 1fr;
  }
  
  .freelance-main-info {
    flex-direction: column;
    text-align: center;
  }
  
  .freelance-stats-grid,
  .stats-grid,
  .impact-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .freelance-actions,
  .deliverable-footer,
  .footer-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .deliverable-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .deliverable-title-section {
    width: 100%;
    justify-content: space-between;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .freelance-stats-grid,
  .stats-grid,
  .impact-stats,
  .deliverable-meta-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .deliverables-summary {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>