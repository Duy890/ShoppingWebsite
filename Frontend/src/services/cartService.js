import api from './api';

export const cartService = {
  async getOrCreateCart(userId) {
    const { data } = await api.get('/cart');
    return data;
  },

  async getCartItems(userId) {
    const cart = await this.getOrCreateCart(userId);
    return cart.items;
  },

  async addToCart(userId, productId, quantity = 1) {
    const { data } = await api.post('/cart/items', {
      product_id: productId,
      quantity,
    });
    return data;
  },

  async updateCartItem(itemId, quantity) {
    const { data } = await api.patch(`/cart/items/${itemId}`, {
      quantity,
    });
    return data;
  },

  async removeFromCart(itemId) {
    await api.delete(`/cart/items/${itemId}`);
  },

  async clearCart(userId) {
    await api.delete('/cart/clear');
  },
};
