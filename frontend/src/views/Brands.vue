<template>
  <div class="brands-page">
    <h1>مدیریت برندها</h1>
    <form @submit.prevent="addBrand">
      <input v-model="newBrand.name" placeholder="نام برند" required>
      <input v-model="newBrand.description" placeholder="توضیحات برند">
      <button type="submit">افزودن برند</button>
    </form>

    <!-- جدول برندها -->
    <table class="brands-table" v-if="brands.length">
      <thead>
        <tr>
          <th>ردیف</th>
          <th>نام برند</th>
          <th>کد</th>
          <th>توضیحات</th>
          <th>عملیات</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(brand, i) in brands" :key="brand.id">
          <td>{{ i + 1 }}</td>
          <td><b>{{ brand.name }}</b></td>
          <td>{{ brand.code }}</td>
          <td style="max-width:130px; white-space:pre-wrap;">{{ brand.description }}</td>
          <td>
            <button class="secondary" @click="setEdit(brand)">ویرایش</button>
            <button class="danger" @click="deleteBrand(brand.id)">حذف</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else class="empty-list">برند فعالی ثبت نشده است.</div>

    <!-- فرم ویرایش برند -->
    <div v-if="editingBrand" class="edit-box">
      <h3>ویرایش برند</h3>
      <input v-model="editingBrand.name" placeholder="نام برند">
      <input v-model="editingBrand.description" placeholder="توضیحات برند">
      <div class="actions">
        <button @click="updateBrand">ذخیره</button>
        <button class="secondary" @click="cancelEdit">لغو</button>
      </div>
    </div>

    <div v-if="loading" class="loading">درحال بارگذاری ...</div>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api"

const brands = ref([])
const newBrand = ref({ name: '', description: '' })
const editingBrand = ref(null)
const loading = ref(false)
const error = ref('')

function getAuthHeaders() {
  const token = localStorage.getItem('access_token')
  return token
    ? { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
    : { 'Content-Type': 'application/json' }
}

// دریافت لیست برندها
async function fetchBrands() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${API_URL}/brands/`, {
      headers: getAuthHeaders()
    })
    const contentType = res.headers.get("content-type");
    const rawText = await res.text();


    if (!res.ok) {
      throw new Error(`خطا (${res.status}): ${rawText}`);
    }
    if (!contentType || !contentType.includes("application/json")) {
      throw new Error('پاسخ سرور JSON نیست!');
    }
    brands.value = JSON.parse(rawText).sort((a, b) => a.name.localeCompare(b.name, 'fa'))
  } catch (err) {
    error.value = err.message
    brands.value = []
  } finally {
    loading.value = false
  }
}



async function addBrand() {
  error.value = ''
  try {
    const res = await fetch(`${API_URL}/brands/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(newBrand.value)
    })
    if (res.status === 401) throw new Error('ابتدا وارد حساب شوید.')
    if (!res.ok) throw new Error('خطا در افزودن برند')
    const data = await res.json()
    brands.value.push(data)
    newBrand.value = { name: '', description: '' }
  } catch (err) {
    error.value = err.message
  }
}

async function deleteBrand(id) {
  if(!confirm('آیا مطمئن هستید؟')) return
  error.value = ''
  try {
    const res = await fetch(`${API_URL}/brands/${id}/`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    if (res.status === 401) throw new Error('ابتدا وارد حساب شوید.')
    if (!res.ok) throw new Error('خطا در حذف برند')
    brands.value = brands.value.filter(b => b.id !== id)
  } catch (err) {
    error.value = err.message
  }
}

function setEdit(brand) {
  editingBrand.value = { ...brand }
}
function cancelEdit() {
  editingBrand.value = null
}

async function updateBrand() {
  error.value = ''
  try {
    const res = await fetch(`${API_URL}/brands/${editingBrand.value.id}/`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(editingBrand.value)
    })
    if (res.status === 401) throw new Error('ابتدا وارد حساب شوید.')
    if (!res.ok) throw new Error('خطا در ویرایش برند')
    const data = await res.json()
    const idx = brands.value.findIndex(b => b.id === editingBrand.value.id)
    brands.value[idx] = data
    editingBrand.value = null
  } catch (err) {
    error.value = err.message
  }
}

onMounted(fetchBrands)
</script>

<style scoped>
.brands-page {
  max-width: 670px;
  margin: 2.5rem auto 1.7rem auto;
  background: #fff;
  box-shadow: 0 8px 28px rgba(60, 72, 88, 0.13), 0 1.5px 6px rgba(71, 110, 247, 0.08);
  border-radius: 16px;
  padding: 2.1rem 2.3rem 2.2rem 2.3rem;
  direction: rtl;
  font-family: Vazirmatn, IRANSans, tahoma, sans-serif;
}

