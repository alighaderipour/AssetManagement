<template>
  <div class="all-transfers">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">تمام انتقال‌های دارایی</h1>
        <p class="page-subtitle">مدیریت و پیگیری انتقال دارایی بین بخش‌ها</p>
      </div>
      <div class="header-actions">
        <router-link to="/assets" class="btn btn-primary">
          <span class="btn-icon">➕</span>
          انتقال جدید
        </router-link>
      </div>
    </div>

    <!-- Filters & Controls -->
    <div class="controls-section">
      <div class="filters-row">
        <!-- Search -->
        <div class="search-group">
          <div class="search-input-wrapper">
            <span class="search-icon">🔍</span>
            <input
              v-model="searchQuery"
              type="search"
              placeholder="جستجو بر اساس نام دارایی، کد، یا یادداشت..."
              class="search-input"
              @input="debouncedSearch"
            />
            <button
              v-if="searchQuery"
              @click="clearSearch"
              class="clear-search-btn"
              title="پاک کردن جستجو"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Department Filters -->
        <div class="filter-group">
          <label class="filter-label">از بخش:</label>
          <select v-model="filters.fromDepartment" class="filter-select">
            <option value="">تمام بخش‌ها</option>
            <option v-for="dept in departments" :key="dept.id" :value="dept.id">
              {{ dept.name }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">به بخش:</label>
          <select v-model="filters.toDepartment" class="filter-select">
            <option value="">تمام بخش‌ها</option>
            <option v-for="dept in departments" :key="dept.id" :value="dept.id">
              {{ dept.name }}
            </option>
          </select>
        </div>

        <!-- Persian Date Range - اصلاح شده -->
        <div class="filter-group">
          <label class="filter-label">از تاریخ:</label>
          <DatePicker
            v-model="filters.dateFrom"
            format="YYYY-MM-DD"
            display-format="jYYYY/jMM/jDD"
            :editable="false"
            :clearable="true"
            :auto-submit="true"
            color="#3b82f6"
            class="date-input-persian"
            placeholder="انتخاب تاریخ"
          />
        </div>

        <div class="filter-group">
          <label class="filter-label">تا تاریخ:</label>
          <DatePicker
            v-model="filters.dateTo"
            format="YYYY-MM-DD"
            display-format="jYYYY/jMM/jDD"
            :editable="false"
            :clearable="true"
            :auto-submit="true"
            color="#3b82f6"
            class="date-input-persian"
            placeholder="انتخاب تاریخ"
          />
        </div>

        <!-- Clear Filters -->
        <button
          @click="clearAllFilters"
          class="btn btn-outline"
          :disabled="!hasActiveFilters"
        >
          پاک کردن فیلترها
        </button>
      </div>

      <!-- Results Summary & Sort -->
      <div class="results-row">
        <div class="results-info">
          <span class="results-count">
            {{ filteredTransfers.length }} از {{ allTransfers.length }} انتقال
          </span>
          <span v-if="hasActiveFilters" class="filter-indicator">
            (فیلتر شده)
          </span>
        </div>

        <div class="sort-controls">
          <label class="sort-label">مرتب‌سازی بر اساس:</label>
          <select v-model="sortBy" class="sort-select">
            <option value="transfer_date">تاریخ انتقال</option>
            <option value="asset_name">نام دارایی</option>
            <option value="from_department_name">از بخش</option>
            <option value="to_department_name">به بخش</option>
            <option value="transferred_by_name">انتقال دهنده</option>
            <option value="price">قیمت</option>
          </select>
          <button
            @click="toggleSortOrder"
            class="sort-order-btn"
            :title="sortOrder === 'desc' ? 'مرتب‌سازی صعودی' : 'مرتب‌سازی نزولی'"
          >
            {{ sortOrder === 'desc' ? '↓' : '↑' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <span>در حال بارگذاری انتقال‌ها...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h3>خطا در بارگذاری انتقال‌ها</h3>
      <p>{{ error }}</p>
      <button @click="fetchTransfers" class="btn btn-primary">
        تلاش مجدد
      </button>
    </div>

    <!-- Empty State -->
    <div v-else-if="allTransfers.length === 0" class="empty-container">
      <div class="empty-icon">📦</div>
      <h3>هیچ انتقالی یافت نشد</h3>
      <p>هنوز هیچ انتقال داراییی ثبت نشده است.</p>
      <router-link to="/transfers/add" class="btn btn-primary">
        ایجاد اولین انتقال
      </router-link>
    </div>

    <!-- No Results State -->
    <div v-else-if="filteredTransfers.length === 0" class="empty-container">
      <div class="empty-icon">🔍</div>
      <h3>هیچ انتقال مطابقی یافت نشد</h3>
      <p>فیلترها یا عبارت جستجو را تغییر دهید.</p>
      <button @click="clearAllFilters" class="btn btn-outline">
        پاک کردن تمام فیلترها
      </button>
    </div>

    <!-- Transfers Table -->
    <div v-else class="table-container">
      <div class="table-wrapper">
        <table class="transfers-table">
          <thead>
            <tr>
              <th class="col-asset">دارایی</th>
              <th class="col-transfer">جهت انتقال</th>
              <th class="col-date">تاریخ</th>
              <th class="col-user">انتقال دهنده</th>
              <th class="col-notes">یادداشت</th>
              <th class="col-price">قیمت</th>
              <th class="col-image">فاکتور/تصویر</th>
              <th class="col-actions">عملیات</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="transfer in paginatedTransfers"
              :key="transfer.id"
              class="transfer-row"
            >
              <!-- Asset Info -->
              <td class="col-asset">
                <div class="asset-info">
                  <div class="asset-name">{{ transfer.asset_name || 'دارایی نامعلوم' }}</div>
                  <div class="asset-code">{{ transfer.asset_code || 'ندارد' }}</div>
                </div>
              </td>

              <!-- Transfer Direction -->
              <td class="col-transfer">
                <div class="transfer-direction">
                  <div class="dept-from">
                    <span class="dept-label">از:</span>
                    <span class="dept-name">{{ transfer.from_department_name || 'نامعلوم' }}</span>
                  </div>
                  <div class="arrow">←</div>
                  <div class="dept-to">
                    <span class="dept-label">به:</span>
                    <span class="dept-name">{{ transfer.to_department_name || 'نامعلوم' }}</span>
                  </div>
                </div>
              </td>

              <!-- Transfer Date -->
              <td class="col-date">
                <div class="date-info">
                  <div class="date-main">{{ formatDate(transfer.transfer_date) }}</div>
                  <div class="date-time">{{ formatTime(transfer.transfer_date) }}</div>
                </div>
              </td>

              <!-- Transferred By -->
              <td class="col-user">
                <div class="user-info">
                  <span class="user-icon">👤</span>
                  <span class="user-name">{{ transfer.transferred_by_name || 'نامعلوم' }}</span>
                </div>
              </td>

              <!-- Notes -->
              <td class="col-notes">
                <div class="notes-content">
                  <span v-if="transfer.notes" class="notes-text" :title="transfer.notes">
                    {{ truncateText(transfer.notes, 50) }}
                  </span>
                  <span v-else class="no-notes">—</span>
                </div>
              </td>

              <!-- Price -->
              <td class="col-price">
                <span v-if="transfer.price">
                  {{ Number(transfer.price).toLocaleString() }} تومان
                </span>
                <span v-else>—</span>
              </td>

              <!-- Image (invoice/receipt) -->
              <td class="col-image">
                <span v-if="transfer.image">
                  <a :href="getTransferImageUrl(transfer.image)" target="_blank">
                    <img
                      :src="getTransferImageUrl(transfer.image)"
                      alt="فاکتور/تصویر"
                      style="height:36px;max-width:90px;object-fit:contain;"
                    />
                  </a>
                </span>
                <span v-else>—</span>
              </td>

              <!-- Actions -->
              <td class="col-actions">
                <div class="action-buttons">
                  <button
                    @click="viewTransferDetails(transfer)"
                    class="action-btn view-btn"
                    title="مشاهده جزئیات"
                  >
                    👁️
                  </button>
                  <button
                    @click="editTransfer(transfer)"
                    class="action-btn edit-btn"
                    title="ویرایش انتقال"
                  >
                    ✏️
                  </button>
                  <button
                    @click="deleteTransfer(transfer)"
                    class="action-btn delete-btn"
                    title="حذف انتقال"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination-container">
        <div class="pagination-info">
          نمایش {{ startIndex + 1 }}-{{ endIndex }} از {{ filteredTransfers.length }} انتقال
        </div>

        <div class="pagination-controls">
          <!-- Items per page -->
          <div class="per-page-control">
            <label class="per-page-label">نمایش:</label>
            <select v-model="itemsPerPage" class="per-page-select">
              <option :value="10">10</option>
              <option :value="25">25</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
            <span class="per-page-suffix">در صفحه</span>
          </div>

          <!-- Page Navigation -->
          <div class="page-navigation">
            <button
              @click="goToPage(1)"
              :disabled="currentPage === 1"
              class="page-btn"
              title="صفحه اول"
            >
              ⏮️
            </button>
            <button
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="page-btn"
              title="صفحه قبل"
            >
              ◀️
            </button>

            <div class="page-numbers">
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="goToPage(page)"
                :class="['page-number', { active: page === currentPage }]"
              >
                {{ page }}
              </button>
            </div>

            <button
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="page-btn"
              title="صفحه بعد"
            >
              ▶️
            </button>
            <button
              @click="goToPage(totalPages)"
              :disabled="currentPage === totalPages"
              class="page-btn"
              title="صفحه آخر"
            >
              ⏭️
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Transfer Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>جزئیات انتقال</h3>
          <button @click="closeDetailsModal" class="modal-close">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedTransfer" class="transfer-details">
            <div class="detail-row">
              <span class="detail-label">دارایی:</span>
              <span class="detail-value">{{ selectedTransfer.asset_name }} ({{ selectedTransfer.asset_code }})</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">از بخش:</span>
              <span class="detail-value">{{ selectedTransfer.from_department_name }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">به بخش:</span>
              <span class="detail-value">{{ selectedTransfer.to_department_name }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">تاریخ انتقال:</span>
              <span class="detail-value">{{ formatFullDate(selectedTransfer.transfer_date) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">انتقال دهنده:</span>
              <span class="detail-value">{{ selectedTransfer.transferred_by_name }}</span>
            </div>
            <div v-if="selectedTransfer.notes" class="detail-row">
              <span class="detail-label">یادداشت:</span>
              <span class="detail-value">{{ selectedTransfer.notes }}</span>
            </div>
            <!-- PRICE -->
            <div class="detail-row">
              <span class="detail-label">قیمت:</span>
              <span class="detail-value">
                <template v-if="selectedTransfer.price">
                  {{ Number(selectedTransfer.price).toLocaleString() }} تومان
                </template>
                <template v-else>—</template>
              </span>
            </div>
            <!-- IMAGE -->
            <div class="detail-row">
              <span class="detail-label">تصویر:</span>
              <span class="detail-value">
                <template v-if="selectedTransfer.image">
                  <a
                    :href="backendMediaUrl + selectedTransfer.image"
                    target="_blank"
                  >
                    <img
                      :src="backendMediaUrl + selectedTransfer.image"
                      alt="تصویر انتقال"
                      style="height:60px;max-width:140px;object-fit:contain;"
                    />
                  </a>
                </template>
                <template v-else>—</template>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import jalaali from 'jalaali-js'
import DatePicker from 'vue3-persian-datetime-picker'

// Stores
const authStore = useAuthStore()

// Data
const allTransfers = ref([])
const departments = ref([])
const loading = ref(false)
const error = ref(null)
const backendMediaUrl = "http://localhost:8000/media/"

// Search & Filters - اصلاح شده
const searchQuery = ref('')
const filters = ref({
  fromDepartment: '',
  toDepartment: '',
  dateFrom: '', // حالا رشته میلادی می‌شه
  dateTo: ''    // حالا رشته میلادی می‌شه
})

// Sorting
const sortBy = ref('transfer_date')
const sortOrder = ref('desc')

// Pagination
const currentPage = ref(1)
const itemsPerPage = ref(25)

// Modal
const showDetailsModal = ref(false)
const selectedTransfer = ref(null)

// Persian Date Utility Functions
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
    return `${j.jy}/${j.jm.toString().padStart(2, '0')}/${j.jd.toString().padStart(2, '0')} ${hours}:${minutes}`
  } catch (error) {
    return 'تاریخ نامعتبر'
  }
}

// Computed Properties
const hasActiveFilters = computed(() => {
  return searchQuery.value ||
         filters.value.fromDepartment ||
         filters.value.toDepartment ||
         filters.value.dateFrom ||
         filters.value.dateTo
})

const getTransferImageUrl = (img) => {
  if (!img) return ""
  if (img.startsWith("http")) return img
  if (img.startsWith("/media/")) return "http://localhost:8000" + img
  return "http://localhost:8000/media/" + img
}

const filteredTransfers = computed(() => {
  let result = [...allTransfers.value]

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(transfer =>
      (transfer.asset_name && transfer.asset_name.toLowerCase().includes(query)) ||
      (transfer.asset_code && transfer.asset_code.toLowerCase().includes(query)) ||
      (transfer.notes && transfer.notes.toLowerCase().includes(query)) ||
      (transfer.from_department_name && transfer.from_department_name.toLowerCase().includes(query)) ||
      (transfer.to_department_name && transfer.to_department_name.toLowerCase().includes(query))
    )
  }

  // Department filters
  if (filters.value.fromDepartment) {
    result = result.filter(transfer => transfer.from_department === parseInt(filters.value.fromDepartment))
  }

  if (filters.value.toDepartment) {
    result = result.filter(transfer => transfer.to_department === parseInt(filters.value.toDepartment))
  }

  // Date range filter - اصلاح شده
  if (filters.value.dateFrom) {
    result = result.filter(transfer => {
      const transferDate = new Date(transfer.transfer_date).toISOString().split('T')[0]
      return transferDate >= filters.value.dateFrom
    })
  }

  if (filters.value.dateTo) {
    result = result.filter(transfer => {
      const transferDate = new Date(transfer.transfer_date).toISOString().split('T')[0]
      return transferDate <= filters.value.dateTo
    })
  }

  // Sorting
  result.sort((a, b) => {
    let aValue = a[sortBy.value] || ''
    let bValue = b[sortBy.value] || ''

    // Special handling for dates
    if (sortBy.value === 'transfer_date') {
      aValue = new Date(aValue)
      bValue = new Date(bValue)
    } else {
      aValue = aValue.toString().toLowerCase()
      bValue = bValue.toString().toLowerCase()
    }

    if (sortOrder.value === 'asc') {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0
    } else {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0
    }
  })

  return result
})

const totalPages = computed(() => {
  return Math.ceil(filteredTransfers.value.length / itemsPerPage.value)
})

const startIndex = computed(() => {
  return (currentPage.value - 1) * itemsPerPage.value
})

const endIndex = computed(() => {
  return Math.min(startIndex.value + itemsPerPage.value, filteredTransfers.value.length)
})

const paginatedTransfers = computed(() => {
  return filteredTransfers.value.slice(startIndex.value, endIndex.value)
})

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const delta = 2

  let pages = []

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    const start = Math.max(1, current - delta)
    const end = Math.min(total, current + delta)

    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
  }

  return pages
})

// Methods
const fetchTransfers = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await fetch('http://localhost:8000/api/transfers/', {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    allTransfers.value = data.results || data

  } catch (err) {
    console.error('❌ Error fetching transfers:', err)
    error.value = 'خطا در بارگذاری انتقال‌ها. لطفاً دوباره تلاش کنید.'
  } finally {
    loading.value = false
  }
}

const fetchDepartments = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/departments/', {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
        'Content-Type': 'application/json'
      }
    })

    if (response.ok) {
      const data = await response.json()
      departments.value = data.results || data
    }
  } catch (err) {
    console.error('❌ Error fetching departments:', err)
  }
}

