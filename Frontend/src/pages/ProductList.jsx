import { useEffect, useMemo, memo, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { setFilters } from '../store/productSlice';
import { useProducts } from '../hooks/useProducts';
import ProductCard from '../components/ProductCard';
import { SlidersHorizontal, ChevronDown } from 'lucide-react';

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
  const { products, categories, loading, filters } = useProducts();
  const navTree = useSelector((state) => state.navigation.navTree);

  const categoryParam = searchParams.get('category');
  const typeParam = searchParams.get('type');
  const brandParam = searchParams.get('brand');
  const searchParam = searchParams.get('q') || '';

  useEffect(() => {
    const urlFilters = {
      category: categoryParam,
      type: typeParam,
      brand: brandParam,
      search: searchParam,
    };

    const currentFilters = {
      category: filters.category,
      type: filters.type,
      brand: filters.brand,
      search: filters.search || '',
    };

    const urlMatchesState = Object.keys(urlFilters).every(
      (key) => urlFilters[key] === currentFilters[key]
    );

    if (!urlMatchesState) {
      dispatch(setFilters(urlFilters));
    }
  }, [dispatch, categoryParam, typeParam, brandParam, searchParam, filters.category, filters.type, filters.brand, filters.search]);

  const handleReset = useCallback(() => {
    setSearchParams({});
  }, [setSearchParams]);

  const handleSortChange = useCallback((e) => {
    dispatch(setFilters({ sortBy: e.target.value }));
  }, [dispatch]);

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
            <span>{products.length} Items</span>
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
                      value={filters.sortBy}
                      onChange={handleSortChange}
                      className="w-full appearance-none bg-gray-50 border-none rounded-2xl px-5 py-3 text-sm font-bold text-gray-700 focus:ring-2 focus:ring-primary/20 transition-all cursor-pointer"
                     >
                        <option value="created_at">Latest Arrivals</option>
                        <option value="price">Price: Low to High</option>
                     </select>
                     <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none group-hover:text-primary transition-colors" />
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
            {loading ? (
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
            
            {!loading && products.length > 0 && products.length < 5 && (
              <div className="mt-16 bg-white rounded-3xl p-12 text-center border border-gray-100">
                <p className="text-sm font-bold text-gray-400 uppercase tracking-widest">End of results</p>
                <div className="mt-6 flex justify-center">
                  <button 
                    onClick={() => {
                      dispatch(clearFilters());
                      setSearchParams({});
                    }}
                    className="bg-gray-50 text-gray-900 px-8 py-3 rounded-full text-xs font-bold uppercase tracking-widest hover:bg-primary hover:text-white transition-all border border-gray-100"
                  >
                    Clear All Filters
                  </button>
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
