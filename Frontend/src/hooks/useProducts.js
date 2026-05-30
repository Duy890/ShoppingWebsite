import { useEffect, useRef, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  setProducts,
  setCategories,
  setSelectedProduct,
  setLoading,
  setError,
  setFilters,
  setPagination,
} from '../store/productSlice';
import { productService } from '../services/productService';

export const useProducts = () => {
  const dispatch = useDispatch();

  const products = useSelector((state) => state.product.products);
  const categories = useSelector((state) => state.product.categories);
  const selectedProduct = useSelector((state) => state.product.selectedProduct);
  const loading = useSelector((state) => state.product.loading);
  const error = useSelector((state) => state.product.error);
  const filters = useSelector((state) => state.product.filters);
  const pagination = useSelector((state) => state.product.pagination);

  const requestIdRef = useRef(0);
  const loadingRef = useRef(false);

  const loadCategories = useCallback(async () => {
    try {
      const data = await productService.getCategories();
      dispatch(setCategories(data));
    } catch (err) {
      dispatch(setError(err.message));
    }
  }, [dispatch]);

  const loadProducts = useCallback(async (explicitFilters) => {
    if (!explicitFilters) {
      console.warn('[useProducts] loadProducts called without filters, skipping');
      return;
    }
    if (loadingRef.current) return;
    loadingRef.current = true;

    const requestId = ++requestIdRef.current;
    console.log('[useProducts] loadProducts requestId:', requestId, 'filters:', explicitFilters);

    try {
      dispatch(setLoading(true));
      const data = await productService.getProducts(explicitFilters);
      if (requestId !== requestIdRef.current) {
        console.log('[useProducts] Stale response ignored, requestId:', requestId, 'current:', requestIdRef.current);
        return;
      }
      console.log('[useProducts] Products loaded:', data.items?.length || 0, 'total:', data.pagination?.total_items);
      dispatch(setProducts(data));
      dispatch(setError(null));
    } catch (err) {
      if (requestId !== requestIdRef.current) {
        console.log('[useProducts] Stale error ignored, requestId:', requestId);
        return;
      }
      console.error('[useProducts] Error loading products:', err);
      dispatch(setError(err.message || 'Failed to load products'));
    } finally {
      loadingRef.current = false;
      dispatch(setLoading(false));
    }
  }, [dispatch]);

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    return () => {
      loadingRef.current = false;
    };
  }, []);

  const loadProduct = useCallback(async (id) => {
    try {
      dispatch(setLoading(true));
      const data = await productService.getProductById(id);
      dispatch(setSelectedProduct(data));
      return data;
    } catch (err) {
      dispatch(setError(err.message));
      throw err;
    } finally {
      dispatch(setLoading(false));
    }
  }, [dispatch]);

  const createProduct = useCallback(async (product) => {
    try {
      dispatch(setLoading(true));
      const data = await productService.createProduct(product);
      dispatch(setPagination({ page: 1 }));
      await loadProducts({ ...filters, page: 1, limit: pagination.limit });
      return data;
    } catch (err) {
      dispatch(setError(err.message));
      throw err;
    } finally {
      dispatch(setLoading(false));
    }
  }, [dispatch, loadProducts, filters, pagination.limit]);

  const createCategory = useCallback(async (category) => {
    try {
      dispatch(setLoading(true));
      const data = await productService.createCategory(category);
      await loadCategories();
      return data;
    } catch (err) {
      dispatch(setError(err.message));
      throw err;
    } finally {
      dispatch(setLoading(false));
    }
  }, [dispatch, loadCategories]);

  const deleteCategory = useCallback(async (categoryId) => {
    try {
      dispatch(setLoading(true));
      await productService.deleteCategory(categoryId);
      await loadCategories();
    } catch (err) {
      dispatch(setError(err.message));
      throw err;
    } finally {
      dispatch(setLoading(false));
    }
  }, [dispatch, loadCategories]);

  const updateProduct = useCallback(async (id, updates) => {
    try {
      dispatch(setLoading(true));
      const data = await productService.updateProduct(id, updates);
      await loadProducts({ ...filters, page: pagination.page, limit: pagination.limit });
      return data;
    } catch (err) {
      dispatch(setError(err.message));
      throw err;
    } finally {
      dispatch(setLoading(false));
    }
  }, [dispatch, loadProducts, filters, pagination.page, pagination.limit]);

  const deleteProduct = useCallback(async (id) => {
    try {
      dispatch(setLoading(true));
      await productService.deleteProduct(id);
      await loadProducts({ ...filters, page: pagination.page, limit: pagination.limit });
    } catch (err) {
      dispatch(setError(err.message));
      throw err;
    } finally {
      dispatch(setLoading(false));
    }
  }, [dispatch, loadProducts, filters, pagination.page, pagination.limit]);

  const updateFilters = useCallback((newFilters) => {
    dispatch(setFilters(newFilters));
  }, [dispatch]);

  return {
    products,
    categories,
    selectedProduct,
    loading,
    error,
    filters,
    pagination,
    loadProducts,
    loadProduct,
    createProduct,
    updateProduct,
    deleteProduct,
    updateFilters,
    createCategory,
    deleteCategory,
  };
};
