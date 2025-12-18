<template>
  <div class="create-mission-page">
    <!-- En-tête avec navigation -->
    <div class="page-header">
      <div class="header-container">
        <div class="back-section">
          <button class="back-btn" @click="goBack">
            <i class="fas fa-arrow-left"></i>
            Retour
          </button>
          <div class="header-info">
            <h1>
              <i class="fas fa-plus-circle"></i>
              Créer une mission
            </h1>
            <p class="header-subtitle">
              Publiez votre projet et trouvez les meilleurs freelances camerounais
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Contenu principal -->
    <div class="page-content">
      <div class="form-container">
        <!-- Carte du formulaire -->
        <div class="mission-form-card">
          <div class="form-header">
            <h2>
              <i class="fas fa-clipboard-list"></i>
              Informations de la mission
            </h2>
            <p class="form-subtitle">
              Remplissez les détails de votre projet pour attirer les meilleurs talents
            </p>
          </div>

          <form class="mission-form" @submit.prevent="submitMission">
            <!-- Titre -->
            <div class="form-group">
              <label for="title">
                <i class="fas fa-heading"></i>
                Titre de la mission *
              </label>
              <div class="input-with-icon">
                <i class="fas fa-edit input-prefix"></i>
                <input
                  id="title"
                  v-model="form.title"
                  type="text"
                  placeholder="Ex: Développement d'une application web"
                  required
                />
              </div>
            </div>

            <!-- Description -->
            <div class="form-group">
              <label for="description">
                <i class="fas fa-align-left"></i>
                Description détaillée *
              </label>
              <textarea
                id="description"
                v-model="form.description"
                placeholder="Décrivez votre projet en détail..."
                required
                rows="6"
              ></textarea>
              <div class="textarea-footer">
                <span class="format-tips">
                  <i class="fas fa-lightbulb"></i>
                  Soyez le plus précis possible
                </span>
              </div>
            </div>

            <!-- Budget et Date -->
            <div class="form-row">
              <!-- Budget -->
              <div class="form-group half">
                <label for="budget">
                  <i class="fas fa-money-bill-wave"></i>
                  Budget (FCFA) *
                </label>
                <div class="input-with-icon">
                  <i class="fas fa-coins input-prefix"></i>
                  <input
                    id="budget"
                    type="number"
                    v-model.number="form.budget"
                    placeholder="Ex: 500000"
                    required
                    min="10000"
                  />
                  <span class="input-suffix">FCFA</span>
                </div>
                <div class="budget-suggestions">
                  <span class="suggestion-label">Suggéré :</span>
                  <button type="button" class="suggestion-btn" @click="form.budget = 250000">
                    250K
                  </button>
                  <button type="button" class="suggestion-btn" @click="form.budget = 500000">
                    500K
                  </button>
                  <button type="button" class="suggestion-btn" @click="form.budget = 1000000">
                    1M
                  </button>
                </div>
              </div>

              <!-- Date limite -->
              <div class="form-group half">
                <label for="deadline">
                  <i class="fas fa-calendar-alt"></i>
                  Date limite
                </label>
                <div class="input-with-icon">
                  <i class="fas fa-calendar input-prefix"></i>
                  <input
                    id="deadline"
                    type="date"
                    v-model="form.deadline"
                    :min="minDate"
                  />
                </div>
                <div class="deadline-suggestions">
                  <button type="button" class="suggestion-btn outline" @click="setDeadline(7)">
                    <i class="fas fa-clock"></i>
                    1 semaine
                  </button>
                  <button type="button" class="suggestion-btn outline" @click="setDeadline(30)">
                    <i class="fas fa-calendar"></i>
                    1 mois
                  </button>
                </div>
              </div>
            </div>

            <!-- Compétences -->
            <div class="form-group">
              <label for="required_skills">
                <i class="fas fa-code"></i>
                Compétences requises
              </label>
              <div class="input-with-icon">
                <i class="fas fa-tags input-prefix"></i>
                <input
                  id="required_skills"
                  v-model="form.required_skills"
                  type="text"
                  placeholder="Ex: Vue.js, Node.js, MongoDB, Design UI/UX"
                />
              </div>
              
              <!-- Suggestions de compétences -->
              <div class="skills-suggestions">
                <div class="skills-tags">
                  <span class="skill-tag" @click="addSkill('Vue.js')">Vue.js</span>
                  <span class="skill-tag" @click="addSkill('React')">React</span>
                  <span class="skill-tag" @click="addSkill('Node.js')">Node.js</span>
                  <span class="skill-tag" @click="addSkill('Laravel')">Laravel</span>
                  <span class="skill-tag" @click="addSkill('Python')">Python</span>
                  <span class="skill-tag" @click="addSkill('Figma')">Figma</span>
                  <span class="skill-tag" @click="addSkill('UI/UX')">UI/UX</span>
                  <span class="skill-tag" @click="addSkill('Mobile')">Mobile</span>
                </div>
              </div>

              <!-- Compétences ajoutées -->
              <div v-if="selectedSkills.length > 0" class="selected-skills">
                <span class="selected-label">Compétences sélectionnées :</span>
                <div class="selected-tags">
                  <span v-for="(skill, index) in selectedSkills" :key="index" class="selected-tag">
                    {{ skill }}
                    <button type="button" class="remove-skill" @click="removeSkill(index)">
                      <i class="fas fa-times"></i>
                    </button>
                  </span>
                </div>
              </div>
            </div>

            <!-- Message d'erreur -->
            <div v-if="missionsStore.error" class="error-message">
              <i class="fas fa-exclamation-circle"></i>
              <span>{{ missionsStore.error }}</span>
            </div>

            <!-- Actions -->
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="goBack">
                <i class="fas fa-times"></i>
                Annuler
              </button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <template v-if="loading">
                  <i class="fas fa-spinner fa-spin"></i>
                  Création en cours...
                </template>
                <template v-else>
                  <i class="fas fa-rocket"></i>
                  Publier la mission
                </template>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, ref } from 'vue'
