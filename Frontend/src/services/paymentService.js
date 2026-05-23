import api from './api';

export const paymentService = {
  async createMoMoPayment(orderId, amount, orderInfo) {
    const response = await api.post('/payment/momo/create', {
      order_id: orderId,
      amount: Math.round(amount),
      order_info: orderInfo,
    });
    return response.data;
  },
};
