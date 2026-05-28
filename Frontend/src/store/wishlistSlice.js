import { createSlice } from '@reduxjs/toolkit';

const wishlistSlice = createSlice({
  name: 'wishlist',
  initialState: {
    ids: [],
    initialized: false,
  },
  reducers: {
    setWishlistIds(state, action) {
      state.ids = action.payload;
    },
    addWishlistId(state, action) {
      if (!state.ids.includes(action.payload)) {
        state.ids.push(action.payload);
      }
    },
    removeWishlistId(state, action) {
      state.ids = state.ids.filter(id => id !== action.payload);
    },
    setInitialized(state, action) {
      state.initialized = action.payload;
    },
  },
});

export const { setWishlistIds, addWishlistId, removeWishlistId, setInitialized } = wishlistSlice.actions;
export default wishlistSlice.reducer;
