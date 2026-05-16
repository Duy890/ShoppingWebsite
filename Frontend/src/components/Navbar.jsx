import { useState, useEffect, useRef, memo, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { logout as logoutAction } from '../store/authSlice';
import { productService } from '../services/productService';
import { authService } from '../services/authService';
import { useNavigation } from '../hooks/useNavigation';
import { setFilters } from '../store/productSlice';
import SearchSuggestions from './SearchSuggestions';
import CategoryMegaMenu from './CategoryMegaMenu';
import {
  ShoppingCart,
  User,
  LogOut,
  Search,
  ChevronDown,
  Heart,
  LayoutDashboard,
  Menu,
  X,
  Settings,
} from 'lucide-react';

const languageOptions = [
  { code: 'en', label: 'English' },
  { code: 'vi', label: 'Tiếng Việt' },
];

const translations = {
  en: {
    settings: 'Settings',
    language: 'Language',
    darkMode: 'Dark Mode',
  },
  vi: {
    settings: 'Cài đặt',
    language: 'Ngôn ngữ',
    darkMode: 'Chế độ tối',
  },
};

const Navbar = memo(() => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { navTree } = useNavigation();
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
  const profile = useSelector((state) => state.auth.profile);
  const cartItems = useSelector((state) => state.cart.items);

  const cartCount = cartItems.reduce((count, item) => count + item.quantity, 0);

  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [language, setLanguage] = useState(() => localStorage.getItem('app_language') || 'en');
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('app_theme') === 'dark');
  const [searchTerm, setSearchTerm] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [isSuggestionsOpen, setIsSuggestionsOpen] = useState(false);
  const [activeSuggestion, setActiveSuggestion] = useState(-1);
  const [isMegaOpen, setIsMegaOpen] = useState(false);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const suggestionsTimerRef = useRef(null);
  const searchInputRef = useRef(null);

  useEffect(() => {
    console.count("Navbar render");
  });

  useEffect(() => {
    localStorage.setItem('app_language', language);
    document.documentElement.lang = language;
  }, [language]);

  useEffect(() => {
    localStorage.setItem('app_theme', darkMode ? 'dark' : 'light');
    document.documentElement.classList.toggle('dark', darkMode);
  }, [darkMode]);

  useEffect(() => {
    const handleEsc = (event) => {
      if (event.key === 'Escape') {
        setIsSuggestionsOpen(false);
        setIsMegaOpen(false);
        setActiveSuggestion(-1);
      }
    };
    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, []);

  const fetchSuggestions = useCallback(async (query) => {
    if (!query) {
      setSuggestions([]);
      return;
    }
    setLoadingSuggestions(true);
    try {
      const results = await productService.getSearchSuggestions(query);
      setSuggestions(results);
      setIsSuggestionsOpen(true);
      setActiveSuggestion(-1);
    } catch (error) {
      console.error('Unable to load search suggestions', error);
      setSuggestions([]);
    } finally {
      setLoadingSuggestions(false);
    }
  }, []);

  const updateSearchTerm = useCallback((value) => {
    setSearchTerm(value);
    clearTimeout(suggestionsTimerRef.current);
    if (!value.trim()) {
      setSuggestions([]);
      setIsSuggestionsOpen(false);
      return;
    }
    suggestionsTimerRef.current = setTimeout(() => {
      fetchSuggestions(value.trim());
    }, 180);
  }, [fetchSuggestions]);

  const handleSearch = useCallback((event) => {
    event.preventDefault();
    const sanitized = searchTerm.trim();
    setIsSuggestionsOpen(false);
    setActiveSuggestion(-1);
    if (sanitized) {
      navigate(`/search?q=${encodeURIComponent(sanitized)}`);
      return;
    }
    navigate('/products');
  }, [navigate, searchTerm]);

  const handleCategoryClick = useCallback((categorySlug) => {
    setIsMegaOpen(false);
    setIsSuggestionsOpen(false);
    setSearchTerm('');
    if (categorySlug) {
      navigate(`/products?category=${categorySlug}`);
      return;
    }
    navigate('/products');
  }, [navigate]);

  const handleSuggestionSelect = useCallback((item) => {
    if (!item) return;
    setIsSuggestionsOpen(false);
    setSearchTerm('');
    setActiveSuggestion(-1);
    if (item.type === 'product') {
      navigate(`/product/${item.id}`);
      return;
    }
    navigate(`/products?category=${item.id}`);
  }, [navigate]);

  const handleSearchKeyDown = useCallback((event) => {
    if (!isSuggestionsOpen || suggestions.length === 0) return;
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setActiveSuggestion((current) => Math.min(current + 1, suggestions.length - 1));
    }
    if (event.key === 'ArrowUp') {
      event.preventDefault();
      setActiveSuggestion((current) => Math.max(current - 1, 0));
    }
    if (event.key === 'Enter' && activeSuggestion >= 0) {
      event.preventDefault();
      handleSuggestionSelect(suggestions[activeSuggestion]);
    }
  }, [isSuggestionsOpen, suggestions, activeSuggestion, handleSuggestionSelect]);

  const handleLogout = useCallback(async () => {
    await authService.signOut();
    dispatch(logoutAction());
  }, [dispatch]);

  const clearSuggestions = useCallback(() => {
    setSuggestions([]);
    setIsSuggestionsOpen(false);
    setActiveSuggestion(-1);
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full">
      <div className="bg-gray-100 py-1 hidden sm:block">
        <div className="max-w-7xl mx-auto px-4 flex justify-end space-x-6 text-[10px] font-medium text-gray-500 uppercase tracking-wider">
          <Link to="#" className="hover:text-primary transition-colors">Order Tracking</Link>
          <Link to="#" className="hover:text-primary transition-colors">Store Locator</Link>
          <Link to="#" className="hover:text-primary transition-colors">Support</Link>
        </div>
      </div>

      <nav className="bg-primary text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-20 gap-4">
            <Link to="/" className="flex-shrink-0 flex items-center space-x-1">
              <span className="text-3xl font-extrabold tracking-tighter">e-shop.</span>
            </Link>

            <div className="hidden md:flex flex-1 max-w-3xl items-center gap-2 relative">
              <button
                type="button"
                className="inline-flex items-center space-x-2 px-4 py-3 bg-white text-gray-700 rounded-l-full font-semibold text-sm hover:text-primary transition-colors"
                onMouseEnter={() => setIsMegaOpen(true)}
                onClick={() => setIsMegaOpen((value) => !value)}
              >
                <span>Categories</span>
                <ChevronDown className="w-4 h-4" />
              </button>

              <div className="relative flex-1">
                <form onSubmit={handleSearch} className="relative">
                  <input
                    ref={searchInputRef}
                    type="text"
                    value={searchTerm}
                    onChange={(e) => updateSearchTerm(e.target.value)}
                    onFocus={() => searchTerm.trim() && setIsSuggestionsOpen(true)}
                    onKeyDown={handleSearchKeyDown}
                    placeholder="Search for electronics, gadgets..."
                    className="w-full bg-white text-gray-900 text-sm rounded-full py-3 pl-4 pr-14 shadow-sm border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/30"
                  />
                  <button
                    type="submit"
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-primary transition-colors"
                  >
                    <Search className="w-5 h-5" />
                  </button>
                </form>

                <SearchSuggestions
                  suggestions={suggestions}
                  query={searchTerm}
                  activeIndex={activeSuggestion}
                  loading={loadingSuggestions}
                  isOpen={isSuggestionsOpen}
                  onSelect={handleSuggestionSelect}
                  onClear={clearSuggestions}
                />
              </div>

              <CategoryMegaMenu
                isOpen={isMegaOpen}
                onDismiss={() => setIsMegaOpen(false)}
              />
            </div>

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

              <div className="relative">
                <button
                  type="button"
                  onClick={() => setSettingsOpen((value) => !value)}
                  className="p-2 hover:bg-white/10 rounded-full transition-colors"
                >
                  <Settings className="w-6 h-6" />
                </button>
                {settingsOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white text-gray-900 shadow-xl rounded-xl border border-gray-100 overflow-hidden z-20">
                    <div className="px-4 py-3 border-b border-gray-100">
                      <p className="text-xs font-semibold uppercase tracking-widest text-gray-400">{translations[language].settings}</p>
                    </div>
                    <div className="px-4 py-3">
                      <p className="text-xs font-semibold uppercase tracking-widest text-gray-400">{translations[language].language}</p>
                      <div className="mt-2 space-y-2">
                        {languageOptions.map((option) => (
                          <button
                            key={option.code}
                            type="button"
                            onClick={() => setLanguage(option.code)}
                            className={`w-full text-left rounded-xl px-3 py-2 text-sm ${language === option.code ? 'bg-primary/10 text-primary' : 'text-gray-700 hover:bg-gray-50'}`}
                          >
                            {option.label}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div className="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
                      <span className="text-sm font-semibold text-gray-700">{translations[language].darkMode}</span>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={darkMode}
                          onChange={() => setDarkMode((value) => !value)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 rounded-full peer-focus:ring-4 peer-focus:ring-primary/30 peer-checked:bg-primary transition-colors"></div>
                        <span className={`absolute left-1 top-1 w-4 h-4 bg-white rounded-full shadow transform transition ${darkMode ? 'translate-x-5' : ''}`}></span>
                      </label>
                    </div>
                  </div>
                )}
              </div>

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
                        onClick={handleLogout}
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

              <button 
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="md:hidden p-2 hover:bg-white/10 rounded-full transition-colors"
              >
                {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

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
                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Quick Links</p>
                <button 
                  onClick={() => handleCategoryClick(null)}
                  className="block w-full text-left px-2 py-2 text-sm font-semibold hover:text-primary"
                >
                  All Products
                </button>
                <Link 
                  to="/products?type=phone"
                  className="block w-full text-left px-2 py-2 text-sm font-semibold hover:text-primary"
                >
                  Điện thoại
                </Link>
                <Link 
                  to="/products?type=laptop"
                  className="block w-full text-left px-2 py-2 text-sm font-semibold hover:text-primary"
                >
                  Laptop
                </Link>
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
});

Navbar.displayName = 'Navbar';

export default Navbar;
