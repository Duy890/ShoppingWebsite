import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useCart } from '../hooks/useCart';
import { useProducts } from '../hooks/useProducts';
import { 
  ShoppingCart, 
  User, 
  LogOut, 
  Search, 
  ChevronDown, 
  Heart,
  LayoutDashboard,
  Menu,
  X
} from 'lucide-react';

const Navbar = () => {
  const navigate = useNavigate();
  const { isAuthenticated, profile, logout } = useAuth();
  const { cartCount } = useCart();
  const { categories, updateFilters } = useProducts();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    updateFilters({ search: searchTerm });
    navigate('/products');
  };

  const handleCategoryClick = (categoryId) => {
    updateFilters({ category: categoryId });
    navigate('/products');
    setIsMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 w-full">
      {/* Top Utility Bar */}
      <div className="bg-gray-100 py-1 hidden sm:block">
        <div className="max-w-7xl mx-auto px-4 flex justify-end space-x-6 text-[10px] font-medium text-gray-500 uppercase tracking-wider">
          <Link to="#" className="hover:text-primary transition-colors">Order Tracking</Link>
          <Link to="#" className="hover:text-primary transition-colors">Store Locator</Link>
          <Link to="#" className="hover:text-primary transition-colors">Support</Link>
        </div>
      </div>

      {/* Main Orange-Red Header */}
      <nav className="bg-primary text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-20 gap-4">
            
            {/* Logo */}
            <Link to="/" className="flex-shrink-0 flex items-center space-x-1">
              <span className="text-3xl font-extrabold tracking-tighter">e-shop.</span>
            </Link>

            {/* Category Dropdown & Search (Desktop) */}
            <div className="hidden md:flex flex-1 max-w-2xl items-center bg-white rounded-md overflow-hidden shadow-inner">
              <div className="relative group px-4 py-2 border-r border-gray-200">
                <button className="flex items-center space-x-1 text-gray-700 font-semibold text-sm hover:text-primary transition-colors">
                  <span>Categories</span>
                  <ChevronDown className="w-4 h-4" />
                </button>
                <div className="absolute top-full left-0 w-48 bg-white shadow-xl rounded-b-md hidden group-hover:block border-t border-gray-100 py-2">
                  <button 
                    onClick={() => handleCategoryClick(null)}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary"
                  >
                    All Products
                  </button>
                  {categories.map(cat => (
                    <button 
                      key={cat.id}
                      onClick={() => handleCategoryClick(cat.id)}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary"
                    >
                      {cat.name}
                    </button>
                  ))}
                </div>
              </div>
              
              <form onSubmit={handleSearch} className="flex-1 flex items-center px-4">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search for electronics, gadgets..."
                  className="w-full bg-transparent border-none focus:ring-0 text-gray-800 text-sm py-2"
                />
                <button type="submit" className="text-gray-400 hover:text-primary transition-colors p-2">
                  <Search className="w-5 h-5" />
                </button>
              </form>
            </div>

            {/* Utility Icons */}
            <div className="flex items-center space-x-2 sm:space-x-5">
              <Link to="/cart" className="relative p-2 hover:bg-white/10 rounded-full transition-colors group">
                <ShoppingCart className="w-6 h-6" />
                {cartCount > 0 && (
                  <span className="absolute top-0 right-0 bg-white text-primary text-[10px] font-bold rounded-full h-5 w-5 flex items-center justify-center border-2 border-primary">
                    {cartCount}
                  </span>
                )}
                <span className="hidden lg:inline ml-2 text-xs font-semibold uppercase tracking-wide">Cart</span>
              </Link>

              {isAuthenticated ? (
                <div className="flex items-center space-x-1 sm:space-x-3">
                   <Link to="#" className="p-2 hover:bg-white/10 rounded-full transition-colors hidden sm:block">
                    <Heart className="w-6 h-6" />
                  </Link>
                  {profile?.is_admin && (
                    <Link to="/admin/dashboard" className="p-2 hover:bg-white/10 rounded-full transition-colors">
                      <LayoutDashboard className="w-6 h-6" />
                    </Link>
                  )}
                  <div className="relative group">
                    <button className="flex items-center space-x-1 p-2 hover:bg-white/10 rounded-full transition-colors">
                      <User className="w-6 h-6" />
                    </button>
                    <div className="absolute top-full right-0 w-48 bg-white shadow-xl rounded-md hidden group-hover:block border border-gray-100 py-2">
                      <div className="px-4 py-2 border-b border-gray-100 mb-2">
                        <p className="text-xs text-gray-400">Welcome,</p>
                        <p className="text-sm font-bold text-gray-800 truncate">{profile?.full_name || profile?.email}</p>
                      </div>
                      <Link to="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary">Profile</Link>
                      <button 
                        onClick={logout}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center"
                      >
                        <LogOut className="w-4 h-4 mr-2" />
                        Sign Out
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Link to="/login" className="text-xs font-bold uppercase tracking-widest px-4 py-2 hover:bg-white/10 rounded transition-colors">Login</Link>
                  <Link to="/register" className="bg-white text-primary px-4 py-2 rounded font-bold text-xs uppercase tracking-widest hover:bg-gray-100 transition-colors shadow-lg">Sign Up</Link>
                </div>
              )}

              {/* Mobile Menu Button */}
              <button 
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="md:hidden p-2 hover:bg-white/10 rounded-full transition-colors"
              >
                {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden bg-white text-gray-800 border-t border-gray-100 animate-in slide-in-from-top duration-300">
            <div className="px-4 py-6 space-y-4">
              <form onSubmit={handleSearch} className="relative">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search..."
                  className="w-full bg-gray-100 border-none rounded-md px-4 py-3 text-sm"
                />
                <button type="submit" className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                  <Search className="w-5 h-5" />
                </button>
              </form>
              <div className="space-y-2">
                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Categories</p>
                <button 
                  onClick={() => handleCategoryClick(null)}
                  className="block w-full text-left px-2 py-2 text-sm font-semibold hover:text-primary"
                >
                  All Products
                </button>
                {categories.map(cat => (
                  <button 
                    key={cat.id}
                    onClick={() => handleCategoryClick(cat.id)}
                    className="block w-full text-left px-2 py-2 text-sm font-semibold hover:text-primary"
                  >
                    {cat.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
};

export default Navbar;
