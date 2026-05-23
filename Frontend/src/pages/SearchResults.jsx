import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSearchParams, Link } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import { productService } from '../services/productService';

const SearchResults = () => {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadResults = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await productService.getProducts({ search: query });
        setProducts(data);
      } catch (err) {
        setError(t('search_results.error_loading'));
      } finally {
        setLoading(false);
      }
    };

    loadResults();
  }, [query]);

  return (
    <div className="min-h-screen bg-white">
      <div className="bg-gray-900 py-16 text-white">
        <div className="max-w-7xl mx-auto px-4">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-primary">{t('search_results.section_title')}</p>
          <h1 className="mt-4 text-5xl font-black tracking-tight">
            {query ? t('search_results.results_for', { query }) : t('search_results.search_everything')}
          </h1>
          <p className="mt-4 max-w-2xl text-gray-300 text-lg">
            {query
              ? t('search_results.query_description')
              : t('search_results.default_description')}
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-12">
        {loading ? (
          <div className="flex justify-center py-24">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : error ? (
          <div className="rounded-3xl border border-red-100 bg-red-50 p-8 text-center text-red-700">
            {t('search_results.error_loading')}
          </div>
        ) : products.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-8">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="rounded-3xl border border-dashed border-gray-200 bg-gray-50 p-16 text-center">
            <p className="text-2xl font-black text-gray-900">{t('search_results.no_results_title')}</p>
            <p className="mt-4 text-gray-500">{t('search_results.no_results_desc')}</p>
            <div className="mt-8 flex flex-wrap justify-center gap-3">
              <Link to="/products" className="rounded-full border border-gray-200 px-6 py-3 text-sm font-semibold text-gray-700 hover:border-primary hover:text-primary transition">
                {t('search_results.browse_all_products')}
              </Link>
              <Link to="/products" className="rounded-full bg-primary px-6 py-3 text-sm font-semibold text-white hover:bg-orange-700 transition">
                {t('search_results.explore_popular_items')}
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchResults;
