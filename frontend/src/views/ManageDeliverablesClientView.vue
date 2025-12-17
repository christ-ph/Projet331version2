<template>
  <div class="client-deliverables-page">
    <!-- En-tête -->
    <div class="page-header">
      <div class="header-main">
        <h1 class="page-title">Livrables - {{ mission?.title }}</h1>
        <div class="header-actions">
          <router-link 
            :to="{ name: 'MissionDetails', params: { id: missionId } }"
            class="back-btn"
          >
            ← Retour à la mission
          </router-link>
          <span class="mission-status" :class="mission?.status">
            {{ getMissionStatusLabel(mission?.status) }}
          </span>
        </div>
      </div>
      
      <div class="header-info">
        <div class="info-item">
          <span class="info-label">Freelance assigné:</span>
          <span class="info-value">{{ assignedFreelance?.name || 'Non assigné' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Budget:</span>
          <span class="info-value">{{ formatCurrency(mission?.budget) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Deadline:</span>
          <span class="info-value">{{ formatDate(mission?.deadline) || 'Non définie' }}</span>
        </div>
      </div>
    </div>

    <!-- Tableau de bord -->
    <div class="dashboard-cards">
      <div class="dashboard-card">
        <div class="card-icon" style="background: #dbeafe;">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="card-content">
          <div class="card-value">{{ statusStats.accepted || 0 }}</div>
          <div class="card-label">Acceptés</div>
        </div>
      </div>
      
      <div class="dashboard-card">
        <div class="card-icon" style="background: #fef3c7;">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="card-content">
          <div class="card-value">{{ statusStats.under_review || 0 }}</div>
          <div class="card-label">En attente</div>
        </div>
      </div>
      
      <div class="dashboard-card">
        <div class="card-icon" style="background: #fee2e2;">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="card-content">
          <div class="card-value">{{ statusStats.rejected || 0 }}</div>
          <div class="card-label">Rejetés</div>
        </div>
      </div>
      
      <div class="dashboard-card">
        <div class="card-icon" style="background: #f3f4f6;">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <div class="card-content">
          <div class="card-value">{{ deliverables.length }}</div>
          <div class="card-label">Total livrables</div>
        </div>
      </div>
    </div>

    <!-- Contenu principal -->
    <div class="main-content">
      <!-- Filtres rapides -->
      <div class="filters-section">
        <div class="filters-header">
          <h2 class="filters-title">Livrables de la mission</h2>
          <div class="filters-actions">
            <button 
              @click="refreshData" 
              class="refresh-btn"
              :class="{ refreshing: loading }"
            >
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Actualiser
            </button>
          </div>
        </div>
        
        <div class="status-filters">
          <button
            v-for="filter in statusFilters"
            :key="filter.value"
            @click="toggleStatusFilter(filter.value)"
            :class="['status-filter-btn', { active: activeStatusFilters.includes(filter.value) }]"
            :style="{ borderColor: filter.color, color: activeStatusFilters.includes(filter.value) ? filter.color : '#6b7280' }"
          >
            {{ filter.label }}
            <span class="filter-count">{{ getDeliverableCount(filter.value) }}</span>
          </button>
        </div>
        
        <div class="search-filter">
          <div class="search-input">
            <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Rechercher un livrable..."
              class="search-field"
            />
          </div>
          <select v-model="sortBy" class="sort-select">
            <option value="created_at">Plus récents</option>
            <option value="submitted_at">Date de soumission</option>
            <option value="title">Titre A-Z</option>
          </select>
        </div>
      </div>

      <!-- Tableau des livrables -->
      <div class="deliverables-table">
        <div class="table-header">
          <div class="table-cell" style="flex: 3;">Livrable</div>
          <div class="table-cell" style="flex: 2;">Statut</div>
          <div class="table-cell" style="flex: 2;">Date de soumission</div>
          <div class="table-cell" style="flex: 2;">Actions</div>
        </div>
        
        <div v-if="loading" class="loading-row">
          <div class="loading-spinner"></div>
          <span>Chargement des livrables...</span>
        </div>
        
        <div v-else-if="filteredDeliverables.length === 0" class="empty-row">
          <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="empty-title">Aucun livrable trouvé</p>
          <p class="empty-message">
            {{ searchQuery || activeStatusFilters.length > 0 ? 'Aucun résultat pour vos critères' : 'Aucun livrable n\'a été soumis pour cette mission' }}
          </p>
        </div>
        
        <div v-else class="table-body">
          <div
            v-for="deliverable in filteredDeliverables"
            :key="deliverable.id"
            :class="['table-row', { expanded: expandedRow === deliverable.id }]"
            @click="toggleRow(deliverable.id)"
          >
            <div class="row-main">
              <div class="row-content" style="flex: 3;">
                <h3 class="deliverable-title">{{ deliverable.title }}</h3>
                <p class="deliverable-description">{{ truncateText(deliverable.description, 100) }}</p>
                <div class="deliverable-meta">
                  <span class="meta-item">
                    <svg class="meta-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    {{ deliverable.freelance_name || 'Freelance' }}
                  </span>
                  <span class="meta-item">
                    <svg class="meta-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Créé le {{ formatDate(deliverable.created_at) }}
                  </span>
                </div>
              </div>
              
              <div class="row-content" style="flex: 2;">
                <span :class="['status-badge', deliverable.status]">
                  {{ getStatusLabel(deliverable.status) }}
                </span>
                <div v-if="deliverable.status === 'submitted'" class="submission-info">
                  <span class="submission-label">En attente de review</span>
                  <span class="submission-time">{{ getTimeSince(deliverable.submitted_at) }}</span>
                </div>
              </div>
              
              <div class="row-content" style="flex: 2;">
                <div v-if="deliverable.submitted_at" class="date-info">
                  <div class="date-value">{{ formatDateTime(deliverable.submitted_at) }}</div>
                  <div class="date-diff">{{ getTimeSince(deliverable.submitted_at) }}</div>
                </div>
                <span v-else class="date-na">Non soumis</span>
              </div>
              
              <div class="row-content actions-cell" style="flex: 2;">
                <div class="action-buttons">
                  <!-- Téléchargement -->
                  <button
                    v-if="deliverable.file_url"
                    @click.stop="downloadFile(deliverable.id)"
                    class="action-btn download"
                    title="Télécharger le fichier"
                  >
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </button>
                  
                  <!-- Démarrer review (soumis seulement) -->
                  <button
                    v-if="deliverable.status === 'submitted'"
                    @click.stop="startReview(deliverable.id)"
                    class="action-btn review"
                    title="Commencer la review"
                  >
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  
                  <!-- Accepter (en review seulement) -->
                  <button
                    v-if="deliverable.status === 'under_review'"
                    @click.stop="showAcceptModal = deliverable.id"
                    class="action-btn accept"
                    title="Accepter le livrable"
                  >
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </button>
                  
                  <!-- Rejeter (en review seulement) -->
                  <button
                    v-if="deliverable.status === 'under_review'"
                    @click.stop="showRejectModal = deliverable.id"
                    class="action-btn reject"
                    title="Rejeter le livrable"
                  >
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                  
                  <!-- Demander révision (en review seulement) -->
                  <button
                    v-if="deliverable.status === 'under_review'"
                    @click.stop="showRevisionModal = deliverable.id"
                    class="action-btn revision"
                    title="Demander une révision"
                  >
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  
                  <!-- Voir détails -->
                  <button
                    @click.stop="toggleRow(deliverable.id)"
                    class="action-btn details"
                    :title="expandedRow === deliverable.id ? 'Masquer détails' : 'Voir détails'"
                  >
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path v-if="expandedRow !== deliverable.id" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Détails expandus -->
            <div v-if="expandedRow === deliverable.id" class="row-details">
              <div class="details-grid">
                <div class="details-section">
                  <h4 class="details-title">Description détaillée</h4>
                  <p class="details-content">{{ deliverable.description || 'Aucune description fournie' }}</p>
                </div>
                
                <div class="details-section">
                  <h4 class="details-title">Informations du fichier</h4>
                  <div class="file-info">
                    <div class="file-item">
                      <span class="file-label">URL:</span>
                      <a :href="deliverable.file_url" target="_blank" class="file-link">{{ deliverable.file_url }}</a>
                    </div>
                    <div v-if="deliverable.file_name" class="file-item">
                      <span class="file-label">Nom:</span>
                      <span class="file-value">{{ deliverable.file_name }}</span>
                    </div>
                    <div v-if="deliverable.file_size" class="file-item">
                      <span class="file-label">Taille:</span>
                      <span class="file-value">{{ formatFileSize(deliverable.file_size) }}</span>
                    </div>
                    <div v-if="deliverable.file_type" class="file-item">
                      <span class="file-label">Type:</span>
                      <span class="file-value">{{ deliverable.file_type }}</span>
                    </div>
                  </div>
                </div>
                
                <div v-if="deliverable.client_feedback" class="details-section">
                  <h4 class="details-title">Votre feedback</h4>
                  <div class="feedback-box">
                    {{ deliverable.client_feedback }}
                    <div class="feedback-date">
                      Donné le {{ formatDateTime(deliverable.reviewed_at || deliverable.accepted_at) }}
                    </div>
                  </div>
                </div>
                
                <div class="details-section">
                  <h4 class="details-title">Historique</h4>
                  <div class="timeline">
                    <div v-if="deliverable.created_at" class="timeline-item">
                      <div class="timeline-dot created"></div>
                      <div class="timeline-content">
                        <div class="timeline-title">Créé</div>
                        <div class="timeline-date">{{ formatDateTime(deliverable.created_at) }}</div>
                      </div>
                    </div>
                    <div v-if="deliverable.submitted_at" class="timeline-item">
                      <div class="timeline-dot submitted"></div>
                      <div class="timeline-content">
                        <div class="timeline-title">Soumis pour review</div>
                        <div class="timeline-date">{{ formatDateTime(deliverable.submitted_at) }}</div>
                      </div>
                    </div>
                    <div v-if="deliverable.reviewed_at" class="timeline-item">
                      <div class="timeline-dot reviewed"></div>
                      <div class="timeline-content">
                        <div class="timeline-title">Review commencée</div>
                        <div class="timeline-date">{{ formatDateTime(deliverable.reviewed_at) }}</div>
                      </div>
                    </div>
                    <div v-if="deliverable.accepted_at" class="timeline-item">
                      <div class="timeline-dot accepted"></div>
                      <div class="timeline-content">
                        <div class="timeline-title">Accepté</div>
                        <div class="timeline-date">{{ formatDateTime(deliverable.accepted_at) }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Actions dans les détails -->
              <div class="details-actions">
                <button
                  v-if="deliverable.file_url"
                  @click="downloadFile(deliverable.id)"
                  class="details-action-btn download"
                >
                  <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Télécharger le fichier
                </button>
                
                <div v-if="deliverable.status === 'submitted'" class="review-actions">
                  <button @click="startReview(deliverable.id)" class="details-action-btn review">
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    Commencer la review
                  </button>
                </div>
                
                <div v-if="deliverable.status === 'under_review'" class="decision-actions">
                  <button @click="showAcceptModal = deliverable.id" class="details-action-btn accept">
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Accepter le livrable
                  </button>
                  
                  <button @click="showRejectModal = deliverable.id" class="details-action-btn reject">
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Rejeter
                  </button>
                  
                  <button @click="showRevisionModal = deliverable.id" class="details-action-btn revision">
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Demander une révision
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Panneau latéral pour actions rapides -->
    <div v-if="selectedDeliverable && !showModals" class="sidebar-panel">
      <div class="sidebar-header">
        <h3 class="sidebar-title">Actions rapides</h3>
        <button @click="selectedDeliverable = null" class="close-sidebar">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div class="sidebar-content">
        <div class="current-selection">
          <h4 class="selection-title">{{ selectedDeliverable.title }}</h4>
          <span :class="['status-badge', selectedDeliverable.status]">
            {{ getStatusLabel(selectedDeliverable.status) }}
          </span>
        </div>
        
        <div class="action-buttons-vertical">
          <button
            v-if="selectedDeliverable.file_url"
            @click="downloadFile(selectedDeliverable.id)"
            class="sidebar-action-btn download"
          >
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Télécharger le fichier
          </button>
          
          <button
            v-if="selectedDeliverable.status === 'submitted'"
            @click="startReview(selectedDeliverable.id)"
            class="sidebar-action-btn review"
          >
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Commencer la review
          </button>
          
          <div v-if="selectedDeliverable.status === 'under_review'" class="decision-buttons">
            <button @click="showAcceptModal = selectedDeliverable.id" class="sidebar-action-btn accept">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Accepter
            </button>
            
            <button @click="showRejectModal = selectedDeliverable.id" class="sidebar-action-btn reject">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              Rejeter
            </button>
            
            <button @click="showRevisionModal = selectedDeliverable.id" class="sidebar-action-btn revision">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Demander révision
            </button>
          </div>
        </div>
        
        <div v-if="selectedDeliverable.client_feedback" class="sidebar-feedback">
          <h4 class="feedback-title">Votre dernier feedback</h4>
          <p class="feedback-content">{{ selectedDeliverable.client_feedback }}</p>
        </div>
      </div>
    </div>

    <!-- Overlay modals -->
    <div v-if="showModals" class="modal-overlay" @click.self="closeAllModals">
      <!-- Modal Acceptation -->
      <div v-if="showAcceptModal" class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Accepter le livrable</h3>
          <button @click="showAcceptModal = null" class="modal-close">
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="modal-content">
          <p>Êtes-vous sûr de vouloir accepter ce livrable ? Cette action est définitive.</p>
          <div class="modal-info">
            <strong>Livrable:</strong> {{ getDeliverableTitle(showAcceptModal) }}
          </div>
          <div class="modal-actions">
            <button @click="handleAccept(showAcceptModal)" class="modal-btn confirm">
              Oui, accepter
            </button>
            <button @click="showAcceptModal = null" class="modal-btn cancel">
              Annuler
            </button>
          </div>
        </div>
      </div>
      
      <!-- Modal Rejet -->
      <div v-if="showRejectModal" class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Rejeter le livrable</h3>
          <button @click="showRejectModal = null" class="modal-close">
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="modal-content">
          <p>Pourquoi rejetez-vous ce livrable ? Veuillez fournir un feedback constructif au freelance.</p>
          <textarea
            v-model="rejectFeedback"
            placeholder="Ex: Le livrable ne correspond pas aux spécifications demandées..."
            class="feedback-input"
            rows="4"
          ></textarea>
          <div class="modal-actions">
            <button @click="handleReject(showRejectModal, rejectFeedback)" class="modal-btn confirm reject">
              Confirmer le rejet
            </button>
            <button @click="showRejectModal = null" class="modal-btn cancel">
              Annuler
            </button>
          </div>
        </div>
      </div>
      
      <!-- Modal Demande de révision -->
      <div v-if="showRevisionModal" class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Demander une révision</h3>
          <button @click="showRevisionModal = null" class="modal-close">
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="modal-content">
          <p>Quelles modifications souhaitez-vous que le freelance apporte ?</p>
          <textarea
            v-model="revisionFeedback"
            placeholder="Ex: Veuillez corriger les points suivants..."
            class="feedback-input"
            rows="4"
          ></textarea>
          <div class="modal-info">
            <p><small>Le freelance pourra modifier et resoumettre le livrable.</small></p>
          </div>
          <div class="modal-actions">
            <button @click="handleRevision(showRevisionModal, revisionFeedback)" class="modal-btn confirm revision">
              Demander la révision
            </button>
            <button @click="showRevisionModal = null" class="modal-btn cancel">
              Annuler
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast notifications -->
    <div v-if="toastMessage" :class="['toast', toastType]" @click="toastMessage = null">
      <div class="toast-content">
        <svg v-if="toastType === 'success'" class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <svg v-else class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ toastMessage }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useDeliverablesStore } from '@/stores/deliverables'
import { useMissionStore } from '@/stores/missions'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const deliverablesStore = useDeliverablesStore()
const missionsStore = useMissionStore()
const authStore = useAuthStore()

const missionId = parseInt(route.params.missionId)
const loading = ref(false)
const searchQuery = ref('')
const sortBy = ref('created_at')
const activeStatusFilters = ref(['submitted', 'under_review'])
const expandedRow = ref(null)
const selectedDeliverable = ref(null)
const showAcceptModal = ref(null)
const showRejectModal = ref(null)
const showRevisionModal = ref(null)
const rejectFeedback = ref('')
const revisionFeedback = ref('')
const toastMessage = ref(null)
const toastType = ref('success')

const statusFilters = [
  { label: 'Soumis', value: 'submitted', color: '#3b82f6' },
  { label: 'En review', value: 'under_review', color: '#f59e0b' },
  { label: 'Acceptés', value: 'accepted', color: '#10b981' },
  { label: 'Rejetés', value: 'rejected', color: '#ef4444' },
  { label: 'Révision demandée', value: 'needs_revision', color: '#f97316' },
  { label: 'Brouillons', value: 'draft', color: '#6b7280' }
]

// Computed
const user = computed(() => authStore.user)
const mission = computed(() => missionsStore.currentMission)
const deliverables = computed(() => deliverablesStore.deliverables)

const assignedFreelance = computed(() => {
  if (!mission.value?.postulations) return null
  const accepted = mission.value.postulations.find(p => p.status === 'accepted')
  return accepted?.freelance
})

const statusStats = computed(() => {
  const stats = {}
  deliverables.value.forEach(d => {
    stats[d.status] = (stats[d.status] || 0) + 1
  })
  return stats
})

const filteredDeliverables = computed(() => {
  let filtered = [...deliverables.value]
  
  // Filtre par statut
  if (activeStatusFilters.value.length > 0) {
    filtered = filtered.filter(d => activeStatusFilters.value.includes(d.status))
  }
  
  // Filtre par recherche
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(d => 
      d.title.toLowerCase().includes(query) ||
      d.description?.toLowerCase().includes(query)
    )
  }
  
  // Tri
  filtered.sort((a, b) => {
    if (sortBy.value === 'created_at') {
      return new Date(b.created_at) - new Date(a.created_at)
    } else if (sortBy.value === 'submitted_at') {
      return new Date(b.submitted_at || 0) - new Date(a.submitted_at || 0)
    } else {
      return a.title.localeCompare(b.title)
    }
  })
  
  return filtered
})

const showModals = computed(() => {
  return showAcceptModal.value || showRejectModal.value || showRevisionModal.value
})

// Methods
function getStatusLabel(status) {
  const labels = {
    draft: 'Brouillon',
    submitted: 'Soumis',
    under_review: 'En review',
    accepted: 'Accepté',
    rejected: 'Rejeté',
    needs_revision: 'Révision demandée'
  }
  return labels[status] || status
}

function getMissionStatusLabel(status) {
  const labels = {
    draft: 'Brouillon',
    open: 'Ouverte',
    in_progress: 'En cours',
    completed: 'Terminée',
    cancelled: 'Annulée'
  }
  return labels[status] || status
}

function formatDate(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('fr-FR')
}

function formatDateTime(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('fr-FR')
}

function formatCurrency(amount) {
  if (!amount) return 'Non défini'
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR'
  }).format(amount)
}

