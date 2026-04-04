import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ShoppingCart, ArrowLeft } from 'lucide-react';
import { formatPrice } from '../utils/formatPrice';
import { useCart } from '../hooks/useCart';
import { useAuth } from '../hooks/useAuth';
import { productService } from '../services/productService';

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { isAuthenticated } = useAuth();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    loadProduct();
  }, [id]);

  const loadProduct = async () => {
    try {
      const data = await productService.getProductById(id);
      setProduct(data);
    } catch (error) {
      console.error('Error loading product:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      alert('Please sign in to add items to cart');
      navigate('/login');
      return;
    }
    try {
      await addToCart(product.id, quantity);
      alert('Product added to cart!');
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

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-2xl text-gray-600 mb-4">Product not found</p>
          <button
            onClick={() => navigate('/products')}
            className="text-blue-600 hover:text-blue-700"
          >
            Back to Products
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back</span>
        </button>

        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 p-8">
            <div className="aspect-square bg-gray-200 rounded-lg overflow-hidden">
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">
                  No Image
                </div>
              )}
            </div>

            <div className="flex flex-col">
              <div className="mb-4">
                {product.category && (
                  <span className="inline-block bg-blue-100 text-blue-600 px-3 py-1 rounded-full text-sm font-medium">
                    {product.category.name}
                  </span>
                )}
              </div>

              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                {product.name}
              </h1>

              <div className="text-4xl font-bold text-blue-600 mb-6">
                {formatPrice(product.price)}
              </div>

              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-6">
                <span className="font-semibold text-gray-900">
                  {product.rating?.toFixed(1) ?? '0.0'} / 5
                </span>
                <span>{product.review_count ?? 0} reviews</span>
                <span>{product.view_count ?? 0} views</span>
              </div>

              <p className="text-gray-600 mb-6 leading-relaxed">
                {product.description}
              </p>

              <div className="mb-6">
                <p className="text-sm text-gray-600 mb-2">
                  Stock: <span className="font-semibold">{product.stock} available</span>
                </p>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quantity
                </label>
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    -
                  </button>
                  <span className="text-xl font-semibold">{quantity}</span>
                  <button
                    onClick={() =>
                      setQuantity(Math.min(product.stock, quantity + 1))
                    }
                    className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    +
                  </button>
                </div>
              </div>

              <button
                onClick={handleAddToCart}
                disabled={product.stock === 0}
                className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
              >
                <ShoppingCart className="w-6 h-6" />
                <span>{product.stock === 0 ? 'Out of Stock' : 'Add to Cart'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;
