import { Outlet, NavLink, Navigate } from 'react-router-dom';
import { FolderTree, Home, LayoutDashboard, LogOut, Package, PlusCircle, ShoppingCart } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const navItems = [
  { to: '/', label: 'Home', icon: Home, end: true },
  { to: '/admin/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/admin/products', label: 'Products', icon: Package, end: true },
  { to: '/admin/products/add', label: 'Add Product', icon: PlusCircle },
  { to: '/admin/categories', label: 'Categories', icon: FolderTree },
  { to: '/admin/orders', label: 'Orders', icon: ShoppingCart },
];

const AdminLayout = () => {
  const { profile, logout, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50/30">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!profile?.is_admin) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="min-h-screen bg-gray-50/30">
      <div className="flex">
        <aside className="w-72 bg-white border-r border-gray-100 min-h-screen sticky top-0">
          <div className="p-6 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-2xl bg-primary text-white flex items-center justify-center font-black">
                A
              </div>
              <div>
                <p className="text-[10px] font-black uppercase tracking-widest text-primary">Store Control</p>
                <h1 className="text-xl font-black text-gray-900 tracking-tight">Admin Panel</h1>
              </div>
            </div>
          </div>

          <nav className="p-4 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 rounded-2xl text-sm font-bold transition-colors ${
                    isActive
                      ? 'bg-primary text-white shadow-md shadow-primary/20'
                      : 'text-gray-600 hover:bg-primary/5 hover:text-primary'
                  }`
                }
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.label}
              </NavLink>
            ))}

            <button
              onClick={logout}
              className="flex items-center w-full px-4 py-3 rounded-2xl text-sm font-bold text-gray-600 hover:bg-red-50 hover:text-red-600 transition-colors"
            >
              <LogOut className="w-5 h-5 mr-3" />
              Logout
            </button>
          </nav>
        </aside>

        <main className="flex-1 min-w-0">
          <div className="max-w-7xl mx-auto p-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
