<template>
  <div class="chat-view">
    <!-- En-tête -->
    <div class="chat-header">
      <div class="header-left">
        <h1 class="page-title">Messages</h1>
        <div class="user-type-badge" :class="userType">
          {{ userType === 'client' ? '👔 Client' : '💼 Freelance' }}
        </div>
      </div>
      
      <div class="header-actions">
        <button @click="refreshChats" class="refresh-btn" title="Actualiser">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
        
        <!-- Bouton créer chat pour client seulement -->
        <button 
          v-if="isClient"
          @click="createMissionChat"
          class="create-chat-btn"
        >
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>Nouveau chat</span>
        </button>
        
        <button @click="openSupportChat" class="support-btn">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <span>Support</span>
        </button>
      </div>
    </div>

    <!-- Contenu principal -->
    <div class="chat-container">
      <!-- Sidebar avec liste des chats -->
      <div class="chat-sidebar" :class="{ 'mobile-hidden': activeChat && isMobile }">
        <div class="sidebar-header">
          <h3>Conversations</h3>
          <div class="sidebar-info">
            <div v-if="unreadCount > 0" class="unread-indicator">
              {{ unreadCount }} non lu{{ unreadCount > 1 ? 's' : '' }}
            </div>
            <div v-if="filteredChats.length > 0" class="chat-count">
              {{ filteredChats.length }} conversation{{ filteredChats.length > 1 ? 's' : '' }}
            </div>
          </div>
        </div>

        <!-- Filtres spécifiques selon le type d'utilisateur -->
        <div class="chat-filters">
          <button 
            v-for="filter in userFilters" 
            :key="filter.value"
            :class="{ active: activeFilter === filter.value }"
            @click="activeFilter = filter.value"
          >
            {{ filter.label }}
            <span v-if="filter.badge > 0" class="filter-badge">
              {{ filter.badge }}
            </span>
          </button>
        </div>

        <!-- Recherche pour les clients -->
        <div v-if="isClient && chats.length > 0" class="chat-search">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher un freelance ou une mission..."
            class="search-input"
          />
        </div>

        <!-- Liste des chats -->
        <div class="chats-list">
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>Chargement des conversations...</p>
          </div>

          <div v-else-if="filteredChats.length === 0" class="empty-state">
            <div class="empty-icon">
              <span v-if="isClient">💼</span>
              <span v-else>💬</span>
            </div>
            
            <h4 v-if="isClient">Aucune conversation avec des freelances</h4>
            <h4 v-else>Aucune conversation avec des clients</h4>
            
            <p v-if="activeFilter === 'all'">
              <span v-if="isClient">
                Commencez une conversation avec un freelance pour discuter de vos missions
              </span>
              <span v-else>
                Les clients vous contacteront pour discuter de vos candidatures
              </span>
            </p>
            <p v-else>
              Aucune conversation {{ getFilterText(activeFilter) }}
            </p>
            
            <button v-if="isClient" @click="createMissionChat" class="start-conversation-btn">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Démarrer une conversation
            </button>
            
            <button @click="openSupportChat" class="support-link-btn">
              Contacter le support
            </button>
          </div>

          <div v-else class="chat-items">
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
              <!-- Avatar avec statut -->
              <div class="chat-item-avatar">
                <div class="avatar" :style="getAvatarStyle(chat)">
                  {{ getAvatarInitials(chat) }}
                </div>
                <div v-if="getParticipantStatus(chat)" class="online-status" :class="getParticipantStatus(chat)"></div>
              </div>

              <div class="chat-item-content">
                <div class="chat-item-header">
                  <h4 class="chat-item-title">{{ getChatTitle(chat) }}</h4>
                  <span class="chat-item-time">
                    {{ formatTime(chat.updated_at) }}
                  </span>
                </div>

                <p class="chat-item-preview">
                  {{ getLastMessagePreview(chat) }}
                </p>

                <div class="chat-item-meta">
                  <span v-if="chat.chat_type === 'mission'" class="chat-type mission">
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Mission
                  </span>
                  <span v-else-if="chat.chat_type === 'support'" class="chat-type support">
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                    Support
                  </span>
                  
                  <span v-if="chat.mission" class="mission-title">
                    {{ chat.mission.title }}
                  </span>
                  
                  <!-- Badge spécifique au freelance -->
                  <span v-if="isClient && chat.freelance" class="freelance-rating">
                    ⭐ {{ chat.freelance.rating || 'N/A' }}
                  </span>
                </div>
              </div>

              <div v-if="chat.unread_count > 0" class="chat-item-badge">
                {{ chat.unread_count }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Fenêtre de chat principale -->
      <div class="chat-main" :class="{ 'mobile-full': activeChat && isMobile }">
        <!-- Aucun chat sélectionné -->
        <div v-if="!activeChat" class="no-chat-selected">
          <div class="welcome-card">
            <div class="welcome-icon">
              <span v-if="isClient">👔</span>
              <span v-else>💼</span>
            </div>
            
            <h2 v-if="isClient">
              Bienvenue dans vos messages Client
            </h2>
            <h2 v-else>
              Bienvenue dans vos messages Freelance
            </h2>
            
            <p v-if="isClient">
              Gérez vos conversations avec les freelances sur vos missions
            </p>
            <p v-else>
              Communiquez avec les clients concernant vos candidatures
            </p>
            
            <div class="welcome-actions">
              <button v-if="isClient" @click="createMissionChat" class="primary-btn">
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Démarrer un chat
              </button>
              
              <button @click="openSupportChat" class="secondary-btn">
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                Support
              </button>
            </div>
          </div>

          <!-- Stats selon le type d'utilisateur -->
          <div class="chat-stats">
            <div class="stat-card">
              <div class="stat-value">{{ chats.length }}</div>
              <div class="stat-label">Conversations</div>
            </div>
            
            <div class="stat-card">
              <div class="stat-value">{{ unreadCount }}</div>
              <div class="stat-label">Messages non lus</div>
            </div>
            
            <div v-if="isClient" class="stat-card">
              <div class="stat-value">{{ missionChats.length }}</div>
              <div class="stat-label">Chats de mission</div>
            </div>
            
            <div v-else class="stat-card">
              <div class="stat-value">{{ activeMissionChats.length }}</div>
              <div class="stat-label">Missions actives</div>
            </div>
          </div>
        </div>

        <!-- Chat actif -->
        <div v-else class="active-chat-container">
          <!-- En-tête du chat avec infos spécifiques -->
          <div class="active-chat-header">
            <button v-if="isMobile" @click="backToChatList" class="back-btn">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
            </button>

            <div class="chat-info">
              <div class="chat-title-row">
                <div class="avatar-container">
                  <div class="avatar" :style="getAvatarStyle(activeChat)">
                    {{ getAvatarInitials(activeChat) }}
                  </div>
                  <div v-if="getParticipantStatus(activeChat)" class="online-status" :class="getParticipantStatus(activeChat)"></div>
                </div>
                
                <div class="chat-info-details">
                  <h3 class="chat-title">{{ getChatTitle(activeChat) }}</h3>
                  
                  <div class="chat-subtitle">
                    <span v-if="activeChat.chat_type === 'mission' && activeChat.mission">
                      <span class="mission-label">Mission:</span>
                      {{ activeChat.mission.title }}
                    </span>
                    <span v-else-if="activeChat.chat_type === 'support'">
                      <span class="support-label">Support technique</span>
                    </span>
                    
                    <!-- Infos freelance pour le client -->
                    <span v-if="isClient && activeChat.freelance" class="freelance-info">
                      <span class="separator">•</span>
                      <span class="rating">⭐ {{ activeChat.freelance.rating || 'N/A' }}</span>
                      <span class="separator">•</span>
                      <span class="missions-count">{{ activeChat.freelance.completed_missions || 0 }} missions</span>
                    </span>
                    
                    <!-- Infos client pour le freelance -->
                    <span v-if="!isClient && activeChat.client" class="client-info">
                      <span class="separator">•</span>
                      <span class="client-name">{{ activeChat.client.name }}</span>
                      <span class="separator">•</span>
                      <span class="client-rating">⭐ {{ activeChat.client.rating || 'N/A' }}</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div class="chat-actions">
              <button @click="markAsRead" class="action-btn" title="Marquer comme lu">
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </button>
              
              <button v-if="activeChat.chat_type === 'mission' && isClient" 
                @click="goToMission"
                class="action-btn"
                title="Voir la mission"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
              
              <button v-if="activeChat.chat_type === 'mission' && !isClient"
                @click="goToFreelanceMission"
                class="action-btn"
                title="Voir ma mission"
              >
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
              
              <button @click="refreshMessages" class="action-btn" title="Actualiser">
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Messages -->
          <div ref="messagesContainer" class="messages-container">
            <div v-if="loadingMessages" class="loading-messages">
              <div class="spinner"></div>
              <p>Chargement des messages...</p>
            </div>

            <div v-else-if="messages.length === 0" class="no-messages">
              <div class="empty-chat-icon">
                <span v-if="activeChat.chat_type === 'mission'">📋</span>
                <span v-else>💬</span>
              </div>
              
              <h4 v-if="activeChat.chat_type === 'mission'">
                {{ isClient ? 'Discutez avec votre freelance' : 'Discutez avec votre client' }}
              </h4>
              <h4 v-else>
                Support technique
              </h4>
              
              <p v-if="activeChat.chat_type === 'mission'">
                <span v-if="isClient">
                  Échangez avec le freelance sur les détails de la mission
                </span>
                <span v-else>
                  Discutez avec le client pour clarifier les attentes
                </span>
              </p>
              <p v-else>
                Notre équipe de support est là pour vous aider
              </p>
            </div>

            <div v-else class="messages-list">
              <!-- Date separator -->
              <div v-for="(group, date) in groupedMessages" :key="date" class="message-group">
                <div class="date-separator">
                  <span>{{ formatDateSeparator(date) }}</span>
                </div>
                
                <div 
                  v-for="message in group"
                  :key="message.id"
                  class="message"
                  :class="{ 
                    'sent': message.sender_id === currentUserId,
                    'received': message.sender_id !== currentUserId 
                  }"
                >
                  <!-- Avatar pour les messages reçus -->
                  <div v-if="message.sender_id !== currentUserId" class="message-avatar">
                    <div class="avatar" :style="getMessageAvatarStyle(message)">
                      {{ getMessageAvatarInitials(message) }}
                    </div>
                  </div>
                  
                  <div class="message-content">
                    <!-- Nom de l'expéditeur pour les messages reçus -->
                    <div v-if="message.sender_id !== currentUserId" class="message-sender">
                      {{ getMessageSenderName(message) }}
                    </div>
                    
                    <div class="message-bubble">
                      <div class="message-text">
                        {{ message.content }}
                      </div>
                      <div class="message-footer">
                        <span class="message-time">
                          {{ formatMessageTime(message.created_at) }}
                        </span>
                        <span v-if="message.sender_id === currentUserId && message.read_at" class="read-indicator">
                          <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/>
                          </svg>
                          Lu
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Input d'envoi avec suggestions pour les missions -->
          <div class="message-input-area">
            <!-- Suggestions pour les missions -->
            <div v-if="activeChat.chat_type === 'mission' && showMissionSuggestions" 
                 class="mission-suggestions">
              <button 
                v-for="suggestion in missionSuggestions" 
                :key="suggestion.text"
                @click="useSuggestion(suggestion.text)"
                class="suggestion-btn"
              >
                {{ suggestion.text }}
              </button>
            </div>
            
            <form @submit.prevent="sendMessage" class="message-form">
              <input
                ref="messageInput"
                v-model="newMessage"
                type="text"
                :placeholder="getInputPlaceholder()"
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useChatStore } from '@/stores/chat';
import { useAuthStore } from '@/stores/auth';
import { useMissionStore } from '@/stores/missions';

