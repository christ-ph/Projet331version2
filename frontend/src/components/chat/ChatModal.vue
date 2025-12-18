<template>
  <!-- Overlay -->
  <div v-if="isOpen" class="chat-modal-overlay" @click="closeModal">
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
          <span v-if="unreadCount > 0" class="header-badge">
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
          
          <div v-else-if="chats.length === 0" class="no-chats">
            <div class="empty-icon">💬</div>
            <h4>Aucune conversation</h4>
            <p>Commencez une nouvelle discussion</p>
            <button @click="openSupportChat" class="start-chat-btn">
              Contacter le support
            </button>
          </div>
          
          <div v-else class="chats-list">
            <div 
              v-for="chat in chats"
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
            </button>
            
            <div class="chat-info">
              <h4>{{ getChatTitle(activeChat) }}</h4>
              <p v-if="activeChat.mission" class="chat-subtitle">
                Mission: {{ activeChat.mission.title }}
              </p>
            </div>
            
            <button @click="markAsRead" class="mark-read-btn" title="Marquer comme lu">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </button>
          </div>

          <!-- Messages -->
          <div ref="messagesContainer" class="messages-container">
            <div v-if="loadingMessages" class="loading-messages">
              <div class="spinner"></div>
            </div>
            
            <div v-else-if="messages.length === 0" class="no-messages">
              <p>Aucun message</p>
              <p>Soyez le premier à envoyer un message !</p>
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
                  <p>{{ message.content }}</p>
                  <span class="message-time">
                    {{ formatMessageTime(message.created_at) }}
                  </span>
                </div>
              </div>
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
            
            <div v-if="sending" class="sending-indicator">
              Envoi en cours...
            </div>
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

// Refs
const activeChat = ref(null);
const newMessage = ref('');
const loading = ref(false);
const loadingMessages = ref(false);
const sending = ref(false);
const messagesContainer = ref(null);
const messageInput = ref(null);

// Computed
const currentUserId = computed(() => authStore.user?.id);
const chats = computed(() => chatStore.chats);
const messages = computed(() => chatStore.messages);
const unreadCount = computed(() => chatStore.unreadCount);

// Fonctions utilitaires
function getChatTitle(chat) {
  if (chat.chat_type === 'support') return 'Support';
  
  if (chat.other_user) {
    return chat.other_user.email.split('@')[0];
  }
  
  return chat.user1_id === currentUserId.value 
    ? `Utilisateur ${chat.user2_id}`
    : `Utilisateur ${chat.user1_id}`;
}

function getAvatarInitials(chat) {
  if (chat.chat_type === 'support') return 'S';
  
  const title = getChatTitle(chat);
  return title.charAt(0).toUpperCase();
}

function getLastMessagePreview(chat) {
  if (!chat.last_message) return 'Aucun message';
  const msg = chat.last_message.content;
  return msg.length > 50 ? msg.substring(0, 50) + '...' : msg;
}

function formatTime(dateString) {
  if (!dateString) return '';
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
}

