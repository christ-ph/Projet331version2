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
        <!-- Recherche globale -->
        <div class="global-search">
          <input
            v-model="globalSearchQuery"
            type="text"
            placeholder="Rechercher un utilisateur..."
            @focus="showUserSearchResults = true"
            @blur="onSearchBlur"
            @keyup.enter="searchUsers"
          />
          <button @click="searchUsers" class="search-btn">
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
          
          <!-- Résultats de recherche -->
          <div v-if="showUserSearchResults && userSearchResults.length > 0" 
               class="user-search-results">
            <div 
              v-for="user in userSearchResults"
              :key="user.id"
              class="user-result"
              @click="startChatWithUser(user)"
            >
              <div class="user-avatar">
                {{ getUserInitials(user) }}
              </div>
              <div class="user-info">
                <strong>{{ user.name || user.email.split('@')[0] }}</strong>
                <span class="user-role">{{ user.role === 'client' ? '👔 Client' : '💼 Freelance' }}</span>
              </div>
              <div class="user-action">
                <button class="start-chat-btn">
                  💬 Discuter
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <button @click="refreshChats" class="refresh-btn" title="Actualiser">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
        
        <button @click="showNewChatModal = true" class="create-chat-btn">
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

    <!-- Modal de nouveau chat -->
    <div v-if="showNewChatModal" class="modal-overlay" @click.self="showNewChatModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Nouvelle conversation</h3>
          <button class="close-btn" @click="showNewChatModal = false">×</button>
        </div>
        
        <div class="modal-body">
          <div class="chat-type-selection">
            <div class="tabs">
              <button 
                :class="{ active: newChatType === 'mission' }"
                @click="newChatType = 'mission'"
              >
                🎯 Mission
              </button>
              <button 
                :class="{ active: newChatType === 'user' }"
                @click="newChatType = 'user'"
              >
                👤 Utilisateur
              </button>
              <button 
                :class="{ active: newChatType === 'support' }"
                @click="newChatType = 'support'"
              >
                🛟 Support
              </button>
            </div>
            
            <!-- Sélection de mission -->
            <div v-if="newChatType === 'mission'" class="mission-section">
              <label>Sélectionnez une mission :</label>
              <select v-model="selectedMissionId" @change="loadMissionFreelances">
                <option value="">-- Choisir une mission --</option>
                <option 
                  v-for="mission in userMissions"
                  :key="mission.id"
                  :value="mission.id"
                >
                  {{ mission.title }} ({{ mission.status }})
                </option>
              </select>
              
              <!-- Liste des freelances -->
              <div v-if="missionFreelances.length > 0" class="freelance-list">
                <label>Sélectionnez un freelance :</label>
                <div 
                  v-for="freelance in missionFreelances"
                  :key="freelance.id"
                  class="freelance-item"
                  :class="{ selected: selectedFreelanceId === freelance.id }"
                  @click="selectedFreelanceId = freelance.id"
                >
                  <div class="freelance-avatar">
                    {{ getUserInitials(freelance) }}
                  </div>
                  <div class="freelance-info">
                    <strong>{{ freelance.name || freelance.email }}</strong>
                    <span class="freelance-rating">⭐ {{ freelance.rating || 'N/A' }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Recherche d'utilisateur -->
            <div v-if="newChatType === 'user'" class="user-section">
              <div class="search-container">
                <input
                  v-model="userSearchInput"
                  type="text"
                  placeholder="Rechercher un utilisateur par nom ou email..."
                  @keyup.enter="searchUsersForChat"
                />
                <button @click="searchUsersForChat" class="search-btn">
                  🔍
                </button>
              </div>
              
              <!-- Résultats de recherche -->
              <div v-if="userSearchResults.length > 0" class="search-results">
                <div 
                  v-for="user in userSearchResults"
                  :key="user.id"
                  class="user-result-item"
                  :class="{ selected: selectedUserId === user.id }"
                  @click="selectUserForChat(user)"
                >
                  <div class="user-avatar-small">
                    {{ getUserInitials(user) }}
                  </div>
                  <div class="user-details">
                    <div class="user-name">{{ user.name || user.email }}</div>
                    <div class="user-role-badge" :class="user.role">
                      {{ user.role === 'client' ? '👔 Client' : '💼 Freelance' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Support -->
            <div v-if="newChatType === 'support'" class="support-section">
              <label>Décrivez votre problème :</label>
              <textarea
                v-model="supportMessage"
                placeholder="Expliquez votre problème en détail..."
                rows="4"
              ></textarea>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="showNewChatModal = false" class="cancel-btn">
            Annuler
          </button>
          <button 
            @click="createNewChat"
            :disabled="!canCreateNewChat"
            class="confirm-btn"
          >
            {{ getCreateButtonText() }}
          </button>
        </div>
      </div>
    </div>

    <!-- Contenu principal -->
    <div class="chat-container">
      <!-- Sidebar -->
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

        <!-- Filtres -->
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

        <!-- Recherche locale -->
        <div class="local-search">
          <input
            v-model="localSearchQuery"
            type="text"
            placeholder="Rechercher dans les conversations..."
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
            
            <h4 v-if="localSearchQuery">
              Aucun résultat pour "{{ localSearchQuery }}"
            </h4>
            <h4 v-else-if="isClient">Aucune conversation avec des freelances</h4>
            <h4 v-else>Aucune conversation avec des clients</h4>
            
            <p v-if="activeFilter === 'all' && !localSearchQuery">
              <span v-if="isClient">
                Commencez une conversation avec un freelance pour discuter de vos missions
              </span>
              <span v-else>
                Les clients vous contacteront pour discuter de vos candidatures
              </span>
            </p>
            <p v-else-if="localSearchQuery">
              Essayez avec d'autres termes de recherche
            </p>
            <p v-else>
              Aucune conversation
            </p>
            
            <button @click="showNewChatModal = true" class="start-conversation-btn">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Démarrer une conversation
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
                  <span v-else class="chat-type user">
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Utilisateur
                  </span>
                  
                  <span v-if="chat.mission" class="mission-title">
                    {{ chat.mission.title }}
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
              <button @click="showNewChatModal = true" class="primary-btn">
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Nouvelle conversation
              </button>
              
              <button @click="openSupportChat" class="secondary-btn">
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                Support
              </button>
            </div>
          </div>

          <!-- Stats -->
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
            
            <div class="stat-card">
              <div class="stat-value">{{ userChats.length }}</div>
              <div class="stat-label">Chats utilisateur</div>
            </div>
          </div>
        </div>

        <!-- Chat actif -->
        <div v-else class="active-chat-container">
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
                    <span class="chat-type-label" :class="activeChat.chat_type">
                      {{ getChatTypeLabel(activeChat.chat_type) }}
                    </span>
                    
                    <span v-if="activeChat.chat_type === 'mission' && activeChat.mission" class="mission-info">
                      <span class="separator">•</span>
                      <span class="mission-name">{{ activeChat.mission.title }}</span>
                    </span>
                    
                    <span v-if="activeChat.other_participant" class="participant-details">
                      <span class="separator">•</span>
                      <span v-if="activeChat.other_participant.role === 'freelance'">
                        ⭐ {{ activeChat.other_participant.rating || 'N/A' }}
                      </span>
                      <span v-if="activeChat.other_participant.role === 'client'">
                        👔 {{ activeChat.other_participant.company || 'Client' }}
                      </span>
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
              
              <button v-if="activeChat.chat_type === 'mission'" 
                @click="goToMission"
                class="action-btn"
                :title="isClient ? 'Voir la mission' : 'Voir ma mission'"
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
                <span v-else-if="activeChat.chat_type === 'support'">🛟</span>
                <span v-else>💬</span>
              </div>
              
              <h4>{{ getWelcomeMessage() }}</h4>
              <p>{{ getWelcomeDescription() }}</p>
              
              <div v-if="activeChat.chat_type !== 'support'" class="initial-suggestions">
                <button 
                  v-for="suggestion in getInitialSuggestions()"
                  :key="suggestion"
                  @click="newMessage = suggestion"
                  class="suggestion-btn"
                >
                  {{ suggestion }}
                </button>
              </div>
            </div>

            <div v-else class="messages-list">
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
                  <div v-if="message.sender_id !== currentUserId" class="message-avatar">
                    <div class="avatar" :style="getMessageAvatarStyle(message)">
                      {{ getMessageAvatarInitials(message) }}
                    </div>
                  </div>
                  
                  <div class="message-content">
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
                          ✓ Lu
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Input d'envoi -->
          <div class="message-input-area">
            <div class="message-actions">
              <button @click="toggleFileUpload" class="action-btn" title="Ajouter un fichier">
                📎
              </button>
              <button @click="showMissionSuggestions = !showMissionSuggestions" 
                      v-if="activeChat.chat_type === 'mission'"
                      class="action-btn"
                      title="Suggestions">
                💡
              </button>
            </div>
            
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
import axios from 'axios';

// Router et Stores
const route = useRoute();
const router = useRouter();
const chatStore = useChatStore();
const authStore = useAuthStore();

// Refs
const userMissions = ref([]); 
const activeChat = ref(null);
const newMessage = ref('');
const loading = ref(false);
const loadingMessages = ref(false);
const sending = ref(false);
const activeFilter = ref('all');
const localSearchQuery = ref('');
const globalSearchQuery = ref('');
const messagesContainer = ref(null);
const messageInput = ref(null);
const isMobile = ref(window.innerWidth < 768);
const showMissionSuggestions = ref(false);
const showUserSearchResults = ref(false);
const showNewChatModal = ref(false);

// Variables pour le nouveau chat
const newChatType = ref('mission');
const selectedMissionId = ref(null);
const selectedFreelanceId = ref(null);
const userSearchInput = ref('');
const selectedUserId = ref(null);
const selectedUser = ref(null);
const supportMessage = ref('');

// Résultats de recherche
const userSearchResults = ref([]);
const missionFreelances = ref([]);
const selectedUserMissions = ref([]);
const activeChatUserMissions = ref([]);

// Computed
const currentUserId = computed(() => authStore.user?.id);
const userType = computed(() => authStore.user?.role || 'freelance');
const isClient = computed(() => userType.value === 'client');
const chats = computed(() => chatStore.chats || []);
const messages = computed(() => chatStore.messages || []);
const unreadCount = computed(() => chatStore.unreadCount || 0);

const missionChats = computed(() => 
  chats.value.filter(chat => chat.chat_type === 'mission')
);

const userChats = computed(() => 
  chats.value.filter(chat => chat.chat_type === 'direct')
);

const supportChats = computed(() => 
  chats.value.filter(chat => chat.chat_type === 'support')
);

const filteredChats = computed(() => {
  let filtered = chats.value;

  // Filtre principal
  if (activeFilter.value === 'unread') {
    filtered = filtered.filter(chat => chat.unread_count > 0);
  } else if (activeFilter.value === 'mission') {
    filtered = filtered.filter(chat => chat.chat_type === 'mission');
  } else if (activeFilter.value === 'user') {
    filtered = filtered.filter(chat => chat.chat_type === 'direct');
  } else if (activeFilter.value === 'support') {
    filtered = filtered.filter(chat => chat.chat_type === 'support');
  }

  // Recherche locale
  if (localSearchQuery.value.trim()) {
    const query = localSearchQuery.value.toLowerCase();
    filtered = filtered.filter(chat => {
      const title = getChatTitle(chat).toLowerCase();
      const participantEmail = chat.other_participant?.email?.toLowerCase() || '';
      const missionTitle = chat.mission?.title?.toLowerCase() || '';
      
      return title.includes(query) || 
             participantEmail.includes(query) ||
             missionTitle.includes(query);
    });
  }

  return [...filtered].sort((a, b) => {
    return new Date(b.updated_at || 0) - new Date(a.updated_at || 0);
  });
});

const userFilters = computed(() => {
  const baseFilters = [
    { value: 'all', label: 'Tous', badge: chats.value.length },
    { value: 'unread', label: 'Non lus', badge: unreadCount.value },
    { value: 'mission', label: 'Missions', badge: missionChats.value.length },
    { value: 'user', label: 'Utilisateurs', badge: userChats.value.length },
    { value: 'support', label: 'Support', badge: supportChats.value.length }
  ];
  
  return baseFilters;
});

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

const missionSuggestions = computed(() => {
  if (!activeChat.value || activeChat.value.chat_type !== 'mission') return [];
  
  const suggestions = [];
  
  if (isClient.value) {
    suggestions.push(
      { text: 'Pouvez-vous me donner une mise à jour sur l\'avancement ?' },
      { text: 'Avez-vous besoin de précisions supplémentaires ?' },
      { text: 'Quand pensez-vous pouvoir livrer le travail ?' }
    );
  } else {
    suggestions.push(
      { text: 'J\'ai une question sur les spécifications de la mission' },
      { text: 'Voici une mise à jour sur mon avancement' },
      { text: 'J\'ai besoin de plus d\'informations pour continuer' }
    );
  }
  
  return suggestions;
});

const canCreateNewChat = computed(() => {
  if (newChatType.value === 'mission') {
    return !!selectedMissionId.value && !!selectedFreelanceId.value;
  }
  if (newChatType.value === 'user') {
    return !!selectedUserId.value;
  }
  if (newChatType.value === 'support') {
    return supportMessage.value.trim().length > 0;
  }
  return false;
});

// Fonctions utilitaires
function getChatTitle(chat) {
  if (!chat) return 'Chat';
  if (chat.chat_type === 'support') return 'Support';
  
  if (chat.other_participant) {
    return chat.other_participant.name || 
           chat.other_participant.email?.split('@')[0] || 
           `Utilisateur ${chat.other_participant.id}`;
  }
  
  return `Chat ${chat.id}`;
}

function getChatTypeLabel(type) {
  const labels = {
    'mission': 'Mission',
    'support': 'Support',
    'direct': 'Utilisateur'
  };
  return labels[type] || 'Chat';
}

function getUserInitials(user) {
  if (!user) return '??';
  if (user.name) {
    return user.name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
  }
  return user.email?.substring(0, 2).toUpperCase() || '??';
}

function getLastMessagePreview(chat) {
  if (!chat || !chat.last_message) return 'Aucun message';
  
  let msg = chat.last_message.content;
  if (msg.length > 60) {
    msg = msg.substring(0, 60) + '...';
  }
  
  if (chat.last_message.sender_id === currentUserId.value) {
    return `Vous: ${msg}`;
  }
  
  return msg;
}

function getAvatarStyle(chat) {
  if (chat.chat_type === 'support') {
    return { background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' };
  }
  return { background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' };
}

function getMessageAvatarStyle(message) {
  return { background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' };
}

function getMessageAvatarInitials(message) {
  return message.sender?.name?.charAt(0) || 'U';
}

function getMessageSenderName(message) {
  if (message.sender_id === currentUserId.value) return 'Vous';
  return message.sender?.name || 'Utilisateur';
}

function getParticipantStatus() {
  return Math.random() > 0.3 ? 'online' : null;
}

function getInputPlaceholder() {
  if (!activeChat.value) return 'Tapez votre message...';
  
  if (activeChat.value.chat_type === 'mission') {
    return isClient.value 
      ? 'Envoyez un message à votre freelance...' 
      : 'Envoyez un message à votre client...';
  }
  
  return 'Envoyez un message...';
}

function getCreateButtonText() {
  switch (newChatType.value) {
    case 'mission': return 'Créer chat de mission';
    case 'user': return 'Démarrer la conversation';
    case 'support': return 'Contacter le support';
    default: return 'Créer';
  }
}

function getWelcomeMessage() {
  if (!activeChat.value) return '';
  
  switch (activeChat.value.chat_type) {
    case 'mission':
      return isClient.value ? 'Discutez avec votre freelance' : 'Discutez avec votre client';
    case 'support':
      return 'Support technique';
    default:
      return 'Conversation privée';
  }
}

function getWelcomeDescription() {
  if (!activeChat.value) return '';
  
  switch (activeChat.value.chat_type) {
    case 'mission':
      return isClient.value 
        ? 'Échangez avec le freelance sur les détails de la mission'
        : 'Discutez avec le client pour clarifier les attentes';
    case 'support':
      return 'Notre équipe de support est là pour vous aider';
    default:
      return 'Échangez en privé avec cet utilisateur';
  }
}

function getInitialSuggestions() {
  if (!activeChat.value) return [];
  
  const suggestions = [];
  
  if (activeChat.value.chat_type === 'mission') {
    if (isClient.value) {
      suggestions.push('Bonjour, pouvez-vous me donner des nouvelles du projet ?');
    } else {
      suggestions.push('Bonjour, j\'ai une question concernant la mission');
    }
  } else if (activeChat.value.chat_type === 'direct') {
    suggestions.push('Bonjour ! Comment allez-vous ?');
  }
  
  return suggestions;
}

function formatTime(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '';
  
  const now = new Date();
  const diffHours = (now - date) / (1000 * 60 * 60);
  
  if (diffHours < 24) {
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  } else if (diffHours < 48) {
    return 'Hier';
  } else {
    return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
  }
}

function formatDateSeparator(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '';

  const today = new Date();
  if (date.toDateString() === today.toDateString()) {
    return "Aujourd'hui";
  }
  
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  if (date.toDateString() === yesterday.toDateString()) {
    return "Hier";
  }

  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long'
  });
}

function formatMessageTime(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '';
  
  return date.toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit'
  });
}

// Fonctions principales
async function searchUsers() {
  if (!globalSearchQuery.value.trim()) {
    userSearchResults.value = [];
    return;
  }
  
  try {
    const response = await axios.get('/api/users/search', {
      params: {
        query: globalSearchQuery.value,
        exclude_current: true,
        limit: 10
      }
    });
    
    userSearchResults.value = response.data.users || [];
  } catch (error) {
    console.error('Erreur recherche utilisateurs:', error);
    userSearchResults.value = [];
  }
}

function onSearchBlur() {
  setTimeout(() => {
    showUserSearchResults.value = false;
  }, 200);
}

async function searchUsersForChat() {
  if (!userSearchInput.value.trim()) {
    userSearchResults.value = [];
    return;
  }
  
  try {
    const response = await axios.get('/api/users/search', {
      params: {
        query: userSearchInput.value,
        exclude_current: true,
        role: isClient.value ? 'freelance' : 'client'
      }
    });
    
    userSearchResults.value = response.data.users || [];
  } catch (error) {
    console.error('Erreur recherche pour chat:', error);
    userSearchResults.value = [];
  }
}

async function startChatWithUser(user) {
  try {
    const existingChat = chats.value.find(chat => 
      chat.chat_type === 'direct' && 
      chat.other_participant?.id === user.id
    );
    
    if (existingChat) {
      await selectChat(existingChat);
    } else {
      const response = await axios.post('/api/chats/direct', {
        user_id: user.id
      });
      
      if (response.data.chat) {
        await refreshChats();
        const newChat = chats.value.find(c => c.id === response.data.chat.id);
        if (newChat) {
          await selectChat(newChat);
        }
      }
    }
    
    showUserSearchResults.value = false;
    globalSearchQuery.value = '';
  } catch (error) {
    console.error('Erreur démarrage chat:', error);
  }
}

async function selectUserForChat(user) {
  selectedUserId.value = user.id;
  selectedUser.value = user;
}

async function loadMissionFreelances() {
  if (!selectedMissionId.value) {
    missionFreelances.value = [];
    return;
  }
  
  try {
    const response = await axios.get(`/api/missions/${selectedMissionId.value}/freelances`);
    missionFreelances.value = response.data.freelances || [];
    
    if (missionFreelances.value.length > 0) {
      selectedFreelanceId.value = missionFreelances.value[0].id;
    }
  } catch (error) {
    console.error('Erreur chargement freelances mission:', error);
    missionFreelances.value = [];
  }
}

async function createNewChat() {
  try {
    let response;
    
    switch (newChatType.value) {
      case 'mission':
        response = await axios.post('/api/chats/mission/create', {
          mission_id: selectedMissionId.value,
          freelance_id: selectedFreelanceId.value
        });
        break;
        
      case 'user':
        response = await axios.post('/api/chats/direct', {
          user_id: selectedUserId.value
        });
        break;
        
      case 'support':
        response = await axios.post('/api/chats/support', {
          message: supportMessage.value
        });
        break;
    }
    
    if (response.data.chat) {
      await refreshChats();
      const newChat = chats.value.find(c => c.id === response.data.chat.id);
      if (newChat) {
        await selectChat(newChat);
      }
      
      showNewChatModal.value = false;
      resetNewChatForm();
    }
    
  } catch (error) {
    console.error('Erreur création chat:', error);
  }
}

function resetNewChatForm() {
  newChatType.value = 'mission';
  selectedMissionId.value = null;
  selectedFreelanceId.value = null;
  userSearchInput.value = '';
  selectedUserId.value = null;
  selectedUser.value = null;
  supportMessage.value = '';
  userSearchResults.value = [];
  missionFreelances.value = [];
  selectedUserMissions.value = [];
}

async function selectChat(chat) {
  activeChat.value = chat;
  loadingMessages.value = true;
  
  try {
    await chatStore.fetchChatMessages(chat.id);
    
    if (chat.unread_count > 0) {
      await chatStore.markChatAsRead(chat.id);
    }
    
    showMissionSuggestions.value = chat.chat_type === 'mission';
    
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
    await chatStore.fetchChatMessages(activeChat.value.id);
    nextTick(scrollToBottom);
  } catch (error) {
    console.error('Erreur envoi message:', error);
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

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
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

async function openSupportChat() {
  try {
    await chatStore.openSupportChat();
    await refreshChats();
  } catch (error) {
    console.error('Erreur ouverture support:', error);
  }
}

function backToChatList() {
  activeChat.value = null;
  chatStore.messages = [];
  showMissionSuggestions.value = false;
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

function toggleFileUpload() {
  console.log('Upload fichier');
}

function goToMission() {
  if (activeChat.value?.mission) {
    router.push(`/missions/${activeChat.value.mission.id}`);
  }
}

// Lifecycle
onMounted(async () => {
  await initializeChatSystem();
  
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth < 768;
  });
});

onUnmounted(() => {
  window.removeEventListener('resize', () => {
    isMobile.value = window.innerWidth < 768;
  });
});

async function initializeChatSystem() {
  loading.value = true;
  try {
    await chatStore.fetchMyChats();
    
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
}
// --- UTILS VISUELS POUR LES AVATARS ---

/**
 * Génère les initiales pour l'avatar (ex: "Jean Dupont" -> "JD")
 */
const getAvatarInitials = (chat) => {
  if (!chat) return '?'
  if (chat.chat_type === 'support') return 'S'
  
  const name = getChatTitle(chat)
  if (!name) return '?'
  
  return name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
    .substring(0, 2)
}

</script>

<style scoped>
.chat-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f9fafb;
  overflow: hidden;
}

/* Header */
.chat-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  color: #111827;
}

.user-type-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.global-search {
  position: relative;
  min-width: 250px;
}

.global-search input {
  width: 100%;
  padding: 0.5rem 1rem;
  padding-right: 2.5rem;
  border: 1px solid #d1d5db;
  border-radius: 1.5rem;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s;
  background: #f3f4f6;
}

.global-search input:focus {
  background: white;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.user-search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  margin-top: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.user-result {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid #f3f4f6;
}

.user-result:hover {
  background: #f9fafb;
}

.user-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-info strong {
  display: block;
  font-size: 0.875rem;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 0.75rem;
  color: #6b7280;
}

.start-chat-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.start-chat-btn:hover {
  opacity: 0.9;
}

.refresh-btn,
.create-chat-btn,
.support-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s;
  white-space: nowrap;
}

.refresh-btn {
  background: #f3f4f6;
  color: #374151;
}

.refresh-btn:hover {
  background: #e5e7eb;
}

.create-chat-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
}

.create-chat-btn:hover {
  opacity: 0.9;
}

.support-btn {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
}

.support-btn:hover {
  opacity: 0.9;
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
  stroke-width: 2;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 1rem;
  width: 100%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
}

.close-btn:hover {
  background: #f3f4f6;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 1rem;
}

.tabs button {
  flex: 1;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.875rem;
  color: #6b7280;
  transition: all 0.2s;
}

.tabs button.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.tabs button:hover:not(.active) {
  background: #f3f4f6;
}

.mission-section select,
.user-section input,
.support-section textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  background: white;
  outline: none;
  transition: border-color 0.2s;
}

