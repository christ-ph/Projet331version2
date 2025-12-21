<template>
  <!-- Overlay -->
  <div v-if="isOpen" class="chat-modal-overlay" @click.self="closeModal">
    <!-- Modal -->
    <div class="chat-modal" @click.stop>
      <!-- En-tête -->
      <div class="chat-header">
        <div class="header-left">
          <h3 class="chat-title">
            <span v-if="activeChat">
              {{ getChatTitle(activeChat) }}
            </span>
            <span v-else>Messages</span>
          </h3>
          <span v-if="unreadCount > 0 && !activeChat" class="header-badge">
            {{ unreadCount }} non lu{{ unreadCount > 1 ? 's' : '' }}
          </span>
        </div>
        
        <div class="header-right">
          <!-- Bouton support -->
          <button 
            v-if="!activeChat || activeChat.chat_type !== 'support'"
            @click="openSupportChat"
            class="support-btn"
            title="Contacter le support"
          >
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </button>
          
          <!-- Bouton fermer -->
          <button @click="closeModal" class="close-btn" title="Fermer">
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Contenu principal -->
      <div class="chat-content">
        <!-- Liste des chats (si pas de chat actif) -->
        <div v-if="!activeChat" class="chat-list-container">
          <div v-if="loading" class="loading-chats">
            <div class="spinner"></div>
            <p>Chargement des conversations...</p>
          </div>
          
          <div v-else-if="filteredChats.length === 0" class="no-chats">
            <div class="empty-icon">💬</div>
            <h4>Aucune conversation</h4>
            <p>Commencez une nouvelle discussion</p>
            <button @click="openSupportChat" class="start-chat-btn">
              Contacter le support
            </button>
          </div>
          
          <div v-else class="chats-list">
            <div 
              v-for="chat in filteredChats"
              :key="chat.id"
              class="chat-item"
              :class="{ 
                'active': activeChat?.id === chat.id,
                'unread': chat.unread_count > 0 
              }"
              @click="selectChat(chat)"
            >
              <div class="chat-item-avatar">
                <div class="avatar">
                  {{ getAvatarInitials(chat) }}
                </div>
              </div>
              
              <div class="chat-item-content">
                <div class="chat-item-header">
                  <h5 class="chat-item-title">{{ getChatTitle(chat) }}</h5>
                  <span class="chat-item-time">
                    {{ formatTime(chat.updated_at) }}
                  </span>
                </div>
                
                <p class="chat-item-preview">
                  {{ getLastMessagePreview(chat) }}
                </p>
                
                <div v-if="chat.chat_type === 'mission'" class="chat-item-meta">
                  <span class="mission-tag">Mission</span>
                  <span v-if="chat.mission" class="mission-title">
                    {{ truncateText(chat.mission.title, 20) }}
                  </span>
                </div>
              </div>
              
              <div v-if="chat.unread_count > 0" class="chat-item-badge">
                {{ chat.unread_count }}
              </div>
            </div>
          </div>
        </div>

        <!-- Fenêtre de chat active -->
        <div v-else class="chat-window-container">
          <!-- En-tête du chat -->
          <div class="chat-window-header">
            <button @click="backToList" class="back-btn">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              <span class="back-text">Retour</span>
            </button>
            
            <div class="chat-info">
              <h4>{{ getChatTitle(activeChat) }}</h4>
              <p v-if="activeChat.mission" class="chat-subtitle">
                Mission: {{ activeChat.mission.title }}
              </p>
              <p v-else-if="activeChat.other_user" class="chat-subtitle">
                {{ activeChat.other_user.email }}
              </p>
            </div>
            
            <button 
              v-if="activeChat.unread_count > 0"
              @click="markAsRead"
              class="mark-read-btn" 
              title="Marquer comme lu"
            >
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </button>
          </div>

          <!-- Messages -->
          <div ref="messagesContainer" class="messages-container">
            <div v-if="loadingMessages" class="loading-messages">
              <div class="spinner small"></div>
              <p>Chargement des messages...</p>
            </div>
            
            <div v-else-if="messages.length === 0" class="no-messages">
              <div class="empty-messages-icon">📭</div>
              <p>Aucun message</p>
              <p class="subtext">Soyez le premier à envoyer un message !</p>
            </div>
            
            <div v-else class="messages-list">
              <div 
                v-for="message in messages"
                :key="message.id"
                class="message"
                :class="{ 
                  'sent': message.sender_id === currentUserId,
                  'received': message.sender_id !== currentUserId 
                }"
              >
                <div class="message-content">
                  <p class="message-text">{{ message.content }}</p>
                  <span class="message-time">
                    {{ formatMessageTime(message.created_at) }}
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Indicateur de chargement lors de l'envoi -->
            <div v-if="sending" class="sending-indicator-messages">
              <div class="sending-spinner"></div>
              <span>Envoi en cours...</span>
            </div>
          </div>

          <!-- Input d'envoi -->
          <div class="message-input-container">
            <form @submit.prevent="sendMessage" class="message-form">
              <input
                ref="messageInput"
                v-model="newMessage"
                type="text"
                placeholder="Tapez votre message..."
                :disabled="sending"
                @keydown.enter.exact.prevent="sendMessage"
              />
              
              <button 
                type="submit" 
                class="send-btn"
                :disabled="!newMessage.trim() || sending"
                title="Envoyer"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useChatStore } from '@/stores/chat';