function formatMessageTime(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Fonctions principales
async function selectChat(chat) {
  activeChat.value = chat;
  loadingMessages.value = true;
  
  try {
    await chatStore.fetchChatMessages(chat.id);
    // Marquer comme lu automatiquement
    if (chat.unread_count > 0) {
      await chatStore.markChatAsRead(chat.id);
    }
    
    // Focus sur l'input après chargement
    nextTick(() => {
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
}

async function sendMessage() {
  if (!newMessage.value.trim() || !activeChat.value || sending.value) return;
  
  sending.value = true;
  const messageToSend = newMessage.value.trim();
  newMessage.value = '';
  
  try {
    await chatStore.sendMessage(activeChat.value.id, messageToSend);
    
    // Recharger les messages pour avoir l'ID du message
    await chatStore.fetchChatMessages(activeChat.value.id);
    
    // Scroll vers le bas
    nextTick(scrollToBottom);
  } catch (error) {
    console.error('Erreur envoi message:', error);
    // Remettre le message en cas d'erreur
    newMessage.value = messageToSend;
  } finally {
    sending.value = false;
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
}

function backToList() {
  activeChat.value = null;
  chatStore.messages = [];
}

async function markAsRead() {
  if (activeChat.value) {
    await chatStore.markChatAsRead(activeChat.value.id);
  }
}

function openSupportChat() {
  emit('open-support');
}

function closeModal() {
  activeChat.value = null;
  chatStore.messages = [];
  newMessage.value = '';
  emit('close');
}

// Charger les chats quand le modal s'ouvre
watch(() => props.isOpen, async (isOpen) => {
  if (isOpen && !chatStore.chats.length) {
    loading.value = true;
    try {
      await chatStore.fetchMyChats();
    } catch (error) {
      console.error('Erreur chargement chats:', error);
    } finally {
      loading.value = false;
    }
  }
  
  // Focus sur l'input quand on ouvre le modal
  if (isOpen) {
    nextTick(() => {
      if (messageInput.value) {
        messageInput.value.focus();
      }
    });
  }
});

// Polling pour les nouvelles notifications
let pollingInterval = null;

onMounted(() => {
  pollingInterval = setInterval(() => {
    if (props.isOpen && document.visibilityState === 'visible') {
      chatStore.checkForNewMessages().catch(() => {});
    }
  }, 10000);
});

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval);
});
</script>

<style scoped>
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
  padding: 2px 8px;
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
  padding: 6px;
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

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.start-chat-btn {
  margin-top: 16px;
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.start-chat-btn:hover {
  background: #5a67d8;
}

/* Items de chat */
.chat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 8px;
  border: 1px solid #e5e7eb;
}

.chat-item:hover {
  background: #f9fafb;
}

.chat-item.active {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.chat-item.unread {
  border-left: 4px solid #667eea;
}

.avatar {
  width: 40px;
  height: 40px;
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
  align-items: center;
  margin-bottom: 4px;
}

.chat-item-title {
  font-weight: 600;
  color: #111827;
  margin: 0;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-item-time {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
}

.chat-item-preview {
  font-size: 13px;
  color: #6b7280;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-item-meta {
  display: flex;
  gap: 4px;
}

.mission-tag {
  font-size: 11px;
  color: #667eea;
  background: #e0e7ff;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 500;
}

.chat-item-badge {
  background: #ef4444;
  color: white;
  border-radius: 50%;
  min-width: 20px;
  height: 20px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
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
}

.back-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  transition: background 0.2s;
}

.back-btn:hover {
  background: #f3f4f6;
}

.chat-info {
  flex: 1;
}

.chat-info h4 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #111827;
}

.chat-subtitle {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

.mark-read-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  transition: background 0.2s;
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
}

.loading-messages {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.no-messages {
  text-align: center;
  color: #6b7280;
  padding: 40px 20px;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  max-width: 80%;
  animation: fadeIn 0.3s ease;
}

.message.sent {
  align-self: flex-end;
}

.message.received {
  align-self: flex-start;
}

.message-content {
  position: relative;
  padding: 10px 14px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.4;
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
}

.message-time {
  font-size: 11px;
  opacity: 0.8;
  margin-top: 4px;
  display: block;
}

.message.sent .message-time {
  color: rgba(255, 255, 255, 0.9);
  text-align: right;
}

.message.received .message-time {
  color: #6b7280;
  text-align: left;
}

/* Input d'envoi */
.message-input-container {
  border-top: 1px solid #e5e7eb;
  background: white;
  padding: 16px 20px;
}

.message-form {
  display: flex;
  gap: 8px;
}

.message-form input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #d1d5db;
  border-radius: 24px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.message-form input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.message-form input:disabled {
  background: #f9fafb;
  cursor: not-allowed;
}

.send-btn {
  width: 44px;
  height: 44px;
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

.sending-indicator {
  font-size: 12px;
  color: #6b7280;
  text-align: center;
  margin-top: 8px;
  animation: pulse 2s infinite;
}

/* Animations */
@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
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
  
  .message {
    max-width: 90%;
  }
}
</style>