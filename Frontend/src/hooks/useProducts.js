import { useEffect } from 'react';
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

export const useProducts = () => {
  const dispatch = useDispatch();
  const { products, categories, selectedProduct, loading, error, filters } =
    useSelector((state) => state.product);

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    loadProducts();
  }, [filters]);

  const loadProducts = async () => {
    try {
      dispatch(setLoading(true));
      const data = await productService.getProducts(filters);
      dispatch(setProducts(data));
    } catch (err) {
      dispatch(setError(err.message));
    } finally {
      dispatch(setLoading(false));
    }
  };

  const loadCategories = async () => {
    try {
      const data = await productService.getCategories();
      dispatch(setCategories(data));
    } catch (err) {
      dispatch(setError(err.message));
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

  const updateFilters = (newFilters) => {
    dispatch(setFilters(newFilters));
  };

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
