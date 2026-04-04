import { useState } from 'react';
import { Search } from 'lucide-react';
import { useProducts } from '../hooks/useProducts';

const SearchBar = () => {
  const { updateFilters, filters } = useProducts();
  const [searchTerm, setSearchTerm] = useState(filters.search || '');

  const handleSearch = (e) => {
    e.preventDefault();
    updateFilters({ search: searchTerm });
  };

  return (
    <form onSubmit={handleSearch} className="w-full max-w-2xl">
      <div className="relative">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search products..."
          className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <button
          type="submit"
          className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          Search
        </button>
      </div>
    </form>
  );
};

export default SearchBar;
