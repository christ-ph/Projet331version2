<!-- src/views/MissionDetails.vue -->
<template>
  <div class="mission-details-page">
    <!-- En-tête -->
    <div class="mission-details-header">
      <div class="container">
        <button class="back-button" @click="$router.go(-1)">
          <i class="fas fa-arrow-left"></i>
          Retour
        </button>
        <h1 class="mission-title">{{ mission.title }}</h1>
        <div class="mission-meta">
          <span class="mission-category">
            <i :class="getCategoryIcon(mission.category)"></i>
            {{ getCategoryLabel(mission.category) }}
          </span>
          <span class="mission-date">
            <i class="far fa-clock"></i>
            Publiée le {{ formatDate(mission.created_at) }}
          </span>
        </div>
      </div>
    </div>

    <div class="container">
      <div class="mission-details-content">
        <!-- Colonne principale -->
        <div class="main-column">
          <!-- Description -->
          <section class="mission-section">
            <h2 class="section-title">
              <i class="fas fa-align-left"></i>
              Description de la mission
            </h2>
            <div class="description-content">
              <p>{{ mission.description }}</p>
            </div>
          </section>

          <!-- Compétences requises -->
          <section class="mission-section" v-if="missionSkills.length > 0">
            <h2 class="section-title">
              <i class="fas fa-tools"></i>
              Compétences requises
            </h2>
            <div class="skills-container">
              <div 
                v-for="skill in missionSkills" 
                :key="skill"
                class="skill-item"
                :class="{ 'match': userHasSkill(skill) }"
              >
                {{ skill }}
                <i v-if="userHasSkill(skill)" class="fas fa-check"></i>
              </div>
            </div>
            <div v-if="matchingSkillsCount > 0" class="match-info">
              <i class="fas fa-thumbs-up"></i>
              Vous correspondez à {{ matchingSkillsCount }} compétence(s) sur {{ missionSkills.length }}
            </div>
          </section>

          <!-- Détails supplémentaires -->
          <section class="mission-section">
            <h2 class="section-title">
              <i class="fas fa-info-circle"></i>
              Détails supplémentaires
            </h2>
            <div class="details-grid">
              <div class="detail-card">
                <div class="detail-icon">
                  <i class="fas fa-calendar-alt"></i>
                </div>
                <div class="detail-info">
                  <h3>Deadline</h3>
                  <p>{{ mission.deadline ? formatDate(mission.deadline) : 'Non spécifiée' }}</p>
                </div>
              </div>
              
              <div class="detail-card">
                <div class="detail-icon">
                  <i class="fas fa-clock"></i>
                </div>
                <div class="detail-info">
                  <h3>Durée estimée</h3>
                  <p>{{ estimateDuration(mission) }}</p>
                </div>
              </div>
              
              <div class="detail-card">
                <div class="detail-icon">
                  <i class="fas fa-users"></i>
                </div>
                <div class="detail-info">
                  <h3>Candidats</h3>
                  <p>{{ mission.postulations_total || 0 }} freelance(s) ont postulé</p>
                </div>
              </div>
              
              <div class="detail-card">
                <div class="detail-icon">
                  <i class="fas fa-map-marker-alt"></i>
                </div>
                <div class="detail-info">
                  <h3>Localisation</h3>
                  <p>{{ mission.location || 'À distance' }}</p>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- Sidebar -->
        <div class="sidebar-column">
          <!-- Carte budget -->
          <div class="budget-card">
            <div class="budget-header">
              <h3>
                <i class="fas fa-money-bill-wave"></i>
                Budget
              </h3>
            </div>
            <div class="budget-content">
              <div class="budget-amount">
                {{ mission.budget ? mission.budget.toLocaleString() + ' FCFA' : 'À discuter' }}
              </div>
              <p class="budget-note">
                {{ mission.budget ? 'Budget fixe pour la mission' : 'Budget à négocier avec le client' }}
              </p>
            </div>
          </div>

          <!-- Carte client -->
          <div class="client-card">
            <div class="client-header">
              <h3>
                <i class="fas fa-user-tie"></i>
                Client
              </h3>
            </div>
            <div class="client-content">
              <div class="client-avatar">
                {{ getClientInitials(mission.client_name) }}
              </div>
              <div class="client-info">
                <h4>{{ mission.client_name || `Client #${mission.client_id}` }}</h4>
                <div class="client-stats">
                  <div class="stat">
                    <i class="fas fa-star"></i>
                    <span>4.8/5</span>
                  </div>
                  <div class="stat">
                    <i class="fas fa-check-circle"></i>
                    <span>Vérifié</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="actions-card">
            <button 
              v-if="!mission.applied"
              class="action-button apply-button"
              @click="applyToMission"
              :disabled="loading"
            >
              <i class="fas fa-paper-plane"></i>
              Postuler à cette mission
            </button>
            
            <button 
              v-else
              class="action-button applied-button"
              disabled
            >
              <i class="fas fa-check-circle"></i>
              Vous avez déjà postulé
            </button>
            
            <button 
              class="action-button secondary-button"
              @click="toggleSaveMission"
            >
              <i :class="mission.saved ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
              {{ mission.saved ? 'Retirer des sauvegardes' : 'Sauvegarder la mission' }}
            </button>
            
            <button 
              class="action-button outline-button"
              @click="shareMission"
            >
              <i class="fas fa-share-alt"></i>
              Partager
            </button>
          </div>

          <!-- Contact -->
          <div class="contact-card">
            <h3>
              <i class="fas fa-question-circle"></i>
              Questions ?
            </h3>
            <p>Contactez le support pour toute question concernant cette mission.</p>
            <button class="contact-button">
              <i class="fas fa-envelope"></i>
              Contacter
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import missionService from '@/services/missionService';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const loading = ref(true);
const mission = ref({});
const userSkills = ref([]);