.mission-section select:focus,
.user-section input:focus,
.support-section textarea:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.freelance-list,
.search-results {
  margin-top: 1rem;
}

.freelance-item,
.user-result-item {
  padding: 0.75rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
}

.freelance-item:hover,
.user-result-item:hover {
  border-color: #667eea;
  background: #f0f5ff;
}

.freelance-item.selected,
.user-result-item.selected {
  border-color: #667eea;
  background: #e0e7ff;
}

.freelance-avatar,
.user-avatar-small {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.freelance-info,
.user-details {
  flex: 1;
  min-width: 0;
}

.freelance-info strong,
.user-name {
  display: block;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.freelance-rating {
  color: #f59e0b;
  font-weight: 600;
  font-size: 0.875rem;
}

.user-role-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.user-role-badge.client {
  background: #dbeafe;
  color: #1e40af;
}

.user-role-badge.freelance {
  background: #f3e8ff;
  color: #7c3aed;
}

.modal-footer {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.cancel-btn,
.confirm-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.cancel-btn {
  background: white;
  border: 1px solid #d1d5db;
  color: #374151;
}

.cancel-btn:hover {
  background: #f9fafb;
}

.confirm-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Main container */
.chat-container {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

/* Sidebar */
.chat-sidebar {
  width: 350px;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform 0.3s ease;
}

@media (max-width: 768px) {
  .chat-sidebar.mobile-hidden {
    transform: translateX(-100%);
  }
  
  .chat-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 100%;
    max-width: 350px;
    z-index: 100;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
  }
}

.sidebar-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.sidebar-header h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
  color: #111827;
}

.sidebar-info {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.unread-indicator {
  background: #ef4444;
  color: white;
  padding: 0.25rem 0.625rem;
  border-radius: 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.chat-count {
  font-size: 0.75rem;
  color: #6b7280;
}

.chat-filters {
  display: flex;
  padding: 1rem 1.5rem;
  gap: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
  flex-wrap: wrap;
}

.chat-filters button {
  flex: 1;
  min-width: 80px;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.75rem;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  transition: all 0.2s;
}

.chat-filters button:hover {
  border-color: #9ca3af;
}

.chat-filters button.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: white;
}

.filter-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.125rem 0.375rem;
  border-radius: 0.75rem;
  font-size: 0.625rem;
  font-weight: 600;
}

.local-search {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.search-input {
  width: 100%;
  padding: 0.625rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.chats-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.5rem;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #6b7280;
  padding: 3rem 1rem;
}

.spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
  color: #111827;
}

.empty-state p {
  margin: 0 0 1.5rem 0;
  font-size: 0.875rem;
  color: #6b7280;
  max-width: 300px;
}

.start-conversation-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.start-conversation-btn:hover {
  opacity: 0.9;
}

.chat-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.chat-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
  position: relative;
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

.chat-item-avatar {
  position: relative;
  flex-shrink: 0;
}

.avatar {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.online-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  border: 2px solid white;
  background: #10b981;
}

.online-status.offline {
  background: #9ca3af;
}

.chat-item-content {
  flex: 1;
  min-width: 0;
}

.chat-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.25rem;
}

.chat-item-title {
  font-weight: 600;
  color: #111827;
  margin: 0;
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-item-time {
  font-size: 0.75rem;
  color: #6b7280;
  white-space: nowrap;
  margin-left: 0.5rem;
}

.chat-item-preview {
  font-size: 0.8125rem;
  color: #6b7280;
  margin: 0 0 0.5rem 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-item-meta {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.chat-type {
  font-size: 0.6875rem;
  padding: 0.125rem 0.5rem;
  border-radius: 0.75rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  white-space: nowrap;
}

.chat-type.mission {
  background: #e0e7ff;
  color: #4f46e5;
}

.chat-type.support {
  background: #dcfce7;
  color: #059669;
}

.chat-type.user {
  background: #f3e8ff;
  color: #7c3aed;
}

.mission-title {
  font-size: 0.75rem;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
}

.chat-item-badge {
  background: #ef4444;
  color: white;
  border-radius: 50%;
  min-width: 1.375rem;
  height: 1.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
}

/* Chat main */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: white;
}

@media (max-width: 768px) {
  .chat-main.mobile-full {
    width: 100%;
  }
}

.no-chat-selected {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.welcome-card {
  background: white;
  border-radius: 1rem;
  padding: 2.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  margin-bottom: 2rem;
}

.welcome-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
}

.welcome-card h2 {
  font-size: 1.5rem;
  color: #111827;
  margin: 0 0 0.75rem 0;
}

.welcome-card p {
  color: #6b7280;
  margin: 0 0 1.5rem 0;
  font-size: 1rem;
  line-height: 1.5;
}

.welcome-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  flex-wrap: wrap;
}

.primary-btn,
.secondary-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  font-size: 0.875rem;
}

.primary-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.primary-btn:hover {
  opacity: 0.9;
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
  gap: 1rem;
  margin-top: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.stat-card {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  text-align: center;
  min-width: 120px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}

/* Active chat */
.active-chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.active-chat-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background: white;
  flex-shrink: 0;
}

.back-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.375rem;
  display: none;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  transition: background 0.2s;
}

