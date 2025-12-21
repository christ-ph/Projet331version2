<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const router = useRouter();
const mobileMenuOpen = ref(false);
const showNotifications = ref(false);
const unreadNotifications = ref(5);
const unreadMessages = ref(3);

// ✅ Rôle de l'utilisateur
const role = computed(() => authStore.user?.role || null);
const userName = computed(() => authStore.user?.name || authStore.user?.email?.split('@')[0] || 'Utilisateur');

// ✅ Menu principal dynamique
const mainMenuItems = computed(() => {
  if (!role.value) return [];

  if (role.value === "FREELANCE") {
    return [
      { label: "Dashboard", icon: "fas fa-chart-line", path: "/dashboard", badge: null },
      { label: "Missions", icon: "fas fa-tasks", path: "/missions", badge: unreadNotifications.value },
      { label: "Propositions", icon: "fas fa-paper-plane", path: "/applications", badge: null },
      { label: "Discussions", icon: "fas fa-comments", path: `/chat/${ authStore.user.id}`, badge: unreadMessages.value },
      { label: "Statistiques", icon: "fas fa-chart-bar", path: "/stats", badge: null },
      { label: "Relations", icon: "fas fa-user-friends", path: "/network", badge: null },
      { label: "Mon Profil", icon: "fas fa-user-circle", path: "/freelance-profile", badge: null },
      { label: "Plaintes", icon: "fas fa-exclamation-triangle", path: "/plainte", badge: null },
    ];
  }

  if (role.value === "CLIENT") {
    return [
      { label: "Dashboard", icon: "fas fa-chart-line", path: "/dashboard", badge: null },
      { label: "Créer mission", icon: "fas fa-plus-circle", path: "/missions/create", badge: null },
      { label: "Mes missions", icon: "fas fa-briefcase", path: "/client/missions", badge: 2 },
      { label: "Discussions", icon: "fas fa-comments", path: `/chat/${authStore.user.id}`, badge: unreadMessages.value },
      { label: "Statistiques", icon: "fas fa-chart-bar", path: "/stats", badge: null },
      { label: "Relations", icon: "fas fa-user-friends", path: "/network", badge: null },
      { label: "Mon Profil", icon: "fas fa-user-circle", path: "/client-profile", badge: null },
      { label: "Plaintes", icon: "fas fa-exclamation-triangle", path: "/plainte", badge: null },
    ];
  }

  return [
    { label: "Dashboard", icon: "fas fa-chart-line", path: "/dashboard", badge: null },
    { label: "Compléter profil", icon: "fas fa-user-edit", path: "/profile-setup", badge: null },
  ];
});

// ✅ Menu secondaire (actions rapides)
const quickActions = computed(() => [
  { label: "Paramètres", icon: "fas fa-cog", path: "/settings" },
  { label: "Aide & Support", icon: "fas fa-question-circle", path: "/help" },
  { label: "Centre de formation", icon: "fas fa-graduation-cap", path: "/training" },
  { label: "Facturation", icon: "fas fa-file-invoice-dollar", path: "/billing" },
]);

// ✅ Navigation
const navigateTo = (path) => {
  router.push(path);
  mobileMenuOpen.value = false;
  showNotifications.value = false;
};

// ✅ Déconnexion
const logout = () => {
  if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
    authStore.logout();
    router.push('/login');
  }
};

// ✅ Gestion du clic en dehors
const handleClickOutside = (event) => {
  const menu = document.querySelector('.mobile-menu');
  const hamburger = document.querySelector('.hamburger-btn');
  const notifications = document.querySelector('.notifications-dropdown');
  
  if (mobileMenuOpen.value && 
      !menu?.contains(event.target) && 
      !hamburger?.contains(event.target)) {
    mobileMenuOpen.value = false;
  }
  
  if (showNotifications.value && 
      !notifications?.contains(event.target) && 
      !event.target.closest('.notification-btn')) {
    showNotifications.value = false;
  }
};

