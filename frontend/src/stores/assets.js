// frontend/src/stores/assets.js
import { defineStore } from "pinia";
import { ref } from "vue";
import { useAuthStore } from "@/stores/auth"; // Make sure this path is correct

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// API helper function

export async function apiRequest(url, method = "GET", data = null) {
  const token = localStorage.getItem("access_token");

  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };

  const config = {
    method,
    headers,
  };

  if (data) {
    config.body = JSON.stringify(data);
  }

  const response = await fetch(`http://localhost:8000${url}`, config);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

async function transferAsset(assetId, departmentId) {
  const payload = { department: departmentId };

  const response = await apiRequest(
    `/api/assets/${assetId}/transfer/`,
    "PUT",
    payload
  );
  return response;
}



export const useAssetsStore = defineStore("assets", () => {
  // At the top-level inside defineStore:
  const count = ref(0);
  const next = ref(null);
  const previous = ref(null);
  const error = ref(null);

  // State
  const assets = ref([]);
  const departments = ref([]);
  const categories = ref([]);
  const loading = ref(false);

  // Actions
 const fetchAssets = async (params = {}) => {
    loading.value = true;
    error.value = null;
    try {
      const queryParams = new URLSearchParams(params);
      const data = await apiRequest(`/api/assets/?${queryParams}`);
      assets.value = data.results || data;
      count.value = data.count ?? assets.value.length;
      next.value = data.next;
      previous.value = data.previous;
      return data;
    } catch (err) {
      error.value = "Error fetching assets";
      throw err;
    } finally {
      loading.value = false;
    }
  };


  const getAsset = async (id) => {
    try {
      const data = await apiRequest(`/api/assets/${id}/`);
      return data;
    } catch (error) {
      console.error("Error fetching asset:", error);
      throw error;
    }
  };

const addAsset = async (assetData) => {
  try {
    // ✅ CORRECT: method string, then data
    const data = await apiRequest("/api/assets/", "POST", assetData);
    assets.value.push(data);
    return data;
  } catch (error) {
    console.error("Error adding asset:", error);
    throw error;
  }
};


const updateAsset = async (id, assetData) => {
  try {
    const data = await apiRequest(`/api/assets/${id}/`, "PATCH", assetData);
    const index = assets.value.findIndex((p) => p.id === parseInt(id));
    if (index !== -1) assets.value[index] = data;
    return data;
  } catch (error) {
    console.error("Error updating asset:", error);
    throw error;
  }
};


const deleteAsset = async (id) => {
  try {
    await apiRequest(`/api/assets/${id}/`, "DELETE");
    assets.value = assets.value.filter((p) => p.id !== parseInt(id));
    return true;
  } catch (error) {
    console.error("Error deleting asset:", error);
    throw error;
  }
};

  const fetchDepartments = async () => {
    try {
      const data = await apiRequest("/api/departments/");
      departments.value = data.results || data;
      return data;
    } catch (error) {
      console.error("Error fetching departments:", error);
      throw error;
    }
  };

  const fetchCategories = async () => {
    try {
      const data = await apiRequest("/api/categories/");
      categories.value = data.results || data;
      return data;
    } catch (error) {
      console.error("Error fetching categories:", error);
      throw error;
    }
  };

  const getAssetById = (id) => {
    return assets.value.find((p) => p.id === parseInt(id));
  };

  return {
  assets, departments, categories, loading,
  count, next, previous, error,       // <== add these
  fetchAssets, getAsset, addAsset, updateAsset, deleteAsset,
  fetchDepartments, fetchCategories, getAssetById,
  transferAsset
};


});
