<template>
  <div class="categories-page">
    <h2>مدیریت دسته‌بندی‌ها</h2>

    <!-- پیام موفقیت و خطا -->
    <div v-if="successMsg" class="msg success">{{ successMsg }}</div>
    <div v-if="errorMsg" class="msg error">{{ errorMsg }}</div>

    <form @submit.prevent="handleSubmit" class="form">
      <input v-model="form.name" required placeholder="نام" class="input" />
      <input v-model="form.code" required placeholder="کد (یکتا)" class="input" />
      <input v-model="form.description" placeholder="توضیحات" class="input" />
      <button type="submit" class="btn primary">
        {{ form.id ? "ویرایش" : "افزودن" }}
      </button>
      <button v-if="form.id" type="button" @click="resetForm" class="btn secondary">
        لغو
      </button>
    </form>

    <div v-if="categories.length === 0" class="no-data">دسته‌بندی‌ای یافت نشد.</div>

    <table v-else class="table">
      <thead>
        <tr>
          <th>نام</th>
          <th>کد</th>
          <th>توضیحات</th>
          <th>عملیات</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="cat in categories" :key="cat.id">
          <td>{{ cat.name }}</td>
          <td>{{ cat.code }}</td>
          <td>{{ cat.description }}</td>
          <td>
            <button @click="edit(cat)" class="btn small">ویرایش</button>
            <button @click="remove(cat.id)" class="btn danger small">حذف</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
// اگر با axios کار می‌کنی این خط رو uncomment کن: import axios from 'axios'
// اگر apiRequest شخصی داری، این رو نگه دار:
import { apiRequest } from '@/stores/assets'

const authStore = useAuthStore()
const categories = ref([])
const form = ref({ name: '', code: '', description: '', id: null })

const successMsg = ref('')
const errorMsg = ref('')

const fetchCategories = async () => {
  try {
    const res = await apiRequest('/api/categories/')
    categories.value = res.results || res
  } catch (err) {
    errorMsg.value = 'دریافت دسته‌بندی‌ها با خطا مواجه شد'
    setTimeout(() => errorMsg.value = '', 4000)
  }
}

const handleSubmit = async () => {
  errorMsg.value = successMsg.value = ''
  try {
    if (form.value.id) {
      await apiRequest(`/api/categories/${form.value.id}/`, 'PATCH', form.value)
      successMsg.value = 'دسته‌بندی با موفقیت ویرایش شد.'
    } else {
      await apiRequest('/api/categories/', 'POST', form.value)
      successMsg.value = 'دسته‌بندی جدید اضافه شد.'
    }
    resetForm()
    await fetchCategories()
    setTimeout(() => successMsg.value = '', 2500)
  } catch (err) {
    errorMsg.value = err?.response?.data?.name?.[0] || 'خطا در ثبت اطلاعات'
    setTimeout(() => errorMsg.value = '', 3200)
  }
}

const edit = (cat) => {
  form.value = { ...cat }
}

const resetForm = () => {
  form.value = { name: '', code: '', description: '', id: null }
}

const remove = async (id) => {
  if (!confirm('آیا از حذف این دسته‌بندی مطمئن هستید؟')) return
  try {
    await apiRequest(`/api/categories/${id}/`, 'DELETE')
    await fetchCategories()
    successMsg.value = 'دسته‌بندی حذف شد.'
    setTimeout(() => successMsg.value = '', 2000)
  } catch (err) {
    errorMsg.value = 'خطا در حذف دسته‌بندی'
    setTimeout(() => errorMsg.value = '', 2800)
  }
}

onMounted(fetchCategories)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600&display=swap');

