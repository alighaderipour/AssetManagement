<template>
  <div class="recent-transfers">
    <div class="section-header">
      <h3>انتقالات اخیر</h3>
      <router-link to="/transfers" class="view-all-link">مشاهده همه انتقالات</router-link>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>در حال بارگذاری انتقالات...</span>
    </div>

    <div v-else-if="error" class="error-message">
      <span>{{ error }}</span>
      <button @click="fetchTransfers" class="retry-btn">تلاش مجدد</button>
    </div>

    <div v-else-if="transfers.length === 0" class="no-transfers">
      <div class="no-data-icon">📦</div>
      <p>هیچ انتقال اخیری یافت نشد</p>
    </div>

    <div v-else class="transfers-list">
      <div
        v-for="transfer in displayedTransfers"
        :key="transfer.id"
        class="transfer-item"
        @click="viewTransferDetails(transfer)"
      >
        <div class="transfer-main">
          <div class="asset-info">
            <h4 class="asset-name">{{ transfer.asset_name || 'دارایی نامعلوم' }}</h4>
            <span class="asset-code">{{ transfer.asset_code || 'ندارد' }}</span>
          </div>

          <div class="transfer-direction">
            <div class="department from-dept">
              <span class="dept-label">از:</span>
              <span class="dept-name">{{ transfer.from_department_name || 'نامعلوم' }}</span>
            </div>
            <div class="arrow">←</div>
            <div class="department to-dept">
              <span class="dept-label">به:</span>
              <span class="dept-name">{{ transfer.to_department_name || 'نامعلوم' }}</span>
            </div>
          </div>
        </div>

        <div class="transfer-meta">
          <div class="transfer-date">
            <span class="date-icon">📅</span>
            <span>{{ formatDate(transfer.transfer_date) }}</span>
          </div>

          <div v-if="transfer.transferred_by_name" class="transferred-by">
            <span class="user-icon">👤</span>
            <span>{{ transfer.transferred_by_name }}</span>
          </div>

          <div v-if="transfer.price" class="transfer-price">
            <span class="price-icon">💰</span>
            <span>{{ Number(transfer.price).toLocaleString() }} ریال</span>
          </div>
        </div>

        <div v-if="transfer.notes" class="transfer-notes">
          <span class="notes-icon">💬</span>
          <span class="notes-text">{{ truncateText(transfer.notes, 80) }}</span>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div v-if="transfers.length > 0" class="quick-actions">
      <router-link to="/transfers" class="action-btn view-all">
        مشاهده همه
      </router-link>
      <router-link to="/assets" class="action-btn add-new">
        + انتقال جدید
      </router-link>
    </div>

    <!-- Transfer Details Modal (Simple) -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>جزئیات انتقال</h3>
          <button @click="closeModal" class="modal-close">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedTransfer" class="transfer-details">
            <div class="detail-item">
              <span class="label">دارایی:</span>
              <span class="value">{{ selectedTransfer.asset_name }} ({{ selectedTransfer.asset_code }})</span>
            </div>
            <div class="detail-item">
              <span class="label">از بخش:</span>
              <span class="value">{{ selectedTransfer.from_department_name }}</span>
            </div>
            <div class="detail-item">
              <span class="label">به بخش:</span>
              <span class="value">{{ selectedTransfer.to_department_name }}</span>
            </div>
            <div class="detail-item">
              <span class="label">تاریخ:</span>
              <span class="value">{{ formatFullDate(selectedTransfer.transfer_date) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">انتقال دهنده:</span>
              <span class="value">{{ selectedTransfer.transferred_by_name }}</span>
            </div>
            <div v-if="selectedTransfer.price" class="detail-item">
              <span class="label">قیمت:</span>
              <span class="value">{{ Number(selectedTransfer.price).toLocaleString() }} تومان</span>
            </div>
            <div v-if="selectedTransfer.notes" class="detail-item">
              <span class="label">یادداشت:</span>
              <span class="value">{{ selectedTransfer.notes }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <router-link :to="`/transfers/${selectedTransfer.id}`" class="btn-primary">
            مشاهده کامل
          </router-link>
          <button @click="closeModal" class="btn-secondary">بستن</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import jalaali from 'jalaali-js'

// Persian Date Functions
const toJalali = (dateString) => {
  if (!dateString) return 'تاریخ نامعتبر'

  try {
    const date = new Date(dateString)
    const j = jalaali.toJalaali(date)
    return `${j.jy}/${j.jm.toString().padStart(2, '0')}/${j.jd.toString().padStart(2, '0')}`
  } catch (error) {
    return 'تاریخ نامعتبر'
  }
}

const toJalaliWithTime = (dateString) => {
  if (!dateString) return 'تاریخ نامعتبر'

  try {
    const date = new Date(dateString)
    const j = jalaali.toJalaali(date)
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    return `${j.jy}/${j.jm.toString().padStart(2, '0')}/${j.jd.toString().padStart(2, '0')} - ${hours}:${minutes}`
  } catch (error) {
    return 'تاریخ نامعتبر'
  }
}

// Props
const props = defineProps({
  maxItems: {
    type: Number,
    default: 5
  }
})

// Reactive data
const authStore = useAuthStore()
const transfers = ref([])
const loading = ref(false)
const error = ref(null)
const showModal = ref(false)
const selectedTransfer = ref(null)

// Computed
const displayedTransfers = computed(() => {
  return transfers.value.slice(0, props.maxItems)
})

// Methods
const fetchTransfers = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await fetch('http://localhost:8000/api/transfers/?limit=20', {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()

    // Sort by transfer_date descending (most recent first)
    transfers.value = (data.results || data).sort((a, b) => {
      return new Date(b.transfer_date) - new Date(a.transfer_date)
    })

    console.log('✅ Recent transfers loaded:', transfers.value.length)

  } catch (err) {
    console.error('❌ Error fetching transfers:', err)
    error.value = 'خطا در بارگذاری انتقالات اخیر'
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'تاریخ نامعلوم'
  return toJalali(dateString)
}

const formatFullDate = (dateString) => {
  if (!dateString) return 'تاریخ نامعلوم'
  return toJalaliWithTime(dateString)
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const viewTransferDetails = (transfer) => {
  selectedTransfer.value = transfer
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedTransfer.value = null
}

// Lifecycle
onMounted(() => {
  fetchTransfers()
})
</script>

<style scoped>
.recent-transfers {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  direction: rtl;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.section-header h3 {
  margin: 0;
  color: #1e293b;
  font-size: 18px;
  font-weight: 600;
}

.view-all-link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s ease;
}

.view-all-link:hover {
  color: #2563eb;
}

/* Loading State */
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: #64748b;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error State */
.error-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  color: #dc2626;
  text-align: center;
}

.retry-btn {
  background: #dc2626;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.2s ease;
}

.retry-btn:hover {
  background: #b91c1c;
}

/* No Data State */
.no-transfers {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}

.no-data-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.no-transfers p {
  margin: 0;
  font-style: italic;
}

/* Transfers List */
.transfers-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.transfer-item {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s ease;
  cursor: pointer;
}

.transfer-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
  transform: translateY(-1px);
}

.transfer-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  gap: 1rem;
}

.asset-info {
  flex: 1;
}

.asset-name {
  margin: 0 0 0.25rem 0;
  color: #1e293b;
  font-size: 16px;
  font-weight: 600;
}

.asset-code {
  color: #64748b;
  font-size: 12px;
  background: #f1f5f9;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}

.transfer-direction {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 2;
}

.department {
  text-align: center;
  min-width: 0;
  flex: 1;
}

.dept-label {
  display: block;
  font-size: 10px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.25rem;
}

.dept-name {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  word-wrap: break-word;
}

.from-dept .dept-name {
  color: #dc2626;
}

.to-dept .dept-name {
  color: #059669;
}

.arrow {
  color: #3b82f6;
  font-weight: bold;
  font-size: 16px;
  flex-shrink: 0;
}

.transfer-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.transfer-date,
.transferred-by,
.transfer-price {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  white-space: nowrap;
}

.date-icon,
.user-icon,
.price-icon {
  font-size: 12px;
}

.transfer-price {
  color: #059669;
  font-weight: 500;
}

.transfer-notes {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 12px;
  color: #64748b;
  background: #f8fafc;
  padding: 0.5rem;
  border-radius: 4px;
  margin-top: 0.5rem;
}

.notes-icon {
  font-size: 12px;
  margin-top: 2px;
  flex-shrink: 0;
}

.notes-text {
  line-height: 1.4;
}

/* Quick Actions */
.quick-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
  flex: 1;
  text-align: center;
}

.view-all {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.view-all:hover {
  background: #e2e8f0;
  color: #334155;
}

.add-new {
  background: #3b82f6;
  color: white;
  border: 1px solid #3b82f6;
}

.add-new:hover {
  background: #2563eb;
  border-color: #2563eb;
}

/* Modal Styles */
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
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0.25rem;
  border-radius: 4px;
}

.modal-close:hover {
  color: #374151;
  background: #f3f4f6;
}

.modal-body {
  padding: 1.5rem;
}

.transfer-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item .label {
  font-weight: 500;
  color: #374151;
  min-width: 80px;
  flex-shrink: 0;
}

.detail-item .value {
  color: #1f2937;
  text-align: left;
  word-break: break-word;
}

.modal-footer {
  display: flex;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn-primary, .btn-secondary {
  flex: 1;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  text-align: center;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

/* Responsive Design */
@media (max-width: 768px) {
  .recent-transfers {
    padding: 1rem;
  }

  .transfer-main {
    flex-direction: column;
    align-items: stretch;
  }

  .transfer-direction {
    justify-content: space-between;
    margin-top: 0.75rem;
  }

  .transfer-meta {
    gap: 0.5rem;
  }

  .quick-actions {
    flex-direction: column;
  }

  .modal-content {
    margin: 1rem;
    max-width: none;
  }
}

@media (max-width: 480px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .transfer-direction {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }

  .arrow {
    transform: rotate(90deg);
  }

  .detail-item {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .detail-item .value {
    text-align: right;
  }
}
</style>
