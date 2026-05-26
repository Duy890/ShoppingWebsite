import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Heart, ShoppingCart, ChevronLeft } from 'lucide-react';
import { formatPrice } from '../utils/formatPrice';
import { productService } from '../services/productService';
import { useCart } from '../hooks/useCart';
import { useAuth } from '../hooks/useAuth';
import StarRating from '../components/StarRating';

const Wishlist = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { addToCart } = useCart();
  const [wishlist, setWishlist] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    loadWishlist();
  }, [isAuthenticated]);

  const loadWishlist = async () => {
    try {
      const data = await productService.getWishlist();
      setWishlist(data);
    } catch (error) {
      console.error('Error loading wishlist:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeItem = async (productId) => {
    try {
      await productService.removeFromWishlist(productId);
      await loadWishlist();
    } catch (error) {
      console.error('Error removing item:', error);
    }
  };

  const handleAddToCart = async (product) => {
    try {
      await addToCart(product.id, 1);
      navigate('/cart');
    } catch (error) {
      alert(error.message);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const items = wishlist?.items || [];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-blue-600 mb-4 hover:text-blue-700"
          >
            <ChevronLeft className="w-5 h-5" />
            {t('edit_profile.back')}
          </button>
          <div className="flex items-center gap-3 mb-4">
            <Heart className="w-8 h-8 text-red-600 fill-red-600" />
            <h1 className="text-3xl font-bold text-gray-900">{t('wishlist.title')}</h1>
          </div>
          <p className="text-gray-600">{items.length} {t('order_tracking.items')}</p>
        </div>

        {/* Content */}
        {items.length === 0 ? (
          <div className="bg-white rounded-lg p-12 text-center space-y-4">
            <Heart className="w-16 h-16 text-gray-300 mx-auto" />
            <h2 className="text-2xl font-semibold text-gray-900">{t('wishlist.empty_title')}</h2>
            <p className="text-gray-600">{t('wishlist.empty_desc')}</p>
            <button
              onClick={() => navigate('/products')}
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 inline-block mt-4"
            >
              {t('wishlist.browse_products')}
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((item) => (
              <div key={item.product.id} className="bg-white rounded-lg overflow-hidden shadow hover:shadow-lg transition">
                <div className="relative bg-gray-100 aspect-square overflow-hidden">
                  {item.product.image_url ? (
                    <img
                      src={item.product.image_url}
                      alt={item.product.name}
                      className="w-full h-full object-cover hover:scale-105 transition"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-300">
                      {t('product_detail.no_image')}
                    </div>
                  )}
                  <button
                    onClick={() => removeItem(item.product.id)}
                    className="absolute top-3 right-3 bg-red-500 text-white p-2 rounded-lg hover:bg-red-600"
                  >
                    <Heart className="w-5 h-5 fill-current" />
                  </button>
                </div>

                <div className="p-4 space-y-3">
                  <h3 className="font-semibold text-gray-900 line-clamp-2">{item.product.name}</h3>

                  <div className="space-y-1">
                    <p className="text-blue-600 font-bold text-lg">{formatPrice(item.product.price)}</p>
                    <StarRating rating={item.product.rating} size={3} />
                  </div>

                  {item.product.short_description && (
                    <p className="text-sm text-gray-600 line-clamp-2">{item.product.short_description}</p>
                  )}

                  <div className="space-y-2 pt-3 border-t border-gray-100">
                    <button
                      onClick={() => navigate(`/product/${item.product.id}`)}
                      className="w-full bg-gray-100 text-gray-900 py-2 rounded-lg font-semibold hover:bg-gray-200 transition"
                    >
                      {t('product_detail.back_to_products')}
                    </button>
                    <button
                      onClick={() => handleAddToCart(item.product)}
                      className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 transition flex items-center justify-center gap-2"
                    >
                      <ShoppingCart className="w-4 h-4" />
                      {t('wishlist.add_to_cart')}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Wishlist;
