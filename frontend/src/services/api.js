// ─────────────────────────────────────────────────────────────
//  frontend/src/services/api.js
// ─────────────────────────────────────────────────────────────
import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  headers: { "Content-Type": "application/json" },
});

// Ajout du Token automatique pour que le Dashboard fonctionne
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token"); 
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Auth (Corrigé avec /users/) ───────────────────────────────
export const authAPI = {
  // On utilise 'username' comme dans votre image de connexion
  login: (username, password) => 
    API.post("/users/auth/login/", { username, password }),
    
  register: (data) => 
    API.post("/users/auth/register/", data),
};

// ── Profil utilisateur (Corrigé avec /users/) ──────────────────
export const profileAPI = {
  get: (userId) => 
    API.get(`/users/users/${userId}/`), // Double 'users' selon votre urls.py
    
  update: (userId, data) => 
    API.put(`/users/users/${userId}/`, data),
};

// ── Matching (Corrigé avec /matching/) ────────────────────────
export const matchingAPI = {
  uploadCV: (file) => {
    const form = new FormData();
    form.append("cv", file);
    return API.post("/matching/match-cv/", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  
  mapOffers: () => 
    API.get("/matching/map-offers/"),
};

export default API;