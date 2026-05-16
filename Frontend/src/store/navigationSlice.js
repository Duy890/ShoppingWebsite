import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  navTree: [],
  navLoading: false,
};

const navigationSlice = createSlice({
  name: 'navigation',
  initialState,
  reducers: {
    setNavTree: (state, action) => {
      state.navTree = action.payload;
    },
    setNavLoading: (state, action) => {
      state.navLoading = action.payload;
    },
  },
});

export const { setNavTree, setNavLoading } = navigationSlice.actions;
export default navigationSlice.reducer;
