<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import Footer from '@/components/layout/footer.vue'; // Si vous avez un footer component

const authStore = useAuthStore();

// Données réactives
const loading = ref(true);
const activeTab = ref('all');
const searchQuery = ref('');
const selectedCategory = ref('all');
const selectedBudget = ref('all');

// Données mockées (à remplacer par API)
const userSkills = ref(['JavaScript', 'Vue.js', 'React', 'Node.js', 'API REST', 'MongoDB']);
const missions = ref([]);
const categories = ref([
  { id: 'all', label: 'Toutes catégories', icon: 'fas fa-layer-group' },
  { id: 'web', label: 'Développement Web', icon: 'fas fa-code' },
  { id: 'mobile', label: 'Mobile', icon: 'fas fa-mobile-alt' },
  { id: 'design', label: 'Design', icon: 'fas fa-paint-brush' },
  { id: 'marketing', label: 'Marketing', icon: 'fas fa-bullhorn' },
  { id: 'writing', label: 'Rédaction', icon: 'fas fa-pen-fancy' },
  { id: 'video', label: 'Vidéo/Montage', icon: 'fas fa-video' }
]);

const budgetRanges = ref([
  { id: 'all', label: 'Tous les budgets' },
  { id: 'small', label: '< 100.000 FCFA' },
  { id: 'medium', label: '100.000 - 500.000 FCFA' },
  { id: 'large', label: '> 500.000 FCFA' }
]);

// Computed pour les missions filtrées
const filteredMissions = computed(() => {
  let filtered = [...missions.value];
  
  // Filtre par catégorie
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(mission => mission.category === selectedCategory.value);
  }
  
  // Filtre par budget
  if (selectedBudget.value !== 'all') {
    const budgets = {
      small: (budget) => budget < 100000,
      medium: (budget) => budget >= 100000 && budget <= 500000,
      large: (budget) => budget > 500000
    };
    filtered = filtered.filter(mission => budgets[selectedBudget.value](mission.budget));
  }
  
  // Filtre par recherche
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim();
    filtered = filtered.filter(mission =>
      mission.title.toLowerCase().includes(query) ||
      mission.description.toLowerCase().includes(query) ||
      mission.client.toLowerCase().includes(query) ||
      mission.skills.some(skill => skill.toLowerCase().includes(query))
    );
  }
  
  // Filtre par onglet
  switch (activeTab.value) {
    case 'matching':
      filtered = filtered.filter(mission =>
        mission.skills.some(skill => userSkills.value.includes(skill))
      );
      break;
    case 'urgent':
      filtered = filtered.filter(mission => mission.urgency === 'high');
      break;
    case 'saved':
      filtered = filtered.filter(mission => mission.saved);
      break;
  }
  
  return filtered;
});

// Méthodes
const getMatchingSkills = (missionSkills) => {
  return missionSkills.filter(skill => userSkills.value.includes(skill));
};

const applyToMission = (missionId) => {
  const missionIndex = missions.value.findIndex(m => m.id === missionId);
  if (missionIndex !== -1) {
    missions.value[missionIndex].applied = true;
    missions.value[missionIndex].proposals += 1;
    // TODO: Appeler l'API pour postuler
    console.log('Postulation à la mission:', missionId);
  }
};

const saveMission = (missionId) => {
  const missionIndex = missions.value.findIndex(m => m.id === missionId);
  if (missionIndex !== -1) {
    missions.value[missionIndex].saved = !missions.value[missionIndex].saved;
    // TODO: Sauvegarder dans l'API
  }
};

const clearFilters = () => {
  searchQuery.value = '';
  selectedCategory.value = 'all';
  selectedBudget.value = 'all';
  activeTab.value = 'all';
};

// Chargement initial
onMounted(() => {
  setTimeout(() => {
    loadMissions();
    loading.value = false;
  }, 500); // Simuler un chargement
});

