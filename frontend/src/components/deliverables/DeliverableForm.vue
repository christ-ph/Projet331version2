<template>
  <div class="deliverable-form-container">
    <!-- En-tête -->
    <div class="form-header" v-if="props.deliverable">
      <h3 class="form-title">
        <i class="fas fa-edit"></i>
        Modifier le livrable
      </h3>
      <p class="form-subtitle">
        Mission: <strong>{{ missionTitle }}</strong>
      </p>
    </div>
    <div class="form-header" v-else>
      <h3 class="form-title">
        <i class="fas fa-plus-circle"></i>
        Nouveau livrable
      </h3>
      <p class="form-subtitle">
        Pour la mission: <strong>{{ missionTitle }}</strong>
      </p>
      <p class="form-note">
        <i class="fas fa-info-circle"></i>
        Un fichier est obligatoire pour créer un livrable
      </p>
    </div>

    <!-- Formulaire -->
    <form @submit.prevent="handleSubmit" class="deliverable-form">
      <!-- Titre -->
      <div class="form-group">
        <label for="deliverable-title" class="form-label">
          <i class="fas fa-heading"></i>
          Titre du livrable *
        </label>
        <input
          id="deliverable-title"
          v-model="form.title"
          type="text"
          required
          placeholder="Ex: Maquette finale, Rapport de projet, Code source..."
          class="form-input"
          :class="{ 'error': errors.title }"
        />
        <div v-if="errors.title" class="error-message">
          {{ errors.title }}
        </div>
      </div>
      
      <!-- Description -->
      <div class="form-group">
        <label for="deliverable-description" class="form-label">
          <i class="fas fa-align-left"></i>
          Description
        </label>
        <textarea
          id="deliverable-description"
          v-model="form.description"
          rows="4"
          placeholder="Décrivez votre livrable en détail..."
          class="form-textarea"
        ></textarea>
        <div class="char-counter" v-if="form.description">
          {{ form.description.length }}/500 caractères
        </div>
      </div>
      
      <!-- Fichier -->
      <div class="form-group">
        <label class="form-label">
          <i class="fas fa-paperclip"></i>
          Fichier {{ props.deliverable ? '(optionnel pour modification)' : '*' }}
        </label>
        
        <!-- Zone de dépôt de fichier -->
        <div 
          class="file-drop-zone"
          :class="{ 
            'dragover': isDragging, 
            'has-file': selectedFile,
            'error': fileError
          }"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <div v-if="!selectedFile" class="drop-zone-content">
            <i class="fas fa-cloud-upload-alt"></i>
            <p>Glissez-déposez votre fichier ici</p>
            <p class="drop-zone-hint">ou cliquez pour parcourir</p>
          </div>
          <div v-else class="file-info">
            <i class="fas fa-file"></i>
            <div class="file-details">
              <strong>{{ selectedFile.name }}</strong>
              <span>{{ formatFileSize(selectedFile.size) }}</span>
            </div>
            <button @click.stop="removeFile" class="remove-file-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
        
        <input
          type="file"
          ref="fileInput"
          @change="handleFileChange"
          :required="!props.deliverable"
          class="file-input"
          style="display: none;"
        />
        
        <div v-if="fileError" class="error-message">
          {{ fileError }}
        </div>
        
        <div class="file-requirements">
          <i class="fas fa-info-circle"></i>
          <span>Formats acceptés: documents, images, vidéos, archives, code source, design</span>
          <br>
          <span>Taille maximale: 50 Mo</span>
        </div>
        
        <!-- Fichier existant -->
        <div v-if="props.deliverable?.file_url && !selectedFile" class="existing-file">
          <div class="file-info">
            <i class="fas fa-file"></i>
            <div class="file-details">
              <strong>Fichier actuel</strong>
              <span>{{ getFileName(props.deliverable.file_url) }}</span>
            </div>
            <button @click="downloadExistingFile" class="download-file-btn">
              <i class="fas fa-download"></i>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Instructions -->
      <div class="instructions">
        <h4><i class="fas fa-lightbulb"></i> Conseils pour votre livrable:</h4>
        <ul>
          <li>Donnez un titre clair et descriptif</li>
          <li>Décrivez précisément ce que vous livrez</li>
          <li>Assurez-vous que le fichier est correctement nommé</li>
          <li>Vérifiez la qualité de votre travail avant de soumettre</li>
        </ul>
      </div>
      
      <!-- Actions -->
      <div class="form-actions">
        <button
          type="button"
          @click="$emit('cancel')"
          class="btn btn-cancel"
          :disabled="submitting"
        >
          <i class="fas fa-times"></i>
          Annuler
        </button>
        <button
          type="submit"
          :disabled="submitting || !form.title.trim() || (!props.deliverable && !selectedFile)"
          class="btn btn-submit"
        >
          <span v-if="submitting">
            <i class="fas fa-spinner fa-spin"></i>
            Enregistrement...
          </span>
          <span v-else>
            <i class="fas fa-save"></i>
            {{ props.deliverable ? 'Mettre à jour' : 'Créer le livrable' }}
          </span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMissionStore } from '@/stores/missions'
