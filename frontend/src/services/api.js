// ─────────────────────────────────────────────────────────────
//  frontend/src/services/api.js
//  Toutes les communications avec le backend Django REST
// ─────────────────────────────────────────────────────────────
import axios from "axios";

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000/api",
  headers: { "Content-Type": "application/json" },
});

// ── Auth ──────────────────────────────────────────────────────
export const authAPI = {
  login:    (email, password) => API.post("/auth/login/",    { email, password }),
  register: (data)            => API.post("/auth/register/", data),
};

// ── Profil utilisateur ────────────────────────────────────────
export const profileAPI = {
  get:      (userId) => API.get(`/users/${userId}/`),
  update:   (userId, data) => API.put(`/users/${userId}/`, data),
  uploadCV: (file) => {
    const form = new FormData();
    form.append("cv", file);
    return API.post("/match-cv/", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

// ── Matching ──────────────────────────────────────────────────
export const matchingAPI = {
  uploadCV:    (file) => {
    const form = new FormData();
    form.append("cv", file);
    return API.post("/match-cv/", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  mapOffers:   ()   => API.get("/map-offers/"),
};

export default API;