// Router
const route = useRoute();
const router = useRouter();

// Stores
const chatStore = useChatStore();
const authStore = useAuthStore();
const missionStore = useMissionStore();

// Refs
const activeChat = ref(null);
const newMessage = ref('');
const loading = ref(false);
const loadingMessages = ref(false);
const sending = ref(false);
const activeFilter = ref('all');
const searchQuery = ref('');
const messagesContainer = ref(null);
const messageInput = ref(null);
const isMobile = ref(window.innerWidth < 768);
const showMissionSuggestions = ref(false);

// Computed
const currentUserId = computed(() => authStore.user?.id);
const userType = computed(() => authStore.user?.role || 'freelance');
const isClient = computed(() => userType.value === 'client');
const chats = computed(() => chatStore.chats);
const messages = computed(() => chatStore.messages);
const unreadCount = computed(() => chatStore.unreadCount);

// Filtres selon le type d'utilisateur
const userFilters = computed(() => {
  const baseFilters = [
    { value: 'all', label: 'Tous', badge: chats.value.length },
    { value: 'unread', label: 'Non lus', badge: unreadCount.value },
    { value: 'support', label: 'Support', badge: chats.value.filter(c => c.chat_type === 'support').length }
  ];
  
  if (isClient.value) {
    baseFilters.splice(2, 0, { 
      value: 'mission', 
      label: 'Missions', 
      badge: missionChats.value.length 
    });
    baseFilters.push({ 
      value: 'archived', 
      label: 'Archivés', 
      badge: chats.value.filter(c => c.is_archived).length 
    });
  } else {
    baseFilters.splice(2, 0, { 
      value: 'mission', 
      label: 'Mes missions', 
      badge: missionChats.value.length 
    });
    baseFilters.push({ 
      value: 'completed', 
      label: 'Terminées', 
      badge: chats.value.filter(c => c.mission?.status === 'completed').length 
    });
  }
  
  return baseFilters;
});

