<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import missionService from '@/services/missionService';
import Footer from '@/components/layout/footer.vue';

const authStore = useAuthStore();

// Données réactives
const loading = ref(true);
const activeTab = ref('all');
const searchQuery = ref('');
const selectedCategory = ref('all');
const selectedBudget = ref('all');

// Données réelles
const userSkills = ref([]);
const missions = ref([]);
const userApplications = ref([]);
const savedMissionsIds = ref([]);

// Statistiques
const dashboardStats = ref({
  totalMissions: 0,
  appliedMissions: 0,
  savedMissions: 0,
  matchingMissions: 0
});

// Catégories statiques (à adapter selon votre modèle)
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

// Variables de pagination
const currentPage = ref(1);
const itemsPerPage = ref(10);
const totalMissions = ref(0);

// Computed pour les missions filtrées - CORRIGÉ
const filteredMissions = computed(() => {
  let filtered = [...missions.value];
  
  // Ajouter des propriétés calculées pour l'UI
  filtered = filtered.map(mission => ({
    ...mission,
    // Déterminer si la mission est sauvegardée
    saved: savedMissionsIds.value.includes(mission.id),
    // Déterminer si l'utilisateur a postulé
    applied: userApplications.value.some(app => app.mission_id === mission.id),
    // Calculer l'urgence (exemple basé sur le délai)
    urgency: getMissionUrgency(mission),
    // Catégorie fictive pour le moment (à adapter selon votre modèle)
    category: determineCategory(mission),
    // Durée fictive
    duration: estimateDuration(mission),
    // Nombre de propositions
    proposals: mission.postulations_total || 0,
    // Compétences sous forme de tableau
    skills: Array.isArray(mission.required_skills) ? mission.required_skills : 
           (typeof mission.required_skills === 'string' ? mission.required_skills.split(',').map(s => s.trim()) : [])
  }));
  
  // Filtre par catégorie
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(mission => mission.category === selectedCategory.value);
  }
  
  // Filtre par budget - CORRIGÉ
  if (selectedBudget.value !== 'all') {
    const budgetFunctions = {
      small: (budget) => {
        if (!budget) return false;
        return budget > 100000;
      },
      medium: (budget) => {
        if (!budget) return false;
        return budget >= 100000 && budget <= 500000;
      },
      large: (budget) => {
        if (!budget) return false;
        return budget < 500000;
      }
    };
    
    filtered = filtered.filter(mission => {
      // Vérifier si la mission a un budget
      if (!mission.budget && mission.budget !== 0) return false;
      
      // Convertir le budget en nombre si nécessaire
      const budgetValue = Number(mission.budget);
      if (isNaN(budgetValue)) return false;
      
      // Appliquer le filtre
      return budgetFunctions[selectedBudget.value](budgetValue);
    });
  }
  
  // Filtre par recherche
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim();
    filtered = filtered.filter(mission =>
      mission.title.toLowerCase().includes(query) ||
      mission.description.toLowerCase().includes(query) ||
      (mission.skills && mission.skills.some(skill => 
        skill.toLowerCase().includes(query)
      ))
    );
  }
  
  // Filtre par onglet
  switch (activeTab.value) {
    case 'matching':
      filtered = filtered.filter(mission =>
        mission.skills && 
        mission.skills.some(skill => 
          userSkills.value.some(userSkill => 
            userSkill.toLowerCase().includes(skill.toLowerCase()) ||
            skill.toLowerCase().includes(userSkill.toLowerCase())
          )
        )
      );
      break;
    case 'urgent':
      filtered = filtered.filter(mission => mission.urgency === 'high');
      break;
    case 'saved':
      filtered = filtered.filter(mission => savedMissionsIds.value.includes(mission.id));
      break;
  }
  
  return filtered;
});