// Charger la mission
const loadMission = async () => {
  try {
    loading.value = true;
    const missionId = route.params.id;
    
    // Charger les données de la mission
    const missionData = await missionService.getMissionById(missionId);
    mission.value = missionData;
    
    // Charger les compétences de l'utilisateur
    await loadUserSkills();
    
    // Vérifier si l'utilisateur a déjà postulé
    await checkIfApplied();
    
    // Vérifier si la mission est sauvegardée
    checkIfSaved();
    
  } catch (error) {
    console.error('Erreur lors du chargement de la mission:', error);
    router.push('/missions');
  } finally {
    loading.value = false;
  }
};

const loadUserSkills = async () => {
  try {
    const skills = await missionService.getUserSkills();
    userSkills.value = skills;
  } catch (error) {
    console.error('Erreur lors du chargement des compétences:', error);
    userSkills.value = [];
  }
};

const checkIfApplied = async () => {
  try {
    const applications = await missionService.getMyApplications();
    mission.value.applied = applications.some(app => app.mission_id == route.params.id);
  } catch (error) {
    console.error('Erreur lors de la vérification de la candidature:', error);
    mission.value.applied = false;
  }
};

const checkIfSaved = () => {
  try {
    const saved = localStorage.getItem('savedMissions');
    if (saved) {
      const savedMissions = JSON.parse(saved);
      mission.value.saved = savedMissions.includes(route.params.id);
    }
  } catch (error) {
    mission.value.saved = false;
  }
};

// Computed properties
const missionSkills = computed(() => {
  if (!mission.value.required_skills) return [];
  if (Array.isArray(mission.value.required_skills)) {
    return mission.value.required_skills;
  }
  if (typeof mission.value.required_skills === 'string') {
    return mission.value.required_skills.split(',').map(s => s.trim());
  }
  return [];
});

const matchingSkillsCount = computed(() => {
  return missionSkills.value.filter(skill => 
    userSkills.value.some(userSkill => 
      userSkill.toLowerCase().includes(skill.toLowerCase()) ||
      skill.toLowerCase().includes(userSkill.toLowerCase())
    )
  ).length;
});