import { useAuthStore } from '@/stores/auth';

// Props
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
});

// Émits
const emit = defineEmits(['close', 'open-support']);

// Stores
const chatStore = useChatStore();
const authStore = useAuthStore();

// Refs - les variables d'état locales
const activeChat = ref(null);
const newMessage = ref('');
const loading = ref(false);
const loadingMessages = ref(false);
const sending = ref(false);
const messagesContainer = ref(null);
const messageInput = ref(null);

// Variables pour le polling
let pollingInterval = null;
const pollingActive = ref(false);

// Computed
const currentUserId = computed(() => authStore.user?.id);
const chats = computed(() => chatStore.chats);
const messages = computed(() => chatStore.messages);
const unreadCount = computed(() => chatStore.unreadCount);

// Filtrer les chats pour éviter les doublons
const filteredChats = computed(() => {
  const uniqueChats = [];
  const seenIds = new Set();
  
  chats.value.forEach(chat => {
    if (!seenIds.has(chat.id)) {
      seenIds.add(chat.id);
      uniqueChats.push(chat);
    }
  });
  
  return uniqueChats;
});

// Fonctions utilitaires
const getChatTitle = (chat) => {
  if (chat.chat_type === 'support') return 'Support';
  
  if (chat.other_user) {
    return chat.other_user.full_name || chat.other_user.email.split('@')[0];
  }
  
  if (chat.mission) {
    return chat.mission.title;
  }
  
  return chat.user1_id === currentUserId.value 
    ? `Utilisateur ${chat.user2_id}`
    : `Utilisateur ${chat.user1_id}`;
};

const getAvatarInitials = (chat) => {
  if (chat.chat_type === 'support') return 'S';
  
  if (chat.other_user?.full_name) {
    const names = chat.other_user.full_name.split(' ');
    return names.map(name => name[0]).join('').toUpperCase().slice(0, 2);
  }
  
  if (chat.mission?.title) {
    return chat.mission.title.charAt(0).toUpperCase();
  }
  
  return 'U';
};

const getLastMessagePreview = (chat) => {
  if (!chat.last_message) return 'Aucun message';
  const msg = chat.last_message.content;
  return msg.length > 40 ? msg.substring(0, 40) + '...' : msg;
};

const formatTime = (dateString) => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays === 1) {
      return 'Hier';
    } else if (diffDays < 7) {
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  } catch (error) {
    return '';
  }
};

const formatMessageTime = (dateString) => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch (error) {
    return '';
  }
};

const truncateText = (text, maxLength) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// Fonctions principales
const selectChat = async (chat) => {
  if (!chat) return;
  
  activeChat.value = chat;
  loadingMessages.value = true;
  
  try {
    // Charger les messages
    await chatStore.fetchChatMessages(chat.id);
    
    // Marquer comme lu si nécessaire
    if (chat.unread_count > 0) {
      await chatStore.markChatAsRead(chat.id);
    }
    
    // Focus sur l'input et scroll
    await nextTick(() => {
      scrollToBottom();
      if (messageInput.value) {
        messageInput.value.focus();
      }
    });
  } catch (error) {
    console.error('Erreur chargement messages:', error);
  } finally {
    loadingMessages.value = false;
  }
};

const sendMessage = async () => {
  if (!newMessage.value.trim() || !activeChat.value || sending.value) return;
  
  sending.value = true;
  const messageToSend = newMessage.value.trim();
  newMessage.value = '';
  
  try {
    // Envoyer le message
    await chatStore.sendMessage(activeChat.value.id, messageToSend);
    
    // Ne pas recharger TOUS les messages, seulement ajouter le nouveau
    await nextTick(() => {
      scrollToBottom();
      if (messageInput.value) {
        messageInput.value.focus();
      }
    });
  } catch (error) {
    console.error('Erreur envoi message:', error);
    // Remettre le message en cas d'erreur
    newMessage.value = messageToSend;
  } finally {
    sending.value = false;
  }
};

