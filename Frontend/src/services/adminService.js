import api from './api';

export const adminService = {
  async getStats() {
    const { data } = await api.get('/admin/stats');
    return data;
  },

  async getRevenueByMonth() {
    const { data } = await api.get('/admin/revenue/monthly');
    return data;
  },

  async getRevenueByYear() {
    const { data } = await api.get('/admin/revenue/yearly');
    return data;
  },

  async getTopSearches() {
    const { data } = await api.get('/admin/analytics/top-searches');
    return data;
  },

  async getTopViewed() {
    const { data } = await api.get('/admin/analytics/top-viewed');
    return data;
  },

  async getCartAbandonment() {
    const { data } = await api.get('/admin/analytics/cart-abandonment');
    return data;
  },
};