const loadMissions = () => {
  // Données mockées - à remplacer par appel API
  missions.value = [
    {
      id: 1,
      title: 'Développement Application E-commerce',
      client: 'Mboa Shop',
      description: 'Développement d\'une application e-commerce complète avec paiement Mobile Money et gestion de stock. Recherche d\'un développeur fullstack expérimenté.',
      budget: 750000,
      proposals: 8,
      duration: '2-3 mois',
      posted: 'Il y a 2 heures',
      skills: ['Vue.js', 'Node.js', 'MongoDB', 'API REST', 'JavaScript'],
      category: 'web',
      urgency: 'high',
      saved: false,
      applied: false,
      clientRating: 4.8,
      verified: true
    },
    {
      id: 2,
      title: 'Design Logo et Identité Visuelle',
      client: 'Startup Yaoundé',
      description: 'Création d\'une identité visuelle complète pour une nouvelle startup dans le domaine de la santé digitale.',
      budget: 150000,
      proposals: 15,
      duration: '2 semaines',
      posted: 'Il y a 5 heures',
      skills: ['Adobe Illustrator', 'Logo Design', 'Branding'],
      category: 'design',
      urgency: 'medium',
      saved: true,
      applied: false,
      clientRating: 4.5,
      verified: true
    },
    {
      id: 3,
      title: 'Application Mobile de Livraison',
      client: 'FastDelivery',
      description: 'Développement d\'une application mobile iOS/Android pour un service de livraison rapide dans la ville de Douala.',
      budget: 1200000,
      proposals: 5,
      duration: '4 mois',
      posted: 'Il y a 1 jour',
      skills: ['React Native', 'Firebase', 'Google Maps API'],
      category: 'mobile',
      urgency: 'high',
      saved: false,
      applied: true,
      clientRating: 4.9,
      verified: true
    },
    {
      id: 4,
      title: 'Rédaction Articles Techniques',
      client: 'TechBlog Africa',
      description: 'Rédaction d\'articles techniques sur les dernières technologies web (15 articles de 1000 mots chacun).',
      budget: 80000,
      proposals: 12,
      duration: '1 mois',
      posted: 'Il y a 2 jours',
      skills: ['Rédaction', 'Français', 'Anglais', 'Technologie'],
      category: 'writing',
      urgency: 'low',
      saved: false,
      applied: false,
      clientRating: 4.3,
      verified: false
    },
    {
      id: 5,
      title: 'Campagne Marketing Facebook Ads',
      client: 'Beauté Naturelle',
      description: 'Gestion complète d\'une campagne Facebook Ads pour une marque de cosmétiques naturels camerounais.',
      budget: 200000,
      proposals: 7,
      duration: '1 mois',
      posted: 'Il y a 3 jours',
      skills: ['Facebook Ads', 'Marketing Digital', 'Analytics'],
      category: 'marketing',
      urgency: 'medium',
      saved: false,
      applied: false,
      clientRating: 4.7,
      verified: true
    },
    {
      id: 6,
      title: 'Montage Vidéo Corporate',
      client: 'Entreprise X',
      description: 'Montage de vidéos corporates (5 vidéos de 3 minutes) pour la présentation de l\'entreprise.',
      budget: 250000,
      proposals: 9,
      duration: '3 semaines',
      posted: 'Il y a 4 jours',
      skills: ['Adobe Premiere Pro', 'After Effects', 'Montage Vidéo'],
      category: 'video',
      urgency: 'low',
      saved: true,
      applied: false,
      clientRating: 4.6,
      verified: true
    }
  ];
};
</script>