@media (max-width: 768px) {
  .back-btn {
    display: flex;
  }
}

.back-btn:hover {
  background: #f3f4f6;
}

.chat-info {
  flex: 1;
  min-width: 0;
}

.chat-title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
}

.avatar-container {
  position: relative;
  flex-shrink: 0;
}

.chat-info-details {
  flex: 1;
  min-width: 0;
}

.chat-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-subtitle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  font-size: 0.875rem;
  color: #6b7280;
}

.chat-type-label {
  padding: 0.125rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
}

.chat-type-label.mission {
  background: #e0e7ff;
  color: #4f46e5;
}

.chat-type-label.support {
  background: #dcfce7;
  color: #059669;
}

.chat-type-label.direct {
  background: #f3e8ff;
  color: #7c3aed;
}

.separator {
  color: #d1d5db;
}

.mission-name {
  font-weight: 500;
  color: #111827;
}

.participant-details {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.chat-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.375rem;
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

/* Messages container */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
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
  color: #6b7280;
  gap: 1rem;
}

.no-messages {
  text-align: center;
  color: #6b7280;
  padding: 3rem 1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-chat-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.no-messages h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
  color: #111827;
}

.no-messages p {
  margin: 0 0 1.5rem 0;
  font-size: 0.875rem;
  max-width: 400px;
}

