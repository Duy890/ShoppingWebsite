import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShoppingBag, ShieldCheck, CreditCard, Truck } from 'lucide-react';
import { formatPrice } from '../utils/formatPrice';
import { useCart } from '../hooks/useCart';
import { orderService } from '../services/orderService';
import { PAYMENT_METHODS, PAYMENT_METHOD_LABELS } from '../utils/constants';

const Checkout = () => {
  const navigate = useNavigate();
  const { items, cartTotal, clearCart } = useCart();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    shipping_address: '',
    paymentMethod: PAYMENT_METHODS.CREDIT_CARD,
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const orderData = {
        items: items.map((item) => ({
          product_id: item.product_id,
          quantity: item.quantity,
        })),
        shipping_address: formData.shipping_address,
        payment_method: formData.paymentMethod,
      };

      await orderService.createOrder(orderData);
      await clearCart();
      alert('Order placed successfully!');
      navigate('/profile');
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50/50 py-16">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center space-x-2 text-primary mb-4">
          <div className="h-1 w-8 bg-primary rounded-full" />
          <span className="text-xs font-bold uppercase tracking-widest">Final Step</span>
        </div>
        <h1 className="text-5xl font-black text-gray-900 tracking-tighter mb-12">Checkout</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          <div className="lg:col-span-2 space-y-8">
            <form onSubmit={handleSubmit} className="space-y-8">
              {/* Shipping Section */}
              <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 space-y-6">
                <div className="flex items-center space-x-3 mb-2">
                  <div className="bg-primary/10 p-2 rounded-lg text-primary">
                    <Truck className="w-5 h-5" />
                  </div>
                  <h2 className="text-xl font-black text-gray-900 uppercase tracking-tight">Shipping Details</h2>
                </div>
                
                <div>
                  <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-2">Delivery Address</label>
                  <textarea
                    name="shipping_address"
                    value={formData.shipping_address}
                    onChange={handleChange}
                    required
                    placeholder="Enter your full shipping address..."
                    rows={4}
                    className="w-full bg-gray-50 border border-gray-100 px-4 py-4 rounded-2xl text-sm font-semibold text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  />
                </div>
              </div>

              {/* Payment Section */}
              <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 space-y-6">
                <div className="flex items-center space-x-3 mb-2">
                  <div className="bg-primary/10 p-2 rounded-lg text-primary">
                    <CreditCard className="w-5 h-5" />
                  </div>
                  <h2 className="text-xl font-black text-gray-900 uppercase tracking-tight">Payment Method</h2>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {Object.entries(PAYMENT_METHODS).map(([key, value]) => (
                    <label 
                      key={value} 
                      className={`flex items-center space-x-4 p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                        formData.paymentMethod === value 
                          ? 'border-primary bg-primary/5' 
                          : 'border-gray-50 bg-gray-50 hover:border-gray-200'
                      }`}
                    >
                      <input
                        type="radio"
                        name="paymentMethod"
                        value={value}
                        checked={formData.paymentMethod === value}
                        onChange={handleChange}
                        className="w-4 h-4 text-primary focus:ring-primary border-gray-300"
                      />
                      <span className="text-sm font-bold text-gray-700">{PAYMENT_METHOD_LABELS[value]}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="bg-primary/5 rounded-2xl p-6 flex items-start space-x-4 border border-primary/10">
                <ShieldCheck className="w-6 h-6 text-primary shrink-0" />
                <p className="text-xs text-gray-600 leading-relaxed font-medium">
                  Your purchase is protected. We use industry-standard encryption to ensure your data stays safe and private. By clicking "Complete Purchase", you agree to our Terms of Service.
                </p>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gray-900 text-white py-6 rounded-2xl text-lg font-black uppercase tracking-widest hover:bg-primary transition-all duration-300 disabled:bg-gray-200 shadow-2xl shadow-gray-900/10 flex items-center justify-center space-x-3"
              >
                {loading ? 'Processing Transaction...' : 'Complete Purchase'}
              </button>
            </form>
          </div>

          <div className="lg:col-span-1">
            <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 sticky top-32">
              <h2 className="text-2xl font-black tracking-tight mb-8">Order Summary</h2>

              <div className="space-y-6 mb-8 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                {items.map((item) => (
                  <div key={item.id} className="flex justify-between items-start gap-4">
                    <div className="space-y-1">
                      <p className="text-sm font-black text-gray-900 line-clamp-1">{item.product?.name}</p>
                      <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Qty: {item.quantity}</p>
                    </div>
                    <span className="text-sm font-black text-primary">
                      {formatPrice((item.product?.price || 0) * item.quantity)}
                    </span>
                  </div>
                ))}
              </div>

              <div className="border-t border-gray-50 pt-8 space-y-4">
                <div className="flex justify-between text-xs font-bold text-gray-400 uppercase tracking-widest">
                  <span>Subtotal</span>
                  <span className="text-gray-900">{formatPrice(cartTotal)}</span>
                </div>
                <div className="flex justify-between text-xs font-bold text-gray-400 uppercase tracking-widest">
                  <span>Shipping</span>
                  <span className="text-green-600 font-black">FREE</span>
                </div>
                <div className="flex justify-between items-end pt-4">
                  <span className="text-xs font-black text-gray-900 uppercase tracking-widest">Total</span>
                  <span className="text-3xl font-black text-primary tracking-tighter">{formatPrice(cartTotal)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
