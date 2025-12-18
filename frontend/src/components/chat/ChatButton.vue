<template>
  <!-- Bouton flottant pour ouvrir le chat -->
  <button 
    class="chat-floating-button"
    :class="{ 'has-notifications': unreadCount > 0 }"
    @click="toggleChatModal"
    title="Ouvrir le chat"
  >
    <!-- Icône chat -->
    <svg v-if="!unreadCount" class="chat-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
    
    <!-- Icône avec notification -->
    <svg v-else class="chat-icon notification" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
    </svg>
    
    <!-- Badge de notification -->
    <span v-if="unreadCount > 0" class="notification-badge">
      {{ unreadCount > 9 ? '9+' : unreadCount }}
    </span>
  </button>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue';
import { useChatStore } from '@/stores/chat';

const chatStore = useChatStore();
const unreadCount = computed(() => chatStore.unreadCount);

// Polling simple pour les notifications
let pollingInterval = null;

onMounted(() => {
  // Charger les chats au démarrage
  chatStore.fetchMyChats().catch(console.error);
  
  // Polling pour les notifications (toutes les 15 secondes)
  pollingInterval = setInterval(() => {
    if (document.visibilityState === 'visible') {
      chatStore.checkForNewMessages().catch(() => {});
    }
  }, 15000);
});

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval);
});

function toggleChatModal() {
  // Émettre un événement global pour ouvrir/fermer le modal
  const event = new CustomEvent('toggle-chat-modal', { 
    detail: { action: 'toggle' } 
  });
  window.dispatchEvent(event);
}
</script>

<style scoped>
.chat-floating-button {
  position: fixed;
  bottom: 25px;
  right: 25px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  z-index: 9998;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.chat-floating-button:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

.chat-floating-button:active {
  transform: translateY(0) scale(0.98);
}

.chat-floating-button.has-notifications {
  animation: pulse 2s infinite;
}

.chat-icon {
  width: 28px;
  height: 28px;
  stroke-width: 1.5;
}

.chat-icon.notification {
  stroke-width: 2;
  animation: shake 0.5s ease-in-out;
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  min-width: 22px;
  height: 22px;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

@keyframes pulse {
  0% { box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4); }
  50% { box-shadow: 0 4px 25px rgba(239, 68, 68, 0.8); }
  100% { box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4); }
}

@keyframes shake {
  0%, 100% { transform: rotate(0); }
  25% { transform: rotate(-10deg); }
  75% { transform: rotate(10deg); }
}
</style>