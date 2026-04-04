import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { orderService } from '../services/orderService';
import { formatPrice } from '../utils/formatPrice';
import { ORDER_STATUS_LABELS } from '../utils/constants';
import { User, Package } from 'lucide-react';

const Profile = () => {
  const { profile, user, updateProfile } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    avatar_url: '',
  });

  useEffect(() => {
    if (profile) {
      setFormData({
        full_name: profile.full_name || '',
        avatar_url: profile.avatar_url || '',
      });
    }
  }, [profile]);

  useEffect(() => {
    loadOrders();
  }, [user]);

  const loadOrders = async () => {
    if (!user) return;

    try {
      const data = await orderService.getUserOrders(user.id);
      setOrders(data);
    } catch (error) {
      console.error('Error loading orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await updateProfile(formData);
      setEditing(false);
      alert('Profile updated successfully!');
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">My Profile</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-center mb-6">
                <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center">
                  <User className="w-12 h-12 text-blue-600" />
                </div>
              </div>

              {editing ? (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Full Name
                    </label>
                    <input
                      type="text"
                      name="full_name"
                      value={formData.full_name}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="flex space-x-2">
                    <button
                      type="submit"
                      className="flex-1 bg-blue-600 text-white py-2 rounded-md font-semibold hover:bg-blue-700 transition-colors"
                    >
                      Save
                    </button>
                    <button
                      type="button"
                      onClick={() => setEditing(false)}
                      className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-md font-semibold hover:bg-gray-300 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              ) : (
                <>
                  <h2 className="text-2xl font-bold text-gray-900 text-center mb-2">
                    {profile?.full_name || 'User'}
                  </h2>
                  <p className="text-gray-600 text-center mb-6">{profile?.email}</p>

                  <button
                    onClick={() => setEditing(true)}
                    className="w-full bg-blue-600 text-white py-2 rounded-md font-semibold hover:bg-blue-700 transition-colors"
                  >
                    Edit Profile
                  </button>
                </>
              )}
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center space-x-2 mb-6">
                <Package className="w-6 h-6 text-gray-700" />
                <h2 className="text-2xl font-bold text-gray-900">Order History</h2>
              </div>

              {loading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
              ) : orders.length > 0 ? (
                <div className="space-y-4">
                  {orders.map((order) => (
                    <div
                      key={order.id}
                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <p className="text-sm text-gray-600">
                            Order #{order.id.slice(0, 8)}
                          </p>
                          <p className="text-sm text-gray-500">
                            {new Date(order.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-gray-900">
                            {formatPrice(order.total_amount)}
                          </p>
                          <span
                            className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                              order.status === 'delivered'
                                ? 'bg-green-100 text-green-700'
                                : order.status === 'cancelled'
                                ? 'bg-red-100 text-red-700'
                                : 'bg-blue-100 text-blue-700'
                            }`}
                          >
                            {ORDER_STATUS_LABELS[order.status]}
                          </span>
                        </div>
                      </div>

                      <div className="space-y-2">
                        {order.items?.map((item) => (
                          <div
                            key={item.id}
                            className="flex justify-between text-sm text-gray-600"
                          >
                            <span>
                              {item.product?.name} x {item.quantity}
                            </span>
                            <span>{formatPrice(item.price * item.quantity)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-12">
                  No orders yet. Start shopping!
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
