<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import RegisterForm from '@/components/auth/RegisterForm.vue';
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
  <div class="register-page">
    <div class="register-container">
      <div class="register-left">
        <p>Créer un compte pour pouvoir accéder à la plateforme</p>
      </div>

      <div class="login-right">
        <RegisterForm />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Tes styles ici */
</style>