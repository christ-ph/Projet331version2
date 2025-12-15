<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useProfileStore } from '@/stores/profile';
import { usePortfolioStore } from '@/stores/portfolio';

const authStore = useAuthStore();
const profileStore = useProfileStore();
const portfolioStore = usePortfolioStore();
const router = useRouter();

// ✅ States réactifs
const loading = ref(true);
const profile = ref(null);
const portfolio = ref([]);

// ✅ Computed pour vérifier l'authentification
const isAuthenticated = computed(() => authStore.isAuthenticated);
const hasProfile = computed(() => !!profile.value);

// ✅ Chargement des données au montage du composant
onMounted(async () => {
  // 1. Vérifier si l'utilisateur est connecté
  if (!isAuthenticated.value) {
    authStore.logout();
    router.push('/login');
    return;
  }

  // 2. Charger le profil
  try {
    profile.value = await profileStore.getMyProfile();
    
    // 3. Si pas de profil, rediriger vers dashboard
    if (!profile.value) {
      router.push('/dashboard');
      return;
    }

    // 4. Charger le portfolio
    portfolio.value = await portfolioStore.fetchPortfolio();
    
    console.log("Profile data:", profile.value);
    console.log("Portfolio data:", portfolio.value);

  } catch (error) {
    console.error('Erreur lors du chargement des données:', error);
    // Si erreur 401, l'intercepteur Axios a déjà géré la déconnexion
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="content-profile">
    <!-- ✅ Afficher un loader pendant le chargement -->
    <div v-if="loading" class="loading">
      Chargement du profil...
    </div>

    <!-- ✅ Afficher le contenu une fois chargé -->
    <template v-else>
      <section id="profile">
        <h1>Profil Freelance</h1>
        
        <!-- ✅ Afficher les données du profil -->
        <div v-if="profile" class="profile-info">
          <p><strong>Nom :</strong> {{ profile.full_name }}</p>
          <p><strong>Titre :</strong> {{ profile.title }}</p>
          <p><strong>Description :</strong> {{ profile.description }}</p>
          <p><strong>Compétences :</strong> {{ profile.skills?.join(', ') }}</p>
          <p><strong>Taux horaire :</strong> {{ profile.hourly_rate }}€/h</p>
        </div>
      </section>

      <section id="portfolio">
        <h2>Portfolio</h2>
        
        <!-- ✅ Afficher les éléments du portfolio -->
        <div v-if="portfolio.length > 0" class="portfolio-grid">
          <div v-for="item in portfolio" :key="item.id" class="portfolio-item">
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
            <a v-if="item.url" :href="item.url" target="_blank">Voir le projet</a>
          </div>
        </div>
        
        <p v-else class="empty">Aucun élément dans votre portfolio.</p>
      </section>
    </template>
  </div>
</template>

<style scoped>
.content-profile {
  margin-top: 100px;
  padding: 20px;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

.loading {
  text-align: center;
  font-size: 18px;
  padding: 40px;
}

/* Profile section */
#profile {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

#profile h1 {
  font-size: 28px;
  color: #1f2937;
  margin-bottom: 20px;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.profile-info p {
  font-size: 16px;
  color: #374151;
}

/* Portfolio section */
#portfolio {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

#portfolio h2 {
  font-size: 24px;
  color: #1f2937;
  margin-bottom: 20px;
}

.portfolio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.portfolio-item {
  background: #f9fafb;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.portfolio-item h3 {
  font-size: 18px;
  color: #1f2937;
  margin-bottom: 10px;
}

.portfolio-item p {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 10px;
}

.portfolio-item a {
  color: #3b82f6;
  text-decoration: none;
  font-size: 14px;
}

.portfolio-item a:hover {
  text-decoration: underline;
}

.empty {
  text-align: center;
  color: #9ca3af;
  font-size: 16px;
  padding: 40px;
}
</style>