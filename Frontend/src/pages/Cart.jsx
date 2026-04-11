import { Link, useNavigate } from 'react-router-dom';
import { Trash2, ShoppingBag, ArrowRight, Minus, Plus } from 'lucide-react';
import { formatPrice } from '../utils/formatPrice';
import { useCart } from '../hooks/useCart';

const Cart = () => {
  const navigate = useNavigate();
  const { items, cartTotal, updateItem, removeItem, loading } = useCart();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center px-4">
        <div className="text-center space-y-6">
          <div className="bg-gray-50 w-32 h-32 rounded-full flex items-center justify-center mx-auto">
            <ShoppingBag className="w-12 h-12 text-gray-300" />
          </div>
          <div className="space-y-2">
            <h2 className="text-4xl font-black text-gray-900 tracking-tighter">Your cart is empty</h2>
            <p className="text-gray-500">Looks like you haven't added any tech yet.</p>
          </div>
          <Link
            to="/products"
            className="inline-block bg-primary text-white px-10 py-4 rounded-xl font-black uppercase tracking-widest text-xs hover:bg-gray-900 transition-colors shadow-xl shadow-primary/20"
          >
            Start Shopping
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50/50 py-16">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center space-x-2 text-primary mb-4">
          <div className="h-1 w-8 bg-primary rounded-full" />
          <span className="text-xs font-bold uppercase tracking-widest">Your Selection</span>
        </div>
        <h1 className="text-5xl font-black text-gray-900 tracking-tighter mb-12">Shopping Cart</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
              {items.map((item) => (
                <div
                  key={item.id}
                  className="flex flex-col sm:items-center sm:flex-row p-8 border-b border-gray-50 last:border-b-0 group"
                >
                  <div className="w-32 h-32 bg-gray-50 rounded-2xl overflow-hidden flex-shrink-0 border border-gray-100 p-4">
                    {item.product?.image_url ? (
                      <img
                        src={item.product.image_url}
                        alt={item.product?.name}
                        className="w-full h-full object-contain group-hover:scale-110 transition-transform duration-500"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-300 italic text-[10px]">
                        No Image
                      </div>
                    )}
                  </div>

                  <div className="flex-1 mt-6 sm:mt-0 sm:ml-8">
                    <div className="flex items-center space-x-2 mb-1">
                       <span className="text-[10px] font-bold text-primary uppercase tracking-widest">{item.product?.category?.name}</span>
                    </div>
                    <h3 className="text-xl font-black text-gray-900 group-hover:text-primary transition-colors">
                      {item.product?.name}
                    </h3>
                    <p className="text-2xl font-black text-primary mt-2">
                      {formatPrice(item.product?.price)}
                    </p>
                  </div>

                  <div className="flex items-center justify-between sm:justify-end space-x-8 mt-6 sm:mt-0">
                    <div className="flex items-center bg-gray-50 rounded-xl border border-gray-100 p-1">
                      <button
                        onClick={() =>
                          updateItem(item.id, Math.max(1, item.quantity - 1))
                        }
                        className="p-2 text-gray-400 hover:text-primary transition-colors"
                      >
                        <Minus className="w-4 h-4" />
                      </button>
                      <span className="text-sm font-black w-8 text-center text-gray-900">
                        {item.quantity}
                      </span>
                      <button
                        onClick={() =>
                          updateItem(
                            item.id,
                            Math.min(item.product?.stock || 99, item.quantity + 1)
                          )
                        }
                        className="p-2 text-gray-400 hover:text-primary transition-colors"
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>

                    <button
                      onClick={() => removeItem(item.id)}
                      className="text-gray-300 hover:text-red-500 transition-colors p-2"
                      title="Remove Item"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="bg-gray-900 rounded-3xl p-8 sticky top-32 text-white shadow-2xl shadow-gray-900/20">
              <h2 className="text-2xl font-black tracking-tight mb-8">Order Summary</h2>

              <div className="space-y-6 mb-8">
                <div className="flex justify-between text-gray-400 font-bold text-xs uppercase tracking-widest">
                  <span>Subtotal</span>
                  <span className="text-white">{formatPrice(cartTotal)}</span>
                </div>
                <div className="flex justify-between text-gray-400 font-bold text-xs uppercase tracking-widest">
                  <span>Shipping</span>
                  <span className="text-green-400">FREE</span>
                </div>
                <div className="border-t border-white/10 pt-6">
                  <div className="flex justify-between items-end">
                    <span className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Total Amount</span>
                    <span className="text-4xl font-black text-primary tracking-tighter">
                      {formatPrice(cartTotal)}
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => navigate('/checkout')}
                className="w-full bg-primary text-white py-5 rounded-2xl font-black uppercase tracking-widest text-xs hover:bg-white hover:text-primary transition-all duration-300 flex items-center justify-center group"
              >
                <span>Proceed to Checkout</span>
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </button>

              <Link
                to="/products"
                className="block text-center text-gray-400 hover:text-white font-bold text-[10px] uppercase tracking-widest mt-6 transition-colors"
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
