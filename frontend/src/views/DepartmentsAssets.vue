<template>
  <div class="dep-assets-page">
    <h2>📊 دارایی‌های هر بخش</h2>

    <div class="search-bar-row">
      <input
        v-model="search"
        placeholder="🔍 جستجوی بخش..."
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
        <h3>🏢 {{ dept.department_name }}</h3>
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
              <td class="asset-value">📦 {{ asset.current_value }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination-buttons">
        <button
          @click="prevPage(dept.department_id)"
          :disabled="currentPages[dept.department_id] === 1"
        >⏪ قبلی</button>

        <span>
          صفحه <strong>{{ currentPages[dept.department_id] || 1 }}</strong> از
          <strong>{{ Math.ceil(dept.assets.length / 5) }}</strong>
        </span>

        <button
          @click="nextPage(dept.department_id, dept.assets)"
          :disabled="currentPages[dept.department_id] >= Math.ceil(dept.assets.length / 5)"
        >بعدی ⏩</button>
      </div>
    </div>

    <div v-if="totalDeptPages > 1" class="department-pagination">
      <button @click="prevDeptPage" :disabled="deptPage === 1">◀ قبلی</button>
      <span>صفحه {{ deptPage }} از {{ totalDeptPages }}</span>
      <button @click="nextDeptPage" :disabled="deptPage >= totalDeptPages">
        بعدی ▶
      </button>
    </div>

    <div v-if="departmentsAssets.length === 0" class="not-found">
      <span>❌ نتیجه‌ای یافت نشد</span>
    </div>
  </div>
</template>


<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'

const departmentsAssets = ref([])
const search = ref('')
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const selectedDepartmentId = ref(null) // ✅

const currentPages = ref({})

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
const selectedDepartmentName = ref(null)

const fetchData = async () => {
  let url = 'http://localhost:8000/api/department-assets/'
  if (search.value) url += `?search=${encodeURIComponent(search.value)}`
  const resp = await fetch(url, {
    headers: { Authorization: `Bearer ${authStore.accessToken}` },
  })
  if (resp.ok) {
    let data = await resp.json()
    // اگر فیلتر نام دپارتمان فعال بود فقط همون بخش رو نشون بده
    if (selectedDepartmentName.value) {
      data = data.filter(
        dept => dept.department_name === selectedDepartmentName.value
      )
    }
    departmentsAssets.value = data
    // برا بقیه قسمت‌ها هم مثل قبله...
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


// --- اینو اضافه کن
onMounted(() => {
  const deptParam = route.query.department
  if (deptParam) {
    selectedDepartmentName.value = decodeURIComponent(deptParam)
  }
  fetchData()
})

watch(
  () => route.query.department,
  (newDept) => {
    if (newDept) selectedDepartmentName.value = decodeURIComponent(newDept)
    else selectedDepartmentName.value = null
    fetchData()
  }
)
</script>


<style scoped>


.dep-assets-page {
  direction: rtl;
  text-align: right;
  font-family: 'Vazirmatn', Tahoma, Arial, sans-serif;
  padding: 2.5rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
  background: #f9fbff;
  border-radius: 18px;
  min-height: 90vh;
  box-shadow: 0 6px 32px -10px rgba(100, 120, 200, 0.1);
}

h2 {
  margin-bottom: 2.5rem;
  color: #2e3a59;
  font-weight: 900;
  font-size: 2.2rem;
  text-shadow: 0 1px 6px #dde2fa4a;
  letter-spacing: -0.4px;
}

.search-bar-row {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 2rem;
}

.search-input {
  width: 400px;
  max-width: 100%;
  font-size: 1rem;
  padding: 0.9rem 1.3rem;
  border-radius: 12px;
  border: 1.5px solid #b4c0e0;
  background: #fff;
  outline: none;
  transition: border 0.2s;
  box-shadow: 0 2px 10px -6px #2d3a6747;
}

.search-input:focus {
  border-color: #3e6cff;
  background: #eef4ff;
}

.dep-block {
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 3px 14px -8px #b8c4dfb3;
  padding: 1.6rem 1.5rem;
  margin-bottom: 2.5rem;
  border-right: 6px solid #547bff;
}

.dep-header {
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1.5px dashed #d0d9fa;
  padding-bottom: 10px;
}

.dep-header h3 {
  color: #2e3a59;
  font-weight: 700;
  font-size: 1.3rem;
  margin: 0;
}

.assets-table-wrapper {
  overflow-x: auto;
}

.assets-table {
  width: 100%;
  border-collapse: collapse;
  background: transparent;
  font-size: 1.05rem;
  margin-top: 0.6rem;
}

.assets-table th,
.assets-table td {
  padding: 12px 14px;
  text-align: right;
}

.assets-table th {
  background: #e4eaff;
  color: #24325c;
  font-weight: 800;
  border-bottom: 2px solid #c5cdee;
}

.assets-table td {
  border-bottom: 1px solid #edf0f7;
  color: #2e3a59;
  vertical-align: middle;
}

.asset-code {
  font-family: 'Vazirmatn', monospace, Tahoma;
  background: #eef4ff;
  border-radius: 6px;
  font-size: 0.93rem;
  color: #4255a4;
  padding: 0.25em 0.9em;
  border: 1px solid #d9e3f7;
}

.asset-name {
  font-weight: 600;
  color: #2a2e6a;
}

.asset-value {
  color: #197b73;
  font-weight: 600;
}

.clickable-row {
  cursor: pointer;
  user-select: none;
  transition: background 0.2s, box-shadow 0.2s;
}

.clickable-row:hover {
  background: #f1f5ff;
  box-shadow: 0 2px 6px -6px #bcc5e5;
}

.not-found {
  margin-top: 3rem;
  color: #b21e3b;
  text-align: center;
  padding: 1.7rem;
  background: #ffecec;
  border-radius: 14px;
  box-shadow: 0 3px 10px -7px #e6b6b6;
  font-size: 1.1rem;
}

.pagination-buttons {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 1rem;
  gap: 0.8rem;
}

.pagination-buttons button {
  background: #3e6cff;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 0.5rem 1rem;
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
  color: #2e3a59;
}

.department-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 2rem;
  gap: 1rem;
}

.department-pagination button {
  background: #2f3caa;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 0.55rem 1.2rem;
  font-size: 1rem;
  cursor: pointer;
}

.department-pagination button:disabled {
  background: #c8c8c8;
  cursor: not-allowed;
}

.department-pagination span {
  color: #2d2d2d;
  font-weight: 500;
}

@media (max-width: 768px) {
  .dep-assets-page {
    padding: 1.2rem 1rem;
    border-radius: 0;
  }

  .assets-table th,
  .assets-table td {
    padding: 8px 6px;
    font-size: 0.95rem;
  }

  .search-input {
    width: 100%;
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