// Fonctions utilitaires
const getMissionUrgency = (mission) => {
  if (!mission.deadline) return 'low';
  
  const deadline = new Date(mission.deadline);
  const now = new Date();
  const daysDiff = (deadline - now) / (1000 * 60 * 60 * 24);
  
  if (daysDiff < 3) return 'high';
  if (daysDiff < 7) return 'medium';
  return 'low';
};

const determineCategory = (mission) => {
  // Déterminer la catégorie basée sur les compétences ou le titre
  const title = (mission.title || '').toLowerCase();
  const description = (mission.description || '').toLowerCase();
  
  if (title.includes('web') || description.includes('web')) return 'web';
  if (title.includes('mobile') || description.includes('mobile')) return 'mobile';
  if (title.includes('design') || description.includes('design')) return 'design';
  if (title.includes('marketing') || description.includes('marketing')) return 'marketing';
  if (title.includes('rédaction') || description.includes('écriture')) return 'writing';
  if (title.includes('vidéo') || description.includes('montage')) return 'video';
  
  return 'web'; // par défaut
};

const estimateDuration = (mission) => {
  // Estimation basée sur le budget (à adapter)
  if (!mission.budget) return 'Non spécifié';
  
  const budget = Number(mission.budget);
  if (isNaN(budget)) return 'Non spécifié';
  
  if (budget < 50000) return '1-2 semaines';
  if (budget < 200000) return '2-4 semaines';
  if (budget < 500000) return '1-2 mois';
  return '2-4 mois';
};

const getMatchingSkills = (missionSkills) => {
  if (!missionSkills || !userSkills.value) return [];
  return missionSkills.filter(skill => 
    userSkills.value.some(userSkill => 
      userSkill.toLowerCase().includes(skill.toLowerCase()) ||
      skill.toLowerCase().includes(userSkill.toLowerCase())
    )
  );
};

// Fonctions principales
const applyToMission = async (missionId) => {
  try {
    loading.value = true;
    await missionService.applyToMission(missionId);
    
    // Recharger les applications
    await loadUserApplications();
    await loadDashboardStats();
    
    alert('Votre candidature a été envoyée avec succès!');
  } catch (error) {
    console.error('Error applying to mission:', error);
    alert('Erreur lors de la candidature: ' + (error.response?.data?.error || error.message));
  } finally {
    loading.value = false;
  }
};

const saveMission = async (missionId) => {
  try {
    if (savedMissionsIds.value.includes(missionId)) {
      // Retirer de la liste
      savedMissionsIds.value = savedMissionsIds.value.filter(id => id !== missionId);
    } else {
      // Ajouter à la liste
      savedMissionsIds.value.push(missionId);
    }
    
    // Sauvegarder dans localStorage
    localStorage.setItem('savedMissions', JSON.stringify(savedMissionsIds.value));
    
    // Appeler l'API si disponible
    try {
      await missionService.saveMission(missionId);
    } catch (apiError) {
      console.warn('API save not available, using localStorage');
    }
    
    // Mettre à jour les stats
    await loadDashboardStats();
  } catch (error) {
    console.error('Error saving mission:', error);
  }
};

const loadMissions = async (page = 1) => {
  try {
    loading.value = true;
    currentPage.value = page;
    
    const response = await missionService.getAllMissions({
      page: page,
      perPage: itemsPerPage.value,
      sortBy: 'created_at',
      order: 'desc',
      // Ajouter des filtres si votre endpoint les supporte
      q: searchQuery.value || undefined,
    });
    
    // Gérer la réponse selon la structure de votre API
    if (response.missions && response.total !== undefined) {
      // Structure paginée standard
      missions.value = response.missions;
      totalMissions.value = response.total;
    } else if (Array.isArray(response)) {
      // Simple tableau de missions
      missions.value = response;
      totalMissions.value = response.length;
    } else if (response.data && response.total) {
      // Autre structure possible
      missions.value = response.data;
      totalMissions.value = response.total;
    } else {
      // Fallback
      missions.value = [];
      totalMissions.value = 0;
    }
    
  } catch (error) {
    console.error('Error loading missions:', error);
    missions.value = [];
    totalMissions.value = 0;
  } finally {
    loading.value = false;
  }
};

