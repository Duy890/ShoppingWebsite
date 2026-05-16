import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  setCartItems,
  setLoading,
  setError,
  clearCart as clearCartAction,
} from '../store/cartSlice';
import { cartService } from '../services/cartService';

export const useCart = () => {
  const dispatch = useDispatch();
  const { items, loading, error } = useSelector((state) => state.cart);
  const { user, isAuthenticated } = useSelector((state) => state.auth);

  useEffect(() => {
    if (isAuthenticated && user) {
      loadCart();
    }
  }, [isAuthenticated, user]);

  const loadCart = async () => {
    if (!user) return;

    try {
      dispatch(setLoading(true));
      const cartItems = await cartService.getCartItems(user.id);
      dispatch(setCartItems(cartItems));
    } catch (err) {
      dispatch(setError(err.message));
    } finally {
      dispatch(setLoading(false));
    }
  };

  const addToCart = async (productId, quantity = 1, variantId = null) => {
    if (!user) {
      throw new Error('Please sign in to add items to cart');
    }

    try {
      dispatch(setLoading(true));
      await cartService.addToCart(user.id, productId, quantity, variantId);
      await loadCart();
    } catch (err) {
      dispatch(setError(err.message));
      throw err;
    } finally {
      dispatch(setLoading(false));
    }
  };

  const updateItem = async (itemId, quantity) => {
    try {
      dispatch(setLoading(true));
      await cartService.updateCartItem(itemId, quantity);
      await loadCart();
    } catch (err) {
      dispatch(setError(err.message));
      throw err;
    } finally {
      dispatch(setLoading(false));
    }
  };

  const removeItem = async (itemId) => {
    try {
      dispatch(setLoading(true));
      await cartService.removeFromCart(itemId);
      await loadCart();
    } catch (err) {
      dispatch(setError(err.message));
      throw err;
    } finally {
      dispatch(setLoading(false));
    }
  };

  const clearCart = async () => {
    if (!user) return;

    try {
      dispatch(setLoading(true));
      await cartService.clearCart(user.id);
      dispatch(clearCartAction());
    } catch (err) {
      dispatch(setError(err.message));
      throw err;
    } finally {
      dispatch(setLoading(false));
    }
  };

  const cartTotal = items.reduce(
    (total, item) => total + (item.product?.price || 0) * item.quantity,
    0
  );

  const cartCount = items.reduce((count, item) => count + item.quantity, 0);

  return {
    items,
    loading,
    error,
    cartTotal,
    cartCount,
    addToCart,
    updateItem,
    removeItem,
    clearCart,
    loadCart,
  };
};