// Chats filtrés avec recherche
const filteredChats = computed(() => {
  let filtered = chats.value;

  // Filtre principal
  switch (activeFilter.value) {
    case 'unread':
      filtered = filtered.filter(chat => chat.unread_count > 0);
      break;
    case 'mission':
      filtered = filtered.filter(chat => chat.chat_type === 'mission');
      break;
    case 'support':
      filtered = filtered.filter(chat => chat.chat_type === 'support');
      break;
    case 'archived':
      filtered = filtered.filter(chat => chat.is_archived);
      break;
    case 'completed':
      filtered = filtered.filter(chat => chat.mission?.status === 'completed');
      break;
  }

  // Recherche (pour clients seulement)
  if (isClient.value && searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(chat => {
      const title = getChatTitle(chat).toLowerCase();
      const missionTitle = chat.mission?.title?.toLowerCase() || '';
      const freelanceName = chat.freelance?.name?.toLowerCase() || '';
      
      return title.includes(query) || 
             missionTitle.includes(query) || 
             freelanceName.includes(query);
    });
  }

  // Trier par date de mise à jour (du plus récent au plus ancien)
  return [...filtered].sort((a, b) => {
    return new Date(b.updated_at) - new Date(a.updated_at);
  });
});

// Chats de mission
const missionChats = computed(() => 
  chats.value.filter(chat => chat.chat_type === 'mission')
);

