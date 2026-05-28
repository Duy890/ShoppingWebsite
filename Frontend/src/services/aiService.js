import api from './api';

export const aiService = {
  async getRecommendations(productId, limit = 5) {
    try {
      const { data } = await api.get(`/recommendations/${productId}?limit=${limit}`);
      return data;
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
