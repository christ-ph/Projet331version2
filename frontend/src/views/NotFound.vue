<template>
  <div class="not-found-page">
    <h1>404 - Page introuvable</h1>
    <p>La page que vous recherchez n'existe pas.</p>
    <button @click="$router.push('/')">Retour à l'accueil</button>
  </div>
</template>

<script setup>
</script>

<style scoped>
.not-found-page {
  margin-top: 100px;
  text-align: center;
  font-family: "Segoe UI", sans-serif;
}

h1 {
  font-size: 32px;
  color: #dc2626;
  margin-bottom: 15px;
}

button {
  padding: 10px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s;
}

button:hover {
  background: #2563eb;
}
</style>
