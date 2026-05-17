import { useEffect, useMemo, memo, useCallback, useState, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { setFilters, setPagination, clearFilters } from '../store/productSlice';
import { useProducts } from '../hooks/useProducts';
import ProductCard from '../components/ProductCard';
import { SlidersHorizontal, ChevronDown, ChevronLeft, ChevronRight } from 'lucide-react';

const PAGE_SIZES = [12, 24, 48, 96];

const findCategoryBySlug = (navTree, slug) => {
  for (const cat of navTree) {
    if (cat.slug === slug) return cat;
    if (cat.children) {
      const found = findCategoryBySlug(cat.children, slug);
      if (found) return found;
    }
  }
  return null;
};

const ProductList = () => {
  const dispatch = useDispatch();
  const [searchParams, setSearchParams] = useSearchParams();
  const { products, categories, loading, error, pagination, loadProducts } = useProducts();
  const navTree = useSelector((state) => state.navigation.navTree);
  const sortBy = useSelector((state) => state.product.filters.sortBy);

  const categoryParam = searchParams.get('category');
  const typeParam = searchParams.get('type');
  const brandParam = searchParams.get('brand');
  const searchParam = searchParams.get('q') || '';
  const pageParam = parseInt(searchParams.get('page'), 10) || 1;
  const limitParam = parseInt(searchParams.get('limit'), 10) || 12;

  const [jumpPage, setJumpPage] = useState('');
  const prevUrlKeyRef = useRef('');

  const urlKey = `${categoryParam}|${typeParam}|${brandParam}|${searchParam}`;

  useEffect(() => {
    if (urlKey === prevUrlKeyRef.current) return;
    prevUrlKeyRef.current = urlKey;

    console.log('[ProductList] URL filters changed, syncing to Redux');

    dispatch(setFilters({
      category: categoryParam,
      type: typeParam,
      brand: brandParam,
      search: searchParam,
    }));
  }, [dispatch, categoryParam, typeParam, brandParam, searchParam]);

  useEffect(() => {
    console.log('[ProductList] URL pagination changed, syncing to Redux:', { page: pageParam, limit: limitParam });
    dispatch(setPagination({ page: pageParam, limit: limitParam }));
  }, [dispatch, pageParam, limitParam]);

  const handleReset = useCallback(() => {
    setSearchParams({});
    prevUrlKeyRef.current = '';
  }, [setSearchParams]);

  const handleSortChange = useCallback((e) => {
    dispatch(setFilters({ sortBy: e.target.value }));
    setSearchParams((prev) => {
      prev.delete('page');
      return prev;
    });
    prevUrlKeyRef.current = '';
  }, [dispatch, setSearchParams]);

  const handlePageChange = useCallback((newPage) => {
    const totalPages = pagination.total_pages || 1;
    const clamped = Math.max(1, Math.min(newPage, totalPages));
    setSearchParams((prev) => {
      if (clamped <= 1) prev.delete('page');
      else prev.set('page', String(clamped));
      return prev;
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [setSearchParams, pagination.total_pages]);

  const handleLimitChange = useCallback((newLimit) => {
    setSearchParams((prev) => {
      prev.delete('page');
      prev.set('limit', String(newLimit));
      return prev;
    });
  }, [setSearchParams]);

  const handleJumpSubmit = useCallback(() => {
    const pageNum = parseInt(jumpPage, 10);
    const totalPages = pagination.total_pages || 1;
    if (!isNaN(pageNum) && pageNum >= 1 && pageNum <= totalPages) {
      handlePageChange(pageNum);
    }
    setJumpPage('');
  }, [jumpPage, pagination.total_pages, handlePageChange]);

  const renderedProducts = useMemo(() => {
    if (products.length === 0 && !loading) {
      return (
        <div className="col-span-full py-24 text-center">
          <p className="text-2xl font-black text-gray-300 uppercase italic">No products found</p>
          <p className="text-gray-400 mt-2">Try adjusting your filters or search term.</p>
        </div>
      );
    }
    return products.map((product) => (
      <ProductCard key={product.id} product={product} />
    ));
  }, [products, loading]);

  const activeCategoryName = useMemo(() => {
    if (categoryParam) {
      const found = findCategoryBySlug(navTree, categoryParam);
      if (found) return found.name;
      const foundInCats = categories.find(c => c.id === categoryParam || c.slug === categoryParam);
      return foundInCats?.name || categoryParam;
    }
    if (typeParam) {
      return brandParam ? `${brandParam} ${typeParam}` : typeParam;
    }
    if (brandParam) {
      return brandParam;
    }
    if (searchParam) {
      return `Search: ${searchParam}`;
    }
    return 'All Electronics';
  }, [categoryParam, typeParam, brandParam, searchParam, categories, navTree]);

  const hasActiveFilters = Boolean(categoryParam || typeParam || brandParam || searchParam);

  const totalPages = pagination.total_pages || 1;
  const currentPage = pageParam;

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <div className="bg-primary pt-12 pb-24 text-white">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-5xl font-black tracking-tighter uppercase">
            {activeCategoryName}
          </h1>
          <div className="mt-4 flex items-center space-x-2 text-sm font-bold uppercase tracking-widest opacity-70">
            <span>Products</span>
            <span className="w-1 h-1 rounded-full bg-white opacity-50"></span>
            <span>{pagination.total_items || products.length} Items</span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 -mt-10">
        <div className="flex flex-col lg:flex-row gap-8">
          <aside className="w-full lg:w-72 space-y-6">
            <div className="bg-white rounded-3xl shadow-xl p-6 border border-gray-100">
              <div className="flex items-center justify-between mb-8 pb-4 border-b border-gray-50">
                <h2 className="font-black uppercase tracking-tighter flex items-center gap-2">
                  <SlidersHorizontal className="w-4 h-4 text-primary" />
                  Filters
                </h2>
                {hasActiveFilters && (
                   <button 
                    onClick={handleReset}
                    className="text-[10px] font-bold text-primary hover:underline uppercase tracking-widest"
                   >
                    Reset
                   </button>
                )}
              </div>
              
              <div className="space-y-6">
                <div>
                   <h3 className="text-xs font-black text-gray-400 uppercase tracking-widest mb-4">Sorting</h3>
                   <div className="relative group">
                     <select 
                      value={sortBy}
                      onChange={handleSortChange}
                      className="w-full appearance-none bg-gray-50 border-none rounded-2xl px-5 py-3 text-sm font-bold text-gray-700 focus:ring-2 focus:ring-primary/20 transition-all cursor-pointer"
                     >
                        <option value="created_at">Latest Arrivals</option>
                        <option value="price">Price: Low to High</option>
                     </select>
                     <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none group-hover:text-primary transition-colors" />
                   </div>
                </div>

                <div>
                  <h3 className="text-xs font-black text-gray-400 uppercase tracking-widest mb-4">Per Page</h3>
                  <div className="flex flex-wrap gap-2">
                    {PAGE_SIZES.map((size) => (
                      <button
                        key={size}
                        onClick={() => handleLimitChange(size)}
                        className={`px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-widest transition-all ${
                          limitParam === size
                            ? 'bg-primary text-white'
                            : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-100'
                        }`}
                      >
                        {size}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-900 rounded-3xl p-8 text-white relative overflow-hidden group">
               <div className="relative z-10">
                  <p className="text-xs font-bold text-primary uppercase tracking-[0.2em] mb-2">Member Special</p>
                  <h3 className="text-2xl font-black tracking-tighter mb-4">Get 20% OFF</h3>
                  <p className="text-sm text-gray-400 mb-6">On all laptop accessories for premium members.</p>
                  <button className="bg-white text-gray-900 px-6 py-2.5 rounded-full text-xs font-black uppercase tracking-widest hover:bg-primary hover:text-white transition-all">Join Now</button>
               </div>
               <div className="absolute -bottom-6 -right-6 w-32 h-32 bg-primary/20 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-700"></div>
            </div>
          </aside>

          <main className="flex-1">
            {error ? (
              <div className="col-span-full py-24 text-center">
                <p className="text-2xl font-black text-red-400 uppercase italic">Failed to load products</p>
                <p className="text-gray-400 mt-2">{error}</p>
                <button
                  onClick={() => loadProducts()}
                  className="mt-6 bg-primary text-white px-8 py-3 rounded-full text-xs font-bold uppercase tracking-widest hover:bg-gray-900 transition-all"
                >
                  Retry
                </button>
              </div>
            ) : loading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-8">
                {[1,2,3,4,5,6].map(i => (
                  <div key={i} className="bg-white rounded-3xl h-96 animate-pulse"></div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                {renderedProducts}
              </div>
            )}

            {totalPages > 1 && !loading && (
              <div className="mt-16 bg-white rounded-3xl p-8 border border-gray-100">
                <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage <= 1}
                      className="flex items-center gap-1 px-4 py-2 rounded-xl text-sm font-bold uppercase tracking-widest transition-all disabled:opacity-30 disabled:cursor-not-allowed bg-gray-50 text-gray-700 hover:bg-gray-100"
                    >
                      <ChevronLeft className="w-4 h-4" />
                      Prev
                    </button>

                    <span className="text-sm font-black text-gray-900 px-4">
                      Page {currentPage} of {totalPages}
                    </span>

                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage >= totalPages}
                      className="flex items-center gap-1 px-4 py-2 rounded-xl text-sm font-bold uppercase tracking-widest transition-all disabled:opacity-30 disabled:cursor-not-allowed bg-gray-50 text-gray-700 hover:bg-gray-100"
                    >
                      Next
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="flex items-center gap-3">
                    <input
                      type="number"
                      min={1}
                      max={totalPages}
                      value={jumpPage}
                      onChange={(e) => setJumpPage(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleJumpSubmit()}
                      placeholder="Page #"
                      className="w-20 bg-gray-50 border border-gray-100 rounded-xl px-3 py-2 text-sm font-bold text-center text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                    />
                    <button
                      onClick={handleJumpSubmit}
                      className="px-5 py-2 rounded-xl text-xs font-bold uppercase tracking-widest bg-primary text-white hover:bg-gray-900 transition-all"
                    >
                      Go
                    </button>
                  </div>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};

export default memo(ProductList);