<template>
  <div class="feed-dashboard">
    <!-- Header -->
    <div class="dashboard-header-section">
      <div class="welcome-section">
        <h1 class="welcome-title">
          <i class="fas fa-bell"></i>
          Fil d'actualité des missions
        </h1>
        <p class="welcome-subtitle">
          Découvrez les nouvelles missions publiées par les clients
        </p>
      </div>

      <!-- Barre de recherche -->
      <div class="search-container">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="Rechercher une mission, compétence ou client..."
            class="search-input"
            @keyup.enter="loadMissions"
          />
          <button class="search-btn" @click="loadMissions">
            Rechercher
          </button>
        </div>
        <button class="clear-filters" @click="clearFilters" v-if="searchQuery || selectedCategory !== 'all' || selectedBudget !== 'all'">
          <i class="fas fa-times"></i>
          Effacer les filtres
        </button>
      </div>
    </div>

    <!-- Onglets et Filtres -->
    <div class="tabs-filters-section">
      <!-- Onglets -->
      <div class="tabs-navigation">
        <button 
          class="tab-btn" 
          :class="{ 'active': activeTab === 'all' }"
          @click="activeTab = 'all'"
        >
          <i class="fas fa-globe"></i>
          Toutes les missions
          <span class="tab-count">{{ missions.length }}</span>
        </button>
        
        <button 
          class="tab-btn" 
          :class="{ 'active': activeTab === 'matching' }"
          @click="activeTab = 'matching'"
        >
          <i class="fas fa-star"></i>
          Missions correspondantes
          <span class="tab-count">
            {{ missions.filter(m => m.skills.some(s => userSkills.includes(s))).length }}
          </span>
        </button>
        
        <button 
          class="tab-btn" 
          :class="{ 'active': activeTab === 'urgent' }"
          @click="activeTab = 'urgent'"
        >
          <i class="fas fa-bolt"></i>
          Missions urgentes
          <span class="tab-count">{{ missions.filter(m => m.urgency === 'high').length }}</span>
        </button>
        
        <button 
          class="tab-btn" 
          :class="{ 'active': activeTab === 'saved' }"
          @click="activeTab = 'saved'"
        >
          <i class="fas fa-bookmark"></i>
          Missions sauvegardées
          <span class="tab-count">{{ missions.filter(m => m.saved).length }}</span>
        </button>
      </div>

      <!-- Filtres -->
      <div class="filters-panel">
        <div class="filter-group">
          <label for="category-filter">
            <i class="fas fa-filter"></i>
            Catégorie
          </label>
          <select id="category-filter" v-model="selectedCategory" class="filter-select">
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.label }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label for="budget-filter">
            <i class="fas fa-money-bill-wave"></i>
            Budget
          </label>
          <select id="budget-filter" v-model="selectedBudget" class="filter-select">
            <option v-for="range in budgetRanges" :key="range.id" :value="range.id">
              {{ range.label }}
            </option>
          </select>
        </div>

        <div class="results-info">
          <i class="fas fa-chart-bar"></i>
          <span>{{ filteredMissions.length }} mission(s) trouvée(s)</span>
        </div>
      </div>
    </div>

    <!-- Contenu principal -->
    <div class="feed-content">
      <!-- Colonne des missions -->
      <div class="missions-column">
        <!-- État de chargement -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
          </div>
          <p>Chargement des missions...</p>
        </div>

        <!-- État vide -->
        <div v-else-if="filteredMissions.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-search"></i>
          </div>
          <h3>Aucune mission trouvée</h3>
          <p>Essayez de modifier vos filtres de recherche</p>
          <button class="retry-btn" @click="clearFilters">
            <i class="fas fa-redo"></i>
            Réinitialiser les filtres
          </button>
        </div>

        <!-- Liste des missions -->
        <div v-else class="missions-grid">
          <div 
            v-for="mission in filteredMissions" 
            :key="mission.id"
            class="mission-card"
            :class="{ 
              'urgent': mission.urgency === 'high',
              'applied': mission.applied,
              'saved': mission.saved
            }"
          >
            <!-- En-tête -->
            <div class="card-header">
              <div class="mission-category">
                <i :class="categories.find(c => c.id === mission.category)?.icon || 'fas fa-briefcase'"></i>
                {{ categories.find(c => c.id === mission.category)?.label }}
              </div>
              <div class="mission-actions">
                <button 
                  class="icon-btn save-btn" 
                  @click="saveMission(mission.id)"
                  :title="mission.saved ? 'Retirer des sauvegardes' : 'Sauvegarder'"
                >
                  <i :class="mission.saved ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
                </button>
                
                <span class="urgent-tag" v-if="mission.urgency === 'high'">
                  <i class="fas fa-fire"></i>
                  URGENT
                </span>
              </div>
            </div>

            <!-- Titre -->
            <h3 class="mission-title">{{ mission.title }}</h3>

            <!-- Client -->
            <div class="client-section">
              <div class="client-info">
                <span class="client-name">
                  <i class="fas fa-user-tie"></i>
                  {{ mission.client }}
                </span>
                <div class="client-meta">
                  <span class="rating" v-if="mission.clientRating">
                    <i class="fas fa-star"></i>
                    {{ mission.clientRating }}
                  </span>
                  <span class="verified" v-if="mission.verified">
                    <i class="fas fa-check-circle"></i>
                    Vérifié
                  </span>
                  <span class="posted-time">
                    <i class="far fa-clock"></i>
                    {{ mission.posted }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Description -->
            <div class="mission-description">
              <p>{{ mission.description }}</p>
            </div>

            <!-- Compétences -->
            <div class="skills-section">
              <h4>
                <i class="fas fa-tools"></i>
                Compétences recherchées
              </h4>
              <div class="skills-tags">
                <span 
                  v-for="skill in mission.skills" 
                  :key="skill"
                  class="skill-tag"
                  :class="{ 'match': userSkills.includes(skill) }"
                >
                  {{ skill }}
                  <i v-if="userSkills.includes(skill)" class="fas fa-check match-icon"></i>
                </span>
              </div>
              <div v-if="getMatchingSkills(mission.skills).length > 0" class="match-info">
                <i class="fas fa-thumbs-up"></i>
                Vous correspondez à {{ getMatchingSkills(mission.skills).length }} compétence(s)
              </div>
            </div>

            <!-- Détails -->
            <div class="details-grid">
              <div class="detail-item">
                <div class="detail-icon">
                  <i class="fas fa-money-bill-wave"></i>
                </div>
                <div class="detail-content">
                  <span class="detail-label">Budget</span>
                  <span class="detail-value budget">{{ mission.budget.toLocaleString() }} FCFA</span>
                </div>
              </div>
              
              <div class="detail-item">
                <div class="detail-icon">
                  <i class="far fa-calendar-alt"></i>
                </div>
                <div class="detail-content">
                  <span class="detail-label">Durée</span>
                  <span class="detail-value">{{ mission.duration }}</span>
                </div>
              </div>
              
              <div class="detail-item">
                <div class="detail-icon">
                  <i class="fas fa-users"></i>
                </div>
                <div class="detail-content">
                  <span class="detail-label">Propositions</span>
                  <span class="detail-value">{{ mission.proposals }} freelance(s)</span>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="card-actions">
              <button 
                v-if="!mission.applied"
                class="primary-btn apply-btn"
                @click="applyToMission(mission.id)"
                :disabled="loading"
              >
                <i class="fas fa-paper-plane"></i>
                Postuler
              </button>
              
              <button 
                v-else
                class="success-btn applied-btn"
                disabled
              >
                <i class="fas fa-check-circle"></i>
                Postulé
              </button>
              
              <button class="secondary-btn details-btn" @click="$router.push(`/mission/${mission.id}`)">
                <i class="fas fa-eye"></i>
                Détails
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="sidebar-column">
        <!-- Profil -->
        <div class="sidebar-card profile-widget">
          <div class="profile-header">
            <div class="avatar-circle">
              {{ authStore.user?.name?.charAt(0)?.toUpperCase() || 'F' }}
            </div>
            <div class="profile-details">
              <h3>{{ authStore.user?.name || 'Freelance' }}</h3>
              <p class="role-tag">
                <i class="fas fa-user-tag"></i>
                Freelance
              </p>
            </div>
          </div>
          
          <div class="profile-stats">
            <div class="stat-item">
              <span class="stat-number">3</span>
              <span class="stat-label">Missions actives</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">85%</span>
              <span class="stat-label">Taux de réponse</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">4.7</span>
              <span class="stat-label">Note</span>
            </div>
          </div>
        </div>

        <!-- Conseils -->
        <div class="sidebar-card tips-widget">
          <h3 class="widget-title">
            <i class="fas fa-lightbulb"></i>
            Conseils pour postuler
          </h3>
          <ul class="tips-list">
            <li>
              <i class="fas fa-check"></i>
              Personnalisez chaque proposition
            </li>
            <li>
              <i class="fas fa-check"></i>
              Répondez rapidement aux missions urgentes
            </li>
            <li>
              <i class="fas fa-check"></i>
              Mettez en avant vos compétences
            </li>
            <li>
              <i class="fas fa-check"></i>
              Posez des questions pour clarifier
            </li>
          </ul>
        </div>

        <!-- Fonctionnement -->
        <div class="sidebar-card guide-widget">
          <h3 class="widget-title">
            <i class="fas fa-info-circle"></i>
            Comment ça marche ?
          </h3>
          <div class="steps-guide">
            <div class="step">
              <div class="step-number">1</div>
              <div class="step-content">
                <h4>Trouvez une mission</h4>
                <p>Parcourez le fil d'actualité</p>
              </div>
            </div>
            <div class="step">
              <div class="step-number">2</div>
              <div class="step-content">
                <h4>Postulez</h4>
                <p>Envoyez une proposition détaillée</p>
              </div>
            </div>
            <div class="step">
              <div class="step-number">3</div>
              <div class="step-content">
                <h4>Collaborez</h4>
                <p>Travaillez via la plateforme</p>
              </div>
            </div>
            <div class="step">
              <div class="step-number">4</div>
              <div class="step-content">
                <h4>Recevez</h4>
                <p>Paiements en FCFA sécurisés</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Stats -->
        <div class="sidebar-card stats-widget">
          <h3 class="widget-title">
            <i class="fas fa-chart-line"></i>
            Statistiques
          </h3>
          <div class="quick-stats">
            <div class="quick-stat">
              <i class="fas fa-briefcase"></i>
              <div>
                <span class="stat-value">2,548</span>
                <span class="stat-label">Missions</span>
              </div>
            </div>
            <div class="quick-stat">
              <i class="fas fa-users"></i>
              <div>
                <span class="stat-value">3,847</span>
                <span class="stat-label">Freelances</span>
              </div>
            </div>
            <div class="quick-stat">
              <i class="fas fa-money-bill-wave"></i>
              <div>
                <span class="stat-value">425M</span>
                <span class="stat-label">FCFA</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<style scoped>
/* ==================== STYLES GÉNÉRAUX ==================== */
.feed-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  margin-top:60px;
}

