<template>
  <div class="dep-assets-page">
    <h2>دارایی هر بخش</h2>

    <div class="search-bar-row">
      <input
        v-model="search"
        placeholder="جستجوی بخش..."
        @input="fetchData"
        class="search-input"
      />
    </div>

    <div
      v-for="dept in paginatedDepartments"
      :key="dept.department_id"
      class="dep-block"
    >
      <div class="dep-header">
        <h3>{{ dept.department_name }}</h3>
      </div>

      <div class="assets-table-wrapper">
        <table class="assets-table">
          <thead>
            <tr>
              <th>کد</th>
              <th>نام دارایی</th>
              <th>تعداد</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="asset in getPaginatedAssets(dept.assets, dept.department_id)"
              :key="asset.asset_id"
              class="clickable-row"
              @click="goToAsset(asset.asset_id)"
            >
              <td class="asset-code">{{ asset.code }}</td>
              <td class="asset-name">{{ asset.name }}</td>
              <td class="asset-value">{{ asset.current_value }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination-buttons">
        <button
          @click="prevPage(dept.department_id)"
          :disabled="currentPages[dept.department_id] === 1"
        >
          قبلی
        </button>
        <span>
          صفحه {{ currentPages[dept.department_id] || 1 }} از
          {{ Math.ceil(dept.assets.length / 5) }}
        </span>
        <button
          @click="nextPage(dept.department_id, dept.assets)"
          :disabled="
            currentPages[dept.department_id] >=
            Math.ceil(dept.assets.length / 5)
          "
        >
          بعدی
        </button>
      </div>
    </div>

    <!-- Pagination for departments -->
    <div v-if="totalDeptPages > 1" class="department-pagination">
      <button @click="prevDeptPage" :disabled="deptPage === 1">قبلی</button>
      <span>صفحه {{ deptPage }} از {{ totalDeptPages }}</span>
      <button @click="nextDeptPage" :disabled="deptPage >= totalDeptPages">
        بعدی
      </button>
    </div>

    <div v-if="departmentsAssets.length === 0" class="not-found">
      <span>نتیجه‌ای یافت نشد</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const departmentsAssets = ref([])
const search = ref('')
const authStore = useAuthStore()
const router = useRouter()

// pagination for assets inside each department
const currentPages = ref({})

// pagination for departments
const deptPage = ref(1)
const perDeptPage = 3

const paginatedDepartments = computed(() => {
  const start = (deptPage.value - 1) * perDeptPage
  return departmentsAssets.value.slice(start, start + perDeptPage)
})

const totalDeptPages = computed(() => {
  return Math.ceil(departmentsAssets.value.length / perDeptPage)
})

const nextDeptPage = () => {
  if (deptPage.value < totalDeptPages.value) deptPage.value++
}

const prevDeptPage = () => {
  if (deptPage.value > 1) deptPage.value--
}

const goToAsset = (id) => {
  router.push(`/assets/${id}`)
}

const getPaginatedAssets = (assets, deptId) => {
  const page = currentPages.value[deptId] || 1
  const perPage = 5
  const start = (page - 1) * perPage
  return assets.slice(start, start + perPage)
}

const nextPage = (deptId, assets) => {
  const totalPages = Math.ceil(assets.length / 5)
  if ((currentPages.value[deptId] || 1) < totalPages) {
    currentPages.value[deptId] = (currentPages.value[deptId] || 1) + 1
  }
}

const prevPage = (deptId) => {
  if ((currentPages.value[deptId] || 1) > 1) {
    currentPages.value[deptId] = (currentPages.value[deptId] || 1) - 1
  }
}

const fetchData = async () => {
  let url = 'http://localhost:8000/api/department-assets/'
  if (search.value) url += `?search=${encodeURIComponent(search.value)}`
  const resp = await fetch(url, {
    headers: { Authorization: `Bearer ${authStore.accessToken}` },
  })
  if (resp.ok) {
    const data = await resp.json()
    departmentsAssets.value = data

    // Initialize pages for asset pagination
    data.forEach((dept) => {
      if (!(dept.department_id in currentPages.value)) {
        currentPages.value[dept.department_id] = 1
      }
    })

    deptPage.value = 1
  } else {
    departmentsAssets.value = []
  }
}

// initial load
fetchData()
</script>

<style scoped>
@import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn-font@v33.003/dist/font-face.css');

.dep-assets-page {
  direction: rtl;
  text-align: right;
  font-family: 'Vazirmatn', Tahoma, Arial, sans-serif;
  padding: 2.5rem 1rem;
  max-width: 700px;
  margin: 0 auto;
  background: #f7f8fa;
  border-radius: 24px;
  min-height: 90vh;
  box-shadow: 0 4px 32px -10px rgba(71, 125, 243, 0.08);
}

h2 {
  margin-bottom: 2.5rem;
  color: #283593;
  font-weight: 800;
  font-size: 2.1rem;
  text-shadow: 0 1px 8px #dde2fa49;
  letter-spacing: -0.5px;
}

.search-bar-row {
  display: flex;
  margin-bottom: 2.5rem;
  justify-content: flex-end;
}

.search-input {
  width: 330px;
  max-width: 100%;
  font-size: 1rem;
  padding: 0.85rem 1.3rem;
  border-radius: 14px;
  border: 1.5px solid #cad2ef;
  background: #fff;
  outline: none;
  transition: border 0.2s;
  box-shadow: 0 3px 12px -10px #27399647;
}
.search-input:focus {
  border-color: #577fff;
  background: #eef3fd;
}

.dep-block {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1.5px 10px -6px #90a2c040;
  padding: 1.5rem 1.2rem 0.7rem 1.2rem;
  margin-bottom: 2rem;
  border-right: 5px solid #728fe6;
}

.dep-header {
  margin-bottom: 0.8rem;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1.5px dashed #dde2fa;
  padding-bottom: 8px;
}
.dep-header h3 {
  color: #283593;
  font-weight: 500;
  font-size: 1.25rem;
  margin: 0;
}
.assets-table-wrapper {
  overflow-x: auto;
}
.assets-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: transparent;
  margin-top: 0.3rem;
  font-size: 1.04rem;
}