import { useDeliverablesStore } from '@/stores/deliverables'

const props = defineProps({
  missionId: {
    type: Number,
    required: true
  },
  deliverable: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit', 'cancel'])

const missionsStore = useMissionStore()
const deliverablesStore = useDeliverablesStore()

const form = ref({
  title: props.deliverable?.title || '',
  description: props.deliverable?.description || '',
  // CORRECTION: mission_id n'est pas nécessaire dans le form data réactif,
  // il sera ajouté directement dans FormData
})

const selectedFile = ref(null)
const fileInput = ref(null)
const isDragging = ref(false)
const submitting = ref(false)
const errors = ref({})
const fileError = ref('')

// Récupérer le titre de la mission
const missionTitle = computed(() => {
  const mission = missionsStore.availableMissions.find(m => m.id === props.missionId)
  return mission?.title || 'Mission'
})

onMounted(() => {
  console.log('🔍 DeliverableForm - Mission ID:', props.missionId)
  console.log('🔍 DeliverableForm - Deliverable:', props.deliverable)
  
  // Vérifier que missionId est bien passé
  if (!props.missionId) {
    console.error('❌ ERREUR: Mission ID non fourni')
  }
})

// Obtenir le nom du fichier depuis l'URL
const getFileName = (fileUrl) => {
  if (!fileUrl) return ''
  return fileUrl.split('/').pop()
}

// Télécharger le fichier existant
const downloadExistingFile = async () => {
  if (!props.deliverable?.id) return
  
  try {
    await deliverablesStore.downloadFile(props.deliverable.id)
  } catch (error) {
    console.error('❌ Erreur téléchargement:', error)
    alert('Erreur lors du téléchargement du fichier')
  }
}

// Gestion du drag & drop
const handleDragOver = (e) => {
  e.preventDefault()
  isDragging.value = true
}

const handleDragLeave = (e) => {
  e.preventDefault()
  isDragging.value = false
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  fileError.value = ''
  
  const file = e.dataTransfer.files[0]
  if (file && validateFile(file)) {
    selectedFile.value = file
  }
}

// Déclencher l'input fichier
const triggerFileInput = () => {
  fileInput.value.click()
}

// Gestion du changement de fichier
const handleFileChange = (e) => {
  fileError.value = ''
  const file = e.target.files[0]
  if (file && validateFile(file)) {
    selectedFile.value = file
  }
}

// Validation du fichier
const validateFile = (file) => {
  fileError.value = ''
  
  const maxSize = 50 * 1024 * 1024 // 50 Mo
  
  if (file.size > maxSize) {
    fileError.value = 'Fichier trop volumineux (max 50 Mo)'
    return false
  }
  
  const fileName = file.name.toLowerCase()
  const allowedExtensions = [
    '.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages',
    '.ppt', '.pptx', '.odp', '.key',
    '.xls', '.xlsx', '.ods', '.csv',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.svg', '.webp', '.ico', '.psd', '.ai',
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp',
    '.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a', '.wma',
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
    '.html', '.css', '.js', '.py', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs',
    '.json', '.xml', '.yml', '.yaml', '.sql',
    '.psd', '.ai', '.xd', '.fig', '.sketch', '.indd'
  ]
  
  const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext))
  
  if (!hasValidExtension) {
    fileError.value = 'Type de fichier non supporté'
    return false
  }
  
  return true
}