/* ==================== HEADER SECTION ==================== */
.dashboard-header-section {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  padding: 40px 30px;
  border-bottom: 3px solid #FF6B35;
}

.welcome-section {
  text-align: center;
  margin-bottom: 30px;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 10px;
}

.welcome-title i {
  color: #FFD166;
  font-size: 2.2rem;
}

.welcome-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  max-width: 700px;
  margin: 0 auto;
  line-height: 1.5;
}

/* Barre de recherche */
.search-container {
  max-width: 800px;
  margin: 0 auto;
}

.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.search-box i {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  font-size: 1.2rem;
}

.search-input {
  flex: 1;
  padding: 15px 20px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50px;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.search-input:focus {
  outline: none;
  border-color: #FF6B35;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 5px 20px rgba(255, 107, 53, 0.3);
}

.search-btn {
  padding: 15px 30px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border: none;
  border-radius: 50px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 107, 53, 0.4);
}

.clear-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 0 auto;
}

.clear-filters:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* ==================== TABS & FILTERS ==================== */
.tabs-filters-section {
  background: white;
  padding: 25px 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.tabs-navigation {
  display: flex;
  gap: 10px;
  margin-bottom: 25px;
  overflow-x: auto;
  padding-bottom: 10px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: #f8fafc;
  border: 2px solid #e5e7eb;
  border-radius: 50px;
  color: #6c757d;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  flex-shrink: 0;
}

.tab-btn:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: translateY(-2px);
}