import { useMissionStore } from '@/stores/missions'
import { useRouter } from 'vue-router'

const missionsStore = useMissionStore()
const router = useRouter()

// États
const loading = ref(false)
const form = reactive({
  title: '',
  description: '',
  budget: null,
  deadline: '',
  required_skills: ''
})

// Compétences sélectionnées
const selectedSkills = computed(() => {
  return form.required_skills
    ? form.required_skills
        .split(',')
        .map(skill => skill.trim())
        .filter(Boolean)
    : []
})

// Date minimum (demain)
const minDate = computed(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.toISOString().split('T')[0]
})

// Méthodes
const goBack = () => {
  router.push('/client/missions')
}

const addSkill = (skill) => {
  const currentSkills = form.required_skills ? form.required_skills.split(',').map(s => s.trim()) : []
  if (!currentSkills.includes(skill)) {
    currentSkills.push(skill)
    form.required_skills = currentSkills.join(', ')
  }
}

const removeSkill = (index) => {
  const skills = [...selectedSkills.value]
  skills.splice(index, 1)
  form.required_skills = skills.join(', ')
}

const setDeadline = (days) => {
  const date = new Date()
  date.setDate(date.getDate() + days)
  form.deadline = date.toISOString().split('T')[0]
}

const submitMission = async () => {
  loading.value = true
  
  // Transformation vers format backend
  const payload = {
    title: form.title.trim(),
    description: form.description.trim(),
    budget: form.budget,
    deadline: form.deadline
      ? new Date(form.deadline).toISOString()
      : null,
    required_skills: selectedSkills.value
  }

  const success = await missionsStore.createMission(payload)

  if (success) {
    loading.value = false
    setTimeout(() => {
      router.push('/client/missions')
    }, 1000)
  } else {
    loading.value = false
  }
}
</script>

<style scoped>
/* ==================== STYLES GÉNÉRAUX ==================== */
.create-mission-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* ==================== EN-TÊTE ==================== */
.page-header {
  background: white;
  padding: 20px 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border-bottom: 1px solid #f0f0f0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.back-section {
  display: flex;
  align-items: center;
  gap: 25px;
  margin-bottom: 10px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  color: #6c757d;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: translateX(-5px);
}

.header-info h1 {
  font-size: 2rem;
  color: #2D3047;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-info h1 i {
  color: #FF6B35;
  font-size: 1.8rem;
}

.header-subtitle {
  color: #6c757d;
  margin: 0;
  font-size: 1.1rem;
  line-height: 1.6;
}

/* ==================== CONTENU ==================== */
.page-content {
  max-width: 1200px;
  margin: 30px auto;
  padding: 0 20px;
}

.form-container {
  display: flex;
  justify-content: center;
}

/* ==================== CARTE FORMULAIRE ==================== */
.mission-form-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  width: 100%;
  max-width: 700px;
}

.form-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f5f9;
}