// ✅ Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<template>
  <header class="dashboard-header">
    <div class="header-container">
      <!-- Logo Section -->
      <div class="logo-section" @click="navigateTo('/dashboard')">
        <div class="logo">
          <i class="fas fa-hands-helping logo-icon"></i>
          <span class="logo-text">Freelance<span class="logo-highlight">CMR</span></span>
        </div>
        <div class="user-role-badge" :class="role?.toLowerCase()" v-if="role">
          <i class="fas fa-user-tag"></i>
          <span>{{ role === 'FREELANCE' ? 'Freelance' : 'Client' }}</span>
        </div>
      </div>

      <!-- Desktop Navigation -->
      <nav class="nav-desktop">
        <div class="nav-items">
          <a
            v-for="item in mainMenuItems.slice(0, 5)"
            :key="item.path"
            @click="navigateTo(item.path)"
            class="nav-link"
            :class="{ 'active': $route.path.startsWith(item.path) }"
          >
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
            <span class="nav-badge" v-if="item.badge">{{ item.badge }}</span>
          </a>
          
          <!-- Menu déroulant pour les items restants -->
          <div class="dropdown-nav" v-if="mainMenuItems.length > 5">
            <button class="dropdown-toggle">
              <i class="fas fa-ellipsis-h"></i>
              <span>Plus</span>
            </button>
            <div class="dropdown-menu">
              <a
                v-for="item in mainMenuItems.slice(5)"
                :key="item.path"
                @click="navigateTo(item.path)"
                class="dropdown-item"
              >
                <i :class="item.icon"></i>
                <span>{{ item.label }}</span>
              </a>
            </div>
          </div>
        </div>
      </nav>

      <!-- User Actions -->
      <div class="user-actions">
        <!-- Notifications -->
        <div class="notification-container">
          <button class="notification-btn" @click="showNotifications = !showNotifications">
            <i class="fas fa-bell"></i>
            <span class="notification-badge" v-if="unreadNotifications > 0">{{ unreadNotifications }}</span>
          </button>
          
          <!-- Dropdown Notifications -->
          <div class="notifications-dropdown" v-if="showNotifications">
            <div class="notifications-header">
              <h3>Notifications ({{ unreadNotifications }})</h3>
              <button class="mark-all-read">Tout marquer comme lu</button>
            </div>
            <div class="notifications-list">
              <div class="notification-item unread">
                <i class="fas fa-briefcase notification-icon"></i>
                <div class="notification-content">
                  <p>Nouvelle mission disponible: Développement d'une application web</p>
                  <span class="notification-time">Il y a 2 heures</span>
                </div>
              </div>
              <div class="notification-item unread">
                <i class="fas fa-comment notification-icon"></i>
                <div class="notification-content">
                  <p>Nouveau message de Sarah Mboma</p>
                  <span class="notification-time">Il y a 5 heures</span>
                </div>
              </div>
              <div class="notification-item">
                <i class="fas fa-check-circle notification-icon"></i>
                <div class="notification-content">
                  <p>Votre proposition a été acceptée</p>
                  <span class="notification-time">Hier</span>
                </div>
              </div>
            </div>
            <div class="notifications-footer">
              <a @click="navigateTo('/notifications')">Voir toutes les notifications</a>
            </div>
          </div>
        </div>

        <!-- Messages -->
        <button class="message-btn" @click="navigateTo('/messages')">
          <i class="fas fa-envelope"></i>
          <span class="message-badge" v-if="unreadMessages > 0">{{ unreadMessages }}</span>
        </button>

        <!-- User Profile -->
        <div class="user-profile" @click="mobileMenuOpen = !mobileMenuOpen">
          <div class="avatar">{{ userName.charAt(0).toUpperCase() }}</div>
          <div class="user-info">
            <span class="user-name">{{ userName }}</span>
            <span class="user-role">{{ role === 'FREELANCE' ? 'Freelance' : 'Client' }}</span>
          </div>
          <i class="fas fa-chevron-down" :class="{ 'rotated': mobileMenuOpen }"></i>
        </div>

        <!-- Hamburger Button (Mobile) -->
        <button 
          class="hamburger-btn" 
          @click="mobileMenuOpen = !mobileMenuOpen"
          :aria-expanded="mobileMenuOpen"
          aria-label="Menu principal"
        >
          <span class="hamburger-line" :class="{ 'open': mobileMenuOpen }"></span>
          <span class="hamburger-line" :class="{ 'open': mobileMenuOpen }"></span>
          <span class="hamburger-line" :class="{ 'open': mobileMenuOpen }"></span>
        </button>
      </div>

      <!-- Mobile Menu -->
      <div class="mobile-menu" :class="{ 'open': mobileMenuOpen }">
        <!-- User Info Mobile -->
        <div class="mobile-user-header">
          <div class="mobile-user-avatar">{{ userName.charAt(0).toUpperCase() }}</div>
          <div class="mobile-user-details">
            <h3>{{ userName }}</h3>
            <div class="mobile-user-stats">
              <span class="mobile-role-badge" :class="role?.toLowerCase()">
                {{ role === 'FREELANCE' ? 'Freelance' : 'Client' }}
              </span>
              <div class="mobile-stats">
                <span><i class="fas fa-bell"></i> {{ unreadNotifications }} notifs</span>
                <span><i class="fas fa-envelope"></i> {{ unreadMessages }} messages</span>
              </div>
            </div>
          </div>
          <button class="mobile-close-btn" @click="mobileMenuOpen = false">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <!-- Main Navigation Mobile -->
        <nav class="mobile-main-nav">
          <h4 class="mobile-nav-title">Navigation</h4>
          <a
            v-for="item in mainMenuItems"
            :key="item.path"
            @click="navigateTo(item.path)"
            class="mobile-nav-link"
            :class="{ 'active': $route.path.startsWith(item.path) }"
          >
            <div class="mobile-nav-icon">
              <i :class="item.icon"></i>
              <span class="mobile-nav-badge" v-if="item.badge">{{ item.badge }}</span>
            </div>
            <span>{{ item.label }}</span>
            <i class="fas fa-chevron-right arrow-icon"></i>
          </a>
        </nav>

        <!-- Quick Actions Mobile -->
        <div class="mobile-quick-actions">
          <h4 class="mobile-nav-title">Actions rapides</h4>
          <div class="quick-actions-grid">
            <button
              v-for="action in quickActions"
              :key="action.path"
              @click="navigateTo(action.path)"
              class="quick-action-btn"
            >
              <i :class="action.icon"></i>
              <span>{{ action.label }}</span>
            </button>
          </div>
        </div>

        <!-- Logout Mobile -->
        <button class="mobile-logout-btn" @click="logout">
          <i class="fas fa-sign-out-alt"></i>
          <span>Se déconnecter</span>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
