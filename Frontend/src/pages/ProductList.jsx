import { useEffect } from 'react';
import ProductCard from '../components/ProductCard';
import SearchBar from '../components/SearchBar';
import { useProducts } from '../hooks/useProducts';

const ProductList = () => {
  const { products, categories, loading, filters, updateFilters } = useProducts();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-6">All Products</h1>
          <SearchBar />
        </div>

        <div className="flex flex-col md:flex-row gap-8">
          <aside className="w-full md:w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>

              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Categories</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => updateFilters({ category: null })}
                    className={`block w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                      !filters.category
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    All Categories
                  </button>
                  {categories.map((category) => (
                    <button
                      key={category.id}
                      onClick={() => updateFilters({ category: category.id })}
                      className={`block w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                        filters.category === category.id
                          ? 'bg-blue-50 text-blue-600'
                          : 'text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      {category.name}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Sort By</h3>
                <select
                  value={filters.sortBy}
                  onChange={(e) => updateFilters({ sortBy: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="created_at">Newest</option>
                  <option value="price">Price: Low to High</option>
                  <option value="name">Name: A to Z</option>
                </select>
              </div>
            </div>
          </aside>

          <main className="flex-1">
            {loading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : products.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-md p-12 text-center">
                <p className="text-gray-500 text-lg">No products found.</p>
                <p className="text-gray-400 mt-2">Try adjusting your filters or search terms.</p>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};

export default ProductList;
