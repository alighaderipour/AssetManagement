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
          <li><RouterLink to="/categories" exact-active-class="active">دسته بندي ها</RouterLink></li>
          <li><RouterLink to="/brands" exact-active-class="active">برند ها</RouterLink></li>
          <li><RouterLink to="/usecases" exact-active-class="active">مورد کاربرد</RouterLink></li>
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
  direction: ltr;
  background: #fff;
  padding: 1rem 2rem;
  border-radius: 18px;
  box-shadow: 0 4px 20px rgba(120,120,185,0.08);
  margin: 1.5rem auto 2.5rem;
  max-width: 1240px;
  border: 1px solid #e0e7ef;
  gap: 1.5rem;
  font-family: 'Vazirmatn', 'IRANSans', Tahoma, Arial, sans-serif;
  min-height: 72px;
}

.main-nav-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 1.7rem;
  direction: rtl;
}

.logo-link {
  text-decoration: none;
  display: flex;
  align-items: center;
  margin-left: 2.2rem;
  transition: filter 0.2s;
}
.logo-link:hover {
  filter: brightness(1.15);
}

.logo-img {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  object-fit: cover;
  border: 2px solid #e5e8ef;
  background-color: #f3f7fb;
  transition: transform 0.22s, box-shadow 0.22s;
}
.logo-link:hover .logo-img {
  transform: scale(1.075) rotate(-1deg);
  box-shadow: 0 5px 15px rgba(102,126,234,0.16);
}

/* --------------- MODERN WRAPPED NAV LINKS ----------- */
.nav-links {
  display: flex;
  flex-wrap: wrap;         /* این باعث ردیف دوم/سوم می‌شود */
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 0.45rem 0.9rem;    /* gap: vertical horizontal */
  direction: rtl;
  width: 100%;
  font-size: 1.02rem;
  min-height: 46px;
}

.nav-links li {
  display: flex;
  align-items: center;
  white-space: nowrap;
}

.nav-links a {
  color: #334155;
  background: linear-gradient(90deg,#f1f5fd 0,#f7faff 100%);
  box-shadow: 0 2px 7px rgba(163,179,245,0.06);
  padding: 0.44rem 1.14rem;
  border-radius: 9px;
  font-weight: 500;
  text-decoration: none;
  font-size: 1.04rem;
  margin: 0.12rem 0;
  transition: all 0.17s cubic-bezier(.34,1.56,.64,1);
  position: relative;
  border: 1px solid transparent;
  outline: none;
}
.nav-links a:hover, .nav-links a:focus-visible {
  background: linear-gradient(90deg,#f0f7ff 0,#dbeafe 100%);
  color: #273278;
  border-color: #bfdcff;
  box-shadow: 0 5px 16px rgba(120,160,255,0.12);
}
.nav-links a.active {
  color: #353ef1;
  font-weight: 700;
  background: linear-gradient(92deg,#e0e7ff 60%,#f0f7ff 100%);
  border-color: #a5b4fc;
  box-shadow: 0 1px 16px rgba(85,124,255,0.10);
}

.nav-links a.active::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 18%;
  width: 64%;
  height: 2.5px;
  background-color: #6366f1;
  border-radius: 2.5px;
}

/* سوییچ به حالت کولومنی برای اصلی‌ترین بخش‌ها در موبایل */
@media (max-width: 900px) {
  .fancy-navbar {
    flex-direction: column;
    align-items: stretch;
    padding: 1rem 0.5rem 0.7rem 0.5rem;
    border-radius: 0 0 18px 18px;
    gap: 1.25rem;
  }
  .main-nav-content {
    flex-direction: column;
    align-items: stretch;
    gap: 1.1rem;
  }
  .logo-link {
    margin-left: 0;
    margin-bottom: 1rem;
    justify-content: center;
  }
  .nav-links {
    font-size: 0.97rem;
    gap: 0.35rem 0.57rem;
    justify-content: center;
    min-height: 40px;
    width: 100%;
  }
  .logo-img {
    width: 43px;
    height: 43px;
    margin-bottom: 0.6rem;
  }
}

/* برای موبایل‌های کوچکتر */
@media (max-width: 570px) {
  .fancy-navbar {
    padding: 0.4rem 0.1rem 0.7rem 0.1rem;
    border-radius: 0 0 14px 14px;
  }
  .nav-links {
    font-size: 0.93rem;
    gap: 0.3rem 0.22rem;
    min-height: 35px;
  }
  .logo-img {
    width: 38px;
    height: 38px;
  }
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