/* ==================== BASE STYLES ==================== */
.dashboard-header {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  border-bottom: 3px solid #FF6B35;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 25px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* ==================== LOGO SECTION ==================== */
.logo-section {
  display: flex;
  align-items: center;
  gap: 15px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.logo-section:hover {
  transform: translateY(-2px);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 2rem;
  color: #FF6B35;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}

.logo-highlight {
  color: #FF6B35;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.user-role-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.user-role-badge.freelance {
  background: rgba(106, 17, 203, 0.2);
  color: #D6BCFA;
  border: 1px solid rgba(106, 17, 203, 0.4);
}

.user-role-badge.client {
  background: rgba(255, 107, 53, 0.2);
  color: #FFB8A3;
  border: 1px solid rgba(255, 107, 53, 0.4);
}

/* ==================== DESKTOP NAVIGATION ==================== */
.nav-desktop {
  flex: 1;
  margin: 0 30px;
}

.nav-items {
  display: flex;
  gap: 5px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50px;
  padding: 5px;
  backdrop-filter: blur(10px);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 25px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.nav-link:hover {
  background: rgba(255, 107, 53, 0.2);
  color: white;
}

.nav-link.active {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
}

.nav-badge {
  background: #EF4444;
  color: white;
  font-size: 0.7rem;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
  margin-left: 5px;
}

/* Dropdown Navigation */
.dropdown-nav {
  position: relative;
}

.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 25px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.dropdown-toggle:hover {
  background: rgba(255, 107, 53, 0.2);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 5px);
  right: 0;
  background: #2D3047;
  border-radius: 10px;
  padding: 10px;
  min-width: 200px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  display: none;
  border: 1px solid rgba(255, 107, 53, 0.2);
}

.dropdown-nav:hover .dropdown-menu {
  display: block;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.dropdown-item:hover {
  background: rgba(255, 107, 53, 0.2);
  color: white;
}

/* ==================== USER ACTIONS ==================== */
.user-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

/* Notification Container */
.notification-container {
  position: relative;
}

.notification-btn, .message-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  position: relative;
}

.notification-btn:hover, .message-btn:hover {
  background: rgba(255, 107, 53, 0.2);
  color: white;
  transform: translateY(-2px);
}

.notification-badge, .message-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  font-size: 0.7rem;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

/* Notifications Dropdown */
.notifications-dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 350px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
  z-index: 1001;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.notifications-header {
  padding: 20px;
  background: #2D3047;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notifications-header h3 {
  margin: 0;
  font-size: 1rem;
}

.mark-all-read {
  background: transparent;
  border: none;
  color: #FF6B35;
  font-size: 0.85rem;
  cursor: pointer;
}

.mark-all-read:hover {
  text-decoration: underline;
}

.notifications-list {
  max-height: 300px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  gap: 15px;
  padding: 15px 20px;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.3s ease;
}

.notification-item:hover {
  background: #f9fafb;
}

.notification-item.unread {
  background: #f0f9ff;
}

.notification-icon {
  color: #FF6B35;
  font-size: 1.2rem;
  margin-top: 2px;
}

.notification-content {
  flex: 1;
}

.notification-content p {
  margin: 0 0 5px 0;
  color: #374151;
  font-size: 0.9rem;
}

.notification-time {
  color: #9ca3af;
  font-size: 0.8rem;
}

.notifications-footer {
  padding: 15px 20px;
  text-align: center;
  border-top: 1px solid #e5e7eb;
}

.notifications-footer a {
  color: #FF6B35;
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
}

.notifications-footer a:hover {
  text-decoration: underline;
}

/* User Profile */
.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 200px;
}

.user-profile:hover {
  background: rgba(255, 107, 53, 0.2);
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
}

.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  font-size: 0.95rem;
}

.user-role {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

.fa-chevron-down {
  transition: transform 0.3s ease;
}

.fa-chevron-down.rotated {
  transform: rotate(180deg);
}

/* Hamburger Button */
.hamburger-btn {
  display: none;
  flex-direction: column;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
}

.hamburger-line {
  width: 24px;
  height: 2px;
  background: white;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.hamburger-line.open:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.hamburger-line.open:nth-child(2) {
  opacity: 0;
}

.hamburger-line.open:nth-child(3) {
  transform: rotate(-45deg) translate(7px, -6px);
}

/* ==================== MOBILE MENU ==================== */
.mobile-menu {
  position: fixed;
  top: 70px;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  z-index: 999;
  overflow-y: auto;
  padding-bottom: 80px;
}

.mobile-menu.open {
  transform: translateX(0);
}

/* Mobile User Header */
.mobile-user-header {
  padding: 25px;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  gap: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.mobile-user-avatar {
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

.mobile-user-details {
  flex: 1;
}

.mobile-user-details h3 {
  margin: 0 0 5px 0;
  font-size: 1.2rem;
}

.mobile-user-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mobile-role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.mobile-role-badge.freelance {
  background: rgba(106, 17, 203, 0.2);
  color: #D6BCFA;
  border: 1px solid rgba(106, 17, 203, 0.4);
}

.mobile-role-badge.client {
  background: rgba(255, 107, 53, 0.2);
  color: #FFB8A3;
  border: 1px solid rgba(255, 107, 53, 0.4);
}

.mobile-stats {
  display: flex;
  gap: 15px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

.mobile-close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 5px;
}

/* Mobile Navigation */
.mobile-main-nav {
  padding: 25px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.mobile-nav-title {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 15px;
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  margin-bottom: 5px;
  transition: all 0.3s ease;
}

.mobile-nav-link:hover, .mobile-nav-link.active {
  background: rgba(255, 107, 53, 0.2);
  color: white;
}

.mobile-nav-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.mobile-nav-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #EF4444;
  color: white;
  font-size: 0.7rem;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
}

.arrow-icon {
  color: rgba(255, 255, 255, 0.5);
}

/* Quick Actions */
.mobile-quick-actions {
  padding: 25px;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.quick-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-action-btn:hover {
  background: rgba(255, 107, 53, 0.2);
  color: white;
  transform: translateY(-2px);
}

.quick-action-btn i {
  font-size: 1.5rem;
  margin-bottom: 5px;
}

.quick-action-btn span {
  font-size: 0.8rem;
  text-align: center;
}

/* Logout Button */
.mobile-logout-btn {
  margin: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: calc(100% - 50px);
  padding: 18px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mobile-logout-btn:hover {
  background: linear-gradient(135deg, #FF8E53, #FF6B35);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 107, 53, 0.4);
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 1200px) {
  .nav-desktop {
    margin: 0 15px;
  }
  
  .nav-link {
    padding: 10px 15px;
    font-size: 0.85rem;
  }
}

@media (max-width: 1024px) {
  .user-profile .user-info,
  .user-role-badge,
  .dropdown-nav {
    display: none;
  }
  
  .user-profile {
    min-width: auto;
    padding: 8px;
  }
  
  .hamburger-btn {
    display: flex;
  }
  
  .nav-desktop {
    display: none;
  }
}

@media (max-width: 768px) {
  .header-container {
    padding: 0 15px;
  }
  
  .logo-text {
    font-size: 1.2rem;
  }
  
  .logo-icon {
    font-size: 1.5rem;
  }
  
  .notification-btn, .message-btn {
    width: 36px;
    height: 36px;
  }
  
  .notifications-dropdown {
    width: 300px;
    right: -50px;
  }
  
  .user-profile {
    display: none;
  }
}

@media (max-width: 480px) {
  .logo-text {
    font-size: 1rem;
  }
  
  .logo-icon {
    font-size: 1.2rem;
  }
  
  .notifications-dropdown {
    width: 280px;
    right: -70px;
  }
  
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
  
  .mobile-user-header {
    flex-direction: column;
    text-align: center;
  }
  
  .mobile-stats {
    flex-direction: column;
    gap: 5px;
  }
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.mobile-nav-link {
  animation: fadeIn 0.3s ease forwards;
}

.mobile-nav-link:nth-child(1) { animation-delay: 0.1s; }
.mobile-nav-link:nth-child(2) { animation-delay: 0.2s; }
.mobile-nav-link:nth-child(3) { animation-delay: 0.3s; }
.mobile-nav-link:nth-child(4) { animation-delay: 0.4s; }
.mobile-nav-link:nth-child(5) { animation-delay: 0.5s; }
.mobile-nav-link:nth-child(6) { animation-delay: 0.6s; }
.mobile-nav-link:nth-child(7) { animation-delay: 0.7s; }
</style>