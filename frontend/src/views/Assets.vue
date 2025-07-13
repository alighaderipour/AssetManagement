<template>
  <div class="assets">
    <!-- Success & Error Messages -->
    <div v-if="successMessage" class="success-msg">{{ successMessage }}</div>
    <div v-if="errorMessage" class="error-msg">{{ errorMessage }}</div>

    <!-- Asset Management Header -->
    <div class="assets-header">
      <router-link to="/assets/add" class="add-btn">اضافه کردن کالای جدید</router-link>
      <h1>مدیریت کالاها</h1>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <input
          type="text"
          v-model="filters.search"
          placeholder=" جستجوی کالا ..."
          @input="debouncedSearch"
        />
      </div>
      <div class="filter-group">
        <select v-model="filters.department" @change="applyFilters">
          <option value="">بخش ها</option>
          <option v-for="dept in departments" :key="dept.id" :value="dept.id">
            {{ dept.name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <select v-model="filters.category" @change="applyFilters">
          <option value="">دسته بندی ها</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Assets Grid -->
    <div v-if="loading" class="loading">Loading assets...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="assets-grid">
      <div
        v-for="asset in assets"
        :key="asset.id"
        class="assets-card"
        @click="viewAsset(asset.id)"
      >
        <div class="asset-info">
          <div class="asset-header">
            <h3 class="asset-name">{{ asset.name }}</h3>
            <span class="asset-status" :class="asset.status">
              {{ getStatusLabel(asset.status) }}
            </span>
          </div>
          <div class="asset-details">
            <div class="detail-item">
              <span class="detail-icon">🏷️</span>
              <span class="detail-label">کد کالا:</span>
              <span class="asset-code">{{ asset.asset_code }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-icon">📦</span>
              <span class="detail-label">دسته‌بندی:</span>
              <span class="detail-value">{{ asset.category_name }}</span>
            </div>
            <div class="detail-item" v-if="asset.current_department_name">
              <span class="detail-icon">🏢</span>
              <span class="detail-label">بخش فعلی:</span>
              <span class="detail-value department-info">
                {{ asset.current_department_name }}
                <span class="department-code">{{ asset.current_department_code }}</span>
              </span>
            </div>
            <div class="detail-item cost-item">
              <span class="detail-icon">💰</span>
              <span class="detail-label">جمع هزینه انتقال:</span>
              <span class="cost-value">
                {{ asset.total_transfer_cost ? Number(asset.total_transfer_cost).toLocaleString() : '۰' }}
                <span class="currency">ریال</span>
              </span>
            </div>
          </div>
        </div>
        <div class="asset-actions">
          <button @click.stop="transferAsset(asset)" class="transfer-btn">انتقال</button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination-controls">
      <button @click="changePage(page - 1)" :disabled="page === 1">«</button>
      <span>صفحه {{ page }} از {{ totalPages }}</span>
      <button @click="changePage(page + 1)" :disabled="page === totalPages">»</button>
    </div>

    <!-- Transfer Modal -->
    <div v-if="showTransferModal" class="modal-overlay" @click.self="closeTransferModal">
      <div class="modal">
        <h2>انتقال "{{ selectedAsset?.name }}"</h2>

        <div class="form-group">
          <label for="to_department">بخش مقصد</label>
          <select v-model="transferForm.to_department" id="to_department" required>
            <option disabled value="">انتخاب بخش</option>
            <option v-for="dept in departments" :key="dept.id" :value="dept.id">
              {{ dept.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="reason">دلیل انتقال</label>
          <input type="text" id="reason" v-model="transferForm.reason" />
        </div>

        <div class="form-group">
          <label for="notes">یادداشت</label>
          <textarea id="notes" v-model="transferForm.notes"></textarea>
        </div>

        <div class="form-group">
          <label for="price">قیمت <span v-if="selectedAsset?.current_department_type === 'maintenance'" style="color:red;">*</span></label>
          <input
            type="number"
            id="price"
            v-model="transferForm.price"
            min="0"
            step="1000000"
            placeholder="قیمت انتقال"
          />
          <div v-if="fieldErrors.price" class="field-error">{{ fieldErrors.price }}</div>
        </div>

        <div class="form-group">
          <label for="image">تصویر فاکتور <span v-if="selectedAsset?.current_department_type === 'maintenance'" style="color:red;">*</span></label>
          <input
            type="file"
            id="image"
            accept="image/*"
            @change="onImageChange"
          />
          <div v-if="fieldErrors.image" class="field-error">{{ fieldErrors.image }}</div>
        </div>

        <div class="modal-actions">

          <button type="button" class="submit-btn" :disabled="transferring" @click="submitTransfer">
            {{ transferring ? 'در حال انتقال...' : 'ثبت انتقال' }}
          </button>
          <button type="button" @click="closeTransferModal">لغو</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAssetsStore } from '@/stores/assets'

const router = useRouter()
const assetsStore = useAssetsStore()

const page = ref(1)
const pageSize = 6
const count = computed(() => assetsStore.count ?? 0)
const assets = computed(() => assetsStore.assets)
const departments = computed(() => assetsStore.departments)
const categories = computed(() => assetsStore.categories)
const loading = computed(() => assetsStore.loading)
const error = computed(() => assetsStore.error)
const totalPages = computed(() => Math.max(1, Math.ceil(count.value / pageSize)))

const filters = ref({ search: '', department: '', category: '' })
const showTransferModal = ref(false)
const selectedAsset = ref(null)
const transferForm = ref({ to_department: '', reason: '', notes: '', price: '', image: null })
const transferring = ref(false)
const fieldErrors = ref({ price: '', image: '' })
const successMessage = ref('')
const errorMessage = ref('')

const showSuccessMessage = (msg) => {
  successMessage.value = msg
  setTimeout(() => (successMessage.value = ''), 3000)
}
const showErrorMessage = (msg) => {
  errorMessage.value = msg
  setTimeout(() => (errorMessage.value = ''), 3000)
}

let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => applyFilters(), 300)
}
const applyFilters = () => {
  page.value = 1
  fetchPage()
}
const getStatusLabel = (status) => {
  const labels = {
    active: 'فعال',
    inactive: 'غیرفعال',
    under_maintenance: 'تعمیر',
    disposed: 'خارج از خدمت'
  }
  return labels[status] || status
}
const fetchPage = async () => {
  await assetsStore.fetchAssets({
    search: filters.value.search,
    department: filters.value.department,
    category: filters.value.category,
    page: page.value,
    page_size: pageSize,
  })
}
const changePage = (newPage) => {
  if (newPage < 1 || newPage > totalPages.value) return
  page.value = newPage
  fetchPage()
}
const viewAsset = (id) => router.push(`/assets/${id}/edit`)
const transferAsset = (asset) => {
  selectedAsset.value = asset
  transferForm.value = { to_department: '', reason: '', notes: '', price: '', image: null }
  fieldErrors.value = { price: '', image: '' }
  showTransferModal.value = true
}
const closeTransferModal = () => {
  showTransferModal.value = false
  selectedAsset.value = null
}
const onImageChange = (event) => {
  transferForm.value.image = event.target.files[0] || null
}

const submitTransfer = async () => {
  if (!transferForm.value.to_department) {
    showErrorMessage('بخش مقصد را انتخاب کنید.')
    return
  }

  const isMaintenanceDept = selectedAsset.value?.current_department_type === 'maintenance'
  fieldErrors.value = { price: '', image: '' }
  if (isMaintenanceDept) {
    let hasError = false
    if (!transferForm.value.price || transferForm.value.price <= 0) {
      fieldErrors.value.price = 'وارد کردن مبلغ انتقال الزامی است.'
      hasError = true
    }
    if (!transferForm.value.image) {
      fieldErrors.value.image = 'وارد کردن تصویر فاکتور الزامی است.'
      hasError = true
    }
    if (hasError) return
  }

  transferring.value = true
  try {
    const formData = new FormData()
    formData.append('department', transferForm.value.to_department)
    formData.append('notes', transferForm.value.notes || '')
    formData.append('price', transferForm.value.price || '')
    if (transferForm.value.image) formData.append('image', transferForm.value.image)
    if (transferForm.value.reason) formData.append('reason', transferForm.value.reason)

    await assetsStore.transferAssetWithFormData(selectedAsset.value.id, formData)
    closeTransferModal()
    showSuccessMessage('انتقال با موفقیت انجام شد')
    fetchPage()
    if (assetsStore.fetchTransfers) await assetsStore.fetchTransfers()
  } catch (err) {
    showErrorMessage('خطا در انتقال. ' + (err?.message || 'لطفاً دوباره تلاش کنید.'))
  } finally {
    transferring.value = false
  }
}

onMounted(async () => {
  await assetsStore.fetchDepartments()
  await assetsStore.fetchCategories()
  fetchPage()
})
</script>


<style scoped>
.field-error {
  color: #e53e3e;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}
.assets {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}
.success-msg {
  background: #e6ffe6;
  color: #22543d;
  border: 1px solid #38a169;
  border-radius: 4px;
  padding: 0.75rem;
  margin-bottom: 1.5rem;
  text-align: center;
  font-weight: 500;
}
.error-msg {
  background: #fff6f6;
  color: #c53030;
  border: 1px solid #e53e3e;
  border-radius: 4px;
  padding: 0.75rem;
  margin-bottom: 1.5rem;
  text-align: center;
  font-weight: 500;
}
.assets-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.add-btn {
  background: #38b2ac;
  color: white;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  transition: background 0.2s;
}
.add-btn:hover {
  background: #319795;
}
.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}
.filter-group {
  flex: 1;
  min-width: 200px;
}
.filter-group input,
.filter-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.loading,
.error {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
}
.error {
  color: #e53e3e;
}
.assets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  direction: rtl;
}
.assets-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
}
.assets-card:hover {
  transform: translateY(-2px);
}
.assets-info {
  padding: 1rem;
}
.assets-info h3 {
  margin: 0 0 0.5rem 0;
  color: #2d3748;
}
.assets-code {
  font-family: monospace;
  background: #edf2f7;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.9rem;
  display: inline-block;
  margin-bottom: 0.5rem;
}
.asset-department,
.asset-category {
  color: #718096;
  font-size: 0.9rem;
  margin: 0.25rem 0;
}
.asset-status {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}
.asset-status.active {
  background: #c6f6d5;
  color: #22543d;
}
.asset-status.inactive {
  background: #fed7d7;
  color: #742a2a;
}
.asset-status.maintenance {
  background: #feebc8;
  color: #c05621;
}
.asset-actions {
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
}
.transfer-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
}
.transfer-btn:hover {
  background: #5a67d8;
}
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
.modal {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
   direction: rtl;
  text-align: right;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}