const loadUserSkills = async () => {
  try {
    const skills = await missionService.getUserSkills();
    userSkills.value = skills;
  } catch (error) {
    console.error('Error loading user skills:', error);
    userSkills.value = [];
  }
};

const loadUserApplications = async () => {
  try {
    const applications = await missionService.getMyApplications();
    userApplications.value = applications;
  } catch (error) {
    console.error('Error loading applications:', error);
    userApplications.value = [];
  }
};

const loadSavedMissions = () => {
  try {
    const saved = localStorage.getItem('savedMissions');
    if (saved) {
      savedMissionsIds.value = JSON.parse(saved);
    }
  } catch (error) {
    console.error('Error loading saved missions:', error);
    savedMissionsIds.value = [];
  }
};

const loadDashboardStats = async () => {
  try {
    const stats = await missionService.getDashboardStats();
    dashboardStats.value = stats;
  } catch (error) {
    console.error('Error loading dashboard stats:', error);
    // Calculer manuellement si l'API n'est pas disponible
    const matching = missions.value.filter(mission => {
      if (!mission.required_skills || !userSkills.value.length) return false;
      const missionSkills = Array.isArray(mission.required_skills) ? 
                          mission.required_skills : 
                          (mission.required_skills || '').split(',').map(s => s.trim());
      return missionSkills.some(skill => 
        userSkills.value.some(userSkill => 
          userSkill.toLowerCase().includes(skill.toLowerCase()) ||
          skill.toLowerCase().includes(userSkill.toLowerCase())
        )
      );
    }).length;
    
    dashboardStats.value = {
      totalMissions: missions.value.length,
      appliedMissions: userApplications.value.length,
      savedMissions: savedMissionsIds.value.length,
      matchingMissions: matching
    };
  }
};

const clearFilters = () => {
  searchQuery.value = '';
  selectedCategory.value = 'all';
  selectedBudget.value = 'all';
  activeTab.value = 'all';
  currentPage.value = 1;
  loadMissions();
};

// Fonction pour déboguer les budgets
const debugBudgets = () => {
  console.log('=== DEBUG BUDGETS ===');
  console.log('Filtre sélectionné:', selectedBudget.value);
  console.log('Missions chargées:', missions.value.length);
  
  missions.value.forEach((mission, index) => {
    console.log(`Mission ${index + 1}:`, {
      id: mission.id,
      title: mission.title,
      budget: mission.budget,
      budgetType: typeof mission.budget,
      isNumber: !isNaN(Number(mission.budget)),
      numericValue: Number(mission.budget)
    });
  });
};

// Watch pour recharger les missions quand les filtres changent
watch([searchQuery, selectedCategory, selectedBudget], () => {
  currentPage.value = 1;
  loadMissions();
}, { deep: true });

