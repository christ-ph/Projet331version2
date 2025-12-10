<script setup>

import RegisterForm from '@/components/auth/RegisterForm.vue';
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();
if(authStore.isAuthenticated){
  authStore.logout();

}
</script>

<template>
<div class="register-page">
  <div class="register-container">
    <div class="register-left">
      <p>Creer un Compte pour pouvoir acceder a la platform</p>
    </div>

    <div class="login-rigth">
      <RegisterForm/>
    </div>
  </div>
</div>

</template>