.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.form-group textarea {
  height: 80px;
  resize: vertical;
}
.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}
.modal-actions button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
modal-actions .submit-btn {
  background: #23b682;
  color: #fff;
}
/* دکمه لغو: خاکستری روشن */
.modal-actions button:not(.submit-btn) {
  background: #ececec;
  color: #868686;
}

/* حالت disabled روی دکمه ثبت انتقال */
.modal-actions .submit-btn:disabled {
  background: #9fdac4;
  color: #eee;
  cursor: wait;
}

@media (max-width: 768px) {
  .assets {
    padding: 1rem;
  }
  .filters {
    flex-direction: column;
  }
  .filter-group {
    min-width: unset;
  }
  .assets-grid {
    grid-template-columns: 1fr;
  }
}
.pagination {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  justify-content: center;
  margin: 1.5rem 0;
}
.page-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: #e2e8f0;
  cursor: pointer;
  border-radius: 4px;
}
.page-btn.active {
  background: #667eea;
  color: white;
  font-weight: bold;
}
.pagination button[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}
.pagination-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.25rem;
  margin-top: 2rem;
}
.pagination-controls button {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.5rem 1.15rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 1.1rem;
  font-weight: 500;
}
.pagination-controls button[disabled] {
  opacity: 0.55;
  cursor: not-allowed;
  background: #cbd5e1;
  color: #333;
}
.filter-group input {
  direction: rtl;
  text-align: right;
}
.filter-group select {
  direction: rtl;
  text-align: right;
  /* ظاهر فارسی‌تر و هماهنگی با placeholder input */
  padding-right: 8px; /* کمی فاصله برای زیبایی */
}

