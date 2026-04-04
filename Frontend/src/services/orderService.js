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

  async updateOrderStatus(orderId, status) {
    const { data } = await api.put(`/orders/${orderId}/status`, { status });
    return data;
  },
};