.assets-table th,
.assets-table td {
  padding: 10px 12px;
  text-align: right;
  background: none;
}
.assets-table th {
  background: #e7ebfc;
  color: #2d386e;
  font-weight: 700;
  border-bottom: 2px solid #d1d8ee;
  font-size: 1.03rem;
}

.assets-table td {
  border-bottom: 1px solid #f0f3f9;
  color: #333f54;
  vertical-align: middle;
}

.asset-code {
  font-family: 'Vazirmatn', monospace, Tahoma;
  background: #eff4ff;
  border-radius: 6px;
  font-size: 0.95rem;
  color: #5761af;
  padding: 0.2em 0.85em 0.1em 0.85em;
  border: 1px solid #e2e8f0;
  letter-spacing: 0.2px;
}

.asset-name {
  font-weight: 600;
  color: #373066;
}
.asset-value {
  color: #217971;
  font-weight: 500;
}

.clickable-row {
  cursor: pointer;
  user-select: none;
  transition: background 0.16s, box-shadow 0.16s;
}

.clickable-row:hover {
  background: #f2f6fd;
  box-shadow: 0 2px 6px -7px #c5cded;
}

.not-found {
  margin-top: 3rem;
  color: #af2836;
  text-align: center;
  padding: 1.5rem;
  background: #faecec;
  border-radius: 12px;
  box-shadow: 0 2px 8px -7px #e0b4b4;
  font-size: 1.1rem;
}

/* Pagination for assets inside department */
.pagination-buttons {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 1rem;
  gap: 0.7rem;
}

.pagination-buttons button {
  background: #577fff;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.4rem 0.9rem;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.2s;
}

.pagination-buttons button:disabled {
  background: #cfd8ff;
  cursor: not-allowed;
}

.pagination-buttons span {
  font-size: 0.95rem;
  color: #444f77;
}

/* Pagination for departments */
.department-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 2rem;
  gap: 1rem;
}

.department-pagination button {
  background: #3949ab;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  cursor: pointer;
}

.department-pagination button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.department-pagination span {
  color: #3b3b3b;
  font-weight: 500;
}

@media (max-width: 500px) {
  .dep-assets-page {
    padding: 1rem 0.3rem;
    border-radius: 0;
  }

  .assets-table th,
  .assets-table td {
    padding: 7px 5px;
    font-size: 0.96rem;
  }
}

.assets-table-wrapper::-webkit-scrollbar {
  height: 7px;
}
.assets-table-wrapper::-webkit-scrollbar-thumb {
  background: #d2dffd;
  border-radius: 4px;
}
</style>
