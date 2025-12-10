<script setup>
import { useAuthStore } from '@/stores/auth';
import { computed } from 'vue';
import router from '@/router';

const authStore = useAuthStore();

// ✅ Rôle de l'utilisateur
const role = computed(() => authStore.user?.role || null);

// ✅ Menu dynamique selon le rôle
const menuItems = computed(() => {
  if (!role.value) return [];

  if (role.value === "FREELANCE") {
    return [
      { label: "Dashboard", path: "/dashboard" },
      { label: "Missions", path: "/missions" },
      { label: "Candidatures", path: "/applications" },
      { label: "Portfolio", path: "/portfolio" },
    ];
  }

  if (role.value === "CLIENT") {
    return [
      { label: "Dashboard", path: "/dashboard" },
      { label: "Créer une mission", path: "/missions/create" },
      { label: "Mes missions", path: "/client/missions" },
      { label: "Freelances", path: "/freelancers" },
    ];
  }

  return [];
});

// ✅ Déconnexion
const logout = () => {
  authStore.logout();
  router.push("/login");
};
</script>

<template>
  <header class="app-header">

    <!-- ✅ Logo -->
    <div class="logo" @click="router.push('/dashboard')">
      Freelance<span>CAM</span>
    </div>

    <!-- ✅ Menu dynamique -->
    <nav class="nav-menu">
      <a
        v-for="item in menuItems"
        :key="item.path"
        @click="router.push(item.path)"
        class="nav-link"
      >
        {{ item.label }}
      </a>
    </nav>

    <!-- ✅ Bouton déconnexion -->
    <button class="logout-btn" @click="logout">Déconnexion</button>
  </header>
</template>

<style scoped>
/* ✅ Reset */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* ✅ Header global */
.app-header {
  width: 100%;
  height: 70px;
  background: #1f2937; /* gris foncé moderne */
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 25px;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 50;
  font-family: "Segoe UI", sans-serif;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

/* ✅ Logo */
.logo {
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
}
.logo span {
  color: #3b82f6; /* bleu moderne */
}

/* ✅ Menu */
.nav-menu {
  display: flex;
  gap: 20px;
}
.nav-link {
  cursor: pointer;
  font-size: 15px;
  color: #e5e7eb;
  transition: 0.2s;
}
.nav-link:hover {
  color: #3b82f6;
}

/* ✅ Déconnexion */
.logout-btn {
  background: #ef4444;
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  transition: 0.2s;
}
.logout-btn:hover {
  background: #dc2626;
}
</style>
