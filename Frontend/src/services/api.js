import axios from 'axios';
import { toast } from 'react-hot-toast';

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
});

// Request interceptor - Add auth token
api.interceptors.request.use((config) => {
  if (!config.headers) {
    config.headers = {};
  }

  const token = localStorage.getItem('shop_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// Response interceptor - Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle timeout
    if (error.code === 'ECONNABORTED') {
      toast.error('Request timeout. Please try again.');
      return Promise.reject(error);
    }

    // Handle network errors
    if (!error.response) {
      // Network error or no response
      if (error.message === 'Network Error') {
        toast.error('Network error. Please check your connection.');
        // Dispatch offline event to show offline banner
        window.dispatchEvent(new Event('offline'));
      } else {
        toast.error('Connection error. Please try again.');
      }
      return Promise.reject(error);
    }

    const status = error.response?.status;
    const data = error.response?.data;

    // Handle specific status codes
    switch (status) {
      case 400:
        toast.error(data?.detail || 'Invalid request');
        break;

      case 401:
        // Unauthorized - redirect to login
        localStorage.removeItem('shop_token');
        localStorage.removeItem('shop_user');
        toast.error('Session expired. Please login again.');
        window.location.href = '/login';
        break;

      case 403:
        // Forbidden - access denied
        toast.error('You do not have permission to access this resource.');
        if (window.location.pathname !== '/403') {
          window.location.href = '/403';
        }
        break;

      case 404:
        // Not found
        toast.error(data?.detail || 'Resource not found');
        if (!window.location.pathname.includes('/product')) {
          // For general 404 errors
          if (window.location.pathname !== '/404') {
            window.location.href = '/404';
          }
        }
        break;

      case 422:
        // Validation error
        if (Array.isArray(data?.detail)) {
          data.detail.forEach((err) => {
            toast.error(`${err.loc?.join('.')}: ${err.msg}`);
          });
        } else {
          toast.error(data?.detail || 'Validation error');
        }
        break;

      case 500:
      case 502:
      case 503:
      case 504:
        // Server errors
        if (status === 503) {
          // Service unavailable - maintenance
          window.location.href = '/maintenance';
        } else {
          toast.error('Server error. Please try again later.');
          if (window.location.pathname !== '/500') {
            window.location.href = '/500';
          }
        }
        break;

      default:
        toast.error(data?.detail || `Error: ${status}`);
    }

    return Promise.reject(error);
  }
);

export default api;
