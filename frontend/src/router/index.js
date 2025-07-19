// frontend/src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import Login from "@/views/Login.vue";
import Dashboard from "@/views/Dashboard.vue";
import Assets from "@/views/Assets.vue";
import AddAsset from "@/views/AddAsset.vue";
import EditAsset from "@/components/EditAsset.vue";
import About from "@/views/About.vue";
import Transfers from "@/components/Transfers.vue";
import { useAuthStore } from "@/stores/auth";

const routes = [
  {
    path: "/",
    redirect: "/dashboard",
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
  },
  {
    path: "/about",
    name: "About",
    component: About,
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: "/assets",
    name: "Assets",
    component: Assets,
    meta: { requiresAuth: true },
  },
    {
  path: '/departments',
  name: 'Departments',
  component: () => import('@/views/Departments.vue'),
  meta: { requiresAuth: true }
}
,
    {
  path: '/department-assets',
  name: 'DepartmentAssets',
  component: () => import('@/views/DepartmentsAssets.vue'),
}
,
  {
    path: "/assets/add",
    name: "AddAsset",
    component: AddAsset,
    meta: { requiresAuth: true },
  },
  // ✅ Keep the more specific route BEFORE the general one
  {
    path: "/assets/:id/edit",
    name: "EditAsset",
    component: EditAsset,
    meta: { requiresAuth: true },
  },
    {
  path: '/brands',
  name: 'Brands',
  component: () => import('@/views/Brands.vue'),
  meta: { requiresAuth: true }
},
    {
  path: '/categories',
  name: 'Categories',
  component: () => import('@/views/Categories.vue'),
  meta: { requiresAuth: true }
}
,
  // ✅ This should come after the /edit route
  {
    path: "/assets/:id",
    name: "AssetDetail",
    component: EditAsset, // Using the same component for now
    meta: { requiresAuth: true },
  },
    {
  path: '/usecases',
  name: 'UseCases',
  component: () => import('@/views/UseCases.vue')
},
  {
    path: "/transfers",
    name: "Transfers",
    component: Transfers,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next("/login");
  } else {
    next();
  }
});

export default router;
