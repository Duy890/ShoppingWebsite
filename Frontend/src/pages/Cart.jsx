import { Link, useNavigate } from 'react-router-dom';
import { Trash2, ShoppingBag } from 'lucide-react';
import { formatPrice } from '../utils/formatPrice';
import { useCart } from '../hooks/useCart';

const Cart = () => {
  const navigate = useNavigate();
  const { items, cartTotal, updateItem, removeItem, loading } = useCart();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="text-center">
          <ShoppingBag className="w-24 h-24 text-gray-300 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Your cart is empty</h2>
          <p className="text-gray-600 mb-8">Add some products to get started!</p>
          <Link
            to="/products"
            className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Browse Products
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Shopping Cart</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              {items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center p-6 border-b last:border-b-0"
                >
                  <div className="w-24 h-24 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                    {item.product?.image_url ? (
                      <img
                        src={item.product.image_url}
                        alt={item.product?.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                        No Image
                      </div>
                    )}
                  </div>

                  <div className="flex-1 ml-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {item.product?.name}
                    </h3>
                    <p className="text-xl font-bold text-blue-600">
                      {formatPrice(item.product?.price)}
                    </p>
                  </div>

                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() =>
                          updateItem(item.id, Math.max(1, item.quantity - 1))
                        }
                        className="px-3 py-1 border border-gray-300 rounded-md hover:bg-gray-50"
                      >
                        -
                      </button>
                      <span className="text-lg font-semibold w-8 text-center">
                        {item.quantity}
                      </span>
                      <button
                        onClick={() =>
                          updateItem(
                            item.id,
                            Math.min(item.product?.stock || 99, item.quantity + 1)
                          )
                        }
                        className="px-3 py-1 border border-gray-300 rounded-md hover:bg-gray-50"
                      >
                        +
                      </button>
                    </div>

                    <button
                      onClick={() => removeItem(item.id)}
                      className="text-red-500 hover:text-red-700 p-2"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-24">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Order Summary</h2>

              <div className="space-y-4 mb-6">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal</span>
                  <span>{formatPrice(cartTotal)}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Shipping</span>
                  <span>Calculated at checkout</span>
                </div>
                <div className="border-t pt-4">
                  <div className="flex justify-between text-xl font-bold text-gray-900">
                    <span>Total</span>
                    <span>{formatPrice(cartTotal)}</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => navigate('/checkout')}
                className="w-full bg-blue-600 text-white py-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors mb-4"
              >
                Proceed to Checkout
              </button>

              <Link
                to="/products"
                className="block text-center text-blue-600 hover:text-blue-700 font-medium"
              >
                Continue Shopping
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;