h1 {
  text-align: center;
  margin-bottom: 2.2rem;
  font-size: 2rem;
  color: #2563eb;
  letter-spacing: 0.7px;
  font-weight: 800;
}

/* فرم افزودن */
form {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
  justify-content: center;
  margin-bottom: 2.05rem;
}

input {
  border: 1.5px solid #d5d9ee;
  outline: none;
  border-radius: 7px;
  padding: 0.66rem 1rem;
  font-size: 1rem;
  transition: border 0.22s, background 0.15s;
  background: #f9fafc;
  flex: 1 1 120px;
  min-width: 0;
}
input:focus {
  border-color: #2563eb;
  background: #fff;
}

button {
  background: linear-gradient(90deg, #2563eb 70%, #6698fa 100%);
  color: #fff;
  font-size: 1.05rem;
  border: none;
  border-radius: 7px;
  font-weight: 600;
  padding: 0.62rem 1.40rem;
  cursor: pointer;
  min-width: 100px;
  transition: background 0.18s, box-shadow 0.18s, transform 0.15s;
  box-shadow: 0 2px 12px rgba(37,99,235,0.09);
}
button:active { transform: scale(0.98);}
button:hover:not(.secondary):not(.danger) {
  background: linear-gradient(90deg, #1e429f 70%, #5182e8 100%);
  box-shadow: 0 5px 24px 0 rgba(37,99,235,0.18);
}

button.secondary {
  background: #e6edf9;
  color: #2571ec;
  border: 1.5px solid #b8cfff;
  box-shadow: none;
  min-width: 80px;
  margin-left: 0.2rem;
  font-weight: 500;
}
button.secondary:hover {
  background: #e0e7fa;
  border-color: #2563eb;
  color: #1854b1;
}

button.danger {
  background: #fff2f3;
  color: #c1122f;
  border: 1.5px solid #fdc7d3;
  box-shadow: none;
  font-weight: 500;
  min-width: 80px;
}
button.danger:hover {
  background: #ffd6da;
  border-color: #f04153;
  color: #74091d;
}

/* جدول برندها */
.brands-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: #f7faff;
  border-radius: 12px;
  box-shadow: 0 2px 10px 0 rgba(37,99,235,0.07);
  overflow: hidden;
  margin-bottom: 2.6rem;
  font-size: 1.08rem;
  direction: rtl;
}

.brands-table th, .brands-table td {
  padding: 0.82rem 0.7rem;
  text-align: right;
}
.brands-table th {
  background: #e7f2ff;
  color: #2e4780;
  font-size: 1.04rem;
  font-weight: 700;
  border-bottom: 2px solid #c4dcfb;
  position: sticky;
  top: 0;
  z-index: 2;
}
.brands-table td {
  border-bottom: 1px solid #e0e7f7;
}
.brands-table th:last-child, .brands-table td:last-child {
  text-align: center;
}

.brands-table tbody tr:last-child td {
  border-bottom: none;
}

.brands-table tbody tr {
  transition: background 0.14s;
}
.brands-table tbody tr:hover {
  background: #e6eefe;
}

.empty-list {
  color: #767e9d;
  text-align: center;
  font-size: 1.1rem;
  margin: 2.5rem 0 2rem 0;
}

.loading {
  color: #185abc;
  text-align: center;
  font-size: 1.09rem;
  margin: 1rem 0 .7rem 0;
}

.edit-box {
  background: #f6f9fc;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(60, 72, 88, 0.05);
  padding: 1.3rem 1.2rem 1rem 1.2rem;
  margin-top: 1.5rem;
  direction: rtl;
}
.edit-box h3 {
  color: #2563eb;
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 1rem;
  margin-right: 0.5rem;
}
.edit-box .actions {
  margin-top: 0.9rem;
  display: flex;
  gap: 0.8rem;
}

.error {
  background: #ffe6e9;
  color: #be2236;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  text-align: center;
  margin-top: 1.2rem;
  font-size: 1.04rem;
  box-shadow: 0 2px 8px 0 rgba(185,32,62,0.04)
}

@media (max-width: 850px) {
  .brands-page { max-width: 99vw; padding: 1.2rem 0.6rem; }
  .brands-table th, .brands-table td { font-size: 1.01rem; }
  .brands-page h1 { font-size: 1.4rem; }
}
@media (max-width: 600px) {
  .brands-page { max-width: 99vw; padding: 1rem 0.4rem; }
  .brands-table { font-size: 0.97rem;}
  .brands-page form { flex-direction: column; gap: .75rem;}
  .brands-table th, .brands-table td { padding: 0.5rem 0.18rem;}
}
</style>