// Chargement initial
onMounted(async () => {
  try {
    await Promise.all([
      loadUserSkills(),
      loadMissions(),
      loadUserApplications(),
      loadSavedMissions()
    ]);
    await loadDashboardStats();
  } catch (error) {
    console.error('Error loading dashboard data:', error);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <!-- Le reste du template reste le même, mais les données sont maintenant dynamiques -->
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
        <div class="header-actions">
          <button class="clear-filters" @click="clearFilters" v-if="searchQuery || selectedCategory !== 'all' || selectedBudget !== 'all'">
            <i class="fas fa-times"></i>
            Effacer les filtres
          </button>
          <!-- Bouton de débogage (optionnel) -->
          <button class="debug-btn" @click="debugBudgets" v-if="false" style="display: none;">
            <i class="fas fa-bug"></i>
            Debug
          </button>
        </div>
      </div>
    </div>

    <!-- Statistiques Dashboard -->
    <div class="stats-section" v-if="!loading">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-briefcase"></i>
          </div>
          <div class="stat-content">
            <h3>{{ dashboardStats.totalMissions }}</h3>
            <p>Missions totales</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-star"></i>
          </div>
          <div class="stat-content">
            <h3>{{ dashboardStats.matchingMissions }}</h3>
            <p>Correspond à vos compétences</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-paper-plane"></i>
          </div>
          <div class="stat-content">
            <h3>{{ dashboardStats.appliedMissions }}</h3>
            <p>Candidatures envoyées</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-bookmark"></i>
          </div>
          <div class="stat-content">
            <h3>{{ dashboardStats.savedMissions }}</h3>
            <p>Missions sauvegardées</p>
          </div>
        </div>
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
            {{ dashboardStats.matchingMissions }}
          </span>
        </button>
        
        <button 
          class="tab-btn" 
          :class="{ 'active': activeTab === 'urgent' }"
          @click="activeTab = 'urgent'"
        >
          <i class="fas fa-bolt"></i>
          Missions urgentes
          <span class="tab-count">{{ missions.filter(m => getMissionUrgency(m) === 'high').length }}</span>
        </button>
        
        <button 
          class="tab-btn" 
          :class="{ 'active': activeTab === 'saved' }"
          @click="activeTab = 'saved'"
        >
          <i class="fas fa-bookmark"></i>
          Missions sauvegardées
          <span class="tab-count">{{ dashboardStats.savedMissions }}</span>
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
          <span v-if="selectedBudget !== 'all'" class="budget-info">
            (Budget: {{ budgetRanges.find(b => b.id === selectedBudget)?.label }})
          </span>
        </div>

        <!-- Pagination -->
        <div class="pagination-controls" v-if="totalMissions > itemsPerPage">
          <button 
            class="pagination-btn" 
            @click="loadMissions(currentPage - 1)"
            :disabled="currentPage === 1"
          >
            <i class="fas fa-chevron-left"></i>
          </button>
          <span class="page-info">
            Page {{ currentPage }} sur {{ Math.ceil(totalMissions / itemsPerPage) }}
          </span>
          <button 
            class="pagination-btn" 
            @click="loadMissions(currentPage + 1)"
            :disabled="currentPage >= Math.ceil(totalMissions / itemsPerPage)"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
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
          <p v-if="selectedBudget !== 'all'">
            Aucune mission avec un budget {{ budgetRanges.find(b => b.id === selectedBudget)?.label.toLowerCase() }}
          </p>
          <p v-else>
            Essayez de modifier vos filtres de recherche
          </p>
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
                  :class="{ 'active': mission.saved }"
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
                  {{ mission.client_name || `Client #${mission.client_id}` }}
                </span>
                <div class="client-meta">
                  <span class="posted-time">
                    <i class="far fa-clock"></i>
                    {{ new Date(mission.created_at).toLocaleDateString('fr-FR') }}
                  </span>
                  <span v-if="mission.location" class="location">
                    <i class="fas fa-map-marker-alt"></i>
                    {{ mission.location }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Description -->
            <div class="mission-description">
              <p>{{ mission.description }}</p>
            </div>

            <!-- Compétences -->
            <div v-if="mission.skills && mission.skills.length > 0" class="skills-section">
              <h4>
                <i class="fas fa-tools"></i>
                Compétences recherchées
              </h4>
              <div class="skills-tags">
                <span 
                  v-for="skill in mission.skills" 
                  :key="skill"
                  class="skill-tag"
                  :class="{ 'match': userSkills.some(userSkill => 
                    userSkill.toLowerCase().includes(skill.toLowerCase()) ||
                    skill.toLowerCase().includes(userSkill.toLowerCase())
                  ) }"
                >
                  {{ skill }}
                  <i v-if="userSkills.some(userSkill => 
                    userSkill.toLowerCase().includes(skill.toLowerCase()) ||
                    skill.toLowerCase().includes(userSkill.toLowerCase())
                  )" class="fas fa-check match-icon"></i>
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
                  <span class="detail-value budget">
                    {{ mission.budget ? mission.budget.toLocaleString() + ' FCFA' : 'À discuter' }}
                  </span>
                </div>
              </div>
              
              <div class="detail-item">
                <div class="detail-icon">
                  <i class="far fa-calendar-alt"></i>
                </div>
                <div class="detail-content">
                  <span class="detail-label">Deadline</span>
                  <span class="detail-value">
                    {{ mission.deadline ? new Date(mission.deadline).toLocaleDateString('fr-FR') : 'Non spécifié' }}
                  </span>
                </div>
              </div>
              
              <div class="detail-item">
                <div class="detail-icon">
                  <i class="fas fa-users"></i>
                </div>
                <div class="detail-content">
                  <span class="detail-label">Propositions</span>
                  <span class="detail-value">{{ mission.proposals || 0 }} freelance(s)</span>
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
        <!-- ... reste du sidebar inchangé ... -->
      </div>
    </div>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<style scoped>
/* Ajoute ce CSS supplémentaire */
.header-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 16px;
}