const scrollToBottom = () => {
  if (messagesContainer.value) {
    requestAnimationFrame(() => {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    });
  }
};

const backToList = () => {
  activeChat.value = null;
  chatStore.messages = []; // Réinitialiser seulement les messages
};

const markAsRead = async () => {
  if (activeChat.value && activeChat.value.unread_count > 0) {
    try {
      await chatStore.markChatAsRead(activeChat.value.id);
    } catch (error) {
      console.error('Erreur marquer comme lu:', error);
    }
  }
};

const openSupportChat = () => {
  emit('open-support');
};

const closeModal = () => {
  // Réinitialiser l'état local
  activeChat.value = null;
  newMessage.value = '';
  
  // Émettre l'événement de fermeture
  emit('close');
};

// Fonction pour ouvrir un chat par ID
const openChatById = async (chatId) => {
  loading.value = true;
  try {
    // Chercher le chat dans la liste
    let chat = chats.value.find(c => c.id === chatId);
    
    if (!chat) {
      // Si pas trouvé, recharger les chats
      await chatStore.fetchMyChats();
      await new Promise(resolve => setTimeout(resolve, 100));
      
      chat = chats.value.find(c => c.id === chatId);
    }
    
    if (chat) {
      await selectChat(chat);
    }
  } catch (error) {
    console.error('Erreur ouverture chat:', error);
  } finally {
    loading.value = false;
  }
};

// Gestion du polling
const startPolling = () => {
  if (pollingActive.value) return; // Éviter les doublons
  
  pollingActive.value = true;
  stopPolling(); // S'assurer qu'il n'y a pas de doublon
  
  pollingInterval = setInterval(() => {
    if (props.isOpen && document.visibilityState === 'visible') {
      chatStore.checkForNewMessages().catch(() => {});
    }
  }, 30000); // 30 secondes
};

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
  pollingActive.value = false;
};

// Écouteur d'événement global
const handleOpenChatEvent = (event) => {
  if (event.detail && event.detail.chatId) {
    openChatById(event.detail.chatId);
  }
};

// Surveiller l'état d'ouverture
watch(() => props.isOpen, async (isOpen) => {
  if (isOpen) {
    // Charger les chats si nécessaire
    if (chatStore.chats.length === 0 && !loading.value) {
      loading.value = true;
      try {
        await chatStore.fetchMyChats();
      } catch (error) {
        console.error('Erreur chargement chats:', error);
      } finally {
        loading.value = false;
      }
    }
    
    // Focus
    nextTick(() => {
      if (messageInput.value && activeChat.value) {
        messageInput.value.focus();
      }
    });
    
    // Démarrer le polling
    startPolling();
    
    // Ajouter l'écouteur d'événement
    window.addEventListener('open-chat-modal', handleOpenChatEvent);
  } else {
    // Arrêter le polling
    stopPolling();
    
    // Supprimer l'écouteur d'événement
    window.removeEventListener('open-chat-modal', handleOpenChatEvent);
    
    // Réinitialiser l'état local
    activeChat.value = null;
    newMessage.value = '';
  }
}, { immediate: true });

// Nettoyage
onUnmounted(() => {
  stopPolling();
  window.removeEventListener('open-chat-modal', handleOpenChatEvent);
});
</script>

<style scoped>
/* Vos styles CSS restent exactement les mêmes */
.chat-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(2px);
  animation: fadeIn 0.2s ease-out;
}

.chat-modal {
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Styles inchangés - exactement comme avant */
.chat-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(2px);
  animation: fadeIn 0.2s ease-out;
}

.chat-modal {
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
/* Styles du modal */
.chat-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(2px);
  animation: fadeIn 0.2s ease-out;
}

