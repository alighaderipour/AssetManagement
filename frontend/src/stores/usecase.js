// src/stores/usecase.js

import { defineStore } from "pinia";
import { ref } from "vue";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export const useUsecaseStore = defineStore("usecase", () => {
  const usecases = ref([]);
  const loading = ref(false);
  const error = ref(null);

  async function fetchUsecases() {
    loading.value = true;
    error.value = null;
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${API_BASE}/api/usecases/`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) throw new Error("UseCases load error!");

      const data = await res.json();
      usecases.value = data.results || data; // DRF-style or array
      return usecases.value;
    } catch (err) {
      error.value = err.message;
      usecases.value = [];
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    usecases,
    loading,
    error,
    fetchUsecases,
  };
});
