<template>
  <div class="add-asset">
    <div class="form-header">
      <h1>افزودن دارایی جدید</h1>
      <router-link to="/assets" class="back-btn">← بازگشت به دارایی‌ها</router-link>
    </div>

    <form @submit.prevent="submitAsset" class="asset-form">
      <!-- نام -->
      <div class="form-group">
        <label for="name">نام دارایی *</label>
        <input id="name" v-model="form.name" type="text" required />
      </div>

      <!-- توضیحات -->
      <div class="form-group">
        <label for="description">توضیحات</label>
        <textarea id="description" v-model="form.description" rows="3" />
      </div>

      <!-- دسته و بخش -->
      <div class="form-row">
        <div class="form-group">
          <label for="category">دسته‌بندی *</label>
          <select id="category" v-model="form.category" required>
            <option value="">انتخاب دسته</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label for="department">بخش *</label>
          <select id="department" v-model="form.department" required>
            <option value="">انتخاب بخش</option>
            <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
          </select>
        </div>
      </div>

      <!-- وضعیت و تاریخ خرید -->
      <div class="form-row">
        <div class="form-group">
          <label for="status">وضعیت</label>
          <select id="status" v-model="form.status">
            <option value="active">فعال</option>
            <option value="inactive">غیرفعال</option>
            <option value="under_maintenance">در حال تعمیر</option>
          </select>
        </div>
        <div class="form-group">
          <label for="purchase_date">تاریخ خرید *</label>
          <DatePicker
            v-model="form.purchase_date"
            format="YYYY/MM/DD"
            display-format="jYYYY/jMM/jDD"
            auto-submit

            required
          />
        </div>
      </div>

      <!-- قیمت‌ها -->
      <div class="form-row">
        <div class="form-group">
          <label for="purchase_price">قیمت خرید (ریال) *</label>
          <input id="purchase_price" v-model="form.purchase_price" type="number"  step="100000" required />
        </div>
        <div class="form-group">
  <label for="current_value">تعداد</label>
  <input
    id="current_value"
    v-model="form.current_value"
    type="number"
    step="1"

    disabled
  />
</div>

      </div>

      <!-- شماره سریال، کد، برند -->
      <div class="form-row">
        <div class="form-group">
          <label for="serial_number">شماره سریال</label>
          <input id="serial_number" v-model="form.serial_number" type="text" autocomplete="off" />
        </div>
        <div class="form-group">
          <label for="asset_code">کد دارایی *</label>
          <input id="asset_code" v-model="form.asset_code" type="text" required autocomplete="off" />
        </div>
        <div class="form-group">
  <label for="brand">برند</label>
  <select id="brand" v-model="form.brand">
    <option value="">انتخاب برند</option>
    <option v-for="b in brands" :key="b.id" :value="b.id">{{ b.name }}</option>
  </select>
</div>


      </div>

      <div class="form-group">
        <label for="model">مدل</label>
        <input id="model" v-model="form.model" type="text" />
      </div>
    <div class="form-group">
  <label for="usecase">مورد استفاده</label>
  <select id="usecase" v-model="form.usecase">

    <option v-for="u in usecases" :key="u.id" :value="u.id">{{ u.name }}</option>
  </select>
