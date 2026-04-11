import { useEffect } from 'react';
import ProductCard from '../components/ProductCard';
import { useProducts } from '../hooks/useProducts';
import { SlidersHorizontal, ChevronDown } from 'lucide-react';

const ProductList = () => {
  const { products, categories, loading, filters, updateFilters } = useProducts();

  return (
    <div className="min-h-screen bg-white">
      {/* Category Header */}
      <div className="bg-gray-900 py-16 text-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center space-x-2 text-primary mb-4 text-xs font-bold uppercase tracking-widest">
            <div className="h-1 w-8 bg-primary rounded-full" />
            <span>Catalogue</span>
          </div>
          <h1 className="text-5xl font-black tracking-tighter">
            {filters.category 
              ? categories.find(c => c.id === filters.category)?.name 
              : 'All Electronics'}
          </h1>
          <p className="mt-4 text-gray-400 max-w-xl text-lg">
            Browse our curated collection of high-end gadgets, professional laptops, and immersive audio equipment.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="flex flex-col lg:flex-row gap-12">
          
          {/* Sidebar Filters */}
          <aside className="w-full lg:w-64 space-y-10">
            <div>
              <div className="flex items-center space-x-2 mb-6">
                <SlidersHorizontal className="w-5 h-5 text-primary" />
                <h2 className="text-lg font-black uppercase tracking-tight">Filter By</h2>
              </div>
              
              <div className="space-y-8">
                {/* Categories */}
                <div className="border-b border-gray-100 pb-8">
                  <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Categories</h3>
                  <div className="space-y-1">
                    <button
                      onClick={() => updateFilters({ category: null })}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm font-semibold transition-all ${
                        !filters.category
                          ? 'bg-primary text-white shadow-lg shadow-primary/20'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-primary'
                      }`}
                    >
                      All Products
                    </button>
                    {categories.map((category) => (
                      <button
                        key={category.id}
                        onClick={() => updateFilters({ category: category.id })}
                        className={`w-full text-left px-3 py-2 rounded-lg text-sm font-semibold transition-all ${
                          filters.category === category.id
                            ? 'bg-primary text-white shadow-lg shadow-primary/20'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-primary'
                        }`}
                      >
                        {category.name}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Sort By */}
                <div>
                  <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Sort By</h3>
                  <div className="relative">
                    <select
                      value={filters.sortBy}
                      onChange={(e) => updateFilters({ sortBy: e.target.value })}
                      className="w-full appearance-none bg-gray-50 border border-gray-100 px-4 py-3 rounded-xl text-sm font-bold text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all cursor-pointer"
                    >
                      <option value="created_at">Newest First</option>
                      <option value="price">Price: Low to High</option>
                      <option value="name">Alphabetical</option>
                    </select>
                    <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                  </div>
                </div>
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1">
            <div className="flex items-center justify-between mb-8 pb-4 border-b border-gray-100">
              <p className="text-sm font-bold text-gray-400 uppercase tracking-widest">
                Showing <span className="text-gray-900">{products.length}</span> Products
              </p>
            </div>

            {loading ? (
              <div className="flex justify-center py-24">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
              </div>
            ) : products.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-8">
                {products.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            ) : (
              <div className="bg-gray-50 rounded-3xl p-20 text-center border-2 border-dashed border-gray-200">
                <div className="max-w-xs mx-auto space-y-4">
                  <h3 className="text-xl font-black text-gray-900">No matches found</h3>
                  <p className="text-gray-500 text-sm">We couldn't find any products matching your current filters. Try expanding your search.</p>
                  <button 
                    onClick={() => updateFilters({ category: null, search: '' })}
                    className="bg-primary text-white px-6 py-3 rounded-xl font-bold text-xs uppercase tracking-widest hover:bg-gray-900 transition-colors"
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

export default ProductList;