.categories-page {
  max-width: 860px;
  margin: 2.2rem auto;
  padding: 2.6rem 2rem 2rem 2rem;
  background: linear-gradient(140deg, #f6fafd 70%, #eae9ff 110%);
  border-radius: 19px;
  box-shadow: 0 6px 32px 0 rgba(0,59,119,.08), 0 1.5px 13px 0 rgba(98,0,238,0.08);
  font-family: "Vazirmatn", iransans, sans-serif;
  direction: rtl;
}

h2 {
  margin-bottom: 1.8rem;
  font-size: 24px;
  font-weight: bold;
  color: #2c3453;
  letter-spacing: 0.01em;
  text-align: right;
}

.form {
  display: flex;
  flex-wrap: wrap;
  gap: 1.1rem;
  margin-bottom: 2.2rem;
  background: #fbfbfe;
  padding: 1.1rem 1.1rem 0.7rem .8rem;
  border-radius: 9px;
  box-shadow: 0 2px 11px -4px #779eca05;
}

.input {
  flex: 1 1 220px;
  min-width: 150px;
  padding: .5rem 1rem;
  border: 1px solid #e3e7ef;
  border-radius: 7px;
  font-size: 1rem;
  background: #fff;
  transition: border-color .18s, box-shadow .18s;
  outline: none;
}
.input:focus {
  border-color: #7b4cff;
  box-shadow: 0 2px 9px #a1a9fd17;
}

.btn {
  padding: .48rem 1.2rem;
  border-radius: 7px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-family: inherit;
  font-size: 1.07rem;
  transition: all .14s;
  outline: none;
  box-shadow: 0 2px 7px -6px #787bff38;
  margin-bottom: .2rem;
  margin-left: .3rem;
}
.btn.primary {
  background: linear-gradient(90deg,#7b4cff 60%,#665aff 100%);
  color: #fff;
  font-weight: bold;
}
.btn.primary:hover {
  background: linear-gradient(92deg,#5b2ded 67%,#22146b 100%);
  transform: translateY(-2px) scale(1.04);
}
.btn.secondary {
  background: #f5f6fa;
  color: #664fff;
  border: 1px solid #d4d8f7;
}
.btn.secondary:hover {
  background: #e6e9fd;
}
.btn.small {
  font-size: .91rem;
  padding: 0.3rem 1.1rem;
  background: #f1f4fd;
  color: #615add;
  border: 1px solid #e3eafe;
}
.btn.small:hover {
  background: #e6eafc;
  color: #232365;
  border-color: #c7d2fb;
  transform: scale(1.1);
}
.btn.danger {
  background: linear-gradient(88deg,#fa6060 70%,#f13e4f 110%);
  color: #fff;
}
.btn.danger:hover {
  background: linear-gradient(77deg,#b31240 60%,#88213c 100%);
  color: #fff;
  scale: 1.03;
}

.table {
  width: 100%;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1.5px 7px #7770f008;
  margin-bottom: 1.9rem;
}
.table th,
.table td {
  padding: 1rem 0.9rem;
  text-align: right;
  border-bottom: 1.5px solid #eef1fb;
}
.table th {
  background-color: #f6f5fd;
  color: #474979;
  letter-spacing: 0.015em;
  font-weight: 700;
  font-size: 1.02rem;
  border-bottom: 2.5px solid #e7e7f0;
}
.table tr {
  transition: background .13s;
}
.table tr:nth-child(even) {
  background: #f7faff;
}
.table tr:hover {
  background: #dee7fa4c;
}
.table td {
  color: #292b37;
  font-size: 1.01rem;
}

.no-data {
  padding: 2.5rem 1rem;
  text-align: center;
  font-style: italic;
  color: #b8b9e2;
  letter-spacing: .05em;
  font-size: 1.14rem;
}

.msg {
  margin-bottom: 1.2rem;
  padding: .7rem 1.2rem;
  border-radius: 7px;
  font-weight: 500;
  font-size: 1.02rem;
  box-shadow: 0 0 4px #e1e5fc7c;
  animation: fadein .7s;
}
.msg.success { background: #ecfbec; color: #1b6b28; border: 1px solid #5fb969; }
.msg.error { background: #fff2f2; color: #ba2832; border: 1px solid #ffb8b8; }

@keyframes fadein { from { opacity: 0; transform: translateY(-10px);} to { opacity: 1; transform: none; } }

::-webkit-scrollbar {
  height: 8px; width: 8px;
  background: #f6f6ff;
  border-radius: 20px;
}
::-webkit-scrollbar-thumb {
  background: #dadaf8;
  border-radius: 15px;
}
::-webkit-scrollbar-thumb:hover {
  background: #b8baf2;
}
</style>
