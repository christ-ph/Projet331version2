<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import AdminLoginForm from '@/components/admin/AdminLoginForm.vue';
import { useAdminStore } from '@/stores/admin';

const adminStore = useAdminStore();
const router = useRouter();

// ✅ Si déjà connecté en tant qu'admin, rediriger vers dashboard admin
onMounted(() => {
  if (adminStore.isAdminAuthenticated) {
    router.push('/admin/dashboard');
  }
});
</script>

<template>
  <div class="admin-login-page">
    <div class="admin-login-container">
      <div class="admin-login-right">
        <AdminLoginForm />
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.admin-login-container {
  width: 100%;
  max-width: 450px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.admin-login-right {
  padding: 40px;
}

@media (max-width: 768px) {
  .admin-login-container {
    max-width: 100%;
  }
  
  .admin-login-right {
    padding: 30px 20px;
  }
}
</style>