const clearSearch = () => {
  searchQuery.value = ''
}

const clearAllFilters = () => {
  searchQuery.value = ''
  filters.value = {
    fromDepartment: '',
    toDepartment: '',
    dateFrom: '',
    dateTo: ''
  }
  currentPage.value = 1
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc'
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const viewTransferDetails = (transfer) => {
  selectedTransfer.value = transfer
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedTransfer.value = null
}

const editTransfer = (transfer) => {
  console.log('Edit transfer:', transfer)
  // Navigate to edit page or open edit modal
}

const deleteTransfer = async (transfer) => {
  if (!confirm(`آیا از حذف این انتقال اطمینان دارید؟\n\nدارایی: ${transfer.asset_name}\nاز: ${transfer.from_department_name}\nبه: ${transfer.to_department_name}`)) {
    return
  }

  try {
    const response = await fetch(`http://localhost:8000/api/transfers/${transfer.id}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
      }
    })

    if (response.ok) {
      const index = allTransfers.value.findIndex(t => t.id === transfer.id)
      if (index > -1) {
        allTransfers.value.splice(index, 1)
      }
      alert('انتقال با موفقیت حذف شد!')
    } else {
      throw new Error('خطا در حذف انتقال')
    }
  } catch (err) {
    console.error('❌ Error deleting transfer:', err)
    alert('خطا در حذف انتقال: ' + err.message)
  }
}

// Utility functions
const formatDate = (dateString) => {
  if (!dateString) return 'تاریخ نامعلوم'
  return toJalali(dateString)
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    return `${hours}:${minutes}`
  } catch {
    return ''
  }
}

const formatFullDate = (dateString) => {
  if (!dateString) return 'تاریخ نامعلوم'
  return toJalaliWithTime(dateString)
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

// Debounced search
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
  }, 300)
}

// Watchers
watch([filters, sortBy, sortOrder], () => {
  currentPage.value = 1
}, { deep: true })

watch(itemsPerPage, () => {
  currentPage.value = 1
})

// Debug watchers برای بررسی فیلترها
watch(() => filters.value.dateFrom, (newVal) => {
  console.log('Date From changed:', newVal)
})

watch(() => filters.value.dateTo, (newVal) => {
  console.log('Date To changed:', newVal)
})

// Lifecycle
onMounted(async () => {
  await Promise.all([fetchTransfers(), fetchDepartments()])
})
</script>

<style scoped>
.all-transfers {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: #f8fafc;
  min-height: 100vh;
  direction: rtl;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e2e8f0;
}

.header-content h1 {
  margin: 0 0 0.5rem 0;
  color: #1e293b;
  font-size: 2rem;
  font-weight: 700;
}

.page-subtitle {
  margin: 0;
  color: #64748b;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: 1px solid transparent;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-outline {
  background: white;
  color: #374151;
  border-color: #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.btn-outline:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Controls Section */
.controls-section {
  background: white;
  padding: 1.5rem;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
  margin-bottom: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 120px;
}

.filter-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.filter-select, .date-input-persian {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
}

.filter-select:focus, .date-input-persian:focus {
  outline: 2px solid #3b82f6;
  outline-offset: -2px;
}

/* Persian Date Picker Styling */
.date-input-persian {
  min-width: 150px;
}

/* Search Group */
.search-group {
  flex: 1;
  min-width: 250px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  right: 0.75rem;
  color: #9ca3af;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  background: white;
}

.search-input:focus {
  outline: 2px solid #3b82f6;
  outline-offset: -2px;
}

.clear-search-btn {
  position: absolute;
  left: 0.5rem;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.25rem;
}

.clear-search-btn:hover {
  color: #374151;
}

/* Results Row */
.results-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.results-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.results-count {
  font-weight: 500;
  color: #374151;
}

.filter-indicator {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-label {
  font-size: 0.875rem;
  color: #374151;
}

.sort-select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.sort-order-btn {
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  padding: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
}

.sort-order-btn:hover {
  background: #f3f4f6;
}

/* Loading, Error, Empty States */
.loading-container, .error-container, .empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon, .empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

/* Table Styles */
.table-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

.transfers-table {
  width: 100%;
  border-collapse: collapse;
}

.transfers-table th {
  background: #f8fafc;
  padding: 1rem;
  text-align: right;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
}

.transfers-table td {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.transfer-row:hover {
  background: #f8fafc;
}

/* Column Specific Styles */
.col-asset { min-width: 180px; }
.col-transfer { min-width: 250px; }
.col-date { min-width: 140px; }
.col-user { min-width: 150px; }
.col-notes { min-width: 200px; max-width: 250px; }
.col-price { min-width: 120px; }
.col-image { min-width: 100px; }
.col-actions { min-width: 150px; }

.asset-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.asset-name {
  font-weight: 500;
  color: #1f2937;
}

.asset-code {
  font-size: 0.75rem;
  color: #6b7280;
}

.transfer-direction {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.dept-from, .dept-to {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.dept-label {
  font-size: 0.75rem;
  color: #6b7280;
}

.dept-name {
  font-weight: 500;
  color: #374151;
}

.arrow {
  color: #9ca3af;
  font-weight: bold;
}

.date-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.date-main {
  font-weight: 500;
  color: #1f2937;
}

.date-time {
  font-size: 0.75rem;
  color: #6b7280;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-icon {
  color: #9ca3af;
}

.user-name {
  color: #374151;
}

.notes-content {
  max-width: 200px;
}

.notes-text {
  color: #374151;
  display: block;
  word-break: break-word;
}

.no-notes {
  color: #9ca3af;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: none;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
}

.view-btn:hover {
  background: #dbeafe;
  border-color: #3b82f6;
}

.edit-btn:hover {
  background: #fef3c7;
  border-color: #f59e0b;
}

.delete-btn:hover {
  background: #fee2e2;
  border-color: #ef4444;
}

/* Pagination */
.pagination-container {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.pagination-info {
  color: #6b7280;
  font-size: 0.875rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.per-page-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.per-page-select {
  padding: 0.25rem 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.page-navigation {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-btn {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f9fafb;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
}

.page-number {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.page-number:hover {
  background: #f9fafb;
}

.page-number.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

/* Modal */
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
  border-radius: 0.75rem;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
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
  font-size: 1.25rem;
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
}

.modal-close:hover {
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

.transfer-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 500;
  color: #374151;
  min-width: 120px;
}

.detail-value {
  color: #1f2937;
  text-align: left;
}

/* Responsive Design */
@media (max-width: 768px) {
  .all-transfers {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .filters-row {
    flex-direction: column;
  }

  .results-row {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .pagination-container {
    flex-direction: column;
    gap: 1rem;
  }

  .table-wrapper {
    font-size: 0.875rem;
  }
}
</style>
