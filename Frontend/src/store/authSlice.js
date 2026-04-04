import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  user: null,
  profile: null,
  isAuthenticated: false,
  loading: true,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUser: (state, action) => {
      state.user = action.payload;
      state.isAuthenticated = !!action.payload;
    },
    setProfile: (state, action) => {
      state.profile = action.payload;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    logout: (state) => {
      state.user = null;
      state.profile = null;
      state.isAuthenticated = false;
    },
  },
});

export const { setUser, setProfile, setLoading, logout } = authSlice.actions;
export default authSlice.reducer;
