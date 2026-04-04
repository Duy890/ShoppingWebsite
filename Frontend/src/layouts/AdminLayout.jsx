import { Outlet, Link, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { LayoutDashboard, Package, ShoppingCart, LogOut, Plus } from 'lucide-react';

const AdminLayout = () => {
  const { profile, logout, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (!profile?.is_admin) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex">
        <aside className="w-64 bg-white shadow-lg min-h-screen">
          <div className="p-6">
            <h1 className="text-2xl font-bold text-gray-800">Admin Panel</h1>
          </div>
          <nav className="mt-6">
            <Link
              to="/"
              className="flex items-center px-6 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors"
            >
              <span className="w-5 h-5 mr-3 text-base">⌂</span>
              Home
            </Link>
            <Link
              to="/admin/dashboard"
              className="flex items-center px-6 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors"
            >
              <LayoutDashboard className="w-5 h-5 mr-3" />
              Dashboard
            </Link>
            <Link
              to="/admin/products"
              className="flex items-center px-6 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors"
            >
              <Package className="w-5 h-5 mr-3" />
              Products
            </Link>
            <Link
              to="/admin/products/add"
              className="flex items-center px-6 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors"
            >
              <span className="w-5 h-5 mr-3 text-base">+</span>
              Add Product
            </Link>
            <Link
              to="/admin/categories"
              className="flex items-center px-6 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors"
            >
              <span className="w-5 h-5 mr-3 text-base">+</span>
              Add Category
            </Link>
            <Link
              to="/admin/orders"
              className="flex items-center px-6 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors"
            >
              <ShoppingCart className="w-5 h-5 mr-3" />
              Orders
            </Link>
            <button
              onClick={logout}
              className="flex items-center w-full px-6 py-3 text-gray-700 hover:bg-red-50 hover:text-red-600 transition-colors"
            >
              <LogOut className="w-5 h-5 mr-3" />
              Logout
            </button>
          </nav>
        </aside>
        <main className="flex-1 p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
