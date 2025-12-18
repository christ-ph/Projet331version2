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
  }),

  getters: {
    // ✅ Getter pour vérifier si l'utilisateur a des notifications
    hasUnreadMessages: (state) => state.unreadCount > 0,
    
    // ✅ Getter pour les chats avec notifications
    chatsWithNotifications: (state) => 
      state.chats.filter(chat => chat.unread_count > 0),
    
    // ✅ Getter pour les chats de mission uniquement
    missionChats: (state) => 
      state.chats.filter(chat => chat.chat_type === 'mission'),
    
    // ✅ Getter pour le chat de support (doit en avoir max 1)
    supportChat: (state) => 
      state.chats.find(chat => chat.chat_type === 'support'),
  },

  actions: {
    // ✅ Récupérer tous les chats de l'utilisateur
    async fetchMyChats() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get('/my-chats');
        this.chats = response.data.chats;
        this.calculateUnreadCount();
        return this.chats;
      } catch (error) {
        console.error('Erreur lors de la récupération des chats:', error);
        this.error = 'Impossible de charger les conversations.';
        throw error;
      } finally {
        this.loading = false;
      }
    },
      openChatModal(chatType = null) {
    this.isChatModalOpen = true;
    this.activeChatType = chatType;
  },
  
  closeChatModal() {
    this.isChatModalOpen = false;
    this.activeChatType = null;
  },

    // ✅ Récupérer ou créer un chat de mission
    async getOrCreateMissionChat(missionId) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`/mission/${missionId}`);
        
        // Mettre à jour la liste des chats si nécessaire
        const existingIndex = this.chats.findIndex(c => c.id === response.data.chat.id);
        if (existingIndex === -1) {
          this.chats.push(response.data.chat);
        } else {
          this.chats[existingIndex] = response.data.chat;
        }
        
        this.calculateUnreadCount();
        return response.data.chat;
      } catch (error) {
        console.error('Erreur lors de la récupération du chat de mission:', error);
        this.error = 'Impossible d\'accéder à la conversation.';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // ✅ Récupérer les messages d'un chat
    async fetchChatMessages(chatId) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`/${chatId}/messages`);
        
        // Mettre à jour les messages
        this.messages = response.data.messages;
        
        // Mettre à jour le chat actif
        this.activeChat = response.data.chat;
        
        // Mettre à jour le chat dans la liste
        const chatIndex = this.chats.findIndex(c => c.id === chatId);
        if (chatIndex !== -1) {
          this.chats[chatIndex] = response.data.chat;
        }
        
        // Recalculer les notifications
        this.calculateUnreadCount();
        
        return this.messages;
      } catch (error) {
        console.error('Erreur lors de la récupération des messages:', error);
        this.error = 'Impossible de charger les messages.';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // ✅ Envoyer un message
    async sendMessage(chatId, content) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.post(`/${chatId}/messages`, {
          content: content.trim()
        });
        
        // Ajouter le message localement (optimistic update)
        const newMessage = {
          ...response.data.data,
          sender: { 
            id: useAuthStore().user?.id,
            email: useAuthStore().user?.email,
            role: useAuthStore().user?.role
          }
        };
        
        this.messages.push(newMessage);
        
        // Mettre à jour la date du chat dans la liste
        const chatIndex = this.chats.findIndex(c => c.id === chatId);
        if (chatIndex !== -1) {
          this.chats[chatIndex].updated_at = new Date().toISOString();
        }
        
        return response.data.data;
      } catch (error) {
        console.error('Erreur lors de l\'envoi du message:', error);
        this.error = 'Impossible d\'envoyer le message.';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // ✅ Vérifier les nouvelles notifications (POLLING)
    async checkForNewMessages() {
      try {
        const response = await axios.get('/check-status');
        this.lastChecked = new Date().toISOString();
        
        // Mettre à jour les compteurs
        this.unreadCount = response.data.total_unread;
        
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
        console.error('Erreur lors de la vérification des notifications:', error);
        // Ne pas bloquer l'application en cas d'erreur
        return { has_new_messages: false, total_unread: 0, notifications: [] };
      }
    },

    // ✅ Marquer un chat comme lu
    async markChatAsRead(chatId) {
      try {
        await axios.post(`/${chatId}/read`);
        
        // Mettre à jour localement
        const chatIndex = this.chats.findIndex(c => c.id === chatId);
        if (chatIndex !== -1) {
          this.chats[chatIndex].unread_count = 0;
        }
        
        // Mettre à jour le compteur global
        this.calculateUnreadCount();
        
        return true;
      } catch (error) {
        console.error('Erreur lors du marquage comme lu:', error);
        throw error;
      }
    },

    // ✅ Gérer le chat de support
    async manageSupportChat(action = 'get', initialMessage = null) {
      this.loading = true;
      this.error = null;
      
      try {
        if (action === 'create') {
          const response = await axios.post('/support', {
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
          const response = await axios.get('/support');
          
          // Mettre à jour le chat de support
          if (response.data.chat) {
            const existingIndex = this.chats.findIndex(c => 
              c.chat_type === 'support'
            );
            
            if (existingIndex === -1) {
              this.chats.push(response.data.chat);
            } else {
              this.chats[existingIndex] = response.data.chat;
            }
          }
          
          this.calculateUnreadCount();
          return response.data;
        }
      } catch (error) {
        console.error('Erreur lors de la gestion du chat support:', error);
        this.error = 'Impossible d\'accéder au support.';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // ✅ Supprimer un message
    async deleteMessage(messageId) {
      try {
        await axios.delete(`/messages/${messageId}`);
        
        // Retirer le message localement
        this.messages = this.messages.filter(msg => msg.id !== messageId);
        
        return true;
      } catch (error) {
        console.error('Erreur lors de la suppression du message:', error);
        throw error;
      }
    },

    // ✅ Calculer le nombre total de messages non lus
    calculateUnreadCount() {
      this.unreadCount = this.chats.reduce((total, chat) => {
        return total + (chat.unread_count || 0);
      }, 0);
    },

    // ✅ Définir le chat actif
    setActiveChat(chat) {
      this.activeChat = chat;
      if (chat) {
        // Charger les messages si nécessaire
        if (this.activeChat.id !== chat.id) {
          this.messages = [];
          this.fetchChatMessages(chat.id);
        }
      } else {
        this.messages = [];
      }
    },

    // ✅ Réinitialiser l'état
    reset() {
      this.chats = [];
      this.activeChat = null;
      this.messages = [];
      this.unreadCount = 0;
      this.lastChecked = null;
      this.loading = false;
      this.error = null;
    },
  },
});