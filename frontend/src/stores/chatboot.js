import { defineStore } from 'pinia'
import { useAuthStore } from './auth'
import { useProfileStore } from './profile'

// ⚠️ IMPORTANT : Remplacez par votre vraie clé API Gemini
const GEMINI_API_KEY = 'AIzaSyAsPVoz8oC0xPPc2pZQtTlPhD-Py6XUODE'

// Dataset de connaissances de la plateforme
const PLATFORM_DATASET = {
  nom_plateforme: "FreelanceCMR",
  description: "Plateforme camerounaise de mise en relation entre freelances et clients",
  
  fonctionnalites: {
    signalements: {
      description: "Système de signalement d'utilisateurs inappropriés",
      procedure: "Via la page Signalements, remplir le formulaire avec l'email et le motif détaillé",
      delai_traitement: "24 à 48 heures ouvrables",
      confidentialite: "Totale - l'utilisateur signalé ne connaîtra jamais votre identité"
    },
    profils: {
      types: ["freelance", "client"],
      freelance: "Créer un profil avec compétences, tarif horaire, expérience",
      client: "Créer un profil avec type (particulier/entreprise), secteur d'activité"
    },
    authentification: {
      inscription: "Email + mot de passe, vérification par code email",
      connexion: "Email + mot de passe",
      securite: "Token JWT, sessions sécurisées"
    }
  },
  
  aide_commune: {
    mot_de_passe_oublie: "Utilisez la fonction 'Mot de passe oublié' sur la page de connexion",
    probleme_connexion: "Vérifiez votre email et mot de passe, puis votre connexion internet",
    modifier_profil: "Accédez au Dashboard puis 'Mon Profil'",
    supprimer_compte: "Contactez le support à support@freelancecmr.com"
  },
  
  contact_support: {
    email: "support@freelancecmr.com",
    urgence: "Pour harcèlement grave ou menaces, contactez immédiatement le support d'urgence"
  }
}