// Missions actives (pour freelances)
const activeMissionChats = computed(() => 
  chats.value.filter(chat => 
    chat.chat_type === 'mission' && 
    chat.mission?.status === 'in_progress'
  )
);

// Messages groupés par date
const groupedMessages = computed(() => {
  const groups = {};
  
  messages.value.forEach(message => {
    const date = new Date(message.created_at).toLocaleDateString('fr-FR');
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(message);
  });
  
  return groups;
});

// Suggestions pour les missions
const missionSuggestions = computed(() => {
  if (!activeChat.value || activeChat.value.chat_type !== 'mission') return [];
  
  const suggestions = [];
  
  if (isClient.value) {
    suggestions.push(
      { text: 'Pouvez-vous me donner une mise à jour sur l\'avancement ?' },
      { text: 'Avez-vous besoin de précisions supplémentaires ?' },
      { text: 'Quand pensez-vous pouvoir livrer le travail ?' },
      { text: 'Le budget est-il toujours respecté ?' }
    );
  } else {
    suggestions.push(
      { text: 'J\'ai une question sur les spécifications de la mission' },
      { text: 'Voici une mise à jour sur mon avancement' },
      { text: 'J\'ai besoin de plus d\'informations pour continuer' },
      { text: 'Le travail est terminé, pouvez-vous le vérifier ?' }
    );
  }
  
  return suggestions;
});

