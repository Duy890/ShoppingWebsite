import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setUser, setProfile, setLoading, logout as logoutAction } from '../store/authSlice';
import { authService } from '../services/authService';

export const useAuth = () => {
  const dispatch = useDispatch();
  const { user, profile, isAuthenticated, loading } = useSelector((state) => state.auth);

  useEffect(() => {
    const initAuth = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        if (currentUser) {
          dispatch(setUser(currentUser));
          dispatch(setProfile(currentUser));
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
      } finally {
        dispatch(setLoading(false));
      }
    };

    initAuth();

    const { data: subscription } = authService.onAuthStateChange(async (event, session) => {
      if (session?.user) {
        dispatch(setUser(session.user));
        const userProfile = await authService.getProfile(session.user.id);
        dispatch(setProfile(userProfile));
      } else {
        dispatch(logoutAction());
      }
      dispatch(setLoading(false));
    });

    return () => {
      subscription?.subscription?.unsubscribe();
    };
  }, [dispatch]);

  const signIn = async (email, password) => {
    try {
      const user = await authService.signIn(email, password);
      dispatch(setUser(user));
      dispatch(setProfile(user));
      return user;
    } catch (error) {
      throw error;
    }
  };

  const signUp = async (email, password, fullName) => {
    try {
      const user = await authService.signUp(email, password, fullName);
      dispatch(setUser(user));
      dispatch(setProfile(user));
      return user;
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.signOut();
      dispatch(logoutAction());
    } catch (error) {
      throw error;
    }
  };

  const updateProfile = async (updates) => {
    try {
      const updatedProfile = await authService.updateProfile(user.id, updates);
      dispatch(setProfile(updatedProfile));
      return updatedProfile;
    } catch (error) {
      throw error;
    }
  };

  return {
    user,
    profile,
    isAuthenticated,
    loading,
    signIn,
    signUp,
    logout,
    updateProfile,
  };
};
