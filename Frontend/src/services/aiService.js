import { productService } from './productService';

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
    return {
      message: "Hello! I'm here to help you with your shopping. How can I assist you today?",
      suggestions: [
        "Show me featured products",
        "What's on sale?",
        "Help me find a product",
      ],
    };
  },
};
