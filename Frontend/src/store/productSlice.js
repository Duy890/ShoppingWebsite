import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  products: [],
  categories: [],
  selectedProduct: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    limit: 12,
    total_items: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false,
  },
  filters: {
    category: null,
    search: '',
    sortBy: 'created_at',
    type: null,
    brand: null,
  },
};

const productSlice = createSlice({
  name: 'product',
  initialState,
  reducers: {
    setProducts: (state, action) => {
      if (action.payload?.items) {
        state.products = action.payload.items;
        state.pagination = action.payload.pagination || state.pagination;
      } else {
        state.products = action.payload;
      }
    },
    setCategories: (state, action) => {
      state.categories = action.payload;
    },
    setSelectedProduct: (state, action) => {
      state.selectedProduct = action.payload;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    setPagination: (state, action) => {
      state.pagination = { ...state.pagination, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {
        category: null,
        search: '',
        sortBy: 'created_at',
        type: null,
        brand: null,
      };
      state.pagination.page = 1;
    },
  },
});

export const {
  setProducts,
  setCategories,
  setSelectedProduct,
  setLoading,
  setError,
  setFilters,
  setPagination,
  clearFilters,
} = productSlice.actions;

export default productSlice.reducer;