// Formater la taille du fichier
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Supprimer le fichier
const removeFile = () => {
  selectedFile.value = null
  fileError.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Validation du formulaire
const validateForm = () => {
  errors.value = {}
  fileError.value = ''
  
  if (!form.value.title.trim()) {
    errors.value.title = 'Le titre est obligatoire'
    return false
  }
  
  if (!props.missionId) {
    errors.value.mission = 'ID de mission manquant'
    console.error('❌ ERREUR: missionId est undefined')
    return false
  }
  
  if (!props.deliverable && !selectedFile.value) {
    fileError.value = 'Un fichier est obligatoire pour créer un livrable'
    return false
  }
  
  return true
}

// Soumettre le formulaire
const handleSubmit = async () => {
  if (!validateForm()) return
  
  submitting.value = true
  
  try {
    const formData = new FormData()
    
    // **CORRECTION CRITIQUE: Ajouter mission_id au FormData**
    formData.append('mission_id', props.missionId.toString())
    formData.append('title', form.value.title.trim())
    
    // Ajouter la description si elle existe
    if (form.value.description && form.value.description.trim()) {
      formData.append('description', form.value.description.trim())
    } else {
      formData.append('description', '')
    }
    
    // Ajouter le fichier s'il existe
    if (selectedFile.value instanceof File) {
      formData.append('file', selectedFile.value)
    }
    
    console.log('📤 Envoi du formulaire - Livrable:')
    console.log('  Titre:', form.value.title)
    console.log('  Description:', form.value.description)
    console.log('  Mission ID:', props.missionId)
    console.log('  Fichier:', selectedFile.value?.name || 'Aucun')
    
    // Afficher le contenu du FormData pour déboguer
    console.log('📋 Contenu FormData envoyé:')
    for (let [key, value] of formData.entries()) {
      if (value instanceof File) {
        console.log(`  ${key}:`, {
          name: value.name,
          size: value.size,
          type: value.type
        })
      } else {
        console.log(`  ${key}:`, value)
      }
    }
    
    emit('submit', formData)
    
  } catch (error) {
    console.error('❌ Erreur préparation formulaire:', error)
    alert('Erreur lors de la préparation du formulaire')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.deliverable-form-container {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  animation: fadeIn 0.3s ease-out;
}

.form-header {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 24px;
}

.form-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-subtitle {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
}

.form-note {
  font-size: 12px;
  opacity: 0.8;
  margin: 5px 0 0 0;
  display: flex;
  align-items: center;
  gap: 5px;
}

.form-note i {
  font-size: 14px;
}

.deliverable-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  color: #374151;
  background: white;
  transition: all 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.error {
  border-color: #ef4444;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
  max-height: 200px;
  font-family: inherit;
}

.char-counter {
  text-align: right;
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.error-message {
  color: #ef4444;
  font-size: 12px;
  margin-top: 4px;
}

.file-drop-zone {
  border: 2px dashed #d1d5db;
  border-radius: 10px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #f9fafb;
}

.file-drop-zone.dragover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.file-drop-zone.has-file {
  border-style: solid;
  border-color: #10b981;
  background: #f0fdf4;
  padding: 20px;
}

.file-drop-zone.error {
  border-color: #ef4444;
  background: #fef2f2;
}

.drop-zone-content i {
  font-size: 48px;
  color: #9ca3af;
  margin-bottom: 16px;
}

.drop-zone-content p {
  margin: 0;
  color: #6b7280;
}

.drop-zone-hint {
  font-size: 12px;
  color: #9ca3af;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
}

.file-info i {
  font-size: 24px;
  color: #3b82f6;
}

.file-details {
  flex: 1;
  text-align: left;
}

.file-details strong {
  display: block;
  color: #374151;
  font-size: 14px;
  margin-bottom: 4px;
}

.file-details span {
  font-size: 12px;
  color: #6b7280;
}

.remove-file-btn {
  background: #fee2e2;
  color: #dc2626;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.remove-file-btn:hover {
  background: #fecaca;
}

.download-file-btn {
  background: #dbeafe;
  color: #1d4ed8;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.download-file-btn:hover {
  background: #93c5fd;
}

.existing-file {
  margin-top: 10px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.file-requirements {
  font-size: 12px;
  color: #6b7280;
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.file-requirements i {
  color: #9ca3af;
}

.instructions {
  background: #fef3c7;
  border: 1px solid #fde68a;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 24px;
}

.instructions h4 {
  font-size: 14px;
  color: #92400e;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.instructions ul {
  margin: 0;
  padding-left: 20px;
}

.instructions li {
  font-size: 13px;
  color: #92400e;
  margin-bottom: 4px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}

.btn {
  flex: 1;
  padding: 14px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 2px solid transparent;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
  border-color: #d1d5db;
}

.btn-cancel:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-submit {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.btn-submit:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
</style>