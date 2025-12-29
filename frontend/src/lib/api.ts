import axios from "axios";
import { auth } from "@/lib/firebase";
import { API_URL } from "@/constants/env";
import { paths } from "@/paths";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Use cached token from localStorage
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("auth_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Helper function to format error message
function formatErrorMessage(error: any): string {
  if (!error.response?.data) {
    return error.message || "Đã có lỗi xảy ra";
  }

  const data = error.response.data;

  // Handle FastAPI validation errors (array format)
  if (Array.isArray(data.detail)) {
    return data.detail
      .map((err: any) => {
        if (typeof err === "string") {
          return err;
        }
        // Format validation error object
        const loc = err.loc ? err.loc.join(".") : "";
        const msg = err.msg || err.message || "Validation error";
        return loc ? `${loc}: ${msg}` : msg;
      })
      .join(", ");
  }

  // Handle object with errors array
  if (data.errors && Array.isArray(data.errors)) {
    return data.errors.join(", ");
  }

  // Handle simple string or object detail
  if (typeof data.detail === "string") {
    return data.detail;
  }

  // Handle object detail
  if (typeof data.detail === "object") {
    if (data.detail.message) {
      return data.detail.message;
    }
    // Try to stringify if it's an object
    return JSON.stringify(data.detail);
  }

  // Fallback
  return data.message || "Đã có lỗi xảy ra";
}

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Format error message before rejecting
    if (error.response?.data) {
      error.formattedMessage = formatErrorMessage(error);
    }

    // If 401 and haven't retried yet, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (typeof window !== "undefined") {
        try {
          // Try to get fresh token from Firebase
          const user = auth.currentUser;
          if (user) {
            const token = await user.getIdToken(true); // Force refresh
            localStorage.setItem("auth_token", token);
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest); // Retry request with new token
          }
        } catch (refreshError) {
          console.error("Failed to refresh token:", refreshError);
        }

        // If refresh failed or no user, clear auth and redirect
        localStorage.removeItem("auth_token");
        window.location.href = paths.login;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