.tab-btn.active {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border-color: #FF6B35;
  box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
}

.tab-count {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 0.8rem;
  min-width: 24px;
  height: 24px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  margin-left: 5px;
}

.tab-btn.active .tab-count {
  background: rgba(255, 255, 255, 0.3);
}

.filters-panel {
  display: flex;
  gap: 25px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 200px;
}

.filter-group label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #6c757d;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-select {
  padding: 12px 15px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  background: white;
  color: #2D3047;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #FF6B35;
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.results-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border-radius: 10px;
  color: #0369a1;
  font-weight: 600;
  margin-left: auto;
}

.results-info i {
  font-size: 1.2rem;
  color: #3B82F6;
}

/* ==================== CONTENU PRINCIPAL ==================== */
.feed-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
  padding: 0 30px 40px;
  max-width: 1400px;
  margin: 0 auto;
}

/* ==================== MISSIONS COLUMN ==================== */
.missions-column {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* États */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 60px;
  background: white;
  border-radius: 20px;
  text-align: center;
}

.loading-spinner {
  font-size: 3rem;
  color: #FF6B35;
}

.loading-container p {
  color: #6c757d;
  font-size: 1.1rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 60px 40px;
  background: white;
  border-radius: 20px;
  text-align: center;
  border: 2px dashed #e5e7eb;
}