.form-header h2 {
  font-size: 1.8rem;
  color: #2D3047;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  gap: 15px;
}

.form-header h2 i {
  color: #FF6B35;
  font-size: 1.5rem;
}

.form-subtitle {
  color: #6c757d;
  margin: 0;
  font-size: 1rem;
  line-height: 1.6;
}

/* ==================== FORMULAIRE ==================== */
.mission-form {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-group label {
  font-weight: 600;
  color: #2D3047;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1rem;
}

.form-group label i {
  color: #FF6B35;
  font-size: 1.1rem;
}

/* Input avec icône */
.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-prefix {
  position: absolute;
  left: 16px;
  color: #6c757d;
  font-size: 1rem;
  z-index: 2;
}

.input-with-icon input {
  width: 100%;
  padding: 14px 16px 14px 45px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
  background: white;
  color: #2D3047;
}

.input-with-icon input:focus {
  outline: none;
  border-color: #FF6B35;
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.input-suffix {
  position: absolute;
  right: 16px;
  color: #6c757d;
  font-size: 0.9rem;
  font-weight: 600;
}

/* Textarea */
textarea {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
  background: white;
  color: #2D3047;
  resize: vertical;
  min-height: 150px;
  line-height: 1.6;
}

textarea:focus {
  outline: none;
  border-color: #FF6B35;
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.textarea-footer {
  margin-top: 8px;
  padding: 0 5px;
}

.format-tips {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6c757d;
  font-size: 0.9rem;
}

.format-tips i {
  color: #FF6B35;
  font-size: 0.9rem;
}

/* ==================== LIGNE FORMULAIRE ==================== */
.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-group.half {
  margin: 0;
}

/* ==================== SUGGESTIONS ==================== */
.budget-suggestions,
.deadline-suggestions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
  flex-wrap: wrap;
}

.suggestion-label {
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 500;
}

.suggestion-btn {
  padding: 8px 16px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  color: #6c757d;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.85rem;
}

.suggestion-btn:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: translateY(-2px);
}

.suggestion-btn.outline {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
}

/* ==================== COMPÉTENCES ==================== */
.skills-suggestions {
  margin-top: 15px;
}

.skills-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.skill-tag {
  padding: 8px 16px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  color: #6c757d;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.skill-tag:hover {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border-color: #FF6B35;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 107, 53, 0.2);
}

/* Compétences sélectionnées */
.selected-skills {
  margin-top: 20px;
}

.selected-label {
  display: block;
  font-weight: 600;
  color: #2D3047;
  margin-bottom: 10px;
  font-size: 0.95rem;
}

.selected-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.selected-tag {
  padding: 8px 16px;
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  border-radius: 20px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 5px 15px rgba(255, 107, 53, 0.2);
}

.remove-skill {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.7rem;
}

.remove-skill:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* ==================== ERREUR ==================== */
.error-message {
  padding: 15px 20px;
  background: linear-gradient(135deg, #EF4444, #F87171);
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 10px 0;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateY(-10px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.error-message i {
  font-size: 1.2rem;
}

/* ==================== ACTIONS ==================== */
.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px solid #f1f5f9;
}

.btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 30px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  font-family: inherit;
}

.btn-primary {
  background: linear-gradient(135deg, #FF6B35, #FF8E53);
  color: white;
  flex: 1;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
  border-color: rgba(255, 255, 255, 0.2);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  color: #2D3047;
  border: 2px solid #e5e7eb;
}

.btn-secondary:hover {
  border-color: #FF6B35;
  color: #FF6B35;
  transform: translateY(-3px);
}

/* ==================== RESPONSIVE ==================== */

/* Tablette */
@media (max-width: 768px) {
  .page-header {
    padding: 15px 0;
  }
  
  .back-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header-info h1 {
    font-size: 1.6rem;
  }
  
  .mission-form-card {
    padding: 20px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}

/* Mobile */
@media (max-width: 480px) {
  .page-content {
    padding: 0 15px;
  }
  
  .mission-form-card {
    padding: 15px;
  }
  
  .form-header h2 {
    font-size: 1.4rem;
  }
  
  .skills-tags {
    justify-content: center;
  }
}

/* Support tactile */
@media (hover: none) and (pointer: coarse) {
  .suggestion-btn:hover,
  .skill-tag:hover,
  .btn:hover,
  .back-btn:hover,
  .remove-skill:hover {
    transform: none;
  }
  
  .suggestion-btn:active,
  .skill-tag:active {
    transform: scale(0.95);
  }
}
</style>