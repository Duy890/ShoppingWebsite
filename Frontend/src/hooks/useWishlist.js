import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setWishlistIds, addWishlistId, removeWishlistId, setInitialized } from '../store/wishlistSlice';
import { productService } from '../services/productService';

let wishlistGlobalLoaded = false;

export const useWishlist = () => {
  const dispatch = useDispatch();
  const { ids, initialized } = useSelector((state) => state.wishlist);
  const { isAuthenticated } = useSelector((state) => state.auth);

  useEffect(() => {
    if (!isAuthenticated || wishlistGlobalLoaded) return;
    wishlistGlobalLoaded = true;

    productService.getWishlistIds()
      .then((data) => {
        dispatch(setWishlistIds(Array.isArray(data) ? data : []));
        dispatch(setInitialized(true));
      })
      .catch(() => {
        wishlistGlobalLoaded = false;
      });
  }, [dispatch, isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated) {
      wishlistGlobalLoaded = false;
    }
  }, [isAuthenticated]);

  return {
    wishlistIds: ids,
    isInWishlist: (productId) => ids.includes(productId),
    addToWishlist: async (productId) => {
      await productService.addToWishlist(productId);
      dispatch(addWishlistId(productId));
    },
    removeFromWishlist: async (productId) => {
      await productService.removeFromWishlist(productId);
      dispatch(removeWishlistId(productId));
    },
  };
};