// Méthodes utilitaires
const getCategoryIcon = (category) => {
  const categories = {
    'web': 'fas fa-code',
    'mobile': 'fas fa-mobile-alt',
    'design': 'fas fa-paint-brush',
    'marketing': 'fas fa-bullhorn',
    'writing': 'fas fa-pen-fancy',
    'video': 'fas fa-video',
    'default': 'fas fa-briefcase'
  };
  return categories[category] || categories.default;
};

const getCategoryLabel = (category) => {
  const labels = {
    'web': 'Développement Web',
    'mobile': 'Mobile',
    'design': 'Design',
    'marketing': 'Marketing',
    'writing': 'Rédaction',
    'video': 'Vidéo/Montage',
    'default': 'Mission'
  };
  return labels[category] || labels.default;
};

const formatDate = (dateString) => {
  if (!dateString) return 'Non spécifiée';
  return new Date(dateString).toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const estimateDuration = (mission) => {
  if (!mission.budget) return 'Non spécifiée';
  
  const budget = Number(mission.budget);
  if (isNaN(budget)) return 'Non spécifiée';
  
  if (budget < 50000) return '1-2 semaines';
  if (budget < 200000) return '2-4 semaines';
  if (budget < 500000) return '1-2 mois';
  return '2-4 mois';
};

const getClientInitials = (clientName) => {
  if (!clientName || !clientName.includes('#')) return 'C';
  const match = clientName.match(/#(\d+)/);
  return match ? `C${match[1]}` : 'C';
};

const userHasSkill = (skill) => {
  return userSkills.value.some(userSkill => 
    userSkill.toLowerCase().includes(skill.toLowerCase()) ||
    skill.toLowerCase().includes(userSkill.toLowerCase())
  );
};

// Actions
const applyToMission = async () => {
  try {
    loading.value = true;
    await missionService.applyToMission(mission.value.id);
    mission.value.applied = true;
    alert('Votre candidature a été envoyée avec succès !');
  } catch (error) {
    console.error('Erreur lors de la candidature:', error);
    alert('Erreur: ' + (error.response?.data?.error || error.message));
  } finally {
    loading.value = false;
  }
};

const toggleSaveMission = async () => {
  try {
    if (mission.value.saved) {
      // Retirer de la liste
      const saved = localStorage.getItem('savedMissions');
      if (saved) {
        const savedMissions = JSON.parse(saved);
        const updated = savedMissions.filter(id => id != mission.value.id);
        localStorage.setItem('savedMissions', JSON.stringify(updated));
      }
      mission.value.saved = false;
    } else {
      // Ajouter à la liste
      const saved = localStorage.getItem('savedMissions');
      const savedMissions = saved ? JSON.parse(saved) : [];
      savedMissions.push(mission.value.id);
      localStorage.setItem('savedMissions', JSON.stringify(savedMissions));
      mission.value.saved = true;
    }
    
    // Appeler l'API si disponible
    try {
      await missionService.saveMission(mission.value.id);
    } catch (apiError) {
      console.warn('API save non disponible, utilisation du localStorage');
    }
    
  } catch (error) {
    console.error('Erreur lors de la sauvegarde:', error);
  }
};

const shareMission = () => {
  if (navigator.share) {
    navigator.share({
      title: mission.value.title,
      text: `Découvrez cette mission : ${mission.value.title}`,
      url: window.location.href
    });
  } else {
    navigator.clipboard.writeText(window.location.href);
    alert('Lien copié dans le presse-papier !');
  }
};

onMounted(() => {
  loadMission();
});
</script>

<style scoped>
.mission-details-page {
  min-height: 100vh;
  background: #f8fafc;
  padding-top: 70px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Header */
.mission-details-header {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  color: white;
  padding: 40px 0;
  position: relative;
  overflow: hidden;
}

.mission-details-header::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  transform: translate(30%, -30%);
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(-2px);
}

.mission-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 16px 0;
  line-height: 1.2;
}

.mission-meta {
  display: flex;
  gap: 20px;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.85);
}