.filter-group option {
  direction: rtl;
  text-align: right;
}
.asset-info {
  padding: 1.25rem;
}

.asset-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 0.75rem;
  flex-direction: row-reverse;
}

.asset-header .asset-name {
  flex: 1;
  text-align: right;
}
.asset-header .asset-status {
  flex-shrink: 0; /* تا این یکی کوچک نشه */
}
.asset-name {
  margin: 0;
  color: #1e293b;
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.4;
  flex: 1;
}

.asset-status {
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  white-space: nowrap;
  flex-shrink: 0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.asset-status.active {
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
  color: #155724;
  border: 1px solid #c3e6cb;
}

.asset-status.inactive {
  background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.asset-status.maintenance {
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  color: #856404;
  border: 1px solid #ffeaa7;
}

.asset-status.retired {
  background: linear-gradient(135deg, #e2e3e5 0%, #d6d8db 100%);
  color: #383d41;
  border: 1px solid #d6d8db;
}

.asset-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.detail-item:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.detail-icon {
  font-size: 1rem;
  min-width: 20px;
  text-align: center;
}

.detail-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
  min-width: 80px;
}

.detail-value {
  font-size: 0.875rem;
  color: #334155;
  font-weight: 400;
  flex: 1;
}

.asset-code {
  font-family: 'Courier New', monospace;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #3730a3;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid #c7d2fe;
  flex: 1;
}

.department-info {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.department-code {
  background: #f1f5f9;
  color: #64748b;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.cost-item {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-color: #bbf7d0;
}

.cost-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #166534;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex: 1;
  justify-content: flex-end;
}

.currency {
  font-size: 0.75rem;
  color: #059669;
  font-weight: 500;
}

/* بهبود استایل کارت کلی */
.assets-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e2e8f0;
}

.assets-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: #cbd5e1;
}

.asset-actions {
  padding: 1rem 1.25rem;
  border-top: 1px solid #f1f5f9;
  background: #fafbfc;
}

.transfer-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  width: 100%;
  font-weight: 500;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
}

.transfer-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .asset-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .asset-status {
    align-self: flex-start;
  }

  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .detail-label {
    min-width: auto;
    font-size: 0.8rem;
  }

  .cost-value {
    justify-content: flex-start;
  }
}
</style>