.empty-icon {
  font-size: 4rem;
  color: #9ca3af;
  margin-bottom: 10px;
}

.empty-state h3 {
  color: #2D3047;
  font-size: 1.5rem;
  margin-bottom: 10px;
}

.empty-state p {
  color: #6c757d;
  max-width: 300px;
  margin-bottom: 20px;
}

.retry-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border: none;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 107, 53, 0.3);
}

/* Grille des missions */
.missions-grid {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* Carte de mission */
.mission-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 2px solid transparent;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.mission-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

.mission-card::before {
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

.mission-card:hover::before {
  transform: scaleX(1);
}

.mission-card.urgent {
  border-color: #EF4444;
  background: linear-gradient(to right, #fff, #fef2f2);
}

.mission-card.urgent::before {
  background: linear-gradient(135deg, #EF4444, #F87171);
}

.mission-card.applied {
  border-color: #10B981;
  background: linear-gradient(to right, #fff, #f0fdf4);
}

.mission-card.applied::before {
  background: linear-gradient(135deg, #10B981, #34D399);
}

.mission-card.saved {
  border-color: #F59E0B;
  background: linear-gradient(to right, #fff, #fef3c7);
}

.mission-card.saved::before {
  background: linear-gradient(135deg, #F59E0B, #FBBF24);
}

/* En-tête de carte */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f1f5f9;
}

.mission-category {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  color: #6c757d;
}

.mission-category i {
  color: #FF6B35;
  font-size: 1.1rem;
}

.mission-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #e5e7eb;
  background: white;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.icon-btn:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: scale(1.1);
}

.save-btn.active {
  background: #FF6B35;
  border-color: #FF6B35;
  color: white;
}

.urgent-tag {
  padding: 6px 12px;
  background: linear-gradient(135deg, #EF4444, #F87171);
  color: white;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
}

/* Titre */
.mission-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #2D3047;
  margin-bottom: 15px;
  line-height: 1.3;
}

/* Client */
.client-section {
  margin-bottom: 20px;
}

.client-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.client-name {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #2D3047;
  font-size: 1.1rem;
}

.client-name i {
  color: #FF6B35;
}

.client-meta {
  display: flex;
  gap: 20px;
  font-size: 0.9rem;
}

.rating, .verified, .posted-time {
  display: flex;
  align-items: center;
  gap: 5px;
}

.rating {
  color: #F59E0B;
  font-weight: 500;
}

.verified {
  color: #10B981;
  font-weight: 500;
}

.posted-time {
  color: #6c757d;
}

.posted-time i {
  color: #9ca3af;
}

/* Description */
.mission-description {
  margin-bottom: 25px;
  color: #4b5563;
  line-height: 1.6;
  font-size: 1rem;
}

/* Compétences */
.skills-section {
  margin-bottom: 25px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
}

.skills-section h4 {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2D3047;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.skills-section h4 i {
  color: #FF6B35;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.skill-tag {
  padding: 8px 16px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #6c757d;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.skill-tag.match {
  background: #D1FAE5;
  border-color: #10B981;
  color: #065F46;
  font-weight: 500;
}

.match-icon {
  font-size: 0.8rem;
  color: #10B981;
}

.match-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  background: #DBEAFE;
  border-radius: 10px;
  color: #1E40AF;
  font-size: 0.9rem;
  font-weight: 500;
}

.match-info i {
  color: #3B82F6;
}

/* Détails */
.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.detail-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.detail-content {
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-size: 0.85rem;
  color: #6c757d;
  margin-bottom: 5px;
}

.detail-value {
  font-weight: 600;
  color: #2D3047;
  font-size: 1.1rem;
}

.detail-value.budget {
  color: #10B981;
  font-size: 1.2rem;
}

/* Actions */
.card-actions {
  display: flex;
  gap: 15px;
  padding-top: 20px;
  border-top: 2px solid #f1f5f9;
}

.primary-btn, .secondary-btn, .success-btn {
  flex: 1;
  padding: 15px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: none;
}

.primary-btn {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 107, 53, 0.3);
}

.secondary-btn {
  background: white;
  color: #2D3047;
  border: 2px solid #e5e7eb;
}

.secondary-btn:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: translateY(-2px);
}

.success-btn {
  background: #10B981;
  color: white;
  cursor: default;
}

/* ==================== SIDEBAR ==================== */
.sidebar-column {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.sidebar-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 2px solid #f1f5f9;
}

/* Profil */
.profile-widget .profile-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f5f9;
}

.avatar-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.5rem;
}

.profile-details h3 {
  margin: 0 0 5px 0;
  color: #2D3047;
  font-size: 1.2rem;
}

.role-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6c757d;
  font-size: 0.9rem;
  font-weight: 500;
}

.role-tag i {
  color: #FF6B35;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 15px;
  background: #f8fafc;
  border-radius: 10px;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2D3047;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.8rem;
  color: #6c757d;
}

/* Conseils */
.tips-widget .widget-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2D3047;
  margin-bottom: 20px;
  font-size: 1.2rem;
}

