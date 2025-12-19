import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

export const useChatStore = defineStore('chat', {
  state: () => ({
    // Chats et messages
    chats: [],               // Liste des chats de l'utilisateur
    activeChat: null,        // Chat actuellement ouvert
    messages: [],            // Messages du chat actif
    
    // État général
    loading: false,
    error: null,
    
    // Notifications
    unreadCount: 0,          // Nombre total de messages non lus
    lastChecked: null,       // Date de la dernière vérification
    
    // Modal
    isChatModalOpen: false,  // État d'ouverture du modal
    activeChatType: null,    // Type de chat actif
    
    // Polling
    pollingInterval: null,   // Référence à l'intervalle de polling
    pollingActive: false,    // État du polling
  }),

  getters: {
    // Getter pour vérifier si l'utilisateur a des notifications
    hasUnreadMessages: (state) => state.unreadCount > 0,
    
    // Getter pour les chats avec notifications
    chatsWithNotifications: (state) => 
      state.chats.filter(chat => chat.unread_count > 0),
    
    // Getter pour les chats de mission uniquement
    missionChats: (state) => 
      state.chats.filter(chat => chat.chat_type === 'mission'),
    
    // Getter pour le chat de support (doit en avoir max 1)
    supportChat: (state) => 
      state.chats.find(chat => chat.chat_type === 'support'),
    
    // Getter pour les chats triés par date de mise à jour
    sortedChats: (state) => 
      [...state.chats].sort((a, b) => 
        new Date(b.updated_at) - new Date(a.updated_at)
      ),
    
    // Getter pour les infos de l'autre participant dans le chat actif
    otherParticipant: (state) => {
      if (!state.activeChat || !state.activeChat.other_participant) return null;
      return state.activeChat.other_participant;
    },
    
    // Getter pour vérifier si l'utilisateur actuel est le client
    isCurrentUserClient: () => {
      const authStore = useAuthStore();
      return authStore.user?.role === 'CLIENT';
    },
    
    // Getter pour vérifier si l'utilisateur actuel est le freelance
    isCurrentUserFreelance: () => {
      const authStore = useAuthStore();
      return authStore.user?.role === 'FREELANCE';
    },
    
    // Getter pour le nom affichable du chat
    chatDisplayName: (state) => (chat) => {
      if (chat.chat_type === 'mission') {
        return chat.mission?.title || 'Chat Mission';
      } else if (chat.chat_type === 'support') {
        return 'Support';
      } else if (chat.other_participant) {
        return chat.other_participant.name || chat.other_participant.email;
      }
      return 'Chat';
    },
  },

  actions: {
    // ============================================
    // INITIALISATION ET RÉCUPÉRATION DES CHATS
    // ============================================

    /**
     * ✅ Initialiser le système de chat
     */
    async initialize() {
      try {
        // Charger les chats de l'utilisateur
        await this.fetchMyChats();
        
        // Démarrer le polling pour les notifications
        this.startPolling();
        
        console.log('✅ Système de chat initialisé');
      } catch (error) {
        console.error('❌ Erreur initialisation chat:', error);
      }
    },

    /**
     * ✅ Récupérer tous les chats de l'utilisateur
     */
    async fetchMyChats() {
      this.loading = true;
      this.error = null;
      
      try {
        console.log('📥 fetchMyChats appelé');
        const response = await axios.get('/api/chats/my-chats');
        this.chats = response.data.chats || [];
        this.calculateUnreadCount();
        console.log(`✅ ${this.chats.length} chats chargés`);
        return this.chats;
      } catch (error) {
        console.error('❌ Erreur lors de la récupération des chats:', error);
        this.error = error.response?.data?.error || 'Impossible de charger les conversations.';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * ✅ Récupérer un chat spécifique
     */
    async getChat(chatId) {
      try {
        console.log(`📥 getChat appelé pour chat: ${chatId}`);
        const response = await axios.get(`/api/chats/${chatId}`);
        return response.data.chat;
      } catch (error) {
        console.error(`❌ Erreur récupération chat ${chatId}:`, error);
        throw error;
      }
    },

    // ============================================
    // GESTION DU MODAL
    // ============================================

    /**
     * ✅ Ouvrir le modal de chat
     */
    openChatModal(chatType = null, initialData = null) {
      this.isChatModalOpen = true;
      this.activeChatType = chatType;
      
      if (initialData) {
        // Si on a des données initiales, créer le chat immédiatement
        if (initialData.type === 'mission') {
          this.openOrCreateMissionChat(initialData.missionId);
        }
      }
    },
    
    /**
     * ✅ Fermer le modal de chat
     */
    closeChatModal() {
      this.isChatModalOpen = false;
      this.activeChatType = null;
    },

    // ============================================
    // CHATS DE MISSION
    // ============================================

    /**
     * ✅ Récupérer ou créer un chat de mission
     */
    async getOrCreateMissionChat(missionId) {
      console.log('🔄 getOrCreateMissionChat appelé pour mission:', missionId);
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`/api/chats/mission/${missionId}`);
        
        console.log('✅ Chat récupéré/créé:', response.data.chat);
        
        const chat = response.data.chat;
        
        // Mettre à jour la liste des chats
        this.updateChatInList(chat);
        
        // Définir comme chat actif
        this.activeChat = chat;
        this.calculateUnreadCount();
        
        return chat;
        
      } catch (error) {
        console.error('❌ Erreur lors de la récupération/création du chat de mission:', error);
        
        // Messages d'erreur spécifiques
        if (error.response?.status === 403) {
          this.error = 'Accès refusé. Votre candidature doit être acceptée pour pouvoir chatter.';
        } else if (error.response?.status === 404) {
          this.error = 'Mission non trouvée.';
        } else {
          this.error = error.response?.data?.error || 'Impossible d\'accéder à la conversation.';
        }
        
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * ✅ Ouvrir ou créer un chat de mission (méthode simplifiée)
     */
    async openOrCreateMissionChat(missionId) {
      try {
        console.log('🚀 openOrCreateMissionChat pour mission:', missionId);
        
        // Vérifier les permissions d'abord
        const permission = await this.checkMissionChatPermission(missionId);
        if (!permission.can_chat) {
          throw new Error(permission.reason);
        }
        
        // Si un chat existe déjà, l'utiliser
        if (permission.chat) {
          this.setActiveChat(permission.chat);
          return permission.chat;
        }
        
        // Sinon créer un nouveau chat
        return await this.getOrCreateMissionChat(missionId);
        
      } catch (error) {
        console.error('❌ Erreur openOrCreateMissionChat:', error);
        throw error;
      }
    },

    /**
     * ✅ Vérifier la permission pour chatter sur une mission
     */
    async checkMissionChatPermission(missionId) {
      try {
        const response = await axios.get(`/api/chats/mission/${missionId}`);
        return { 
          can_chat: true, 
          chat: response.data.chat,
          reason: 'Accès autorisé' 
        };
      } catch (error) {
        return { 
          can_chat: false, 
          reason: error.response?.data?.error || 'Permission refusée' 
        };
      }
    },

    /**
     * ✅ Assigner un freelance à un chat de mission
     */
    async assignFreelanceToMissionChat(missionId, freelanceId) {
      try {
        console.log(`🔄 Assignation freelance ${freelanceId} à mission ${missionId}`);
        
        const response = await axios.post(`/api/chats/mission/${missionId}/assign-freelance`, {
          freelance_id: freelanceId
        });
        
        // Mettre à jour le chat dans la liste
        if (response.data.chat) {
          this.updateChatInList(response.data.chat);
        }
        
        console.log('✅ Freelance assigné avec succès');
        return response.data;
        
      } catch (error) {
        console.error('❌ Erreur assignation freelance:', error);
        throw error;
      }
    },

    // ============================================
    // MESSAGES
    // ============================================

    /**
     * ✅ Récupérer les messages d'un chat
     */
    async fetchChatMessages(chatId) {
      this.loading = true;
      this.error = null;
      
      try {
        console.log(`📥 fetchChatMessages pour chat: ${chatId}`);
        
        const response = await axios.get(`/api/chats/${chatId}/messages`);
        
        // Mettre à jour les messages
        this.messages = response.data.messages || [];
        
        // Mettre à jour le chat actif avec les infos du serveur
        if (response.data.chat) {
          this.activeChat = response.data.chat;
          this.updateChatInList(response.data.chat);
        }
        
        // Recalculer les notifications
        this.calculateUnreadCount();
        
        console.log(`✅ ${this.messages.length} messages chargés`);
        return this.messages;
        
      } catch (error) {
        console.error('❌ Erreur lors de la récupération des messages:', error);
        this.error = error.response?.data?.error || 'Impossible de charger les messages.';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * ✅ Envoyer un message
     */
    async sendMessage(chatId, content, file = null) {
      this.loading = true;
      this.error = null;
      
      try {
        console.log(`📤 Envoi message dans chat ${chatId}:`, content.substring(0, 50) + '...');
        
        const payload = {
          content: content.trim()
        };
        
        if (file) {
          // Gérer l'upload de fichier si nécessaire
          payload.file_name = file.name;
          // payload.file_url = ... (à gérer séparément)
        }
        
        const response = await axios.post(`/api/chats/${chatId}/messages`, payload);
        
        // Ajouter le message localement
        const newMessage = {
          ...response.data.data,
          sender: { 
            id: useAuthStore().user?.id,
            email: useAuthStore().user?.email,
            role: useAuthStore().user?.role
          }
        };
        
        this.messages.push(newMessage);
        
        // Mettre à jour la date du chat
        this.updateChatTimestamp(chatId);
        
        console.log('✅ Message envoyé avec succès');
        return newMessage;
        
      } catch (error) {
        console.error('❌ Erreur lors de l\'envoi du message:', error);
        this.error = error.response?.data?.error || 'Impossible d\'envoyer le message.';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * ✅ Supprimer un message
     */
    async deleteMessage(messageId) {
      try {
        console.log(`🗑️ Suppression message: ${messageId}`);
        
        await axios.delete(`/api/chats/messages/${messageId}`);
        
        // Retirer le message localement
        this.messages = this.messages.filter(msg => msg.id !== messageId);
        
        console.log('✅ Message supprimé avec succès');
        return true;
        
      } catch (error) {
        console.error('❌ Erreur lors de la suppression du message:', error);
        throw error;
      }
    },

    // ============================================
    // CHAT DE SUPPORT
    // ============================================

    /**
     * ✅ Gérer le chat de support
     */
    async manageSupportChat(action = 'get', initialMessage = null) {
      this.loading = true;
      this.error = null;
      
      try {
        console.log(`🔄 manageSupportChat: ${action}`);
        
        if (action === 'create') {
          const response = await axios.post('/api/chats/support', {
            subject: 'Support',
            initial_message: initialMessage
          });
          
          // Ajouter le nouveau chat
          if (response.data.chat) {
            this.chats.push(response.data.chat);
            this.calculateUnreadCount();
          }
          
          return response.data;
          
        } else {
          // GET - récupérer le chat existant
          const response = await axios.get('/api/chats/support');
          
          // Mettre à jour le chat de support
          if (response.data.chat) {
            this.updateChatInList(response.data.chat);
          }
          
          this.calculateUnreadCount();
          return response.data;
        }
        
      } catch (error) {
        console.error('❌ Erreur lors de la gestion du chat support:', error);
        this.error = error.response?.data?.error || 'Impossible d\'accéder au support.';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * ✅ Ouvrir le chat de support
     */
    async openSupportChat() {
      try {
        console.log('🔄 Ouverture chat support');
        
        // Récupérer ou créer le chat de support
        const result = await this.manageSupportChat('get');
        
        if (result.chat) {
          this.setActiveChat(result.chat);
          return result.chat;
        } else {
          // Ouvrir le modal pour créer un nouveau chat support
          this.openChatModal('support');
          return null;
        }
        
      } catch (error) {
        console.error('❌ Erreur ouverture chat support:', error);
        throw error;
      }
    },

    // ============================================
    // NOTIFICATIONS ET POLLING
    // ============================================

    /**
     * ✅ Vérifier les nouvelles notifications (polling)
     */
    async checkForNewMessages() {
      try {
        console.log('🔄 checkForNewMessages');
        
        const response = await axios.get('/api/chats/check-status');
        this.lastChecked = new Date().toISOString();
        
        // Mettre à jour les compteurs
        this.unreadCount = response.data.total_unread || 0;
        
        // Mettre à jour les notifications par chat
        if (response.data.notifications && response.data.notifications.length > 0) {
          response.data.notifications.forEach(notification => {
            const chatIndex = this.chats.findIndex(c => c.id === notification.chat_id);
            if (chatIndex !== -1) {
              this.chats[chatIndex].unread_count = notification.notification_count;
            }
          });
        }
        
        return response.data;
        
      } catch (error) {
        console.error('❌ Erreur lors de la vérification des notifications:', error);
        // Ne pas bloquer l'application en cas d'erreur
        return { has_new_messages: false, total_unread: 0, notifications: [] };
      }
    },

    /**
     * ✅ Démarrer le polling pour les notifications
     */
    startPolling(interval = 30000) { // 30 secondes par défaut
      if (this.pollingActive) {
        console.log('⚠️ Polling déjà actif');
        return;
      }
      
      console.log('🚀 Démarrage polling notifications...');
      this.pollingActive = true;
      
      // Première vérification immédiate
      this.checkForNewMessages();
      
      // Configurer l'intervalle
      this.pollingInterval = setInterval(() => {
        this.checkForNewMessages();
      }, interval);
    },

    /**
     * ✅ Arrêter le polling
     */
    stopPolling() {
      if (this.pollingInterval) {
        console.log('🛑 Arrêt polling notifications');
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
        this.pollingActive = false;
      }
    },

    // ============================================
    // GESTION DE LA LECTURE
    // ============================================

    /**
     * ✅ Marquer un chat comme lu
     */
    async markChatAsRead(chatId) {
      try {
        console.log(`👁️ Marquer chat ${chatId} comme lu`);
        
        await axios.post(`/api/chats/${chatId}/read`);
        
        // Mettre à jour localement
        const chatIndex = this.chats.findIndex(c => c.id === chatId);
        if (chatIndex !== -1) {
          this.chats[chatIndex].unread_count = 0;
        }
        
        // Mettre à jour le chat actif
        if (this.activeChat?.id === chatId) {
          this.activeChat.unread_count = 0;
        }
        
        // Mettre à jour le compteur global
        this.calculateUnreadCount();
        
        console.log('✅ Chat marqué comme lu');
        return true;
        
      } catch (error) {
        console.error('❌ Erreur lors du marquage comme lu:', error);
        throw error;
      }
    },

    /**
     * ✅ Définir le chat actif
     */
    async setActiveChat(chat) {
      console.log(`🎯 setActiveChat: ${chat?.id} - ${chat?.chat_type}`);
      
      this.activeChat = chat;
      
      if (chat) {
        // Si c'est un nouveau chat, charger les messages
        if (!this.activeChat || this.activeChat.id !== chat.id) {
          this.messages = [];
          await this.fetchChatMessages(chat.id);
        }
        
        // Marquer le chat comme lu
        await this.markChatAsRead(chat.id);
        
        // Ouvrir le modal si fermé
        if (!this.isChatModalOpen) {
          this.isChatModalOpen = true;
        }
      } else {
        this.messages = [];
      }
    },

    // ============================================
    // UTILITAIRES
    // ============================================

    /**
     * ✅ Mettre à jour un chat dans la liste
     */
    updateChatInList(chat) {
      const index = this.chats.findIndex(c => c.id === chat.id);
      
      if (index === -1) {
        this.chats.push(chat);
      } else {
        this.chats[index] = chat;
      }
      
      // Trier par date de mise à jour
      this.chats.sort((a, b) => 
        new Date(b.updated_at) - new Date(a.updated_at)
      );
    },

    /**
     * ✅ Mettre à jour le timestamp d'un chat
     */
    updateChatTimestamp(chatId) {
      const now = new Date().toISOString();
      
      // Mettre à jour dans la liste
      const chatIndex = this.chats.findIndex(c => c.id === chatId);
      if (chatIndex !== -1) {
        this.chats[chatIndex].updated_at = now;
      }
      
      // Mettre à jour le chat actif
      if (this.activeChat?.id === chatId) {
        this.activeChat.updated_at = now;
      }
      
      // Retrier
      this.chats.sort((a, b) => 
        new Date(b.updated_at) - new Date(a.updated_at)
      );
    },

    /**
     * ✅ Calculer le nombre total de messages non lus
     */
    calculateUnreadCount() {
      this.unreadCount = this.chats.reduce((total, chat) => {
        return total + (chat.unread_count || 0);
      }, 0);
      
      console.log(`📊 Unread count: ${this.unreadCount}`);
    },

    /**
     * ✅ Récupérer le chat d'une mission spécifique
     */
    getMissionChat(missionId) {
      return this.chats.find(chat => 
        chat.mission_id === missionId && chat.chat_type === 'mission'
      );
    },

    /**
     * ✅ Vérifier si un chat existe pour une mission
     */
    hasMissionChat(missionId) {
      return !!this.getMissionChat(missionId);
    },
    hasUnreadMissionMessages: (state) => (missionId) => {
        if (!missionId) return false;
        const chat = state.chats.find(
            c => Number(c.mission_id) === Number(missionId) && c.chat_type === 'mission'
        );
        return chat ? (chat.unread_count > 0) : false;
        },
        
        // ===========================================
    // RÉINITIALISATION
    // ============================================

    /**
     * ✅ Réinitialiser l'état
     */
    reset() {
      console.log('🔄 Réinitialisation store chat');
      
      // Arrêter le polling
      this.stopPolling();
      
      // Réinitialiser l'état
      this.chats = [];
      this.activeChat = null;
      this.messages = [];
      this.unreadCount = 0;
      this.lastChecked = null;
      this.loading = false;
      this.error = null;
      this.isChatModalOpen = false;
      this.activeChatType = null;
      this.pollingActive = false;
    },

    /**
     * ✅ Nettoyer à la déconnexion
     */
    cleanup() {
      this.stopPolling();
      this.reset();
      console.log('🧹 Nettoyage store chat');
    },
  },

  // Persistance
  persist: {
    paths: ['chats', 'activeChat', 'unreadCount', 'lastChecked'],
  },
});

// Export nommé pour compatibilité
export default useChatStore;