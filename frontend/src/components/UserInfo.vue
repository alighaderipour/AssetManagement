<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="user-info">
    <button @click="logout" class="logout-btn">خروج</button>

  </div>
</template>

<style scoped>
.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-direction: row-reverse;
}
.farsi-greeting {
  direction: rtl;
  font-family: "Vazirmatn", Tahoma, sans-serif;
  font-weight: 600;
  font-size: 1.1rem;
  color: #2d3748;
  background-color: #edf2f7;
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  display: inline-block;
  line-height: 1.4;
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

/* Responsive (optional): */
@media (max-width: 600px) {
  .user-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
