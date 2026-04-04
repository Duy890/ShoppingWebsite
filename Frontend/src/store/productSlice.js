import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  products: [],
  categories: [],
  selectedProduct: null,
  loading: false,
  error: null,
  filters: {
    category: null,
    search: '',
    sortBy: 'created_at',
  },
};

const productSlice = createSlice({
  name: 'product',
  initialState,
  reducers: {
    setProducts: (state, action) => {
      state.products = action.payload;
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
    clearFilters: (state) => {
      state.filters = {
        category: null,
        search: '',
        sortBy: 'created_at',
      };
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
  clearFilters,
} = productSlice.actions;

export default productSlice.reducer;