function formatFileSize(bytes) {
  if (!bytes) return 'Inconnu'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

function getTimeSince(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 60) return `il y a ${diffMins} min`
  if (diffHours < 24) return `il y a ${diffHours} h`
  if (diffDays === 1) return 'hier'
  if (diffDays < 7) return `il y a ${diffDays} jours`
  return formatDate(dateString)
}

function truncateText(text, maxLength) {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

function toggleStatusFilter(status) {
  const index = activeStatusFilters.value.indexOf(status)
  if (index > -1) {
    activeStatusFilters.value.splice(index, 1)
  } else {
    activeStatusFilters.value.push(status)
  }
}

function toggleRow(deliverableId) {
  expandedRow.value = expandedRow.value === deliverableId ? null : deliverableId
  const deliverable = deliverables.value.find(d => d.id === deliverableId)
  if (deliverable) {
    selectedDeliverable.value = deliverable
  }
}

function getDeliverableCount(status) {
  return deliverables.value.filter(d => d.status === status).length
}

function getDeliverableTitle(id) {
  const deliverable = deliverables.value.find(d => d.id === id)
  return deliverable?.title || ''
}

function showToast(message, type = 'success') {
  toastMessage.value = message
  toastType.value = type
  setTimeout(() => {
    toastMessage.value = null
  }, 3000)
}

// Actions
async function refreshData() {
  await loadData()
  showToast('Données actualisées')
}

async function loadData() {
  loading.value = true
  try {
    await missionsStore.fetchMissionDetails(missionId)
    await deliverablesStore.fetchMissionDeliverables(missionId)
  } catch (error) {
    console.error('Erreur chargement:', error)
    showToast('Erreur lors du chargement', 'error')
  } finally {
    loading.value = false
  }
}

async function downloadFile(id) {
  try {
    await deliverablesStore.downloadFile(id)
  } catch (error) {
    console.error('Erreur téléchargement:', error)
    showToast('Erreur lors du téléchargement', 'error')
  }
}

async function startReview(id) {
  if (confirm('Commencer la review de ce livrable ?')) {
    try {
      await deliverablesStore.startReview(id)
      await loadData()
      showToast('Review démarrée avec succès')
    } catch (error) {
      console.error('Erreur début review:', error)
      showToast('Erreur lors du début de la review', 'error')
    }
  }
}

async function handleAccept(id) {
  try {
    await deliverablesStore.acceptDeliverable(id)
    await loadData()
    showAcceptModal.value = null
    showToast('Livrable accepté avec succès')
  } catch (error) {
    console.error('Erreur acceptation:', error)
    showToast('Erreur lors de l\'acceptation', 'error')
  }
}

async function handleReject(id, feedback) {
  if (!feedback?.trim()) {
    alert('Veuillez fournir un feedback avant de rejeter')
    return
  }
  
  try {
    await deliverablesStore.rejectDeliverable(id, feedback)
    await loadData()
    showRejectModal.value = null
    rejectFeedback.value = ''
    showToast('Livrable rejeté avec succès')
  } catch (error) {
    console.error('Erreur rejet:', error)
    showToast('Erreur lors du rejet', 'error')
  }
}

async function handleRevision(id, feedback) {
  if (!feedback?.trim()) {
    alert('Veuillez spécifier les modifications demandées')
    return
  }
  
  try {
    await deliverablesStore.requestRevision(id, feedback)
    await loadData()
    showRevisionModal.value = null
    revisionFeedback.value = ''
    showToast('Révision demandée avec succès')
  } catch (error) {
    console.error('Erreur demande révision:', error)
    showToast('Erreur lors de la demande de révision', 'error')
  }
}

function closeAllModals() {
  showAcceptModal.value = null
  showRejectModal.value = null
  showRevisionModal.value = null
  rejectFeedback.value = ''
  revisionFeedback.value = ''
}

// Lifecycle
onMounted(async () => {
  await loadData()
})

// Watchers
watch([showAcceptModal, showRejectModal, showRevisionModal], () => {
  if (!showModals.value) {
    rejectFeedback.value = ''
    revisionFeedback.value = ''
  }
})
</script>

<style scoped>
.client-deliverables-page {
  max-width: 1400px;
  margin: 100px auto 50px;
  padding: 0 20px;
  font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
}

/* En-tête */
.page-header {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 32px;
  margin-bottom: 32px;
  border: 1px solid #e5e7eb;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-title {
  font-size: 32px;
  color: #111827;
  font-weight: 800;
  margin: 0;
  line-height: 1.2;
}

.header-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.back-btn {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
  transition: color 0.2s;
}

.back-btn:hover {
  color: #2563eb;
}

.mission-status {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.mission-status.in_progress {
  background: #fef3c7;
  color: #d97706;
  border: 1px solid #fde68a;
}

.header-info {
  display: flex;
  gap: 40px;
  padding-top: 20px;
  border-top: 1px solid #f3f4f6;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.info-value {
  font-size: 16px;
  color: #111827;
  font-weight: 600;
}

/* Tableau de bord */
.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.dashboard-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  transition: transform 0.2s, box-shadow 0.2s;
}

.dashboard-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-icon .icon {
  width: 28px;
  height: 28px;
  color: #374151;
}

.card-content {
  flex: 1;
}

.card-value {
  font-size: 32px;
  font-weight: 800;
  color: #111827;
  line-height: 1;
  margin-bottom: 4px;
}

.card-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 600;
}

