<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <!-- ۱. اکشن‌ها سمت راست -->
      <div class="dashboard-actions">
        <router-link to="/assets/add" class="action-btn">افزودن کالا</router-link>
        <router-link to="/transfers" class="action-btn">مشاهده جابجایی‌ها</router-link>
        <router-link v-if="authStore.isAdmin" to="/admin" class="action-btn admin-btn">پنل ادمین</router-link>
      </div>

      <!-- ۲. عنوان وسط/راست (بسته به نمایش) -->
      <div class="header-right">
        <h1>داشبورد مديريت كالاها</h1>
      </div>

      <!-- ۳. اطلاعات کاربر سمت چپ -->
      <div class="user-info">
        <span class="farsi-greeting">
          خوش آمديد {{ authStore.user?.first_name || authStore.user?.username }}😊
        </span>
      </div>
    </header>

    <div class="stats-grid">
      <router-link to="/assets" class="card-link">
        <div class="stat-card">
          <h3>کل کالاها</h3>
          <p class="stat-number">{{ stats.total_assets }}</p>
        </div>
      </router-link>
      <div class="stat-card">
        <h3>کالاهای فعال</h3>
        <p class="stat-number">{{ stats.active_assets }}</p>
      </div>
      <div class="stat-card clickable" @click="goToDepartmentAssets">
  <h3>بخش‌ها</h3>
  <p class="stat-number">{{ stats.total_departments }}</p>
</div>

      <div class="stat-card clickable" @click="goToCategories">
        <h3>دسته‌بندی‌ها</h3>
        <p class="stat-number">{{ stats.total_categories || 0 }}</p>
      </div>
    </div>

    <RecentTransfers :max-items="5" />

    <div class="department-chart">
      <h3>توزیع کالاها بر اساس بخش</h3>
      <div v-if="Object.keys(stats.assets_by_department).length === 0" class="no-data">
        اطلاعاتی برای بخش‌ها موجود نیست
      </div>
      <div v-else class="chart-container">
        <div
          v-for="(count, dept) in stats.assets_by_department"
          :key="dept"
          class="chart-bar"
        >
          <div class="bar-label">{{ dept }}</div>
          <div class="bar" :style="{ width: `${maxDeptCount > 0 ? (count / maxDeptCount) * 100 : 0}%` }">
            {{ count }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import RecentTransfers from '@/components/RecentTransfers.vue'

const router = useRouter()
const authStore = useAuthStore()

const stats = ref({
  total_assets: 0,
  active_assets: 0,
  total_departments: 0,
  recent_transfers: 0,
  assets_by_department: {}
})

const maxDeptCount = computed(() => {
  const values = Object.values(stats.value.assets_by_department)
  return values.length > 0 ? Math.max(...values) : 0
})
const goToDepartmentAssets = () => {
  router.push('/department-assets')
}

const fetchStats = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/dashboard/stats/', {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      stats.value = data
    } else {
      console.error('❌ Failed to fetch stats:', response.statusText)
    }
  } catch (error) {
    console.error('💥 Error fetching stats:', error)
  }
}

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}

const goToDepartments = () => {
  router.push('/departments')
}
const goToCategories = () => {
  router.push('/categories')
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.dashboard {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  background: #f8fafc;
  min-height: 100vh;
  direction: rtl;
  font-family: "Vazirmatn", Tahoma, sans-serif;
}

/* هدر دکمه ها سمت راست، greeting سمت چپ */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-bottom: 2px solid #e2e8f0;
  flex-direction: row-reverse;
  gap: 1.5rem;
}

.dashboard-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  flex-direction: row-reverse;
  align-items: center;
  margin-left: 2rem; /* فاصله از بخش وسط */
}

/* سایر استایل‌ها همون قبلی */
.header-right h1 {
  margin: 0;
  color: #1e293b;
  font-size: 24px;
  font-weight: 700;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-direction: row-reverse;
}

.user-info span {
  color: #64748b;
  font-weight: 500;
}

.logout-btn {
  background: #e53e3e;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}
.logout-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
  direction: rtl;
}

.stat-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.2s ease;
  cursor: default;
}
.stat-card:hover {
  transform: translateY(-2px);
}
.stat-card h3 {
  margin: 0 0 1rem 0;
  color: #64748b;
  font-size: 15px;
  font-weight: 600;
}
.stat-number {
  font-size: 2.3rem;
  font-weight: bold;
  color: #667eea;
  margin: 0;
}

.clickable {
  cursor: pointer;
  transition: all 0.2s ease;
}
.clickable:hover {
  transform: translateY(-2px);
  background: #edf2f7;
}

.action-btn {
  background: #667eea;
  color: white;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}
.action-btn:hover {
  background: #5a67d8;
  transform: translateY(-1px);
}
.admin-btn {
  background: #38b2ac;
}
.admin-btn:hover {
  background: #319795;
}

.department-chart {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-bar {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
  flex-direction: row-reverse;
}

.bar-label {
  width: 180px;
  text-align: left;
  margin-left: 1rem;
  font-size: 0.95rem;
  color: #374151;
  direction: rtl;
}

.bar {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  min-width: 40px;
  text-align: center;
  font-weight: 600;
  transition: all 0.2s ease;
}
.bar:hover {
  transform: scale(1.02);
}

.no-data {
  text-align: center;
  color: #64748b;
  padding: 2rem;
  font-style: italic;
}
.farsi-greeting {
  direction: rtl;
  font-weight: 600;
  font-size: 1.1rem;
  color: #2d3748;
  background-color: #edf2f7;
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  display: inline-block;
  line-height: 1.4;
  font-family: "Vazirmatn", Tahoma, sans-serif;
}

/* ریسپانسیو */
@media (max-width: 750px) {
  .dashboard-header,
  .dashboard-actions {
    flex-direction: column!important;
    align-items: stretch;
    gap: 1rem;
    text-align: right;
    margin-left: 0;
  }
  .user-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .bar-label {
    width: unset;
    margin-left: 0.5rem;
    font-size: 0.95rem;
  }
}
</style>
