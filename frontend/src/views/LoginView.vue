<script setup>
import LoginForm from '@/components/auth/LoginForm.vue'; 
import router from '@/router';
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();
authStore.logout(false);
let bool = authStore.isAuthenticated;

</script>

<template>
  <div class="login-page">
    <div class="login-container">

   <div class="login-right">
        <LoginForm v-if="!bool" />
        

      </div>
    </div>
  </div>
</template>

<style scoped>

</style>