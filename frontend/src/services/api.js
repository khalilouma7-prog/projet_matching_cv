import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  headers: { "Content-Type": "application/json" },
  withCredentials: true,  //  envoie les cookies de session
});

export const resultsAPI = {
  getResults: () => API.get("/results/"),
  getDashboardStats: () => API.get("/results/dashboard-stats/"),
};

export const authAPI = {
  login: (email, password) => API.post("/users/auth/login/", { email, password }),
  register: (data) => API.post("/users/auth/register/", data),
};

export const profileAPI = {
  get: (userId) => API.get(`/users/users/${userId}/`),
  update: (userId, data) => API.put(`/users/users/${userId}/`, data),
  uploadCV: (file) => {
    const form = new FormData();
    form.append("cv", file);
    return API.post("/matching/match-cv/", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export const matchingAPI = {
  uploadCV: (file) => {
    const form = new FormData();
    form.append("cv", file);
    return API.post("/matching/match-cv/", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  mapOffers: () => API.get("/matching/map-offers/"),
};

export default API;