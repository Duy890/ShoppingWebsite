import api from './api';

export const productService = {
  async getProducts(filters = {}) {
    const params = {};

    if (filters.category) params.category = filters.category;
    if (filters.search) params.search = filters.search;
    if (filters.featured !== undefined) params.featured = filters.featured;
    if (filters.sortBy) params.sortBy = filters.sortBy;

    const { data } = await api.get('/products', { params });
    return data;
  },

  async getProductById(id) {
    const { data } = await api.get(`/products/${id}`);
    return data;
  },

  async uploadProductImage(file) {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post('/upload-image', formData);
    return data;
  },

  async createProduct(product) {
    const { data } = await api.post('/products', product);
    return data;
  },

  async updateProduct(id, updates) {
    const { data } = await api.put(`/products/${id}`, updates);
    return data;
  },

  async deleteProduct(id) {
    await api.delete(`/products/${id}`);
  },

  async getCategories() {
    const { data } = await api.get('/categories');
    return data;
  },

  async createCategory(category) {
    const { data } = await api.post('/categories', category);
    return data;
  },

  async deleteCategory(id) {
    await api.delete(`/categories/${id}`);
  },

  async getProductReviews(productId) {
    const { data } = await api.get(`/products/${productId}/reviews`);
    return data;
  },

  async addProductReview(productId, review) {
    const { data } = await api.post(`/products/${productId}/reviews`, review);
    return data;
  },
};
