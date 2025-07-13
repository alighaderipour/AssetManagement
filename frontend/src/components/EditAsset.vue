<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAssetsStore } from '@/stores/assets'
import { useAuthStore } from '@/stores/auth'
import jalaali from 'jalaali-js'
import DatePicker from 'vue3-persian-datetime-picker'

const router = useRouter()
const route = useRoute()
const assetsStore = useAssetsStore()
const authStore = useAuthStore()

const asset = ref(null)
const form = ref({
  name: '',
  description: '',
  category: '',
  current_department: '',
  status: 'active',
  purchase_date: '',
  purchase_price: '',
  current_value: '',
  serial_number: '',
  brand: '',
  model: ''
})

const loading = ref(false)
const saving = ref(false)
const departments = computed(() => assetsStore.departments)
const categories = computed(() => assetsStore.categories)
const isEditMode = computed(() => route.path.includes('/edit'))

const toJalali = (dateString) => {
  if (!dateString) return ''
  try {
    const dateObj = new Date(dateString)
    const j = jalaali.toJalaali(dateObj)
    return `${j.jy}/${String(j.jm).padStart(2, '0')}/${String(j.jd).padStart(2, '0')}`
  } catch {
    return ''
  }
}

const jalaliCreatedAt = computed(() => toJalali(asset.value?.created_at))

const loadAsset = async () => {
  loading.value = true;
  try {
    const id = route.params.id;
    asset.value = await assetsStore.getAsset(id);
    const assetData = asset.value;

    // ❌ REMOVE THIS MANUAL CONVERSION:
    let pd = assetData.purchase_date || ''

    form.value = {
      name: assetData.name || '',
      description: assetData.description || '',
      category: assetData.category || '',
      current_department: assetData.current_department || '',
      status: assetData.status || 'active',
      purchase_date: assetData.purchase_date || '',  // ❌ This is wrong
      purchase_price: assetData.purchase_price || '',
  current_value: assetData.current_value || '',
  serial_number: assetData.serial_number || '',
  brand: assetData.brand || '',
  model: assetData.model || ''
    };
  } catch (error) {
    // ... error handling
  } finally {
    loading.value = false;
  }
};