.debug-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 107, 53, 0.1);
  color: #FF6B35;
  border: 1px solid rgba(255, 107, 53, 0.3);
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.budget-info {
  font-size: 0.85rem;
  opacity: 0.8;
  margin-left: 8px;
}

/* ==================== STYLES GÉNÉRAUX ==================== */
.feed-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  margin-top: 60px;
}

/* ==================== STATISTIQUES ==================== */
.stats-section {
  padding: 24px 32px;
  background: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  max-width: 1200px;
  margin: 0 auto;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
  border: 1px solid rgba(229, 231, 235, 0.6);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.stat-card:nth-child(2) .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card:nth-child(3) .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card:nth-child(4) .stat-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content h3 {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
  color: #1f2937;
  line-height: 1;
}

.stat-content p {
  margin: 6px 0 0 0;
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 500;
}

/* ==================== HEADER SECTION ==================== */
.dashboard-header-section {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  color: white;
  padding: 48px 32px;
  position: relative;
  overflow: hidden;
}

.dashboard-header-section::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  transform: translate(30%, -30%);
}

.welcome-section {
  text-align: center;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
}

.welcome-title {
  font-size: 2.25rem;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
}

.welcome-title i {
  color: #60a5fa;
  font-size: 2rem;
}

.welcome-subtitle {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.85);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.5;
  font-weight: 400;
}

/* Barre de recherche */
.search-container {
  max-width: 640px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.search-box {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  position: relative;
}

.search-box i {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  font-size: 1.1rem;
  z-index: 2;
}

.search-input {
  flex: 1;
  padding: 16px 20px 16px 48px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.08);
  color: white;
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  font-weight: 400;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
  font-weight: 400;
}

.search-input:focus {
  outline: none;
  border-color: #60a5fa;
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.2);
}

.search-btn {
  padding: 16px 28px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  letter-spacing: 0.3px;
}

.search-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.clear-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.08);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 10px 18px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 0 auto;
  font-weight: 500;
}

.clear-filters:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-1px);
}

/* ==================== TABS & FILTERS ==================== */
.tabs-filters-section {
  background: white;
  padding: 24px 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  margin-bottom: 32px;
  border-bottom: 1px solid #f1f5f9;
}

.tabs-navigation {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  overflow-x: auto;
  padding-bottom: 12px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: #f9fafb;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  color: #6b7280;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  flex-shrink: 0;
  letter-spacing: 0.2px;
}

.tab-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  background: #eff6ff;
}

.tab-btn.active {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border-color: transparent;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25);
}

.tab-count {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 0.75rem;
  min-width: 22px;
  height: 22px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  margin-left: 4px;
  font-weight: 600;
}

