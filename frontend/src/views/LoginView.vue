<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import LoginForm from '@/components/auth/LoginForm.vue'; 
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const router = useRouter();

// ✅ Si déjà connecté, rediriger vers dashboard
onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push('/dashboard');
  }
});
</script>

<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-right">
        <LoginForm />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Tes styles ici */
</style>