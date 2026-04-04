import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  items: [],
  loading: false,
  error: null,
};

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    setCartItems: (state, action) => {
      state.items = action.payload;
    },
    addToCart: (state, action) => {
      const existingItem = state.items.find(
        (item) => item.product_id === action.payload.product_id
      );
      if (existingItem) {
        existingItem.quantity += action.payload.quantity || 1;
      } else {
        state.items.push(action.payload);
      }
    },
    updateCartItem: (state, action) => {
      const { id, quantity } = action.payload;
      const item = state.items.find((item) => item.id === id);
      if (item) {
        item.quantity = quantity;
      }
    },
    removeFromCart: (state, action) => {
      state.items = state.items.filter((item) => item.id !== action.payload);
    },
    clearCart: (state) => {
      state.items = [];
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const {
  setCartItems,
  addToCart,
  updateCartItem,
  removeFromCart,
  clearCart,
  setLoading,
  setError,
} = cartSlice.actions;

export default cartSlice.reducer;