.tab-btn.active .tab-count {
  background: rgba(255, 255, 255, 0.3);
}

.filters-panel {
  display: flex;
  gap: 24px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 180px;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #4b5563;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label i {
  color: #9ca3af;
  font-size: 0.9rem;
}

.filter-select {
  padding: 12px 16px;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  background: white;
  color: #1f2937;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
  padding-right: 40px;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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
  font-size: 0.9rem;
  border: 1px solid #bae6fd;
}

.results-info i {
  font-size: 1.1rem;
  color: #0ea5e9;
}

/* Pagination */
.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}

.pagination-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1.5px solid #e5e7eb;
  background: white;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.pagination-btn:hover:not(:disabled) {
  border-color: #3b82f6;
  color: #3b82f6;
  background: #eff6ff;
  transform: translateY(-1px);
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none !important;
}

.page-info {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
  white-space: nowrap;
}

/* ==================== CONTENU PRINCIPAL ==================== */
.feed-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 32px;
  padding: 0 32px 48px;
  max-width: 1400px;
  margin: 0 auto;
}

/* ==================== MISSIONS COLUMN ==================== */
.missions-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* États */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 60px;
  background: white;
  border-radius: 16px;
  text-align: center;
  border: 1px solid #f1f5f9;
  min-height: 300px;
}

.loading-spinner {
  font-size: 2.5rem;
  color: #3b82f6;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  color: #6b7280;
  font-size: 1rem;
  font-weight: 500;
  margin: 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 60px 40px;
  background: white;
  border-radius: 16px;
  text-align: center;
  border: 2px dashed #e5e7eb;
  min-height: 300px;
}

.empty-icon {
  font-size: 3rem;
  color: #9ca3af;
  margin-bottom: 12px;
  opacity: 0.7;
}

.empty-state h3 {
  color: #1f2937;
  font-size: 1.5rem;
  margin-bottom: 8px;
  font-weight: 600;
}

.empty-state p {
  color: #6b7280;
  max-width: 300px;
  margin-bottom: 24px;
  line-height: 1.5;
  font-size: 0.95rem;
}

.retry-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 0.3px;
}

.retry-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* ==================== CARTES DE MISSIONS ÉLÉGANTES ==================== */
.missions-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Carte de mission - Design moderne et compact */
.mission-card {
  background: white;
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(229, 231, 235, 0.8);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.mission-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: rgba(59, 130, 246, 0.4);
}

.mission-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease;
}

.mission-card:hover::before {
  transform: scaleX(1);
}

.mission-card.urgent {
  border-left: 4px solid #ef4444;
  background: linear-gradient(to right, rgba(254, 242, 242, 0.3), white);
}

.mission-card.applied {
  border-left: 4px solid #10b981;
  background: linear-gradient(to right, rgba(240, 253, 244, 0.3), white);
}

.mission-card.saved {
  border-left: 4px solid #f59e0b;
  background: linear-gradient(to right, rgba(254, 243, 199, 0.3), white);
}

/* En-tête compact */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.mission-category {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  color: #6b7280;
  transition: all 0.2s ease;
}

.mission-card:hover .mission-category {
  background: #eff6ff;
  border-color: #dbeafe;
  color: #3b82f6;
}

.mission-category i {
  color: #9ca3af;
  font-size: 0.85rem;
  transition: color 0.2s ease;
}

.mission-card:hover .mission-category i {
  color: #3b82f6;
}

.mission-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1.5px solid #e5e7eb;
  background: white;
  color: #9ca3af;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.icon-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  background: #eff6ff;
  transform: scale(1.05);
}

.icon-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.urgent-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  color: #dc2626;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border: 1px solid #fecaca;
}

/* Titre élégant */
.mission-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 14px;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Section client compacte */
.client-section {
  margin-bottom: 18px;
}

.client-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.client-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #374151;
  font-size: 0.95rem;
}

.client-name i {
  color: #6b7280;
  font-size: 0.9rem;
}

