<template>
  <div class="usecases-container">
    <h2>موارد استفاده (UseCases)</h2>
    <form @submit.prevent="isEditing ? updateUseCase() : createUseCase()">
      <div>
        <label>نام:</label>
        <input v-model="form.name" required />
      </div>
      <div>
        <label>توضیحات:</label>
        <input v-model="form.description" />
      </div>
      <button type="submit" :disabled="loading">
        {{ isEditing ? 'ویرایش' : 'ایجاد' }}
      </button>
      <button type="button" v-if="isEditing" @click="cancelEdit" class="cancel">لغو</button>
    </form>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="loading" class="loading">در حال بارگذاری...</div>

    <table v-if="usecases.length">
      <thead>
        <tr>
          <th>شناسه</th>
          <th>نام</th>
          <th>کد</th>
          <th>توضیحات</th>
          <th>عملیات</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="uc in usecases" :key="uc.id">
          <td>{{ uc.id }}</td>
          <td>{{ uc.name }}</td>
          <td>{{ uc.code }}</td>
          <td>{{ uc.description }}</td>
          <td>
            <button @click="editUseCase(uc)">ویرایش</button>
            <button @click="deleteUseCase(uc.id)">حذف</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else>هیچ داده‌ای یافت نشد.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const accessToken = localStorage.getItem('access_token')
const usecases = ref([])
const form = ref({ name: '', description: '' })
const isEditing = ref(false)
const editingId = ref(null)
const loading = ref(false)
const error = ref(null)

const fetchUseCases = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await fetch(`${API_URL}/usecases/`, {
      headers: { Authorization: `Bearer ${accessToken}` }
    })
    if (!res.ok) throw new Error('Error loading usecases')
    usecases.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const createUseCase = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await fetch(`${API_URL}/usecases/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(form.value),
    })
    if (!res.ok) {
      const data = await res.json()
      throw new Error(JSON.stringify(data))
    }
    form.value = { name: '', description: '' }
    await fetchUseCases()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const editUseCase = (uc) => {
  form.value = { name: uc.name, description: uc.description }
  isEditing.value = true
  editingId.value = uc.id
}

const updateUseCase = async () => {
  if (!editingId.value) return
  loading.value = true
  error.value = null
  try {
    const res = await fetch(`${API_URL}/usecases/${editingId.value}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(form.value),
    })
    if (!res.ok) {
      const data = await res.json()
      throw new Error(JSON.stringify(data))
    }
    form.value = { name: '', description: '' }
    isEditing.value = false
    editingId.value = null
    await fetchUseCases()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const deleteUseCase = async (id) => {
  if (!confirm('آیا مطمئن هستید؟')) return
  loading.value = true
  error.value = null
  try {
    const res = await fetch(`${API_URL}/usecases/${id}/`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${accessToken}` },
    })
    if (!res.ok) throw new Error('مشکل در حذف مورد استفاده')
    await fetchUseCases()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const cancelEdit = () => {
  isEditing.value = false
  editingId.value = null
  form.value = { name: '', description: '' }
  error.value = null
}

onMounted(fetchUseCases)
</script>

<style scoped>
.usecases-container {
  max-width: 600px;
  margin: 40px auto;
  background: #fff;
  font-family: Vazirmatn, Tahoma, sans-serif;
  border-radius: 15px;
  box-shadow: 0 0 14px #a6a6a655;
  padding: 2rem;
  direction: rtl;
}
form {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: end;
  margin-bottom: 2rem;
}
form > div {
  flex: 1;
  min-width: 160px;
}
input {
  padding: 7px 10px;
  border-radius: 6px;
  border: 1px solid #d4d4d4;
  font-size: 1rem;
}
button {
  background: #137e82;
  color: #fff;
  border: none;
  padding: 8px 18px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-family: inherit;
  transition: 0.2s;
}
button.cancel {
  background: #888;
}
button:disabled { opacity: 0.5; cursor: not-allowed }
.error { color: #b21d17; margin: 9px 0; }
.loading { color: #137e82; }
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 2rem;
  font-size: 1rem;
}
th, td {
  padding: 8px 12px;
  border-bottom: 1px solid #eee;
  text-align: right;
}
th { background: #ededed; }
@media (max-width: 700px) {
  .usecases-container { padding:1rem }
  table { font-size: .9rem }
  th, td { padding:5px 8px }
}
</style>
