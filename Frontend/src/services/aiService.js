import { productService } from './productService';
import api from './api';

export const aiService = {
  async getRecommendations(userId, productId = null) {
    try {
      const products = await productService.getProducts();
      // Simple recommendation logic: return some products that are not the current one
      return products
        .filter((p) => p.id !== productId)
        .sort(() => 0.5 - Math.random())
        .slice(0, 4);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      return [];
    }
  },

  async sendChatMessage(message, context = {}) {
    const { data } = await api.post('/api/chat', {
      message,
      history: context.history || [],
    });
    return data;
  },
};
