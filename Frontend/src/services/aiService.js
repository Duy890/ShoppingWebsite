export const aiService = {
  async getRecommendations(userId, productId = null) {
    return [];
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
