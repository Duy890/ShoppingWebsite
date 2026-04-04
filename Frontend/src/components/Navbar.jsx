import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useCart } from '../hooks/useCart';
import { ShoppingCart, User, LogOut, ShoppingBag, LayoutDashboard } from 'lucide-react';

const Navbar = () => {
  const { isAuthenticated, profile, logout } = useAuth();
  const { cartCount } = useCart();

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <ShoppingBag className="w-8 h-8 text-blue-600" />
              <span className="text-2xl font-bold text-gray-900">Shopping</span>
            </Link>
            <div className="hidden md:flex ml-10 space-x-8">
              <Link
                to="/products"
                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Products
              </Link>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link
                  to="/cart"
                  className="relative text-gray-700 hover:text-blue-600 transition-colors"
                >
                  <ShoppingCart className="w-6 h-6" />
                  {cartCount > 0 && (
                    <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {cartCount}
                    </span>
                  )}
                </Link>
                {profile?.is_admin && (
                  <Link
                    to="/admin/dashboard"
                    className="text-gray-700 hover:text-blue-600 transition-colors"
                  >
                    <LayoutDashboard className="w-6 h-6" />
                  </Link>
                )}
                <Link
                  to="/profile"
                  className="text-gray-700 hover:text-blue-600 transition-colors"
                >
                  <User className="w-6 h-6" />
                </Link>
                <button
                  onClick={logout}
                  className="text-gray-700 hover:text-red-600 transition-colors"
                >
                  <LogOut className="w-6 h-6" />
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-blue-600 px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
