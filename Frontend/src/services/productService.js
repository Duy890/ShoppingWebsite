import api from './api';

export const productService = {
  async getProducts(filters = {}, signal) {
    const params = {};

    if (filters.category) params.category = filters.category;
    if (filters.search) params.search = filters.search;
    if (filters.featured !== undefined) params.featured = filters.featured;
    if (filters.sortBy) params.sortBy = filters.sortBy;
    if (filters.type) params.product_type = filters.type;
    if (filters.brand) params.brand = filters.brand;

    const { data } = await api.get('/products', { params, signal });
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

  async getCategoryTree() {
    const { data } = await api.get('/categories/tree');
    return data;
  },

  async getSearchSuggestions(query) {
    const { data } = await api.get('/search/suggestions', { params: { q: query } });
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

  async getProductSpecifications(productId) {
    const { data } = await api.get(`/products/${productId}/specifications`);
    return data;
  },

  async saveProductSpecifications(productId, specifications) {
    const { data } = await api.put(`/products/${productId}/specifications`, {
      specifications,
    });
    return data;
  },

  async getSpecTemplates(productType) {
    if (!productType) return [];
    const { data } = await api.get(`/spec-templates/${productType}`);
    return data;
  },

  _navCategoriesCache: null,
  _navCategoriesPromise: null,

  async getNavigationCategories() {
    if (this._navCategoriesCache) return this._navCategoriesCache;
    if (this._navCategoriesPromise) return this._navCategoriesPromise;

    this._navCategoriesPromise = api.get('/navigation/categories')
      .then(({ data }) => {
        this._navCategoriesCache = data;
        this._navCategoriesPromise = null;
        return data;
      })
      .catch(err => {
        this._navCategoriesPromise = null;
        throw err;
      });

    return this._navCategoriesPromise;
  },

  _navTreeCache: null,
  _navTreePromise: null,

  async getNavigationTree() {
    if (this._navTreeCache) return this._navTreeCache;
    if (this._navTreePromise) return this._navTreePromise;

    this._navTreePromise = api.get('/navigation/tree')
      .then(({ data }) => {
        this._navTreeCache = data;
        this._navTreePromise = null;
        return data;
      })
      .catch(err => {
        this._navTreePromise = null;
        throw err;
      });

    return this._navTreePromise;
  },
};
