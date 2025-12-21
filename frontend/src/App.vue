<script setup>
import { useAuthStore } from './stores/auth';
import HeaderComponent from './components/layout/HeaderComponent.vue'; 

const authStore = useAuthStore();
</script>

<template>
  <div id="app-wrapper">
    
    <HeaderComponent v-if="authStore.isAuthenticated" /> 
    
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
#app-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
   font-family: Rajdahani, sans-serif;

}

.main-content {
  display: flex;
  flex-direction: column;
  position: relative;
}
</style>