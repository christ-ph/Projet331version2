<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h3 class="modal-title">Rejeter le livrable</h3>
        <button @click="$emit('close')" class="modal-close">✕</button>
      </div>
      
      <div class="modal-body">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Motif du rejet *
          </label>
          <textarea
            v-model="feedback"
            rows="4"
            required
            class="w-full px-3 py-2 border rounded-md"
            placeholder="Expliquez pourquoi vous rejetez ce livrable..."
          ></textarea>
        </div>
        
        <div class="flex justify-end space-x-3">
          <button
            @click="$emit('close')"
            class="px-4 py-2 border rounded-md text-gray-700 hover:bg-gray-50"
          >
            Annuler
          </button>
          <button
            @click="handleReject"
            :disabled="!feedback.trim()"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
          >
            Rejeter
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  deliverableId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['reject', 'close'])

const feedback = ref('')

function handleReject() {
  if (!feedback.value.trim()) return
  emit('reject', props.deliverableId, feedback.value.trim())
}
</script>

<style scoped>
/* Mêmes styles que AcceptModal */
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
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
}

.modal-close:hover {
  color: #374151;
}
</style>