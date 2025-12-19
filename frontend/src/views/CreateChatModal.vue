<template>
  <div class="mission-chat-container">
    <!-- En-tête -->
    <div class="chat-header-section">
      <div class="header-content">
        <button @click="goBack" class="back-button">
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        <div class="header-info">
          <h1 v-if="chat && chat.mission">
            {{ chat.mission.title }}
          </h1>
          <h1 v-else>Chargement...</h1>
          <p v-if="chat" class="header-subtitle">
            Type: {{ chat.chat_type === 'mission' ? '💼 Mission' : '❓ Autre' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Contenu principal -->
    <div class="chat-main">
      <!-- État de chargement -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Ouverture de la conversation...</p>
      </div>

      <!-- Erreur -->
      <div v-else-if="error" class="error-state">
        <svg width="48" height="48" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
            d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3>Erreur</h3>
        <p>{{ error }}</p>
        <button @click="retryChat" class="retry-button">Réessayer</button>
      </div>

      <!-- Messages -->
      <div v-else class="messages-section">
        <!-- Messages vides -->
        <div v-if="messages.length === 0" class="no-messages">
          <div class="empty-icon">💬</div>
          <h3>Démarrez la conversation</h3>
          <p>Soyez le premier à envoyer un message !</p>
        </div>

        <!-- Liste des messages -->
        <div v-else class="messages-list">
          <div 
            v-for="message in messages"
            :key="message.id"
            class="message-item"
            :class="{ 'is-sent': isSent(message) }"
          >
            <div class="message-bubble">
              <p class="message-text">{{ message.content }}</p>
              <span class="message-time">{{ formatTime(message.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Barre d'envoi -->
    <div v-if="!error && chat" class="input-section">
      <form @submit.prevent="sendMessage" class="message-form">
        <input
          ref="messageInput"
          v-model="newMessage"
          type="text"
          placeholder="Écrivez votre message..."
          class="message-input"
          :disabled="sending"
        />
        <button 
          type="submit"
          class="send-button"
          :disabled="!newMessage.trim() || sending"
        >
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </form>
      <div v-if="sending" class="sending-indicator">Envoi...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useChatStore } from '@/stores/chat';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const chatStore = useChatStore();
const authStore = useAuthStore();

// États locaux
const missionId = ref(null);
const loading = ref(false);
const sending = ref(false);
const error = ref(null);
const chat = ref(null);
const newMessage = ref('');
const messageInput = ref(null);
let messagesContainer = null;

// Computed
const messages = computed(() => chatStore.messages);
const currentUserId = computed(() => authStore.user?.id);

// Initialisation
onMounted(async () => {
  // Récupérer l'ID de mission depuis les query params
  missionId.value = router.currentRoute.value.query.mission;
  
  if (missionId.value) {
    await openMissionChat(parseInt(missionId.value));
  } else {
    error.value = 'Aucune mission spécifiée';
  }
});

// Ouvrir le chat de mission
const openMissionChat = async (id) => {
  loading.value = true;
  error.value = null;
  
  try {
    const result = await chatStore.getOrCreateMissionChat(id);
    chat.value = result;
    
    // Charger les messages
    await chatStore.fetchChatMessages(result.id);
    
    // Marquer comme lu si nécessaire
    if (result.unread_count > 0) {
      await chatStore.markChatAsRead(result.id);
    }
    
    // Focus et scroll
    await nextTick(() => {
      if (messageInput.value) {
        messageInput.value.focus();
      }
      scrollToBottom();
    });
  } catch (err) {
    console.error('Erreur:', err);
    error.value = 'Impossible d\'ouvrir la conversation';
  } finally {
    loading.value = false;
  }
};

// Envoyer un message
const sendMessage = async () => {
  if (!newMessage.value.trim() || !chat.value || sending.value) return;
  
  sending.value = true;
  const messageContent = newMessage.value.trim();
  newMessage.value = '';
  
  try {
    await chatStore.sendMessage(chat.value.id, messageContent);
    
    await nextTick(() => {
      scrollToBottom();
      if (messageInput.value) {
        messageInput.value.focus();
      }
    });
  } catch (err) {
    console.error('Erreur envoi:', err);
    newMessage.value = messageContent; // Restaurer le message
    error.value = 'Erreur lors de l\'envoi du message';
  } finally {
    sending.value = false;
  }
};

// Utilitaires
const isSent = (message) => message.sender_id === currentUserId.value;

const formatTime = (dateString) => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch (error) {
    return '';
  }
};

const scrollToBottom = () => {
  // Scroller à la fin des messages
  setTimeout(() => {
    const container = document.querySelector('.messages-list');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, 0);
};

const goBack = () => {
  router.back();
};

const retryChat = () => {
  if (missionId.value) {
    openMissionChat(missionId.value);
  }
};
</script>

<style scoped>
.mission-chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

/* En-tête */
.chat-header-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
  max-width: 1000px;
  margin: 0 auto;
}

.back-button {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-2px);
}

.header-info h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}

.header-subtitle {
  margin: 4px 0 0 0;
  opacity: 0.9;
  font-size: 14px;
}

/* Contenu principal */
.chat-main {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.loading-state,
.error-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: #6b7280;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(102, 126, 234, 0.2);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error-state {
  color: #dc2626;
}

.error-state svg {
  color: #dc2626;
}

.retry-button {
  margin-top: 12px;
  padding: 10px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.retry-button:hover {
  background: #5a67d8;
  transform: translateY(-2px);
}

.messages-section {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.no-messages {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #9ca3af;
}

.empty-icon {
  font-size: 64px;
  opacity: 0.5;
}

.no-messages h3 {
  margin: 0;
  font-size: 18px;
  color: #6b7280;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 20px;
}

.message-item {
  display: flex;
  animation: slideIn 0.3s ease;
}

.message-item.is-sent {
  justify-content: flex-end;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 16px;
  word-wrap: break-word;
}

.message-item.is-sent .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.message-item:not(.is-sent) .message-bubble {
  background: white;
  color: #111827;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.message-text {
  margin: 0 0 6px 0;
  font-size: 14px;
  line-height: 1.5;
}

.message-time {
  font-size: 12px;
  opacity: 0.7;
  display: block;
  text-align: right;
}

/* Section input */
.input-section {
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  background: white;
  padding: 16px 20px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
}

.message-form {
  display: flex;
  gap: 12px;
  align-items: center;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
}

.message-input {
  flex: 1;
  padding: 12px 18px;
  border: 2px solid #d1d5db;
  border-radius: 24px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  background: #f9fafb;
}

.message-input:focus {
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.message-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-button {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  transform: scale(1.08);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sending-indicator {
  text-align: center;
  font-size: 12px;
  color: #667eea;
  margin-top: 8px;
  font-weight: 500;
}

/* Animations */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 640px) {
  .mission-chat-container {
    height: 100%;
  }

  .header-info h1 {
    font-size: 18px;
  }

  .message-bubble {
    max-width: 85%;
  }

  .message-form {
    gap: 8px;
  }

  .message-input,
  .send-button {
    padding: 10px 14px;
  }

  .send-button {
    width: 40px;
    height: 40px;
  }
}

/* Scrollbar personnalisée */
.messages-section::-webkit-scrollbar {
  width: 6px;
}

.messages-section::-webkit-scrollbar-track {
  background: transparent;
}

.messages-section::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 3px;
}

.messages-section::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}
</style>