/* Filtres */
.filters-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid #e5e7eb;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filters-title {
  font-size: 20px;
  color: #111827;
  font-weight: 700;
  margin: 0;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover {
  background: #e5e7eb;
}

.refresh-btn.refreshing .icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.refresh-btn .icon {
  width: 16px;
  height: 16px;
}

.status-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.status-filter-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 2px solid;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.status-filter-btn:hover {
  transform: translateY(-1px);
}

.status-filter-btn.active {
  background: #f8fafc;
}

.filter-count {
  background: currentColor;
  color: white;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

.search-filter {
  display: flex;
  gap: 16px;
}

.search-input {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #9ca3af;
}

.search-field {
  width: 100%;
  padding: 12px 16px 12px 48px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-size: 16px;
  transition: all 0.2s;
}

.search-field:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.sort-select {
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  background: white;
  color: #374151;
  font-size: 16px;
  min-width: 180px;
  cursor: pointer;
}

.sort-select:focus {
  outline: none;
  border-color: #3b82f6;
}

/* Tableau */
.deliverables-table {
  background: white;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.table-header {
  display: flex;
  padding: 20px 24px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 700;
  color: #374151;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table-cell {
  padding: 0 12px;
}

.loading-row, .empty-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f4f6;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.empty-icon {
  width: 60px;
  height: 60px;
  color: #d1d5db;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 18px;
  color: #111827;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.empty-message {
  color: #6b7280;
  margin: 0;
  max-width: 400px;
}

.table-body {
  max-height: 600px;
  overflow-y: auto;
}

.table-row {
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: background-color 0.2s;
}

.table-row:hover {
  background-color: #f9fafb;
}

.table-row.expanded {
  background-color: #f8fafc;
}

.row-main {
  display: flex;
  padding: 20px 24px;
  align-items: flex-start;
}

.row-content {
  padding: 0 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.deliverable-title {
  font-size: 16px;
  color: #111827;
  font-weight: 600;
  margin: 0;
}

.deliverable-description {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
  line-height: 1.5;
}

.deliverable-meta {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #6b7280;
  font-size: 13px;
}

.meta-icon {
  width: 14px;
  height: 14px;
}

/* Badges de statut */
.status-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  align-self: flex-start;
}

.status-badge.draft {
  background: #f3f4f6;
  color: #6b7280;
}

.status-badge.submitted {
  background: #dbeafe;
  color: #1d4ed8;
}

.status-badge.under_review {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.accepted {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.rejected {
  background: #fee2e2;
  color: #dc2626;
}

.status-badge.needs_revision {
  background: #fed7aa;
  color: #c2410c;
}

.submission-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.submission-label {
  font-size: 12px;
  color: #6b7280;
}

.submission-time {
  font-size: 11px;
  color: #9ca3af;
}

.date-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.date-value {
  font-size: 14px;
  color: #111827;
  font-weight: 500;
}

.date-diff {
  font-size: 12px;
  color: #6b7280;
}

.date-na {
  color: #9ca3af;
  font-style: italic;
  font-size: 14px;
}

/* Actions */
.actions-cell {
  display: flex;
  justify-content: flex-end;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 8px;
  background: #f3f4f6;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-btn.download {
  background: #dbeafe;
  color: #1d4ed8;
}

.action-btn.download:hover {
  background: #93c5fd;
}

.action-btn.review {
  background: #fef3c7;
  color: #d97706;
}

.action-btn.review:hover {
  background: #fde68a;
}

.action-btn.accept {
  background: #d1fae5;
  color: #065f46;
}

.action-btn.accept:hover {
  background: #a7f3d0;
}

.action-btn.reject {
  background: #fee2e2;
  color: #dc2626;
}

.action-btn.reject:hover {
  background: #fca5a5;
}

.action-btn.revision {
  background: #fed7aa;
  color: #c2410c;
}

.action-btn.revision:hover {
  background: #fdba74;
}

.action-btn.details {
  background: #f3f4f6;
  color: #374151;
}

.action-btn.details:hover {
  background: #e5e7eb;
}

.action-btn .icon {
  width: 16px;
  height: 16px;
}

/* Détails expandus */
.row-details {
  padding: 0 24px 24px 24px;
  background: #f8fafc;
  border-top: 1px solid #e5e7eb;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.details-section {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
}

.details-title {
  font-size: 14px;
  color: #374151;
  font-weight: 700;
  margin: 0 0 12px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.details-content {
  color: #4b5563;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.file-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-label {
  font-weight: 600;
  color: #374151;
  min-width: 60px;
  font-size: 13px;
}

.file-link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 14px;
  word-break: break-all;
}

.file-link:hover {
  text-decoration: underline;
}

.file-value {
  color: #4b5563;
  font-size: 14px;
}

.feedback-box {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 16px;
  color: #92400e;
  font-size: 14px;
  line-height: 1.5;
}

.feedback-date {
  font-size: 12px;
  color: #b45309;
  margin-top: 8px;
  font-style: italic;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.timeline-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
}

.timeline-dot.created {
  background: #9ca3af;
}

.timeline-dot.submitted {
  background: #3b82f6;
}

.timeline-dot.reviewed {
  background: #f59e0b;
}

.timeline-dot.accepted {
  background: #10b981;
}

.timeline-content {
  flex: 1;
}

.timeline-title {
  font-weight: 600;
  color: #374151;
  font-size: 13px;
}

.timeline-date {
  font-size: 12px;
  color: #6b7280;
}

.details-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.details-action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.details-action-btn.download {
  background: #dbeafe;
  color: #1d4ed8;
}

.details-action-btn.download:hover {
  background: #93c5fd;
  transform: translateY(-1px);
}

.details-action-btn.review {
  background: #fef3c7;
  color: #d97706;
}

.details-action-btn.review:hover {
  background: #fde68a;
  transform: translateY(-1px);
}

.details-action-btn.accept {
  background: #d1fae5;
  color: #065f46;
}

.details-action-btn.accept:hover {
  background: #a7f3d0;
  transform: translateY(-1px);
}

.details-action-btn.reject {
  background: #fee2e2;
  color: #dc2626;
}

.details-action-btn.reject:hover {
  background: #fca5a5;
  transform: translateY(-1px);
}

.details-action-btn.revision {
  background: #fed7aa;
  color: #c2410c;
}

.details-action-btn.revision:hover {
  background: #fdba74;
  transform: translateY(-1px);
}

.details-action-btn .icon {
  width: 16px;
  height: 16px;
}

.review-actions, .decision-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Panneau latéral */
.sidebar-panel {
  position: fixed;
  top: 100px;
  right: 20px;
  width: 350px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border: 1px solid #e5e7eb;
  z-index: 100;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.sidebar-title {
  font-size: 18px;
  color: #111827;
  font-weight: 700;
  margin: 0;
}

.close-sidebar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #f3f4f6;
  color: #374151;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.close-sidebar:hover {
  background: #e5e7eb;
}

.close-sidebar .icon {
  width: 16px;
  height: 16px;
}

.sidebar-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.current-selection {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selection-title {
  font-size: 16px;
  color: #111827;
  font-weight: 600;
  margin: 0;
  line-height: 1.4;
}

.action-buttons-vertical {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sidebar-action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  justify-content: flex-start;
}

.sidebar-action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.sidebar-action-btn.download {
  background: #dbeafe;
  color: #1d4ed8;
}

.sidebar-action-btn.download:hover {
  background: #93c5fd;
}

.sidebar-action-btn.review {
  background: #fef3c7;
  color: #d97706;
}

.sidebar-action-btn.review:hover {
  background: #fde68a;
}

.sidebar-action-btn.accept {
  background: #d1fae5;
  color: #065f46;
}

.sidebar-action-btn.accept:hover {
  background: #a7f3d0;
}

.sidebar-action-btn.reject {
  background: #fee2e2;
  color: #dc2626;
}

.sidebar-action-btn.reject:hover {
  background: #fca5a5;
}

.sidebar-action-btn.revision {
  background: #fed7aa;
  color: #c2410c;
}

.sidebar-action-btn.revision:hover {
  background: #fdba74;
}

.sidebar-action-btn .icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.decision-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar-feedback {
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.feedback-title {
  font-size: 14px;
  color: #374151;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.feedback-content {
  color: #4b5563;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
  font-style: italic;
}

/* Modals */
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
  padding: 20px;
}

.modal {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 20px;
  color: #111827;
  font-weight: 700;
  margin: 0;
}

.modal-close {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #f3f4f6;
  color: #374151;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #e5e7eb;
}

.modal-close .icon {
  width: 16px;
  height: 16px;
}

.modal-content {
  padding: 32px;
}

.modal-content p {
  color: #4b5563;
  font-size: 16px;
  line-height: 1.6;
  margin: 0 0 24px 0;
}

.modal-info {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  font-size: 14px;
  color: #374151;
}

.feedback-input {
  width: 100%;
  padding: 16px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-size: 16px;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 24px;
  transition: all 0.2s;
}

.feedback-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.modal-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-btn.confirm {
  background: #10b981;
  color: white;
}

.modal-btn.confirm:hover {
  background: #059669;
}

.modal-btn.confirm.reject {
  background: #ef4444;
}

.modal-btn.confirm.reject:hover {
  background: #dc2626;
}

.modal-btn.confirm.revision {
  background: #f59e0b;
}

.modal-btn.confirm.revision:hover {
  background: #d97706;
}

.modal-btn.cancel {
  background: #f3f4f6;
  color: #374151;
}

.modal-btn.cancel:hover {
  background: #e5e7eb;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: white;
  border-radius: 12px;
  padding: 16px 24px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  border: 1px solid #e5e7eb;
  z-index: 1001;
  animation: toastSlideIn 0.3s ease-out;
  cursor: pointer;
  max-width: 400px;
}

@keyframes toastSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.toast.success {
  border-left: 4px solid #10b981;
}

.toast.error {
  border-left: 4px solid #ef4444;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toast-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.toast.success .toast-icon {
  color: #10b981;
}

.toast.error .toast-icon {
  color: #ef4444;
}

.toast span {
  color: #374151;
  font-weight: 500;
  font-size: 14px;
}

/* Responsive */
@media (max-width: 1200px) {
  .header-info {
    flex-wrap: wrap;
    gap: 20px;
  }
  
  .dashboard-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .client-deliverables-page {
    margin-top: 80px;
    padding: 0 16px;
  }
  
  .page-header {
    padding: 24px;
  }
  
  .header-main {
    flex-direction: column;
    gap: 16px;
  }
  
  .header-actions {
    align-items: flex-start;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .search-filter {
    flex-direction: column;
  }
  
  .sort-select {
    width: 100%;
  }
  
  .table-header {
    display: none;
  }
  
  .row-main {
    flex-direction: column;
    gap: 16px;
  }
  
  .row-content {
    width: 100%;
    padding: 0;
  }
  
  .actions-cell {
    justify-content: flex-start;
  }
  
  .sidebar-panel {
    position: fixed;
    top: auto;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    border-radius: 20px 20px 0 0;
  }
  
  .modal {
    max-width: 100%;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .modal-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .dashboard-cards {
    grid-template-columns: 1fr;
  }
  
  .status-filters {
    justify-content: center;
  }
  
  .status-filter-btn {
    flex: 1;
    justify-content: center;
    min-width: 0;
  }
  
  .action-buttons {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>