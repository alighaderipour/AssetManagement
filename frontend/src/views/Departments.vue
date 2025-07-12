<template>
  <div class="departments-page">
    <h2>مدیریت بخش‌ها</h2>

    <form @submit.prevent="handleSubmit" class="form">
      <input v-model="form.name" required placeholder="نام بخش" class="input" />
      <input v-model="form.code" required placeholder="کد یکتا" class="input" />
      <input v-model="form.description" placeholder="توضیحات (اختیاری)" class="input" />
      <select v-model="form.type" required class="input">
        <option value="hospital">بخش بیمارستانی</option>
        <option value="maintenance">بخش پشتیبانی/تعمیرات</option>
      </select>
      <button type="submit" class="btn primary">
        {{ form.id ? "ویرایش" : "افزودن" }}
      </button>
      <button v-if="form.id" type="button" @click="resetForm" class="btn secondary">
        انصراف
      </button>
    </form>

    <div v-if="departments.length === 0" class="no-data">
      هیچ بخشی ثبت نشده است.
    </div>

    <table v-else class="table">
      <thead>
        <tr>
          <th>نام بخش</th>
          <th>کد</th>
          <th>توضیحات</th>
          <th>نوع بخش</th>
          <th>عملیات</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="dept in departments" :key="dept.id">
          <td>{{ dept.name }}</td>
          <td>{{ dept.code }}</td>
          <td>{{ dept.description }}</td>
          <td>
            <span class="tag" :class="dept.type">
              {{ dept.type === 'hospital' ? 'بیمارستانی' : 'پشتیبانی/تعمیرات' }}
            </span>
          </td>
          <td class="actions">
            <button @click="edit(dept)" class="btn small">ویرایش</button>
            <button @click="remove(dept.id)" class="btn danger small">حذف</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { apiRequest } from '@/stores/assets'

const authStore = useAuthStore()
const departments = ref([])

const form = ref({ name: '', code: '', type: 'hospital', description: '', id: null })
const fetchDepartments = async () => {
  try {
    const res = await apiRequest('/api/departments/')
    departments.value = res.results || res
  } catch (err) {
    console.error('❌ دریافت بخش‌ها با خطا مواجه شد:', err.message)
  }
}
const handleSubmit = async () => {
  try {
    if (form.value.id) {
      await apiRequest(`/api/departments/${form.value.id}/`, 'PATCH', form.value)
    } else {
      await apiRequest('/api/departments/', 'POST', form.value)
    }
    resetForm()
    await fetchDepartments()
  } catch (err) {
    alert('خطا: ' + err.message)
  }
}
const edit = (dept) => {
  form.value = { ...dept }
}
const resetForm = () => {
  form.value = { name: '', code: '', description: '', type: 'hospital', id: null }
}
const remove = async (id) => {
  if (!confirm('آیا مطمئن هستید می‌خواهید این بخش را حذف کنید؟')) return
  try {
    await apiRequest(`/api/departments/${id}/`, 'DELETE')
    await fetchDepartments()
  } catch (err) {
    alert('خطا: ' + err.message)
  }
}
onMounted(() => {
  fetchDepartments()
})
</script>

<style scoped>
.departments-page {
  direction: rtl;
  font-family: 'Vazirmatn', 'IRANSans', Tahoma, sans-serif;
  max-width: 900px;
  margin: 2rem auto;
  padding: 2.5rem 1.5rem;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 6px 28px 0 rgba(30,41,59,0.12);
}

h2 {
  margin-bottom: 2rem;
  font-size: 1.8rem;
  font-weight: 800;
  color: #334155;
  text-align: center;
  letter-spacing: -0.02em;
}

.form {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: flex-start;
  align-items: flex-end;
  margin-bottom: 2.5rem;
  background: #f9fafb;
  border-radius: 10px;
  padding: 1.4rem;
  box-shadow: 0 1px 5px 0 rgba(30,41,59,0.06);
}

.input {
  flex: 1 1 200px;
  padding: 11px 17px;
  font-size: 1.05rem;
  border: 1.2px solid #d1d5db;
  border-radius: 7px;
  background: #ffffff;
  margin-bottom: 0;
  color: #222;
  transition: border 0.2s;
}
.input:focus {
  border: 1.4px solid #7c3aed;
  outline: none;
}

.btn {
  padding: 0.65rem 1.35rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  margin-right: 0.5rem;
  transition: background 0.18s, box-shadow 0.18s;
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.07);
}

.btn.primary {
  background: linear-gradient(90deg, #7c3aed 0, #818cf8 100%);
  color: white;
}
.btn.primary:hover {
  background: linear-gradient(90deg,#6366f1 0,#4f46e5 100%);
}
.btn.secondary {
  background-color: #e0e7ef;
  color: #373b44;
}
.btn.secondary:hover {
  background-color: #cbd5e1;
}
.btn.small {
  font-size: 0.93rem;
  padding: 0.33rem 1.1rem;
}
.btn.danger {
  background: #ef4444;
  color: #fff;
}
.btn.danger:hover {
  background-color: #b91c1c;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1.2rem;
  background: #fcfcfd;
  border-radius: 10px;
  overflow: hidden;
  font-size: 1.04rem;
  letter-spacing: -0.01em;
  direction: rtl;
}

.table th, .table td {
  padding: 0.85rem 1.25rem;
  border-bottom: 1.5px solid #f1f5f9;
  text-align: right;
  vertical-align: middle;
}
.table th {
  background: #f3f4f6;
  font-weight: 700;
  color: #4f46e5;
  font-size: 1.08em;
}
.table tr:last-child td {
  border-bottom: none;
}
.actions {
  white-space: nowrap;
  display: flex;
  gap: 0.5rem;
}

.no-data {
  padding: 2rem;
  text-align: center;
  font-style: italic;
  color: #64748b;
}

.tag {
  display: inline-block;
  padding: 0.28em 0.95em;
  font-size: 1em;
  border-radius: 8px;
  background: #e0e7ff;
  color: #5b21b6;
  font-weight: 700;
  box-shadow: 0 1px 4px rgba(92, 29, 206, 0.06);
}
.tag.hospital {
  background: #dbeafe;
  color: #0369a1;
}
.tag.maintenance {
  background: #fee2e2;
  color: #c026d3;
}
</style>
