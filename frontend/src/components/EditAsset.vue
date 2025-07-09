<!-- frontend/src/views/EditAsset.vue -->
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAssetsStore } from '@/stores/assets'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const assetsStore = useAssetsStore()
const authStore = useAuthStore()

// Check if we're in edit mode based on the route
const isEditMode = computed(() => route.path.includes('/edit'))

const asset = ref(null)
const form = ref({
  name: '',
  description: '',
  category: '',
  current_department: '', // Only this should be editable
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

const loadAsset = async () => {
  loading.value = true
  try {
    const id = route.params.id
    asset.value = await assetsStore.getAsset(id)
    
    // Fill form with asset data
    form.value = {
      name: asset.value.name || '',
      description: asset.value.description || '',
      category: asset.value.category || '',
      current_department: asset.value.current_department || '',
      status: asset.value.status || 'active',
      purchase_date: asset.value.purchase_date || '',
      purchase_price: asset.value.purchase_price || '',
      current_value: asset.value.current_value || '',
      serial_number: asset.value.serial_number || '',
      brand: asset.value.brand || '',
      model: asset.value.model || ''
    }
  } catch (error) {
    console.error('Error loading asset:', error)
    alert('Error loading asset details')
  } finally {
    loading.value = false
  }
}

const submitAsset = async () => {
  if (!isEditMode.value) return
  
  saving.value = true
  try {
    const payload = {}
    for (const [k, v] of Object.entries(form.value)) {
      if (v !== '') payload[k] = v
    }

    // Convert number fields from string to float
    if (payload.purchase_price) {
      payload.purchase_price = parseFloat(payload.purchase_price)
    }
    if (payload.current_value) {
      payload.current_value = parseFloat(payload.current_value)
    }

    await assetsStore.updateAsset(route.params.id, payload)
    alert('Asset updated successfully!')
    router.push('/assets')
  } catch (error) {
    console.error('Error updating asset:', error)
    alert('Error updating asset: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const cancelEdit = () => {
  router.push('/assets')
}

const deleteAsset = async () => {
  if (!confirm('Are you sure you want to delete this asset? This action cannot be undone.')) {
    return
  }
  
  try {
    await assetsStore.deleteAsset(route.params.id)
    alert('Asset deleted successfully!')
    router.push('/assets')
  } catch (error) {
    console.error('Error deleting asset:', error)
    alert('Error deleting asset: ' + (error.response?.data?.detail || error.message))
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
    <div class="form-header">
      <h1>{{ isEditMode ? 'Edit Asset' : 'Asset Details' }}</h1>
      <div class="header-actions">
        <router-link to="/assets" class="back-btn">← Back to Assets</router-link>
        <button 
          v-if="!isEditMode" 
          @click="router.push(`/assets/${route.params.id}/edit`)"
          class="btn btn-primary"
        >
          Edit Asset
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading asset details...</div>

    <form v-else-if="asset" @submit.prevent="isEditMode ? submitAsset() : null" class="asset-form">
      <!-- Asset Code (Always Read-only) -->
      <div class="form-group">
        <label for="code">Asset Code</label>
        <input 
          id="code" 
          :value="asset.code"
          type="text" 
          disabled 
          class="readonly-field"
        />
      </div>

      <!-- Name -->
      <div class="form-group">
        <label for="name">Asset Name *</label>
        <input 
          id="name" 
          v-model="form.name" 
          type="text" 
          :disabled="!isEditMode"
          required 
        />
      </div>

      <!-- Description -->
      <div class="form-group">
        <label for="description">Description</label>
        <textarea 
          id="description" 
          v-model="form.description" 
          rows="3" 
          :disabled="!isEditMode"
        />
      </div>

      <!-- Category & Original Department -->
      <div class="form-row">
        <div class="form-group">
          <label for="category">Category *</label>
          <select 
            id="category" 
            v-model="form.category" 
            :disabled="!isEditMode"
            required
          >
            <option value="">Select Category</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label for="department">Original Department *</label>
          <input 
            id="department" 
            :value="asset.department_name"
            type="text" 
            disabled 
            class="readonly-field"
            title="Original department cannot be changed"
          />
          <small class="field-help">This is the department that originally owned this asset</small>
        </div>
      </div>

      <!-- Current Department & Status -->
      <div class="form-row">
        <div class="form-group">
          <label for="current_department">Current Department *</label>
          <input 
  id="current_department"
  :value="asset.current_department_name || 'N/A'"
  type="text"
  disabled
  class="readonly-field"
/>
          <small class="field-help">This is where the asset is currently located</small>
        </div>
        <div class="form-group">
          <label for="status">Status</label>
          <select 
            id="status" 
            v-model="form.status"
            :disabled="!isEditMode"
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="under_maintenance">Under Maintenance</option>
            <option value="disposed">Disposed</option>
          </select>
        </div>
      </div>

      <!-- Purchase Date & Price -->
      <div class="form-row">
        <div class="form-group">
          <label for="purchase_date">Purchase Date *</label>
          <input 
            id="purchase_date" 
            v-model="form.purchase_date" 
            type="date" 
            :disabled="!isEditMode"
            required 
          />
        </div>
        <div class="form-group">
          <label for="purchase_price">Purchase Price *</label>
          <input 
            id="purchase_price" 
            v-model="form.purchase_price" 
            type="number" 
            step="0.01" 
            :disabled="!isEditMode"
            required 
          />
        </div>
      </div>

      <!-- Current Value -->
      <div class="form-group">
        <label for="current_value">Current Value</label>
        <input 
          id="current_value" 
          v-model="form.current_value" 
          type="number" 
          step="0.01" 
          :disabled="!isEditMode"
        />
      </div>

      <!-- Serial, Brand, Model -->
      <div class="form-row">
        <div class="form-group">
          <label for="serial_number">Serial Number</label>
          <input 
            id="serial_number" 
            v-model="form.serial_number" 
            type="text" 
            :disabled="!isEditMode"
          />
        </div>
        <div class="form-group">
          <label for="brand">Brand</label>
          <input 
            id="brand" 
            v-model="form.brand" 
            type="text" 
            :disabled="!isEditMode"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="model">Model</label>
        <input 
          id="model" 
          v-model="form.model" 
          type="text" 
          :disabled="!isEditMode"
        />
      </div>

      <!-- Created By & Dates (Always Read-only) -->
      <div class="form-row readonly-info">
        <div class="form-group">
          <label>Created By</label>
          <input 
            :value="asset.created_by_name"
            type="text" 
            disabled 
            class="readonly-field"
          />
        </div>
        <div class="form-group">
          <label>Created At</label>
          <input 
            :value="new Date(asset.created_at).toLocaleDateString()"
            type="text" 
            disabled 
            class="readonly-field"
          />
        </div>
      </div>

      <!-- Form Actions (Only in Edit Mode) -->
      <div v-if="isEditMode" class="form-actions">
        <button type="button" @click="cancelEdit" class="cancel-btn">Cancel</button>
        <button 
          type="button" 
          @click="deleteAsset"
          class="delete-btn"
          v-if="authStore.user?.role === 'admin'"
        >
          Delete Asset
        </button>
        <button type="submit" :disabled="saving" class="submit-btn">
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.edit-asset {
  max-width: 800px;
  margin: 40px auto;
  padding: 24px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  font-family: sans-serif;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.form-header h1 {
  margin: 0;
  font-size: 24px;
  color: #1f2937;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.back-btn {
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
}

.back-btn:hover {
  text-decoration: underline;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

.asset-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-row .form-group {
  flex: 1;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group label {
  font-weight: 600;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

/* Read-only field styles */
.readonly-field,
.form-group input:disabled,
.form-group select:disabled,
.form-group textarea:disabled {
  background-color: #f8fafc !important;
  color: #6b7280 !important;
  cursor: default;
  border-color: #e5e7eb !important;
}

.readonly-info {
  border-top: 1px solid #e5e7eb;
  padding-top: 20px;
  margin-top: 20px;
}

.field-help {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn {
  padding: 10px 20px;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.cancel-btn:hover {
  background: #4b5563;
}

.delete-btn {
  padding: 10px 20px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.delete-btn:hover {
  background: #b91c1c;
}

.submit-btn {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.submit-btn:hover:not(:disabled) {
  background: #0056b3;
}

.submit-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>
