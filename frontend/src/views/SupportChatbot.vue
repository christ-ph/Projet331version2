<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useChatbotStore } from '@/stores/chatbot'
import { useAuthStore } from '@/stores/auth'

const chatbotStore = useChatbotStore()
const authStore = useAuthStore()
const router = useRouter()

const userInput = ref('')
const chatContainer = ref(null)
const showScrollButton = ref(false)

// Initialisation
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  // Charger la conversation ou initialiser
  chatbotStore.loadConversation()
  
  // Scroll vers le bas après le chargement
  await nextTick()
  scrollToBottom()
})

// Watcher pour auto-scroll sur nouveaux messages
watch(() => chatbotStore.messages.length, async () => {
  await nextTick()
  scrollToBottom()
})

// Auto-save toutes les 30 secondes
setInterval(() => {
  if (chatbotStore.messages.length > 0) {
    chatbotStore.saveConversation()
  }
}, 30000)

// Envoyer un message
const sendMessage = async () => {
  if (!userInput.value.trim() || chatbotStore.isLoading) return
  
  const message = userInput.value
  userInput.value = ''
  
  await chatbotStore.sendMessage(message)
  chatbotStore.saveConversation()
}

// Suggestions rapides
const quickSuggestions = [
  "Comment signaler un utilisateur ?",
  "Comment créer mon profil ?",
  "Quels sont les délais de traitement ?",
  "Comment contacter le support ?"
]

const sendQuickMessage = (suggestion) => {
  userInput.value = suggestion
  sendMessage()
}

// Scroll vers le bas
const scrollToBottom = (smooth = true) => {
  if (chatContainer.value) {
    chatContainer.value.scrollTo({
      top: chatContainer.value.scrollHeight,
      behavior: smooth ? 'smooth' : 'auto'
    })
  }
}

// Détecter le scroll pour afficher le bouton
const handleScroll = () => {
  if (chatContainer.value) {
    const { scrollTop, scrollHeight, clientHeight } = chatContainer.value
    showScrollButton.value = scrollHeight - scrollTop - clientHeight > 200
  }
}

// Nouvelle conversation
const startNewConversation = () => {
  if (confirm('Voulez-vous vraiment commencer une nouvelle conversation ? L\'historique actuel sera effacé.')) {
    chatbotStore.resetConversation()
    chatbotStore.saveConversation()
  }
}

// Formater l'heure
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

// Retour
const goBack = () => {
  router.push('/dashboard')
}
</script>

<template>
  <div class="support-page">
    <!-- Header -->
    <header class="chat-header">
      <div class="header-container">
        <div class="header-left">
          <button class="back-btn" @click="goBack">
            <i class="fas fa-arrow-left"></i>
          </button>
          <div class="header-info">
            <div class="bot-avatar">
              <i class="fas fa-robot"></i>
            </div>
            <div class="bot-details">
              <h1>Assistant FreelanceCMR</h1>
              <p class="bot-status">
                <span class="status-indicator"></span>
                Toujours disponible
              </p>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <button class="action-btn" @click="startNewConversation" title="Nouvelle conversation">
            <i class="fas fa-plus"></i>
          </button>
          <button class="action-btn" @click="chatbotStore.saveConversation" title="Sauvegarder">
            <i class="fas fa-save"></i>
          </button>
        </div>
      </div>
    </header>

    <!-- Zone de chat -->
    <div class="chat-container" ref="chatContainer" @scroll="handleScroll">
      <div class="chat-content">
        <!-- Messages -->
        <div
          v-for="message in chatbotStore.messages"
          :key="message.id"
          class="message-wrapper"
          :class="message.sender === 'bot' ? 'bot-message-wrapper' : 'user-message-wrapper'"
        >
          <div class="message-bubble" :class="message.sender === 'bot' ? 'bot-bubble' : 'user-bubble'">
            <div v-if="message.sender === 'bot'" class="message-avatar">
              <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessageText(message.content)"></div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
        </div>

        <!-- Indicateur de chargement -->
        <div v-if="chatbotStore.isLoading" class="message-wrapper bot-message-wrapper">
          <div class="message-bubble bot-bubble typing-indicator">
            <div class="message-avatar">
              <i class="fas fa-robot"></i>
            </div>
            <div class="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>

        <!-- Erreur -->
        <div v-if="chatbotStore.error" class="error-banner">
          <i class="fas fa-exclamation-triangle"></i>
          {{ chatbotStore.error }}
        </div>
      </div>
    </div>

    <!-- Bouton scroll vers le bas -->
    <transition name="fade">
      <button v-if="showScrollButton" class="scroll-to-bottom" @click="scrollToBottom()">
        <i class="fas fa-arrow-down"></i>
      </button>
    </transition>

    <!-- Suggestions rapides -->
    <div v-if="chatbotStore.messages.length <= 2" class="quick-suggestions">
      <p class="suggestions-title">
        <i class="fas fa-lightbulb"></i>
        Questions fréquentes
      </p>
      <div class="suggestions-grid">
        <button
          v-for="(suggestion, index) in quickSuggestions"
          :key="index"
          class="suggestion-btn"
          @click="sendQuickMessage(suggestion)"
          :disabled="chatbotStore.isLoading"
        >
          {{ suggestion }}
        </button>
      </div>
    </div>

    <!-- Zone de saisie -->
    <div class="input-area">
      <div class="input-container">
        <form @submit.prevent="sendMessage" class="input-form">
          <textarea
            v-model="userInput"
            placeholder="Posez votre question..."
            rows="1"
            class="message-input"
            :disabled="chatbotStore.isLoading"
            @keydown.enter.exact.prevent="sendMessage"
          ></textarea>
          <button
            type="submit"
            class="send-btn"
            :disabled="!userInput.trim() || chatbotStore.isLoading"
          >
            <i class="fas fa-paper-plane"></i>
          </button>
        </form>
        <p class="input-hint">
          <i class="fas fa-info-circle"></i>
          Appuyez sur Entrée pour envoyer
        </p>
      </div>
    </div>
  </div>
