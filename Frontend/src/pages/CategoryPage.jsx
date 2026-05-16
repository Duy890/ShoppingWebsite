import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { setFilters } from '../store/productSlice';
import { useProducts } from '../hooks/useProducts';
import ProductCard from '../components/ProductCard';
import { productService } from '../services/productService';

const CategoryPage = () => {
  const { categoryId } = useParams();
  const dispatch = useDispatch();
  const { categories } = useProducts();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const category = categories.find((item) => item.id === categoryId || item.slug === categoryId);

  useEffect(() => {
    if (categoryId) {
      dispatch(setFilters({ category: categoryId }));
    }
  }, [categoryId, dispatch]);

  useEffect(() => {
    const loadCategoryProducts = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await productService.getProducts({ category: categoryId });
        setProducts(data);
      } catch (err) {
        setError('Unable to load category products at this time.');
      } finally {
        setLoading(false);
      }
    };
    if (categoryId) {
      loadCategoryProducts();
    }
  }, [categoryId]);

  return (
    <div className="min-h-screen bg-white">
      <div className="bg-gray-900 py-16 text-white">
        <div className="max-w-7xl mx-auto px-4">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-primary">Category</p>
          <h1 className="mt-4 text-5xl font-black tracking-tight">{category?.name || 'Category'}</h1>
          <p className="mt-4 max-w-2xl text-gray-300 text-lg">{category?.description || 'Browse across the collection and find your next favorite product.'}</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-12">
        {loading ? (
          <div className="flex justify-center py-24">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : error ? (
          <div className="rounded-3xl border border-red-100 bg-red-50 p-8 text-center text-red-700">
            {error}
          </div>
        ) : products.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-8">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="rounded-3xl border border-dashed border-gray-200 bg-gray-50 p-16 text-center">
            <p className="text-2xl font-black text-gray-900">No products in this category yet</p>
            <p className="mt-4 text-gray-500">Try another category or browse the entire catalog.</p>
            <div className="mt-8 flex flex-wrap justify-center gap-3">
              <Link to="/products" className="rounded-full border border-gray-200 px-6 py-3 text-sm font-semibold text-gray-700 hover:border-primary hover:text-primary transition">
                Browse all products
              </Link>
              <Link to="/search?q=" className="rounded-full bg-primary px-6 py-3 text-sm font-semibold text-white hover:bg-orange-700 transition">
                Search all products
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CategoryPage;