.mission-category, .mission-date {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mission-category i {
  color: #60a5fa;
}

.mission-date i {
  color: #9ca3af;
}

/* Contenu principal */
.mission-details-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
  padding: 40px 0;
}

/* Colonne principale */
.main-column {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.mission-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.3rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 20px 0;
}

.section-title i {
  color: #3b82f6;
  font-size: 1.1rem;
}

.description-content {
  line-height: 1.6;
  color: #4b5563;
  font-size: 1rem;
}

/* Compétences */
.skills-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 16px;
}

.skill-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f9fafb;
  border: 1.5px solid #e5e7eb;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #6b7280;
  font-weight: 500;
  transition: all 0.2s ease;
}

.skill-item.match {
  background: #d1fae5;
  border-color: #10b981;
  color: #065f46;
}

.skill-item.match i {
  color: #10b981;
  font-size: 0.8rem;
}

.match-info {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  background: #dbeafe;
  border-radius: 8px;
  color: #1e40af;
  font-weight: 600;
  font-size: 0.9rem;
}

.match-info i {
  color: #3b82f6;
}

/* Détails supplémentaires */
.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.detail-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 10px;
  border: 1px solid #f3f4f6;
  transition: all 0.3s ease;
}

.detail-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.detail-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.detail-info h3 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #6b7280;
  margin: 0 0 4px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-info p {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

/* Sidebar */
.sidebar-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Carte budget */
.budget-card, .client-card, .actions-card, .contact-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.budget-header, .client-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.budget-header h3, .client-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.budget-header i {
  color: #10b981;
}

.client-header i {
  color: #3b82f6;
}

.budget-content {
  text-align: center;
}

.budget-amount {
  font-size: 2rem;
  font-weight: 700;
  color: #10b981;
  margin-bottom: 8px;
}

.budget-note {
  font-size: 0.9rem;
  color: #6b7280;
  margin: 0;
}

/* Carte client */
.client-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.client-avatar {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  flex-shrink: 0;
}

.client-info h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.client-stats {
  display: flex;
  gap: 16px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: #6b7280;
}

.stat i {
  color: #f59e0b;
}

.stat:last-child i {
  color: #10b981;
}

/* Actions */
.actions-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-button {
  padding: 14px 20px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: none;
}

.apply-button {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.apply-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.apply-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.applied-button {
  background: #10b981;
  color: white;
  cursor: default;
}

.secondary-button {
  background: white;
  color: #374151;
  border: 1.5px solid #e5e7eb;
}

.secondary-button:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  background: #eff6ff;
}

.outline-button {
  background: transparent;
  color: #3b82f6;
  border: 1.5px solid #3b82f6;
}

.outline-button:hover {
  background: #3b82f6;
  color: white;
}

/* Contact */
.contact-card h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.contact-card h3 i {
  color: #8b5cf6;
}

.contact-card p {
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.contact-button {
  width: 100%;
  padding: 12px 20px;
  background: #f9fafb;
  color: #374151;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.contact-button:hover {
  border-color: #8b5cf6;
  color: #8b5cf6;
  background: #f5f3ff;
}

/* Responsive */
@media (max-width: 992px) {
  .mission-details-content {
    grid-template-columns: 1fr;
  }
  
  .sidebar-column {
    order: -1;
  }
}

@media (max-width: 768px) {
  .mission-title {
    font-size: 2rem;
  }
  
  .mission-meta {
    flex-direction: column;
    gap: 10px;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .mission-section {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .mission-title {
    font-size: 1.75rem;
  }
  
  .client-content {
    flex-direction: column;
    text-align: center;
  }
  
  .client-stats {
    justify-content: center;
  }
}
</style>