.initial-suggestions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.suggestion-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 1rem;
  font-size: 0.875rem;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.suggestion-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

/* Messages list */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.date-separator {
  text-align: center;
  margin: 0.75rem 0;
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
  padding: 0.375rem 1rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  color: #6b7280;
  position: relative;
  z-index: 1;
  border: 1px solid #e5e7eb;
}

.message {
  display: flex;
  max-width: 80%;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
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
  flex-direction: row-reverse;
}

.message.received {
  align-self: flex-start;
}

.message-avatar {
  flex-shrink: 0;
  margin-right: 0.75rem;
  margin-top: 0.25rem;
}

.message.sent .message-avatar {
  margin-right: 0;
  margin-left: 0.75rem;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-sender {
  font-size: 0.75rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.25rem;
  padding-left: 0.5rem;
}

.message.sent .message-sender {
  text-align: right;
  padding-left: 0;
  padding-right: 0.5rem;
}

.message-bubble {
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  position: relative;
  max-width: 100%;
  word-wrap: break-word;
}

.message.received .message-bubble {
  background: white;
  color: #111827;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 0.25rem;
}

.message.sent .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 0.25rem;
}

.message-text {
  font-size: 0.9375rem;
  line-height: 1.5;
  margin-bottom: 0.25rem;
}

