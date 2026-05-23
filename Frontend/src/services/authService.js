import api from './api';


const TOKEN_KEY = 'shop_token';

export const authService = {
  async signUp(email, password, fullName) {
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });

    const { access_token, user } = response.data;
    localStorage.setItem(TOKEN_KEY, access_token);
    return user;
  },

  async signIn(email, password) {
    const response = await api.post('/auth/login', {
      email,
      password,
    });

    const { access_token, user } = response.data;
    localStorage.setItem(TOKEN_KEY, access_token);
    return user;
  },

  async signOut() {
    localStorage.removeItem(TOKEN_KEY);
  },

  async getCurrentUser() {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      return null;
    }

    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      return null;
    }
  },

  async getProfile(userId) {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      return null;
    }

    const response = await api.get('/auth/me');
    return response.data;
  },

  async updateProfile(userId, updates) {
    const response = await api.put('/users/me', updates);
    return response.data;
  },

  async uploadAvatar(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload-avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async forgotPassword(email) {
    const response = await api.post('/auth/forgot-password', { email });
    return response.data;
  },

  async resetPassword(token, newPassword) {
    const response = await api.post('/auth/reset-password', { token, new_password: newPassword });
    return response.data;
  },

  async requestEmailChange(newEmail) {
    const response = await api.post('/auth/request-email-change', { new_email: newEmail });
    return response.data;
  },

  async changePassword(currentPassword, newPassword) {
    const response = await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },

  // NOTE: This is a no-op stub. JWT auth uses axios interceptors (api.js)
  // for 401 handling. No real-time auth state subscription is needed.
  onAuthStateChange(callback) {
    return {
      subscription: {
        unsubscribe: () => {},
      },
    };
  },
};