</div>

      <!-- دکمه‌ها -->
      <div class="form-actions">
        <button type="button" @click="$router.go(-1)" class="cancel-btn">انصراف</button>
        <button type="submit" :disabled="loading" class="submit-btn">
          {{ loading ? 'در حال افزودن...' : 'افزودن دارایی' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAssetsStore } from '@/stores/assets'
import DatePicker from 'vue3-persian-datetime-picker'
import jalaali from 'jalaali-js'


const router = useRouter()
const assetsStore = useAssetsStore()

const form = ref({
  name: '',
  description: '',
  category: '',
  department: '',
  status: 'active',
  purchase_date: '',
  purchase_price: '',
  current_value: 1,
  serial_number: '',
  asset_code: '',
  brand: '',
  model: ''
})
const brands = ref([])

const loading = ref(false)
const departments = computed(() => assetsStore.departments)
const categories = computed(() => assetsStore.categories)
const usecases = ref([])
async function fetchUseCases() {
  try {
    const res = await fetch(`${API_URL}/usecases/`, {
      headers: getAuthHeaders(),
    })
    if (!res.ok) throw new Error('موارد استفاده بارگذاری نشد!')
    usecases.value = await res.json()
  } catch (err) {
    usecases.value = []
    alert('مشکل در بارگذاری موارد استفاده!')
    console.error('usecases fetch error', err)
  }
}

const submitAsset = async () => {
  loading.value = true
  try {
    const payload = {}
    for (const [k, v] of Object.entries(form.value)) {
      if (v !== '') payload[k] = v
    }

    // ✅ Let DatePicker handle date conversion automatically
    // Remove the manual jalaliToGregorian conversion

    if (payload.purchase_price) {
      payload.purchase_price = parseFloat(payload.purchase_price)
    }
    if (payload.current_value) {
      payload.current_value = parseFloat(payload.current_value)
    }
    if (payload.brand) {
      payload.brand = brands.value.find(b => b.id == payload.brand)?.name || ''
    }
    if (payload.purchase_date) {
  // اگر تاریخ به صورت "2025/07/13" میاد، به "2025-07-13" تبدیل کن:
  payload.purchase_date = payload.purchase_date.replace(/\//g, '-');
}
    // console.log("🚩 PAYLOAD SENDING:", payload)
    await assetsStore.addAsset(payload)
    alert('دارایی با موفقیت افزوده شد!')
    router.push('/assets')
  } catch (err) {
    console.error('💥 خطا در افزودن دارایی:', err)
    alert('خطا: ' + (err.response?.data?.detail || err.message))
  } finally {
    loading.value = false
  }
}


onMounted(async () => {
  await assetsStore.fetchDepartments()
  await assetsStore.fetchCategories()
  await fetchBrands()
   await fetchUseCases()
})

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api"
function getAuthHeaders() {
  const token = localStorage.getItem('access_token')
  return token
    ? { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
    : { 'Content-Type': 'application/json' }
}

async function fetchBrands() {
  try {
    const res = await fetch(`${API_URL}/brands/`, {
      headers: getAuthHeaders()
    })
    const contentType = res.headers.get("content-type");
    const rawText = await res.text();


    if (!res.ok) throw new Error('برندها بارگذاری نشد!')
    if (!contentType || !contentType.includes("application/json")) {
      throw new Error('پاسخ سرور JSON نیست!');
    }
    brands.value = JSON.parse(rawText).sort((a, b) => a.name.localeCompare(b.name, 'fa'))
  } catch (err) {
    brands.value = []
    alert('مشکل در بارگذاری برندها!')
    console.error('brands fetch error', err)
  }
}


</script>

<style scoped>
@import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn-font@v33.003/dist/font-face.css');

.add-asset {
  max-width: 1000px;
  margin: 40px auto;
  padding: 32px;
  background: #fefefe;
  border-radius: 18px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  font-family: Vazirmatn, Tahoma, sans-serif;
  direction: rtl;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.form-header h1 {
  margin: 0;
  font-size: 28px;
  color: #2e3a59;
  font-weight: bold;
}

.back-btn {
  color: #3b82f6;
  text-decoration: none;
  font-size: 16px;
}
.back-btn:hover {
  text-decoration: underline;
}

.asset-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.form-row .form-group {
  flex: 1;
  min-width: 200px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-weight: 600;
  color: #374151;
  font-size: 15px;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 15px;
  background: #fff;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.form-actions {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn {
  padding: 10px 20px;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
}
.cancel-btn:hover {
  background: #4b5563;
}

.submit-btn {
  padding: 10px 24px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
}
.submit-btn:hover:not(:disabled) {
  background: #2563eb;
}
.submit-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
  }

  .form-actions {
    flex-direction: column;
  }
}
</style>
