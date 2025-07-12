<template>
  <header v-if="shouldShowNav">
    <nav class="fancy-navbar">
      <UserInfo />
      <div class="main-nav-content">
        <RouterLink to="/" class="logo-link" aria-label="صفحه اصلی">
          <img
            alt="Logo"
            class="logo-img"
            src="@/assets/logo.jpg"
            width="48"
            height="48"
          />
        </RouterLink>
        <ul class="nav-links">
          <li><RouterLink to="/" exact-active-class="active">داشبورد</RouterLink></li>
          <li><RouterLink to="/assets" exact-active-class="active">کالاها</RouterLink></li>
          <li><RouterLink to="/department-assets" exact-active-class="active">بخش ها و کالاها</RouterLink></li>
          <li><RouterLink to="/transfers" exact-active-class="active">انتقالات</RouterLink></li>
          <li><RouterLink to="/departments" exact-active-class="active">بخش ها</RouterLink></li>
          <li><RouterLink to="/brands" exact-active-class="active">برند ها</RouterLink></li>
          <li><RouterLink to="/about" exact-active-class="active">درباره</RouterLink></li>
        </ul>
      </div>

    </nav>
  </header>
  <RouterView />
</template>

<script setup>
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import UserInfo from '@/components/UserInfo.vue'

const route = useRoute()
const authStore = useAuthStore()
const hideNavOnRoutes = ['/login', '/register']

const shouldShowNav = computed(() => {
  return authStore.isAuthenticated && !hideNavOnRoutes.includes(route.path)
})
</script>

<style scoped>
.fancy-navbar {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  direction: ltr; /* الان LTR شد! */
  background: #fff;
  padding: 1rem 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  margin: 1.5rem auto 2.5rem;
  max-width: 960px;
  border: 1px solid #e2e8f0;
  z-index: 10;
  gap: 1.5rem;
}

.main-nav-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 1.5rem;
  direction: rtl; /* فقط این بخش راست‌چین بمونه */
}

.logo-link {
  text-decoration: none;
  display: flex;
  align-items: center;
  margin-left: 2rem;
}

.logo-img {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  object-fit: cover;
  border: 2px solid #e0e0e0;
  background-color: #f1f5f9;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.logo-link:hover .logo-img {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.nav-links {
  display: flex;
  flex-direction: row;
  align-items: center;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 0.5rem;
  direction: rtl; /* منو راست‌چین */
}

.nav-links li {
  display: flex;
  align-items: center;
  margin: 0 0.4rem;
}

.nav-links a {
  color: #334155;
  background: transparent;
  padding: 0.45rem 1rem;
  border-radius: 8px;
  font-weight: 500;
  text-decoration: none;
  font-size: 1rem;
  transition: all 0.2s ease;
  position: relative;
}

.nav-links a:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.nav-links a.active {
  color: #1e40af;
  font-weight: 600;
}

.nav-links a.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 10%;
  width: 80%;
  height: 2px;
  background-color: #1e40af;
  border-radius: 2px;
}

@media (max-width: 600px) {
  .fancy-navbar {
    flex-direction: column;
    align-items: stretch;
    padding: 1rem;
    border-radius: 0 0 16px 16px;
    gap: 1rem;
  }
  .main-nav-content {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  .logo-link {
    margin-left: 0;
    margin-bottom: 1rem;
    justify-content: center;
  }
  .nav-links {
    flex-direction: column;
    gap: 0.3rem;
    width: 100%;
    align-items: flex-start;
  }
  .logo-img {
    margin-bottom: 0.5rem;
    width: 44px;
    height: 44px;
  }
}
</style>
