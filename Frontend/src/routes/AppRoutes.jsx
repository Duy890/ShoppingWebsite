import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import ErrorBoundary from '../components/ErrorBoundary';
import MainLayout from '../layouts/MainLayout';
import AdminLayout from '../layouts/AdminLayout';
import Home from '../pages/Home';
import ProductList from '../pages/ProductList';
import ProductDetail from '../pages/ProductDetail';
import SearchResults from '../pages/SearchResults';
import CategoryPage from '../pages/CategoryPage';
import Cart from '../pages/Cart';
import Checkout from '../pages/Checkout';
import Login from '../pages/Login';
import Register from '../pages/Register';
import ForgotPassword from '../pages/ForgotPassword';
import ResetPassword from '../pages/ResetPassword';
import Profile from '../pages/Profile';
import EditProfile from '../pages/EditProfile';
import Wishlist from '../pages/Wishlist';
import CompareProducts from '../pages/CompareProducts';
import Dashboard from '../pages/admin/Dashboard';
import Products from '../pages/admin/Products';
import AddProduct from '../pages/admin/AddProduct';
import EditProduct from '../pages/admin/EditProduct';
import Categories from '../pages/admin/Categories';
import Orders from '../pages/admin/Orders';
import SpecTemplates from '../pages/admin/SpecTemplates';
import NotFound from '../pages/NotFound';
import ServerError from '../pages/ServerError';
import Maintenance from '../pages/Maintenance';
import AccessDenied from '../pages/AccessDenied';
import OrderTracking from '../pages/OrderTracking';
import PaymentResult from '../pages/PaymentResult';
import VerifyEmailChange from '../pages/VerifyEmailChange';

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { user, isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (adminOnly && user?.role !== 'admin') {
    return <Navigate to="/403" replace />;
  }

  return children;
};

const AppRoutes = () => {
  return (
    <ErrorBoundary>
      <Routes>
        {/* Error Pages */}
        <Route path="/404" element={<NotFound />} />
        <Route path="/500" element={<ServerError />} />
        <Route path="/maintenance" element={<Maintenance />} />
        <Route path="/403" element={<AccessDenied />} />

        {/* Main Routes */}
        <Route element={<MainLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<ProductList />} />
          <Route path="/search" element={<SearchResults />} />
          <Route path="/category/:categoryId" element={<CategoryPage />} />
          <Route path="/product/:id" element={<ProductDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/register" element={<Register />} />
          <Route path="/signup" element={<Register />} />
          <Route
            path="/cart"
            element={
              <ProtectedRoute>
                <Cart />
              </ProtectedRoute>
            }
          />
          <Route
            path="/checkout"
            element={
              <ProtectedRoute>
                <Checkout />
              </ProtectedRoute>
            }
          />
          <Route
            path="/order/:orderId/tracking"
            element={
              <ProtectedRoute>
                <OrderTracking />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/edit-profile"
            element={
              <ProtectedRoute>
                <EditProfile />
              </ProtectedRoute>
            }
          />
          <Route path="/verify-email-change" element={<VerifyEmailChange />} />
          <Route
            path="/wishlist"
            element={
              <ProtectedRoute>
                <Wishlist />
              </ProtectedRoute>
            }
          />
          <Route path="/compare" element={<CompareProducts />} />
          <Route path="/payment/result" element={<PaymentResult />} />
        </Route>

        {/* Admin Routes */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute adminOnly>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="products" element={<Products />} />
          <Route path="products/add" element={<AddProduct />} />
          <Route path="products/edit/:id" element={<EditProduct />} />
          <Route path="categories" element={<Categories />} />
          <Route path="orders" element={<Orders />} />
          <Route path="spec-templates" element={<SpecTemplates />} />
        </Route>

        {/* Catch-all route - 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </ErrorBoundary>
  );
};

export default AppRoutes;
