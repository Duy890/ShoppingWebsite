import { productService } from './productService';
import api from './api';

export const aiService = {
  async getRecommendations(userId, productId = null) {
    try {
      const response = await productService.getProducts({ limit: 20 });
      // getProducts trả về { items: [...], pagination: {...} }
      // phải lấy .items trước khi filter
      const allProducts = Array.isArray(response)
        ? response
        : (response?.items || []);

      return allProducts
        .filter((p) => p.id !== productId)
        .sort(() => 0.5 - Math.random())
        .slice(0, 8);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      return [];
    }
  },

  async sendChatMessage(message, context = {}) {
    const { data } = await api.post('/api/chat', {
      message,
      session_id: context.sessionId,
      history: [],
    });
    return data;
  },
};