</template>

<script>
// Méthode pour formater le texte (gestion markdown simple)
export default {
  methods: {
    formatMessageText(text) {
      // Remplacer les sauts de ligne
      let formatted = text.replace(/\n/g, '<br>')
      
      // Gras
      formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      
      // Italique
      formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>')
      
      // Listes à puces (lignes commençant par •)
      formatted = formatted.replace(/^• (.+)/gm, '<li>$1</li>')
      if (formatted.includes('<li>')) {
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
      }
      
      return formatted
    }
  }
}
</script>

<style scoped>
.support-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  overflow: hidden;
}

/* Header */
.chat-header {
  background: linear-gradient(135deg, #2D3047 0%, #1A1C2E 100%);
  color: white;
  padding: 15px 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
  z-index: 10;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bot-avatar {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF6B35, #F7931E);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  color: white;
}

.bot-details h1 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.bot-status {
  margin: 2px 0 0 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4ade80;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.header-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Zone de chat */
.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth;
}

.chat-content {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* Messages */
.message-wrapper {
  display: flex;
  animation: slideIn 0.3s ease;
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

.bot-message-wrapper {
  justify-content: flex-start;
}

.user-message-wrapper {
  justify-content: flex-end;
}

.message-bubble {
  display: flex;
  gap: 12px;
  max-width: 70%;
}

.bot-bubble {
  background: white;
  padding: 15px;
  border-radius: 18px 18px 18px 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-bubble {
  background: linear-gradient(135deg, #2D3047, #1A1C2E);
  color: white;
  padding: 15px 20px;
  border-radius: 18px 18px 4px 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.message-avatar {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF6B35, #F7931E);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

.user-bubble .message-text {
  color: white;
}

.message-text :deep(ul) {
  margin: 10px 0;
  padding-left: 20px;
}

.message-text :deep(li) {
  margin: 5px 0;
}

.message-text :deep(strong) {
  font-weight: 700;
}

.message-time {
  font-size: 0.75rem;
  color: #6c757d;
  margin-top: 5px;
}

.user-bubble .message-time {
  color: rgba(255, 255, 255, 0.7);
  text-align: right;
}

/* Indicateur de saisie */
.typing-indicator {
  padding: 15px;
}

.typing-dots {
  display: flex;
  gap: 5px;
  padding: 10px 0;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #6c757d;
  animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* Erreur */
.error-banner {
  background: linear-gradient(135deg, #f8d7da, #f5c6cb);
  border: 1px solid #f5c6cb;
  border-left: 4px solid #dc3545;
  color: #721c24;
  padding: 15px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Bouton scroll */
.scroll-to-bottom {
  position: fixed;
  bottom: 180px;
  right: 30px;
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2D3047, #1A1C2E);
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 5;
}

.scroll-to-bottom:hover {
  transform: scale(1.1);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Suggestions rapides */
.quick-suggestions {
  max-width: 900px;
  margin: 0 auto 20px;
  padding: 0 20px;
}

.suggestions-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6c757d;
  font-size: 0.9rem;
  margin-bottom: 12px;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.suggestion-btn {
  padding: 12px 16px;
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  color: #2D3047;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.suggestion-btn:hover:not(:disabled) {
  border-color: #2D3047;
  background: #f8f9fa;
  transform: translateY(-2px);
}

.suggestion-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Zone de saisie */
.input-area {
  background: white;
  border-top: 1px solid #e9ecef;
  padding: 20px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

.input-container {
  max-width: 900px;
  margin: 0 auto;
}

.input-form {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  padding: 15px 20px;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  font-family: inherit;
  font-size: 1rem;
  resize: none;
  max-height: 120px;
  transition: all 0.3s ease;
}

.message-input:focus {
  outline: none;
  border-color: #2D3047;
  background: #f8f9fa;
}

.message-input:disabled {
  background: #e9ecef;
  cursor: not-allowed;
}

.send-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2D3047, #1A1C2E);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(45, 48, 71, 0.3);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-hint {
  margin: 8px 0 0 0;
  font-size: 0.8rem;
  color: #6c757d;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Responsive */
@media (max-width: 768px) {
  .chat-container {
    padding: 15px;
  }
  
  .message-bubble {
    max-width: 85%;
  }
  
  .bot-details h1 {
    font-size: 1rem;
  }
  
  .suggestions-grid {
    grid-template-columns: 1fr;
  }
  
  .scroll-to-bottom {
    bottom: 160px;
    right: 20px;
  }
}

@media (max-width: 576px) {
  .header-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .message-bubble {
    max-width: 90%;
  }
  
  .input-area {
    padding: 15px;
  }
}

/* Scrollbar personnalisée */
.chat-container::-webkit-scrollbar {
  width: 8px;
}

.chat-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
