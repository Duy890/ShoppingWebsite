import axios from 'axios';
import { toast } from 'react-hot-toast';

const _shownToasts = new Set();
const toastOnce = (message, ttl = 5000) => {
  if (_shownToasts.has(message)) return;
  _shownToasts.add(message);
  toast.error(message);
  setTimeout(() => _shownToasts.delete(message), ttl);
};

// Create axios instance
const getBaseURL = () => {
  const url = import.meta.env.VITE_API_URL;
  if (!url || url === 'undefined' || url === 'null') {
    return 'http://localhost:8000';
  }
  return url;
};

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000,
});

// Token helpers
const TOKEN_KEY = 'shop_token';
const REFRESH_TOKEN_KEY = 'shop_refresh_token';

const getAccessToken = () => localStorage.getItem(TOKEN_KEY);
const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);
const setTokens = (access, refresh) => {
  localStorage.setItem(TOKEN_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
};
const clearTokens = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem('shop_user');
};

// Track refresh state to avoid infinite loops
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  failedQueue = [];
};

// Request interceptor - Add auth token
api.interceptors.request.use((config) => {
  if (!config.headers) {
    config.headers = {};
  }

  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// Response interceptor - Handle errors + auto refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle canceled requests — silently ignore
    if (axios.isCancel(error) || error.code === 'ERR_CANCELED' || error.name === 'CanceledError') {
      return Promise.reject(error);
    }

    // Handle timeout
    if (error.code === 'ECONNABORTED') {
      toastOnce('Request timeout. Please try again.');
      return Promise.reject(error);
    }

    // Handle network errors
    if (!error.response) {
      if (error.message === 'Network Error') {
        toastOnce('Network error. Please check your connection.');
      } else if (error.code === 'ECONNREFUSED') {
        toastOnce('Server is not reachable. Please ensure the backend is running.');
      } else if (error.code === 'ECONNRESET') {
        toastOnce('Connection was reset. Please try again.');
      } else {
        toastOnce(`Connection error: ${error.code || error.message}`);
      }
      return Promise.reject(error);
    }

    const status = error.response?.status;
    const data = error.response?.data;

    // ── Auto-refresh on 401 ──
    if (status === 401 && !originalRequest._retry) {
      const refreshToken = getRefreshToken();
      if (refreshToken && !originalRequest.url?.includes('/auth/refresh')) {
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          }).then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          }).catch((err) => Promise.reject(err));
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
          const { data: tokenData } = await axios.post(
            `${getBaseURL()}/auth/refresh`,
            { refresh_token: refreshToken },
          );
          setTokens(tokenData.access_token, tokenData.refresh_token);
          processQueue(null, tokenData.access_token);
          originalRequest.headers.Authorization = `Bearer ${tokenData.access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          processQueue(refreshError, null);
          clearTokens();
          toastOnce('Session expired. Please login again.');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }

      // No refresh token — force logout
      clearTokens();
      toastOnce('Session expired. Please login again.');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // Handle other status codes
    switch (status) {
      case 400:
        toastOnce(data?.detail || 'Invalid request');
        break;

      case 403:
        toastOnce('You do not have permission to access this resource.');
        if (window.location.pathname !== '/403') {
          window.location.href = '/403';
        }
        break;

      case 404:
        toastOnce(data?.detail || 'Resource not found');
        if (!window.location.pathname.includes('/product') && window.location.pathname !== '/404') {
          window.location.href = '/404';
        }
        break;

      case 422:
        if (Array.isArray(data?.detail)) {
          data.detail.forEach((err) => toastOnce(`${err.loc?.join('.')}: ${err.msg}`));
        } else {
          toastOnce(data?.detail || 'Validation error');
        }
        break;

      case 423:
        toastOnce(data?.detail || 'Account locked. Please try again later.');
        break;

      case 429:
        toastOnce('Too many requests. Please slow down.');
        break;

      case 500: case 502: case 503: case 504:
        if (status === 503) window.location.href = '/maintenance';
        else {
          toastOnce('Server error. Please try again later.');
          if (window.location.pathname !== '/500') window.location.href = '/500';
        }
        break;

      default:
        toastOnce(data?.detail || `Error: ${status}`);
    }

    return Promise.reject(error);
  }
);

export default api;
export { setTokens, clearTokens, getAccessToken, getRefreshToken };