.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  opacity: 0.8;
}

.message-time {
  font-size: 0.6875rem;
}

.read-indicator {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.6875rem;
  margin-left: 0.5rem;
}

/* Message input area */
.message-input-area {
  border-top: 1px solid #e5e7eb;
  background: white;
  padding: 1rem 1.5rem;
  flex-shrink: 0;
}

.message-actions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.mission-suggestions {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 0.75rem;
  overflow-x: auto;
}

.message-form {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.message-form input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 1.5rem;
  font-size: 0.9375rem;
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
  width: 2.5rem;
  height: 2.5rem;
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
  opacity: 0.9;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sending-indicator {
  font-size: 0.75rem;
  color: #6b7280;
  text-align: center;
  margin-top: 0.5rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Responsive */
@media (max-width: 1024px) {
  .chat-sidebar {
    width: 320px;
  }
}

@media (max-width: 768px) {
  .chat-header {
    padding: 0.75rem 1rem;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .global-search {
    order: 1;
    width: 100%;
    margin-bottom: 0.5rem;
  }
  
  .refresh-btn,
  .create-chat-btn,
  .support-btn {
    flex: 1;
    justify-content: center;
  }
  
  .modal-content {
    margin: 0;
    border-radius: 0;
    max-height: 100vh;
    height: 100vh;
  }
  
  .chat-stats {
    flex-direction: column;
    align-items: center;
  }
  
  .stat-card {
    width: 100%;
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  .tabs {
    flex-direction: column;
  }
  
  .tabs button {
    width: 100%;
  }
  
  .chat-filters {
    overflow-x: auto;
    padding: 0.75rem 1rem;
    flex-wrap: nowrap;
  }
  
  .chat-filters button {
    min-width: 100px;
  }
  
  .welcome-card {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .welcome-actions {
    flex-direction: column;
  }
  
  .welcome-actions button {
    width: 100%;
    justify-content: center;
  }
}
</style>