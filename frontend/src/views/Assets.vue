<template>
  <div class="assets">
    <!-- Success & Error Messages -->
    <div v-if="successMessage" class="success-msg">{{ successMessage }}</div>
    <div v-if="errorMessage" class="error-msg">{{ errorMessage }}</div>

    <div class="assets-header">
      <h1>Assets Management</h1>
      <router-link to="/assets/add" class="add-btn">Add New Asset</router-link>
    </div>

    <div class="filters">
      <!-- ... filters exactly as you had ... -->
      <div class="filter-group">
        <input
          type="text"
          v-model="filters.search"
          placeholder="Search assets..."
          @input="debouncedSearch"
        />
      </div>
      <div class="filter-group">
        <select v-model="filters.department" @change="applyFilters">
          <option value="">All Departments</option>
          <option v-for="dept in departments" :key="dept.id" :value="dept.id">
            {{ dept.name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <select v-model="filters.category" @change="applyFilters">
          <option value="">All Categories</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading assets...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="assets-grid">
      <div
        v-for="asset in assets"
        :key="asset.id"
        class="assets-card"
        @click="viewAsset(asset.id)"
      >
        <!-- ... card markup as you have ... -->
        <div class="asset-info">
          <h3>{{ asset.name }}</h3>
          <p class="asset-code">{{ asset.asset_code }}</p>
          <p class="asset-category">{{ asset.category_name }}</p>
          <p class="asset-current-department" v-if="asset.current_department_name">
            <b>Current Department:</b> {{ asset.current_department_name }} {{ asset.current_department_code }}
          </p>
          <span class="asset-status" :class="asset.status">
            {{ asset.status }}
          </span>
        </div>
        <div class="asset-actions">
          <button @click.stop="transferAsset(asset)" class="transfer-btn">
            Transfer
          </button>
        </div>
      </div>
    </div>

    <!-- PAGINATION: controls below the grid -->
    <div v-if="totalPages > 1" class="pagination-controls">
      <button @click="changePage(page - 1)" :disabled="page === 1">«</button>
      <span>Page {{ page }} of {{ totalPages }}</span>
      <button @click="changePage(page + 1)" :disabled="page === totalPages">»</button>
    </div>

    <!-- Transfer Modal ... no changes ... -->
    <div v-if="showTransferModal" class="modal-overlay" @click="closeTransferModal">
  <div class="modal" @click.stop>
    <h2>Transfer "{{ selectedAsset?.name }}"</h2>

    <div class="form-group">
      <label for="to_department">Transfer To Department</label>
      <select v-model="transferForm.to_department" id="to_department">
        <option value="">Select Department</option>
        <option v-for="dept in departments" :key="dept.id" :value="dept.id">
          {{ dept.name }}
        </option>
      </select>
    </div>

    <div class="form-group">
      <label for="reason">Reason</label>
      <input type="text" id="reason" v-model="transferForm.reason" />
    </div>

    <div class="form-group">
      <label for="notes">Notes</label>
      <textarea id="notes" v-model="transferForm.notes"></textarea>
    </div>

    <div class="modal-actions">
      <button @click="closeTransferModal">Cancel</button>
      <button :disabled="transferring" @click="submitTransfer">
        {{ transferring ? 'Transferring...' : 'Submit Transfer' }}
      </button>
    </div>
  </div>
</div>


  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAssetsStore } from '@/stores/assets'

// STATE
const router = useRouter()
const assetsStore = useAssetsStore()

// PAGINATION STATE
const page = ref(1)
const pageSize = 6 // 🔴 show 6 assets per page

const count = computed(() => assetsStore.count ?? 0)
const assets = computed(() => assetsStore.assets)
const departments = computed(() => assetsStore.departments)
const categories = computed(() => assetsStore.categories)
const loading = computed(() => assetsStore.loading)
const error = computed(() => assetsStore.error)

const totalPages = computed(() => Math.max(1, Math.ceil(count.value / pageSize)))

// FILTER STATE
const filters = ref({
  search: '',
  department: '',
  category: ''
})

// MODAL/TRANSFER STATE (exactly as you had)
const showTransferModal = ref(false)
const selectedAsset = ref(null)
const transferForm = ref({
  to_department: '',
  reason: '',
  notes: ''
})
const transferring = ref(false)

// SUCCESS/ERROR MESSAGE
const successMessage = ref("");
const errorMessage = ref("");
function showSuccessMessage(msg) {
  successMessage.value = msg;
  setTimeout(() => successMessage.value = "", 3000);
}
function showErrorMessage(msg) {
  errorMessage.value = msg;
  setTimeout(() => errorMessage.value = "", 3000);
}

// Debounced search
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => applyFilters(), 300)
}

const applyFilters = () => {
  page.value = 1 // Reset to page 1 on filter change!
  fetchPage()
}

// Fetch assets for the current page and filters
const fetchPage = async () => {
  await assetsStore.fetchAssets({
    search: filters.value.search,
    department: filters.value.department,
    category: filters.value.category,
    page: page.value,
    page_size: pageSize,
  })
}

// Pagination change handler
const changePage = (newPage) => {
  if (newPage < 1 || newPage > totalPages.value) return
  page.value = newPage
  fetchPage()
}

// Card action handlers (no change)
const viewAsset = (id) => {
  router.push(`/assets/${id}/edit`)
}
const transferAsset = (asset) => {
  selectedAsset.value = asset
  transferForm.value = {
    to_department: '',
    reason: '',
    notes: ''
  }
  showTransferModal.value = true
}
const closeTransferModal = () => {
  showTransferModal.value = false
  selectedAsset.value = null
}
const submitTransfer = async () => {
  transferring.value = true;
  try {
    await assetsStore.transferAsset(
      selectedAsset.value.id,
      transferForm.value.to_department,
      transferForm.value.notes
    );
    closeTransferModal();
    showSuccessMessage("Transfer successful!");
    fetchPage();
    if (assetsStore.fetchTransfers) await assetsStore.fetchTransfers()
  } catch (err) {
    showErrorMessage("Transfer failed. Please try again.");
  } finally {
    transferring.value = false;
  }
};

onMounted(async () => {
  await assetsStore.fetchDepartments()
  await assetsStore.fetchCategories()
  fetchPage()
})
</script>


<style scoped>
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
.modal-actions button:first-child {
  background: #e2e8f0;
  color: #2d3748;
}
.modal-actions button:last-child {
  background: #667eea;
  color: white;
}
.modal-actions button:disabled {
  background: #a0aec0;
  cursor: not-allowed;
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
</style>
