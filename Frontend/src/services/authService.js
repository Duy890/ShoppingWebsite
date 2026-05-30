import api, { setTokens, clearTokens, getRefreshToken } from './api';

export const authService = {
  async signUp(email, password, fullName) {
    const response = await api.post('/auth/register', {
      email, password, full_name: fullName,
    });
    const { access_token, refresh_token, user } = response.data;
    setTokens(access_token, refresh_token);
    return user;
  },

  async signIn(email, password) {
    const response = await api.post('/auth/login', {
      email, password,
    });
    const data = response.data;

    if (data.mfa_required) {
      return {
        mfa_required: true,
        mfa_challenge_token: data.mfa_challenge_token,
        user: data.user,
      };
    }

    setTokens(data.access_token, data.refresh_token);
    return { mfa_required: false, user: data.user };
  },

  async verifyMFAChallenge(challengeToken, code) {
    const response = await api.post('/auth/mfa/challenge/verify', {
      challenge_token: challengeToken,
      code: code,
    });
    const { access_token, refresh_token, user } = response.data;
    setTokens(access_token, refresh_token);
    return user;
  },

  async signOut() {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      try {
        await api.post('/auth/logout', { refresh_token: refreshToken });
      } catch {
        // ignore network errors on logout
      }
    }
    clearTokens();
  },

  async logoutAllSessions() {
    try {
      await api.post('/auth/logout-all');
    } catch {
      // ignore
    }
    clearTokens();
  },

  async getCurrentUser() {
    const token = localStorage.getItem('shop_token');
    if (!token) return null;
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      return null;
    }
  },

  async getProfile(userId) {
    const token = localStorage.getItem('shop_token');
    if (!token) return null;
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
      headers: { 'Content-Type': 'multipart/form-data' },
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

  async verifyEmailChange(token) {
    const { data } = await api.get(`/auth/verify-email-change?token=${token}`);
    return data;
  },

  async getLoginHistory() {
    const response = await api.get('/auth/login-history');
    return response.data;
  },

  async getMFAStatus() {
    const response = await api.get('/auth/mfa/status');
    return response.data;
  },

  async setupMFA(password) {
    const response = await api.post('/auth/mfa/setup', { password });
    return response.data;
  },

  async verifyMFA(code) {
    const response = await api.post('/auth/mfa/verify', { code });
    return response.data;
  },

  async disableMFA(password, code) {
    const response = await api.post('/auth/mfa/disable', { password, code });
    return response.data;
  },

  onAuthStateChange(callback) {
    return {
      subscription: { unsubscribe: () => {} },
    };
  },
};

