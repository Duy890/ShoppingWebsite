import api from './api';

export const adminService = {
  async getStats() {
    const { data } = await api.get('/admin/stats');
    return data;
  },
};
