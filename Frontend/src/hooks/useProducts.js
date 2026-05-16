import { useEffect, useRef, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  setProducts,
  setCategories,
  setSelectedProduct,
  setLoading,
  setError,
  setFilters,
} from '../store/productSlice';
import { productService } from '../services/productService';

const useDeepCompareRef = (value) => {
  const ref = useRef(value);
  const stringVal = JSON.stringify(value);
  if (stringVal !== JSON.stringify(ref.current)) {
    ref.current = value;
  }
  return ref;
};

export const useProducts = () => {
  const dispatch = useDispatch();

  const products = useSelector((state) => state.product.products);
  const categories = useSelector((state) => state.product.categories);
  const selectedProduct = useSelector((state) => state.product.selectedProduct);
  const loading = useSelector((state) => state.product.loading);
  const error = useSelector((state) => state.product.error);
  const filters = useSelector((state) => state.product.filters);

  const prevFiltersRef = useRef(null);

  const abortControllerRef = useRef(null);

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    const currentStr = JSON.stringify(filters);
    const prevStr = JSON.stringify(prevFiltersRef.current);
    if (currentStr === prevStr) return;
    prevFiltersRef.current = filters;
    loadProducts(filters);
  }, [filters]);

  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const loadCategories = async () => {
    try {
      const data = await productService.getCategories();
      dispatch(setCategories(data));
    } catch (err) {
      dispatch(setError(err.message));
    }
  };

  const loadProducts = async (overrideFilters) => {
    const requestFilters = overrideFilters ?? filters;
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    try {
      dispatch(setLoading(true));
      dispatch(setProducts([]));
      const data = await productService.getProducts(requestFilters, abortController.signal);
      dispatch(setProducts(data));
    } catch (err) {
      if (err?.name === 'CanceledError' || err?.name === 'AbortError' || err?.code === 'ERR_CANCELED') {
        return;
      }
      dispatch(setError(err.message || 'Failed to load products'));
    } finally {
      if (abortControllerRef.current === abortController) {
        abortControllerRef.current = null;
      }
      dispatch(setLoading(false));
    }
  };

  const loadProduct = async (id) => {
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
  };

  const createProduct = async (product) => {
    try {
      dispatch(setLoading(true));
      const data = await productService.createProduct(product);
      await loadProducts();
      return data;
    } catch (err) {
      dispatch(setError(err.message));
      throw err;
    } finally {
      dispatch(setLoading(false));
    }
  };

  const createCategory = async (category) => {
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
  };

  const deleteCategory = async (categoryId) => {
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
  };

  const updateProduct = async (id, updates) => {
    try {
      dispatch(setLoading(true));
      const data = await productService.updateProduct(id, updates);
      await loadProducts();
      return data;
    } catch (err) {
      dispatch(setError(err.message));
      throw err;
    } finally {
      dispatch(setLoading(false));
    }
  };

  const deleteProduct = async (id) => {
    try {
      dispatch(setLoading(true));
      await productService.deleteProduct(id);
      await loadProducts();
    } catch (err) {
      dispatch(setError(err.message));
      throw err;
    } finally {
      dispatch(setLoading(false));
    }
  };

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