export const useChatbotStore = defineStore('chatbot', {
  state: () => ({
    messages: [],
    isLoading: false,
    error: null,
    conversationContext: '',
    messageCounter: 0
  }),

  getters: {
    // Récupérer le nom complet de l'utilisateur
    getUserFullName: () => {
      const profileStore = useProfileStore()
      const authStore = useAuthStore()
      
      if (profileStore.profile?.full_name) {
        return profileStore.profile.full_name
      } else if (profileStore.profile?.fullname) {
        return profileStore.profile.fullname
      }
      return authStore.displayName || 'Utilisateur'
    },
    
    // Compter les messages
    totalMessages: (state) => state.messages.length,
    
    // Dernière réponse du bot
    lastBotMessage: (state) => {
      const botMessages = state.messages.filter(m => m.sender === 'bot')
      return botMessages[botMessages.length - 1]?.content || null
    }
  },

  actions: {
    /**
     * Initialiser le chatbot avec un message de bienvenue
     */
    async initialize() {
      const authStore = useAuthStore()
      const profileStore = useProfileStore()
      
      // Charger le profil si pas déjà fait
      if (!profileStore.profile) {
        try {
          await profileStore.getMyProfile()
        } catch (error) {
          console.log('Pas de profil chargé')
        }
      }
      
      // Construire le contexte
      this.buildContext()
      
      // Si pas de messages, ajouter le message de bienvenue
      if (this.messages.length === 0) {
        this.addBotMessage(
          `Bonjour ${this.getUserFullName} ! 👋\n\n` +
          `Je suis l'assistant virtuel de FreelanceCMR. Je suis là pour vous aider avec :\n\n` +
          `• Les signalements et plaintes\n` +
          `• La gestion de votre profil\n` +
          `• Les questions sur la plateforme\n` +
          `• Toute autre question\n\n` +
          `Comment puis-je vous aider aujourd'hui ?`
        )
      }
    },

    /**
     * Construire le contexte pour l'IA
     */
    buildContext() {
      const authStore = useAuthStore()
      const profileStore = useProfileStore()
      
      let context = `Tu es l'assistant virtuel de FreelanceCMR, une plateforme camerounaise de freelancing.\n\n`
      
      context += `INFORMATIONS UTILISATEUR:\n`
      context += `- Nom: ${this.getUserFullName}\n`
      context += `- Email: ${authStore.user?.email || 'Non défini'}\n`
      context += `- Rôle: ${authStore.role || 'USER'}\n`
      
      if (profileStore.profile) {
        context += `- Type de profil: ${profileStore.profile.type || 'Non défini'}\n`
        if (profileStore.profile.type === 'freelance') {
          context += `- Titre: ${profileStore.profile.title || 'Non défini'}\n`
          context += `- Compétences: ${profileStore.profile.skills?.join(', ') || 'Aucune'}\n`
        }
      }
      
      context += `\n\nCONTEXTE DE LA PLATEFORME:\n`
      context += `${JSON.stringify(PLATFORM_DATASET, null, 2)}\n\n`
      
      context += `INSTRUCTIONS:\n`
      context += `1. Réponds en français de manière claire et professionnelle\n`
      context += `2. Utilise les informations du dataset pour répondre aux questions\n`
      context += `3. Si tu ne connais pas la réponse, oriente vers le support (support@freelancecmr.com)\n`
      context += `4. Sois empathique et serviable\n`
      context += `5. Utilise des emojis pour rendre les réponses plus humaines\n`
      context += `6. Structure tes réponses avec des paragraphes et listes quand nécessaire\n`
      context += `7. Personnalise les réponses avec le nom de l'utilisateur quand approprié\n\n`
      
      this.conversationContext = context
    },

    /**
     * Ajouter un message utilisateur
     */
    addUserMessage(content) {
      this.messageCounter++
      this.messages.push({
        id: this.messageCounter,
        sender: this.getUserFullName,
        content: content,
        timestamp: new Date().toISOString(),
        order: this.messageCounter
      })
    },

    /**
     * Ajouter un message du bot
     */
    addBotMessage(content) {
      this.messageCounter++
      this.messages.push({
        id: this.messageCounter,
        sender: 'bot',
        content: content,
        timestamp: new Date().toISOString(),
        order: this.messageCounter
      })
    },

    /**
     * Envoyer un message et obtenir une réponse de l'IA
     */
    async sendMessage(userMessage) {
      if (!userMessage.trim()) return
      
      // Ajouter le message utilisateur
      this.addUserMessage(userMessage)
      
      this.isLoading = true
      this.error = null
      
      try {
        // Construire l'historique de conversation pour le contexte
        const conversationHistory = this.messages
          .slice(-6) // Garder les 6 derniers messages pour le contexte
          .map(m => `${m.sender}: ${m.content}`)
          .join('\n\n')
        
        // Préparer le prompt complet
        const fullPrompt = `${this.conversationContext}\n\nHISTORIQUE DE CONVERSATION:\n${conversationHistory}\n\nUtilisateur: ${userMessage}\n\nAssistant:`
        
        // Appel à l'API Gemini
        const response = await fetch(
          `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${GEMINI_API_KEY}`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              contents: [{
                parts: [{
                  text: fullPrompt
                }]
              }],
              generationConfig: {
                temperature: 0.7,
                topK: 40,
                topP: 0.95,
                maxOutputTokens: 1024,
              }
            })
          }
        )
        
        if (!response.ok) {
          throw new Error(`Erreur API: ${response.status}`)
        }
        
        const data = await response.json()
        
        // Extraire la réponse
        const botResponse = data.candidates?.[0]?.content?.parts?.[0]?.text || 
                           "Désolé, je n'ai pas pu générer une réponse. Pouvez-vous reformuler votre question ?"
        
        // Ajouter la réponse du bot
        this.addBotMessage(botResponse)
        
        return { success: true }
      } catch (error) {
        console.error('Erreur chatbot:', error)
        this.error = error.message
        
        // Message d'erreur amical
        this.addBotMessage(
          `😔 Désolé, je rencontre un problème technique.\n\n` +
          `Pour une assistance immédiate, contactez notre support à : support@freelancecmr.com`
        )
        
        return { success: false, error: error.message }
      } finally {
        this.isLoading = false
      }
    },

    /**
     * Réinitialiser la conversation
     */
    resetConversation() {
      this.messages = []
      this.messageCounter = 0
      this.error = null
      this.initialize()
    },

    /**
     * Sauvegarder la conversation (localStorage)
     */
    saveConversation() {
      try {
        localStorage.setItem('chatbot_messages', JSON.stringify(this.messages))
        localStorage.setItem('chatbot_counter', this.messageCounter.toString())
      } catch (error) {
        console.error('Erreur sauvegarde conversation:', error)
      }
    },

    /**
     * Charger la conversation sauvegardée
     */
    loadConversation() {
      try {
        const savedMessages = localStorage.getItem('chatbot_messages')
        const savedCounter = localStorage.getItem('chatbot_counter')
        
        if (savedMessages) {
          this.messages = JSON.parse(savedMessages)
        }
        if (savedCounter) {
          this.messageCounter = parseInt(savedCounter)
        }
        
        // Si pas de messages, initialiser
        if (this.messages.length === 0) {
          this.initialize()
        } else {
          this.buildContext()
        }
      } catch (error) {
        console.error('Erreur chargement conversation:', error)
        this.initialize()
      }
    }
  }
})
