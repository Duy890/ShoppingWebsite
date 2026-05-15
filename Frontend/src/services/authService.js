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

  onAuthStateChange(callback) {
    return {
      subscription: {
        unsubscribe: () => {},
      },
    };
  },
};