.tips-widget .widget-title i {
  color: #F59E0B;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips-list li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 15px;
  color: #4b5563;
  font-size: 0.95rem;
  line-height: 1.4;
}

.tips-list li i {
  color: #10B981;
  margin-top: 3px;
  flex-shrink: 0;
}

/* Guide */
.guide-widget .widget-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2D3047;
  margin-bottom: 25px;
  font-size: 1.2rem;
}

.guide-widget .widget-title i {
  color: #3B82F6;
}

.steps-guide {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step {
  display: flex;
  gap: 15px;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.step-content h4 {
  margin: 0 0 5px 0;
  color: #2D3047;
  font-size: 1rem;
}

.step-content p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
  line-height: 1.4;
}

/* Stats */
.stats-widget .widget-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2D3047;
  margin-bottom: 25px;
  font-size: 1.2rem;
}

.stats-widget .widget-title i {
  color: #8B5CF6;
}

.quick-stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.quick-stat {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8fafc;
  border-radius: 10px;
}

.quick-stat i {
  font-size: 1.5rem;
  color: #FF6B35;
  width: 40px;
  flex-shrink: 0;
}

.quick-stat .stat-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: #2D3047;
  display: block;
  margin-bottom: 5px;
}

.quick-stat .stat-label {
  font-size: 0.85rem;
  color: #6c757d;
  display: block;
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 1200px) {
  .feed-content {
    grid-template-columns: 1fr;
  }
  
  .sidebar-column {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 25px;
  }
}

@media (max-width: 768px) {
  .dashboard-header-section {
    padding: 30px 20px;
  }
  
  .welcome-title {
    font-size: 2rem;
    flex-direction: column;
    gap: 10px;
  }
  
  .search-box {
    flex-direction: column;
  }
  
  .search-btn {
    width: 100%;
  }
  
  .tabs-navigation {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 15px;
  }
  
  .filters-panel {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .results-info {
    margin-left: 0;
    justify-content: center;
  }
  
  .feed-content {
    padding: 0 20px 40px;
  }
  
  .sidebar-column {
    grid-template-columns: 1fr;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .card-actions {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .welcome-title {
    font-size: 1.6rem;
  }
  
  .mission-category {
    font-size: 0.8rem;
  }
  
  .client-meta {
    flex-direction: column;
    gap: 5px;
  }
  
  .profile-stats {
    grid-template-columns: 1fr;
  }
}

/* Animations */
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

.mission-card {
  animation: fadeIn 0.5s ease forwards;
}

.mission-card:nth-child(1) { animation-delay: 0.1s; }
.mission-card:nth-child(2) { animation-delay: 0.2s; }
.mission-card:nth-child(3) { animation-delay: 0.3s; }
.mission-card:nth-child(4) { animation-delay: 0.4s; }
.mission-card:nth-child(5) { animation-delay: 0.5s; }
.mission-card:nth-child(6) { animation-delay: 0.6s; }

/* Support tactile */
@media (hover: none) and (pointer: coarse) {
  .mission-card:hover {
    transform: none;
  }
  
  .primary-btn:hover, .secondary-btn:hover, .icon-btn:hover {
    transform: none;
  }
  
  .mission-card:active {
    transform: scale(0.98);
  }
}
</style>