.chat-modal {
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* En-tête */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.header-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.header-right {
  display: flex;
  gap: 8px;
}

.support-btn, .close-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.support-btn:hover, .close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.icon {
  width: 20px;
  height: 20px;
  stroke-width: 2;
}

/* Contenu principal */
.chat-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Liste des chats */
.chat-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.loading-chats, .no-chats {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #6b7280;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.spinner.small {
  width: 24px;
  height: 24px;
  border-width: 2px;
  margin-bottom: 0;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.start-chat-btn {
  margin-top: 16px;
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.start-chat-btn:hover {
  background: #5a67d8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Items de chat */
.chat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 8px;
  border: 1px solid #e5e7eb;
  background: white;
}

.chat-item:hover {
  background: #f9fafb;
  border-color: #d1d5db;
  transform: translateX(2px);
}

.chat-item.active {
  background: #f3f4f6;
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.chat-item.unread {
  border-left: 4px solid #667eea;
  background: #f8fafc;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
  flex-shrink: 0;
}

.chat-item-content {
  flex: 1;
  min-width: 0;
}

.chat-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 6px;
}

.chat-item-title {
  font-weight: 600;
  color: #111827;
  margin: 0;
  font-size: 15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.chat-item-time {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
  flex-shrink: 0;
}

.chat-item-preview {
  font-size: 13px;
  color: #6b7280;
  margin: 0 0 6px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.chat-item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.mission-tag {
  font-size: 11px;
  color: #667eea;
  background: #e0e7ff;
  padding: 3px 8px;
  border-radius: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.mission-title {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.chat-item-badge {
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
  flex-shrink: 0;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Fenêtre de chat */
.chat-window-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-window-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: white;
  flex-shrink: 0;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 8px;
  color: #6b7280;
  transition: all 0.2s;
  font-weight: 500;
}

.back-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.back-text {
  font-size: 14px;
}

.chat-info {
  flex: 1;
  min-width: 0;
}

.chat-info h4 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-subtitle {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mark-read-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  transition: all 0.2s;
}

.mark-read-btn:hover {
  background: #f3f4f6;
  color: #10b981;
}

/* Messages */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
}

.loading-messages {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 12px;
  color: #6b7280;
}

.no-messages {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #6b7280;
}

.empty-messages-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.subtext {
  font-size: 14px;
  color: #9ca3af;
  margin-top: 4px;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 10px;
}

.message {
  max-width: 80%;
  animation: messageSlide 0.3s ease;
}

@keyframes messageSlide {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.sent {
  align-self: flex-end;
}

.message.received {
  align-self: flex-start;
}

.message-content {
  position: relative;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
  max-width: 100%;
}

.message.sent .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.received .message-content {
  background: white;
  color: #111827;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.message-text {
  margin: 0 0 8px 0;
}

.message-time {
  font-size: 11px;
  opacity: 0.8;
  display: block;
  text-align: right;
}

.message.sent .message-time {
  color: rgba(255, 255, 255, 0.9);
}

.message.received .message-time {
  color: #6b7280;
}

.sending-indicator-messages {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  align-self: flex-end;
  margin-top: 8px;
  font-size: 12px;
  color: #6b7280;
}

.sending-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Input d'envoi */
.message-input-container {
  border-top: 1px solid #e5e7eb;
  background: white;
  padding: 16px 20px;
  flex-shrink: 0;
}

.message-form {
  display: flex;
  gap: 10px;
  align-items: center;
}

.message-form input {
  flex: 1;
  padding: 12px 18px;
  border: 2px solid #d1d5db;
  border-radius: 24px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  background: #f9fafb;
}

.message-form input:focus {
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.message-form input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-btn {
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

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn .icon {
  width: 18px;
  height: 18px;
  stroke-width: 2.5;
}

/* Animations */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 640px) {
  .chat-modal {
    width: 100%;
    height: 100%;
    max-width: none;
    max-height: none;
    border-radius: 0;
  }
  
  .chat-modal-overlay {
    padding: 0;
  }
  
  .chat-item-title {
    max-width: 150px;
  }
  
  .message {
    max-width: 85%;
  }
  
  .back-text {
    display: none;
  }
}

@media (max-width: 480px) {
  .chat-header {
    padding: 12px 16px;
  }
  
  .chat-content {
    padding: 0;
  }
  
  .chat-list-container,
  .messages-container {
    padding: 16px;
  }
  
  .message-input-container {
    padding: 12px 16px;
  }
  
  .message-form input {
    padding: 10px 16px;
  }
  
  .send-btn {
    width: 42px;
    height: 42px;
  }
  
  .chat-item {
    padding: 12px;
  }
  
  .avatar {
    width: 40px;
    height: 40px;
    font-size: 14px;
  }
}

/* Scrollbar styling */
.chat-list-container::-webkit-scrollbar,
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.chat-list-container::-webkit-scrollbar-track,
.messages-container::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.chat-list-container::-webkit-scrollbar-thumb,
.messages-container::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.chat-list-container::-webkit-scrollbar-thumb:hover,
.messages-container::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Touch device optimizations */
@media (hover: none) and (pointer: coarse) {
  .chat-item:hover {
    background: white;
    transform: none;
  }
  
  .chat-item:active {
    background: #f3f4f6;
  }
  
  .send-btn:hover:not(:disabled) {
    transform: none;
  }
}
</style>