// Fonctions utilitaires améliorées
function getChatTitle(chat) {
  if (chat.chat_type === 'support') return 'Support';
  
  // Pour les clients : afficher le nom du freelance
  if (isClient.value && chat.freelance) {
    return chat.freelance.name || `Freelance #${chat.freelance.id}`;
  }
  
  // Pour les freelances : afficher le nom du client ou l'entreprise
  if (!isClient.value && chat.client) {
    return chat.client.name || chat.client.company || `Client #${chat.client.id}`;
  }
  
  // Fallback
  if (chat.other_user) {
    return chat.other_user.email.split('@')[0];
  }
  
  return `Utilisateur ${chat.user1_id === currentUserId.value ? chat.user2_id : chat.user1_id}`;
}

function getAvatarInitials(chat) {
  if (chat.chat_type === 'support') return 'S';
  
  const title = getChatTitle(chat);
  return title.charAt(0).toUpperCase();
}

function getAvatarStyle(chat) {
  if (chat.chat_type === 'support') {
    return { background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' };
  }
  
  // Couleurs différentes selon le type d'utilisateur
  if (isClient.value) {
    // Client voit des freelances (bleu)
    return { background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)' };
  } else {
    // Freelance voit des clients (violet)
    return { background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' };
  }
}

function getParticipantStatus(chat) {
  // Simuler le statut en ligne (à remplacer par du WebSocket réel)
  if (chat.chat_type === 'support') return null;
  
  // Pour l'exemple : 70% de chance d'être en ligne
  return Math.random() > 0.3 ? 'online' : 'offline';
}

function getLastMessagePreview(chat) {
  if (!chat.last_message) return 'Aucun message';
  
  let msg = chat.last_message.content;
  if (msg.length > 60) {
    msg = msg.substring(0, 60) + '...';
  }
  
  // Ajouter "Vous: " si c'est votre message
  if (chat.last_message.sender_id === currentUserId.value) {
    return `Vous: ${msg}`;
  }
  
  return msg;
}

function getOtherParticipant(chat) {
  if (chat.chat_type === 'support') return 'le support';
  
  if (isClient.value && chat.freelance) {
    return chat.freelance.name || `le freelance`;
  }
  
  if (!isClient.value && chat.client) {
    return chat.client.name || 'le client';
  }
  
  return `utilisateur ${chat.user1_id === currentUserId.value ? chat.user2_id : chat.user1_id}`;
}

function getMessageAvatarStyle(message) {
  // Style différent pour l'expéditeur
  if (message.sender_id === currentUserId.value) {
    return { background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' };
  } else {
    return { background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' };
  }
}

function getMessageAvatarInitials(message) {
  if (message.sender) {
    return message.sender.name?.charAt(0) || 'U';
  }
  return 'U';
}

function getMessageSenderName(message) {
  if (message.sender_id === currentUserId.value) return 'Vous';
  if (message.sender) return message.sender.name || message.sender.email.split('@')[0];
  return 'Utilisateur';
}

function getInputPlaceholder() {
  if (!activeChat.value) return 'Tapez votre message...';
  
  if (activeChat.value.chat_type === 'mission') {
    return isClient.value 
      ? 'Envoyez un message à votre freelance...' 
      : 'Envoyez un message à votre client...';
  }
  
  return 'Envoyez un message au support...';
}

function getFilterText(filter) {
  const filterTexts = {
    'all': '',
    'unread': 'non lue',
    'mission': 'de mission',
    'support': 'de support',
    'archived': 'archivée',
    'completed': 'terminée'
  };
  return filterTexts[filter] || '';
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
    
    // Afficher les suggestions pour les missions
    showMissionSuggestions.value = chat.chat_type === 'mission';
    
    // Scroll vers le bas après chargement
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
    
    // Recharger les messages
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

function useSuggestion(text) {
  newMessage.value = text;
  if (messageInput.value) {
    messageInput.value.focus();
  }
}

function createMissionChat() {
  if (isClient.value) {
    // Pour le client : ouvrir un modal pour sélectionner une mission et un freelance
    router.push('/missions?createChat=true');
  } else {
    // Pour le freelance : créer un chat support
    openSupportChat();
  }
}

function goToMission() {
  if (activeChat.value?.mission) {
    router.push(`/missions/${activeChat.value.mission.id}`);
  }
}

function goToFreelanceMission() {
  if (activeChat.value?.mission) {
    router.push(`/freelance/missions/${activeChat.value.mission.id}`);
  }
}

async function refreshChats() {
  loading.value = true;
  try {
    await chatStore.fetchMyChats();
  } catch (error) {
    console.error('Erreur actualisation chats:', error);
  } finally {
    loading.value = false;
  }
}

async function refreshMessages() {
  if (!activeChat.value) return;
  
  loadingMessages.value = true;
  try {
    await chatStore.fetchChatMessages(activeChat.value.id);
  } catch (error) {
    console.error('Erreur actualisation messages:', error);
  } finally {
    loadingMessages.value = false;
  }
}

async function markAsRead() {
  if (activeChat.value) {
    await chatStore.markChatAsRead(activeChat.value.id);
  }
}

function openSupportChat() {
  chatStore.manageSupportChat('create')
    .then(() => {
      refreshChats();
    })
    .catch(console.error);
}

function backToChatList() {
  activeChat.value = null;
  chatStore.messages = [];
  showMissionSuggestions.value = false;
}

// Lifecycle hooks
onMounted(async () => {
  // Charger les chats au démarrage
  loading.value = true;
  try {
    await chatStore.fetchMyChats();
    
    // Vérifier s'il y a un chatId dans l'URL
    const chatId = route.query.chatId;
    if (chatId) {
      const chat = chats.value.find(c => c.id === parseInt(chatId));
      if (chat) {
        await selectChat(chat);
      }
    }
  } catch (error) {
    console.error('Erreur initialisation chat:', error);
  } finally {
    loading.value = false;
  }
  
  // Détection mobile
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth < 768;
  });
});

onUnmounted(() => {
  window.removeEventListener('resize', () => {
    isMobile.value = window.innerWidth < 768;
  });
});
</script>

<style scoped>
/* Styles existants à conserver... */

/* Nouveaux styles pour la distinction client/freelance */
.user-type-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  margin-left: 12px;
}

.user-type-badge.client {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
}

.user-type-badge.freelance {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
}

.header-left {
  display: flex;
  align-items: center;
}

.create-chat-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  transition: all 0.2s;
}

.create-chat-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.sidebar-info {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chat-count {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 10px;
}

.chat-search {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.search-input {
  width: 100%;
  padding: 10px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.support-link-btn {
  margin-top: 8px;
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  font-size: 14px;
  text-decoration: underline;
}

.support-link-btn:hover {
  color: #3b82f6;
}

.chat-item-avatar {
  position: relative;
}

.online-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
}

.online-status.online {
  background: #10b981;
}

.online-status.offline {
  background: #9ca3af;
}

.freelance-rating, .client-rating {
  font-size: 11px;
  color: #f59e0b;
  font-weight: 600;
}

.freelance-info, .client-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
}

.separator {
  color: #d1d5db;
}

.avatar-container {
  position: relative;
  width: 40px;
  height: 40px;
  margin-right: 12px;
}

.chat-title-row {
  display: flex;
  align-items: center;
}

.chat-info-details {
  flex: 1;
}

.mission-label, .support-label {
  font-weight: 600;
  color: #374151;
}

.client-name {
  font-weight: 500;
  color: #111827;
}

.missions-count {
  color: #6b7280;
  font-size: 12px;
}

.message-avatar {
  margin-right: 8px;
  align-self: flex-start;
}

.message-sender {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 4px;
}

.message-bubble {
  background: white;
  padding: 10px 14px;
  border-radius: 18px;
  border: 1px solid #e5e7eb;
  max-width: 100%;
}

.message.sent .message-bubble {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border: none;
  color: white;
}

.mission-suggestions {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  overflow-x: auto;
}

.suggestion-btn {
  white-space: nowrap;
  padding: 8px 12px;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 16px;
  font-size: 12px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-btn:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

/* Animation pour les nouveaux messages */
@keyframes highlight {
  0% { background-color: rgba(59, 130, 246, 0.1); }
  100% { background-color: transparent; }
}

.message.new {
  animation: highlight 2s ease;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .user-type-badge {
    display: none;
  }
  
  .create-chat-btn span {
    display: none;
  }
  
  .mission-suggestions {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .suggestion-btn {
    font-size: 11px;
    padding: 6px 10px;
  }
}

/* Styles pour les états de mission */
.chat-item.mission-active .mission-title {
  color: #10b981;
  font-weight: 600;
}

.chat-item.mission-completed .mission-title {
  color: #6b7280;
  text-decoration: line-through;
}

.chat-item.mission-cancelled .mission-title {
  color: #ef4444;
}
.chat-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f9fafb;
}

/* En-tête */
.chat-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  color: #111827;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.refresh-btn, .support-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.refresh-btn {
  background: #f3f4f6;
  color: #374151;
}

.refresh-btn:hover {
  background: #e5e7eb;
}

.support-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.support-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.icon {
  width: 18px;
  height: 18px;
  stroke-width: 2;
}

/* Conteneur principal */
.chat-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* Sidebar */
.chat-sidebar {
  width: 350px;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  color: #111827;
}

.unread-indicator {
  background: #ef4444;
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.chat-filters {
  display: flex;
  padding: 16px;
  gap: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.chat-filters button {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s;
}

.chat-filters button:hover {
  border-color: #9ca3af;
}

.chat-filters button.active {
  background: #667eea;
  border-color: #667eea;
  color: white;
}

.filter-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

/* Liste des chats */
.chats-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #6b7280;
  padding: 40px 20px;
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

.start-conversation-btn {
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

.start-conversation-btn:hover {
  background: #5a67d8;
}

/* Items de chat */
.chat-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.chat-item:hover {
  background: #f9fafb;
  border-color: #e5e7eb;
}

.chat-item.active {
  background: #f0f5ff;
  border-color: #667eea;
}

.chat-item.unread {
  border-left: 4px solid #667eea;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
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
  margin: 0 0 6px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-item-meta {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chat-type {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}

.chat-type.mission {
  background: #e0e7ff;
  color: #4f46e5;
}

.chat-type.support {
  background: #dcfce7;
  color: #059669;
}

.mission-title {
  font-size: 11px;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.chat-item-badge {
  background: #ef4444;
  color: white;
  border-radius: 50%;
  min-width: 22px;
  height: 22px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Chat principal */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: white;
}

.no-chat-selected {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
}

.welcome-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  margin-bottom: 40px;
}

.welcome-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.welcome-card h2 {
  font-size: 24px;
  color: #111827;
  margin: 0 0 12px 0;
}

.welcome-card p {
  color: #6b7280;
  margin: 0 0 24px 0;
}

.welcome-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.primary-btn, .secondary-btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.primary-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

.secondary-btn {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.secondary-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.chat-stats {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  min-width: 120px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
}

/* Chat actif */
.active-chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.active-chat-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: white;
}

.back-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  transition: background 0.2s;
  display: none;
}

.back-btn:hover {
  background: #f3f4f6;
}

.chat-info {
  flex: 1;
}

.chat-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.chat-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #111827;
}

.chat-badge {
  background: #ef4444;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.chat-subtitle {
  font-size: 14px;
  color: #6b7280;
  display: flex;
  gap: 8px;
  align-items: center;
}

.chat-participants {
  font-size: 13px;
  color: #9ca3af;
}

.chat-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
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

.action-btn:hover {
  background: #f3f4f6;
  color: #667eea;
}

/* Messages */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #f9fafb;
}

.loading-messages {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6b7280;
}

.no-messages {
  text-align: center;
  color: #6b7280;
  padding: 60px 20px;
}

.empty-chat-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.message-group {
  margin-bottom: 24px;
}

.date-separator {
  text-align: center;
  margin: 24px 0;
  position: relative;
}

.date-separator::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  height: 1px;
  background: #e5e7eb;
}

.date-separator span {
  background: white;
  padding: 6px 16px;
  border-radius: 16px;
  font-size: 13px;
  color: #6b7280;
  position: relative;
  z-index: 1;
  border: 1px solid #e5e7eb;
}

.message {
  margin-bottom: 12px;
  animation: fadeIn 0.3s ease;
}

.message.sent {
  display: flex;
  justify-content: flex-end;
}

.message.received {
  display: flex;
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
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

.message-text {
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 4px;
}

.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  opacity: 0.8;
}

.message-time {
  font-size: 11px;
}

.read-indicator {
  font-size: 11px;
  opacity: 0.8;
}

/* Input d'envoi */
.message-input-area {
  border-top: 1px solid #e5e7eb;
  background: white;
  padding: 16px 24px;
}

.message-form {
  display: flex;
  gap: 12px;
  align-items: center;
}

.message-form input {
  flex: 1;
  padding: 12px 20px;
  border: 1px solid #d1d5db;
  border-radius: 24px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  background: #f9fafb;
}

.message-form input:focus {
  background: white;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.message-form input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-btn {
  width: 48px;
  height: 48px;
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
  width: 20px;
  height: 20px;
  stroke-width: 2.5;
}

.sending-indicator {
  font-size: 12px;
  color: #6b7280;
  text-align: center;
  margin-top: 8px;
  animation: pulse 2s infinite;
}

/* Bouton mobile */
.mobile-list-toggle {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 24px;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  display: none;
}

/* Responsive */
@media (max-width: 768px) {
  .chat-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    z-index: 1000;
    transition: transform 0.3s ease;
  }
  
  .chat-sidebar.mobile-hidden {
    transform: translateX(-100%);
  }
  
  .chat-main.mobile-full {
    width: 100%;
  }
  
  .back-btn {
    display: flex;
  }
  
  .mobile-list-toggle {
    display: flex;
  }
  
  .chat-header {
    padding: 12px 16px;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .support-btn span {
    display: none;
  }
  
  .chat-filters {
    overflow-x: auto;
    padding: 12px 16px;
  }
  
  .chat-filters button {
    min-width: 80px;
    white-space: nowrap;
  }
  
  .message-content {
    max-width: 85%;
  }
}

@media (max-width: 480px) {
  .chat-stats {
    flex-direction: column;
    gap: 12px;
  }
  
  .stat-card {
    min-width: auto;
    width: 100%;
  }
  
  .welcome-card {
    padding: 24px;
  }
  
  .welcome-actions {
    flex-direction: column;
  }
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
</style>