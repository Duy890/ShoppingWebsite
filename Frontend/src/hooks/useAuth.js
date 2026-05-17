import { useEffect, useRef, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setUser, setProfile, setLoading, logout as logoutAction } from '../store/authSlice';
import { authService } from '../services/authService';

let globalAuthInitialized = false;
let authRequestInProgress = false;

export const useAuth = () => {
  const dispatch = useDispatch();
  const { user, profile, isAuthenticated, loading } = useSelector((state) => state.auth);
  const initializedRef = useRef(false);

  useEffect(() => {
    if (globalAuthInitialized || initializedRef.current || authRequestInProgress) return;
    initializedRef.current = true;
    authRequestInProgress = true;

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
        globalAuthInitialized = true;
        authRequestInProgress = false;
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
        globalAuthInitialized = false;
      }
      dispatch(setLoading(false));
      authRequestInProgress = false;
    });

    return () => {
      subscription?.subscription?.unsubscribe();
    };
  }, [dispatch]);

  const signIn = useCallback(async (email, password) => {
    const user = await authService.signIn(email, password);
    dispatch(setUser(user));
    dispatch(setProfile(user));
    globalAuthInitialized = true;
    return user;
  }, [dispatch]);

  const signUp = useCallback(async (email, password, fullName) => {
    const user = await authService.signUp(email, password, fullName);
    dispatch(setUser(user));
    dispatch(setProfile(user));
    globalAuthInitialized = true;
    return user;
  }, [dispatch]);

  const logout = useCallback(async () => {
    await authService.signOut();
    globalAuthInitialized = false;
    dispatch(logoutAction());
  }, [dispatch]);

  const updateProfile = useCallback(async (updates) => {
    if (!user?.id) throw new Error('No user ID available');
    const updatedProfile = await authService.updateProfile(user.id, updates);
    dispatch(setProfile(updatedProfile));
    return updatedProfile;
  }, [dispatch, user?.id]);

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