.client-meta {
  display: flex;
  gap: 16px;
  font-size: 0.85rem;
  color: #6b7280;
  flex-wrap: wrap;
}

.posted-time, .location {
  display: flex;
  align-items: center;
  gap: 5px;
}

.posted-time i, .location i {
  color: #9ca3af;
  font-size: 0.8rem;
}

/* Description concise */
.mission-description {
  color: #4b5563;
  line-height: 1.5;
  margin-bottom: 18px;
  font-size: 0.9rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Compétences élégantes */
.skills-section {
  margin-bottom: 18px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 10px;
  border: 1px solid #f3f4f6;
}

.skills-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #374151;
  margin-bottom: 12px;
  font-size: 0.95rem;
  font-weight: 600;
}

.skills-section h4 i {
  color: #6b7280;
  font-size: 0.9rem;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.skill-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  background: white;
  border: 1.5px solid #e5e7eb;
  border-radius: 16px;
  font-size: 0.8rem;
  color: #6b7280;
  font-weight: 500;
  transition: all 0.2s ease;
}

.skill-tag:hover {
  border-color: #9ca3af;
  transform: translateY(-1px);
}

.skill-tag.match {
  background: #d1fae5;
  border-color: #10b981;
  color: #065f46;
  font-weight: 600;
}

.match-icon {
  font-size: 0.7rem;
  color: #10b981;
}

.match-info {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #dbeafe;
  border-radius: 8px;
  color: #1e40af;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid #bfdbfe;
}

.match-info i {
  color: #3b82f6;
  font-size: 0.8rem;
}

/* Détails en grille compacte */
.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 10px;
  border: 1px solid #f3f4f6;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}

.detail-content {
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-size: 0.8rem;
  color: #6b7280;
  margin-bottom: 4px;
  font-weight: 500;
}

.detail-value {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.95rem;
}

.detail-value.budget {
  color: #10b981;
  font-size: 1rem;
}

/* Actions compactes */
.card-actions {
  display: flex;
  gap: 12px;
  padding-top: 18px;
  border-top: 1px solid #f3f4f6;
}

.primary-btn, .secondary-btn, .success-btn {
  flex: 1;
  padding: 12px 16px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  letter-spacing: 0.3px;
}

.primary-btn {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.secondary-btn {
  background: white;
  color: #374151;
  border: 1.5px solid #e5e7eb;
  font-weight: 500;
}

.secondary-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  background: #eff6ff;
  transform: translateY(-1px);
}

.success-btn {
  background: #10b981;
  color: white;
  cursor: default;
  opacity: 0.9;
}

/* ==================== SIDEBAR ==================== */
.sidebar-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.sidebar-card {
  background: white;
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f1f5f9;
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 1200px) {
  .feed-content {
    grid-template-columns: 1fr;
  }
  
  .sidebar-column {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-header-section {
    padding: 32px 20px;
  }
  
  .welcome-title {
    font-size: 1.75rem;
    flex-direction: column;
    gap: 8px;
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
    padding-bottom: 16px;
  }
  
  .filters-panel {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .filter-group {
    width: 100%;
    min-width: auto;
  }
  
  .results-info, .pagination-controls {
    margin-left: 0;
    justify-content: center;
  }
  
  .feed-content {
    padding: 0 20px 32px;
    gap: 24px;
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
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .stats-section {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .welcome-title {
    font-size: 1.5rem;
  }
  
  .mission-category {
    font-size: 0.75rem;
  }
  
  .client-meta {
    flex-direction: column;
    gap: 6px;
  }
  
  .mission-title {
    font-size: 1.125rem;
  }
}

/* Animations subtiles */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.mission-card {
  animation: fadeIn 0.4s ease forwards;
  animation-delay: calc(var(--card-index, 0) * 0.05s);
}

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
  
  .skill-tag:hover {
    transform: none;
  }
}
</style>