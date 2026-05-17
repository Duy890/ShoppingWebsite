import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShoppingBag, ShieldCheck, CreditCard, Truck, Clock } from 'lucide-react';
import { formatPrice } from '../utils/formatPrice';
import { useCart } from '../hooks/useCart';
import { orderService } from '../services/orderService';
import AddressSelector from '../components/AddressSelector';
import { PAYMENT_METHODS, PAYMENT_METHOD_LABELS, SHIPPING_METHOD_CONFIG } from '../utils/constants';
import { formatAddress } from '../utils/addressValidation';

const Checkout = () => {
  const navigate = useNavigate();
  const { items, cartTotal, clearCart } = useCart();
  const [loading, setLoading] = useState(false);
  const [selectedAddress, setSelectedAddress] = useState(null);
  const [selectedShipping, setSelectedShipping] = useState('standard');
  const [orderNote, setOrderNote] = useState('');
  const [formData, setFormData] = useState({
    paymentMethod: PAYMENT_METHODS.CREDIT_CARD,
  });

  const shippingFee = SHIPPING_METHOD_CONFIG[selectedShipping]?.shipping_fee || 0;
  const totalAmount = Number(cartTotal || 0) + Number(shippingFee || 0);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleAddressSelect = (address) => {
    setSelectedAddress(address);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (items.length === 0) {
      alert('Your cart is empty');
      return;
    }

    if (!selectedAddress) {
      alert('Please select a delivery address');
      return;
    }

    if (!formData.paymentMethod) {
      alert('Please select a payment method');
      return;
    }

    if (!selectedShipping) {
      alert('Please select a shipping method');
      return;
    }

    setLoading(true);

    try {
      console.log('CHECKOUT ITEMS', items);

      const orderItems = items.map((item) => {
        const productId = item.product?.id || item.product_id;
        const price = item.variant?.price || item.product?.price || 0;

        if (!productId) {
          throw new Error(`Cart item "${item.product?.name || 'Unknown'}" is missing a product ID`);
        }

        return {
          product_id: productId,
          quantity: item.quantity,
          price,
        };
      });

      const orderData = {
        items: orderItems,
        address_id: selectedAddress.id,
        shipping_address: formatAddress(selectedAddress),
        payment_method: formData.paymentMethod,
        shipping_method: selectedShipping,
        shipping_fee: shippingFee,
        order_note: orderNote.trim() || null,
      };

      console.log('ORDER PAYLOAD', JSON.stringify(orderData, null, 2));

      await orderService.createOrder(orderData);
      await clearCart();
      alert('Order placed successfully!');
      navigate('/profile');
    } catch (error) {
      console.error('ORDER ERROR', error.response?.data || error.message);
      alert(error.response?.data ? JSON.stringify(error.response.data) : error.message);
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
              {/* Shipping Address Section */}
              <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 space-y-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="bg-orange-500/10 p-2 rounded-lg text-orange-500">
                    <Truck className="w-5 h-5" />
                  </div>
                  <h2 className="text-xl font-black text-gray-900 uppercase tracking-tight">Shipping Address</h2>
                </div>
                
                <AddressSelector 
                  selectedAddressId={selectedAddress?.id}
                  onAddressSelect={handleAddressSelect}
                />
              </div>

              {/* Shipping Method Section */}
              <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 space-y-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="bg-orange-500/10 p-2 rounded-lg text-orange-500">
                    <Clock className="w-5 h-5" />
                  </div>
                  <h2 className="text-xl font-black text-gray-900 uppercase tracking-tight">Shipping Method</h2>
                </div>
                
                <div className="space-y-3">
                  {Object.values(SHIPPING_METHOD_CONFIG).map((method) => (
                    <label
                      key={method.code}
                      className={`flex items-center justify-between p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                        selectedShipping === method.code
                          ? 'border-orange-500 bg-orange-50'
                          : 'border-gray-50 bg-gray-50 hover:border-gray-200'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <input
                          type="radio"
                          name="shippingMethod"
                          value={method.code}
                          checked={selectedShipping === method.code}
                          onChange={() => setSelectedShipping(method.code)}
                          className="w-4 h-4 accent-orange-500"
                        />
                        <div>
                          <span className="text-sm font-bold text-gray-900">{method.name}</span>
                          <p className="text-xs text-gray-500 font-medium">{method.description}</p>
                        </div>
                      </div>
                      <span className="text-sm font-black text-gray-900">{formatPrice(method.shipping_fee)}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Payment Section */}
              <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 space-y-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="bg-orange-500/10 p-2 rounded-lg text-orange-500">
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
                          ? 'border-orange-500 bg-orange-50' 
                          : 'border-gray-50 bg-gray-50 hover:border-gray-200'
                      }`}
                    >
                      <input
                        type="radio"
                        name="paymentMethod"
                        value={value}
                        checked={formData.paymentMethod === value}
                        onChange={handleChange}
                        className="w-4 h-4 accent-orange-500"
                      />
                      <span className="text-sm font-bold text-gray-700">{PAYMENT_METHOD_LABELS[value]}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Order Note Section */}
              <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 space-y-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="bg-orange-500/10 p-2 rounded-lg text-orange-500">
                    <ShoppingBag className="w-5 h-5" />
                  </div>
                  <h2 className="text-xl font-black text-gray-900 uppercase tracking-tight">Order Note</h2>
                </div>
                
                <textarea
                  value={orderNote}
                  onChange={(e) => setOrderNote(e.target.value.slice(0, 500))}
                  placeholder="Additional delivery instructions (optional)..."
                  rows={3}
                  maxLength={500}
                  className="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-4 text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-none"
                />
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest text-right">
                  {orderNote.length}/500
                </p>
              </div>

              <div className="bg-orange-50/50 rounded-2xl p-6 flex items-start space-x-4 border border-orange-200">
                <ShieldCheck className="w-6 h-6 text-orange-600 shrink-0" />
                <p className="text-xs text-gray-600 leading-relaxed font-medium">
                  Your purchase is protected. We use industry-standard encryption to ensure your data stays safe and private. By clicking "Complete Purchase", you agree to our Terms of Service.
                </p>
              </div>

              <button
                type="submit"
                disabled={loading || !selectedAddress || items.length === 0 || !formData.paymentMethod || !selectedShipping}
                className="w-full bg-gray-900 text-white py-6 rounded-2xl text-lg font-black uppercase tracking-widest hover:bg-orange-600 transition-all duration-300 disabled:bg-gray-300 disabled:cursor-not-allowed shadow-2xl shadow-gray-900/10 flex items-center justify-center space-x-3"
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
                  <span className="text-gray-900">{formatPrice(Number(cartTotal || 0))}</span>
                </div>
                <div className="flex justify-between text-xs font-bold text-gray-400 uppercase tracking-widest">
                  <span>Shipping</span>
                  <span className="text-gray-900">{formatPrice(Number(shippingFee || 0))}</span>
                </div>
                <div className="flex justify-between items-end pt-4 border-t border-gray-50">
                  <span className="text-xs font-black text-gray-900 uppercase tracking-widest">Total</span>
                  <span className="text-3xl font-black text-primary tracking-tighter">{formatPrice(Number(totalAmount || 0))}</span>
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