const submitAsset = async () => {
  if (!isEditMode.value) return
  saving.value = true
  const payload = {}
  try {
    const purchaseDate = form.value.purchase_date
    if (purchaseDate && /^\d{4}\/\d{2}\/\d{2}$/.test(purchaseDate)) {
      const [jy, jm, jd] = purchaseDate.split('/').map(Number)
      const { gy, gm, gd } = jalaali.toGregorian(jy, jm, jd)
      payload.purchase_date = `${gy}-${String(gm).padStart(2, '0')}-${String(gd).padStart(2, '0')}`
    } else if (purchaseDate && !/^\d{4}-\d{2}-\d{2}$/.test(purchaseDate)) {
      alert('فرمت تاریخ خرید نامعتبر است')
      return
    } else {
      payload.purchase_date = purchaseDate
    }

    for (const [key, value] of Object.entries(form.value)) {
      if (value !== '' && key !== 'purchase_date') {
        payload[key] = value
      }
    }

    if (payload.purchase_price) payload.purchase_price = parseFloat(payload.purchase_price)
    if (payload.current_value) payload.current_value = parseFloat(payload.current_value)

    await assetsStore.updateAsset(route.params.id, payload)
    alert('دارایی با موفقیت به‌روزرسانی شد!')
    router.push('/assets')
  } catch (error) {
    console.error('خطا در ذخیره:', error)
    alert('خطا در به‌روزرسانی دارایی: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const cancelEdit = () => router.push('/assets')

const deleteAsset = async () => {
  if (!confirm('آیا مطمئن هستید که می‌خواهید این دارایی را حذف کنید؟')) return
  try {
    await assetsStore.deleteAsset(route.params.id)
    alert('دارایی با موفقیت حذف شد!')
    router.push('/assets')
  } catch (error) {
    let msg = error.response?.status === 404
    ? "این دارایی قبلاً حذف شده است."
    : error.response?.data?.detail || error.message;
  alert('خطا در حذف دارایی: ' + msg)
  }
}

onMounted(async () => {
  await Promise.all([
    assetsStore.fetchDepartments(),
    assetsStore.fetchCategories(),
    loadAsset()
  ])
})
</script>

<template>
  <div class="edit-asset">
    <!-- Header بخش -->
    <div class="form-header">
      <div class="header-content">
        <h1 class="page-title">{{ isEditMode ? 'ویرایش دارایی' : 'جزئیات دارایی' }}</h1>
        <p class="page-subtitle">مدیریت اطلاعات دارایی سازمان</p>
      </div>
      <div class="header-actions">
        <router-link to="/assets" class="back-btn">
          <span class="btn-icon">←</span>
          بازگشت به دارایی‌ها
        </router-link>
        <button
          v-if="!isEditMode"
          @click="router.push(`/assets/${route.params.id}/edit`)"
          class="btn btn-primary"
        >
          <span class="btn-icon">✏️</span>
          ویرایش دارایی
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <span>در حال بارگذاری جزئیات دارایی...</span>
    </div>

    <!-- Form -->
    <form v-else-if="asset" @submit.prevent="isEditMode ? submitAsset() : null" class="asset-form">
      <!-- کد دارایی -->
      <div class="form-section">
        <h3 class="section-title">اطلاعات اصلی</h3>

        <div class="form-group">
          <label for="asset_code" class="form-label">
            <span class="label-icon">🏷️</span>
            کد دارایی
          </label>
          <input
            id="asset_code"
            :value="asset.asset_code || asset.code"
            type="text"
            disabled
            class="form-input readonly-field"
          />
        </div>

        <div class="form-group">
          <label for="name" class="form-label">
            <span class="label-icon">📦</span>
            نام دارایی *
          </label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            :disabled="!isEditMode"
            required
            class="form-input"
            placeholder="نام دارایی را وارد کنید"
          />
        </div>

        <div class="form-group">
          <label for="description" class="form-label">
            <span class="label-icon">📝</span>
            توضیحات
          </label>
          <textarea
            id="description"
            v-model="form.description"
            rows="3"
            :disabled="!isEditMode"
            class="form-input"
            placeholder="توضیحات مربوط به دارایی"
          />
        </div>
      </div>

      <!-- اطلاعات دسته‌بندی -->
      <div class="form-section">
        <h3 class="section-title">دسته‌بندی و موقعیت</h3>

        <div class="form-row">
          <div class="form-group">
            <label for="category" class="form-label">
              <span class="label-icon">📂</span>
              دسته‌بندی *
            </label>
            <select
              id="category"
              v-model="form.category"
              :disabled="!isEditMode"
              required
              class="form-input"
            >
              <option value="">انتخاب دسته‌بندی</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>

          <div class="form-group">
            <label for="department" class="form-label">
              <span class="label-icon">🏢</span>
              بخش اصلی
            </label>
            <input
              id="department"
              :value="asset.department_name"
              type="text"
              disabled
              class="form-input readonly-field"
            />
            <small class="field-help">بخش اولیه مالک این دارایی</small>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="current_department" class="form-label">
              <span class="label-icon">📍</span>
              بخش فعلی
            </label>
            <input
              id="current_department"
              :value="asset.current_department_name || 'ندارد'"
              type="text"
              disabled
              class="form-input readonly-field"
            />
            <small class="field-help">محل فعلی قرارگیری دارایی</small>
          </div>

          <div class="form-group">
            <label for="status" class="form-label">
              <span class="label-icon">🔄</span>
              وضعیت
            </label>
            <select id="status" v-model="form.status" :disabled="!isEditMode" class="form-input">
              <option value="active">فعال</option>
              <option value="inactive">غیرفعال</option>
              <option value="under_maintenance">در حال تعمیر</option>
              <option value="disposed">از رده خارج</option>
            </select>
          </div>
        </div>
      </div>

      <!-- اطلاعات مالی -->
      <div class="form-section">
        <h3 class="section-title">اطلاعات مالی</h3>

        <div class="form-row">
          <div class="form-group">
    <label for="purchase_date" class="form-label">
      <span class="label-icon">📅</span>
      تاریخ خرید (شمسی)
    </label>
    <DatePicker
  v-model="form.purchase_date"
  format="YYYY/MM/DD"
  display-format="jYYYY/jMM/jDD"
  auto-submit
  :disabled="!isEditMode"
  required
/>

    <small class="field-help">تاریخ بر اساس تقویم شمسی نمایش داده می‌شود</small>
  </div>

          <div class="form-group">
            <label for="purchase_price" class="form-label">
              <span class="label-icon">💰</span>
              قیمت خرید (ریال) *
            </label>
            <input
              id="purchase_price"
              v-model="form.purchase_price"
              type="number"
              step="1000000"
              :disabled="!isEditMode"
              required
              class="form-input"
              placeholder="مثال: 1000000"
            />
          </div>
        </div>

        <div class="form-group">
  <label for="current_value">تعداد</label>
  <input
    id="current_value"
    type="number"
    :value="form.current_value"
    readonly
    tabindex="-1"
    class="form-input readonly-field"
    style="pointer-events:none; background:#f8fafc; color:#6c757d;"
  />
</div>

      </div>

      <!-- اطلاعات تکنیکی -->
      <div class="form-section">
        <h3 class="section-title">اطلاعات تکنیکی</h3>

        <div class="form-row">
          <div class="form-group">
            <label for="serial_number" class="form-label">
              <span class="label-icon">🔢</span>
              شماره سریال
            </label>
            <input
              id="serial_number"
              v-model="form.serial_number"
              type="text"
              :disabled="!isEditMode"
              class="form-input"
              placeholder="شماره سریال دارایی"
            />
          </div>

          <div class="form-group">
            <label for="brand" class="form-label">
              <span class="label-icon">🏭</span>
              برند
            </label>
            <input
              id="brand"
              v-model="form.brand"
              type="text"
              :disabled="!isEditMode"
              class="form-input"
              placeholder="نام برند"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="model" class="form-label">
            <span class="label-icon">🏷️</span>
            مدل
          </label>
          <input
            id="model"
            v-model="form.model"
            type="text"
            :disabled="!isEditMode"
            class="form-input"
            placeholder="مدل دارایی"
          />
        </div>
      </div>

      <!-- اطلاعات ثبت -->
      <div class="form-section readonly-info">
        <h3 class="section-title">اطلاعات ثبت</h3>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">
              <span class="label-icon">👤</span>
              ثبت شده توسط
            </label>
            <input
              :value="asset.created_by_name"
              type="text"
              disabled
              class="form-input readonly-field"
            />
          </div>

          <div class="form-group">
            <label class="form-label">
              <span class="label-icon">🕒</span>
              تاریخ ثبت (شمسی)
            </label>
            <input
              :value="jalaliCreatedAt"
              type="text"
              disabled
              class="form-input readonly-field"
            />
          </div>
        </div>
      </div>

      <!-- دکمه‌های عملیات -->
      <div v-if="isEditMode" class="form-actions">
        <button type="button" @click="cancelEdit" class="action-btn cancel-btn">
          <span class="btn-icon">✕</span>
          انصراف
        </button>
        <button
          type="button"
          @click="deleteAsset"
          class="action-btn delete-btn"
          v-if="authStore.user?.role === 'admin'"
        >
          <span class="btn-icon">🗑️</span>
          حذف دارایی
        </button>
        <button type="submit" :disabled="saving" class="action-btn submit-btn">
          <span class="btn-icon">{{ saving ? '⏳' : '💾' }}</span>
          {{ saving ? 'در حال ذخیره...' : 'ذخیره تغییرات' }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.edit-asset {
  max-width: 900px;
  margin: 20px auto;
  padding: 0;
  font-family: 'Vazir', 'Tahoma', sans-serif;
  direction: rtl;
}

/* Header Styles */
.form-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 32px;
  border-radius: 16px 16px 0 0;
  margin-bottom: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.header-content h1.page-title {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.page-subtitle {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
  font-weight: 400;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 10px 16px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  text-decoration: none;
}

.btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 14px;
}

.btn-primary {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(79, 172, 254, 0.6);
}

.btn-icon {
  font-size: 16px;
}

/* Loading Styles */
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  background: white;
  border-radius: 0 0 16px 16px;
  color: #64748b;
  font-size: 16px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Form Styles */
.asset-form {
  background: white;
  border-radius: 0 0 16px 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.form-section {
  padding: 32px;
  border-bottom: 1px solid #e5e7eb;
}

.form-section:last-child {
  border-bottom: none;
}

.section-title {
  margin: 0 0 24px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title::before {
  content: '';
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 20px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.label-icon {
  font-size: 16px;
}

.form-input {
  padding: 14px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.3s ease;
  background: white;
  text-align: right;
  font-family: inherit;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  transform: translateY(-1px);
}

.form-input::placeholder {
  color: #9ca3af;
  font-style: italic;
}

/* Read-only field styles */
.readonly-field {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
  color: #64748b !important;
  cursor: default;
  border-color: #e2e8f0 !important;
  font-weight: 500;
}

.readonly-info {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  margin: 0;
}

.field-help {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
  font-style: italic;
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  padding: 32px;
  background: #f8fafc;
  border-top: 1px solid #e5e7eb;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  font-size: 14px;
  font-family: inherit;
}

.cancel-btn {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(107, 114, 128, 0.3);
}

.cancel-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(107, 114, 128, 0.4);
}

.delete-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
}

.delete-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.submit-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.submit-btn:disabled {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Number inputs direction */
.form-input[type="number"] {
  text-align: left;
  direction: ltr;
}

/* Textarea resize */
.form-input[type="textarea"] {
  resize: vertical;
  min-height: 100px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .edit-asset {
    margin: 10px;
  }

  .form-header {
    padding: 24px;
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .header-actions {
    width: 100%;
    justify-content: center;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .form-section {
    padding: 24px 20px;
  }

  .form-actions {
    flex-direction: column;
    padding: 24px 20px;
  }

  .action-btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .form-header {
    padding: 20px;
  }

  .header-content h1.page-title {
    font-size: 24px;
  }

  .page-subtitle {
    font-size: 14px;
  }

  .section-title {
    font-size: 18px;
  }
}
</style>
