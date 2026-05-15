import api from './api';

export const orderService = {
  async createOrder(userId, orderData) {
    const { data } = await api.post('/orders', orderData);
    return data;
  },

  async getUserOrders(userId) {
    const { data } = await api.get('/orders');
    return data;
  },

  async getOrderById(orderId) {
    const { data } = await api.get(`/orders/${orderId}`);
    return data;
  },

  async getAllOrders() {
    const { data } = await api.get('/admin/orders');
    return data;
  },

  async updateOrderStatus(orderId, status, note = null) {
    const { data } = await api.put(`/orders/${orderId}/status`, { status, note });
    return data;
  },

  async getOrderTracking(orderId) {
    const { data } = await api.get(`/orders/${orderId}/tracking`);
    return data;
  },

  async getOrderTimeline(orderId) {
    const { data } = await api.get(`/orders/${orderId}/timeline`);
    return data;
  },

  async simulateNextOrderStatus(orderId) {
    const { data } = await api.post(`/admin/orders/${orderId}/simulate-next`);
    return data;
  },
};
