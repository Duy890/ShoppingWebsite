import { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { orderService } from '../services/orderService';
import { authService } from '../services/authService';
import { addressService } from '../services/addressService';
import { formatPrice } from '../utils/formatPrice';
import { ORDER_STATUS_LABELS, SHIPPING_METHOD_LABELS } from '../utils/constants';
import { Package, MapPin, User } from 'lucide-react';
import AvatarUploader from '../components/AvatarUploader';
import ProfileDropdown from '../components/ProfileDropdown';
import AddressCard from '../components/AddressCard';
import AddressFormModal from '../components/AddressFormModal';

const Profile = () => {
  const navigate = useNavigate();
  const { profile, user, updateProfile } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    avatar_url: '',
  });
  const [avatarPreview, setAvatarPreview] = useState('');
  const [selectedAvatarFile, setSelectedAvatarFile] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [addressLoading, setAddressLoading] = useState(true);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [addressModalOpen, setAddressModalOpen] = useState(false);
  const [editingAddress, setEditingAddress] = useState(null);
  const [deletingAddressId, setDeletingAddressId] = useState(null);
  const fileInputRef = useRef(null);

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
    loadAddresses().catch(() => {});
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

  const loadAddresses = async () => {
    if (!user) return;

    setAddressLoading(true);
    try {
      const data = await addressService.getAddresses();
      setAddresses(data);
      return data;
    } catch (error) {
      console.error('Error loading addresses:', error);
      throw error;
    } finally {
      setAddressLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleAvatarSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedAvatarFile(file);
    setAvatarPreview(URL.createObjectURL(file));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      let avatar_url = formData.avatar_url;

      if (selectedAvatarFile) {
        const result = await authService.uploadAvatar(selectedAvatarFile);
        avatar_url = result.avatar_url;
      }

      await updateProfile({ full_name: formData.full_name, avatar_url });
      setFormData((prev) => ({ ...prev, avatar_url }));
      setSelectedAvatarFile(null);
      setAvatarPreview('');
      setEditing(false);
      alert('Profile updated successfully!');
    } catch (error) {
      alert(error.message || 'Unable to update profile.');
    }
  };

  const handleAddressModalSubmit = async (addressData) => {
    try {
      let result;
      if (editingAddress) {
        result = await addressService.updateAddress(editingAddress.id, addressData);
      } else {
        const payload = { ...addressData };
        if (addresses.length === 0) {
          payload.is_default = true;
        }
        result = await addressService.createAddress(payload);
      }
      await loadAddresses();
      setAddressModalOpen(false);
      setEditingAddress(null);
      alert(editingAddress ? 'Address updated successfully!' : 'Address added successfully!');
    } catch (error) {
      alert(error.message || 'Unable to save address.');
      throw error;
    }
  };

  const handleDeleteAddress = async (addressId) => {
    if (!window.confirm('Are you sure you want to delete this address?')) return;

    setDeletingAddressId(addressId);
    try {
      await addressService.deleteAddress(addressId);
      await loadAddresses();
      alert('Address deleted successfully!');
    } catch (error) {
      alert(error.message || 'Unable to delete address.');
    } finally {
      setDeletingAddressId(null);
    }
  };

  const handleSetDefaultAddress = async (addressId) => {
    try {
      await addressService.setDefaultAddress(addressId);
      await loadAddresses();
    } catch (error) {
      alert(error.message || 'Unable to set default address.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">My Profile</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex flex-col items-center justify-center mb-6">
                <AvatarUploader
                  avatarUrl={formData.avatar_url}
                  previewUrl={avatarPreview}
                  inputRef={fileInputRef}
                  onClick={() => fileInputRef.current?.click()}
                  onFileChange={handleAvatarSelect}
                />
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
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>

                  <div className="flex space-x-2">
                    <button
                      type="submit"
                      className="flex-1 bg-primary text-white py-2 rounded-md font-semibold hover:bg-orange-600 transition-colors shadow-sm active:scale-[0.98]"
                    >
                      Save
                    </button>
                    <button
                      type="button"
                      onClick={() => setEditing(false)}
                      className="flex-1 bg-gray-100 text-gray-700 py-2 rounded-md font-semibold hover:bg-gray-200 transition-colors"
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

                  <div className="flex items-center justify-center gap-3">
                    <button
                      type="button"
                      onClick={() => setEditing(true)}
                      className="rounded-full bg-primary px-5 py-3 text-sm font-semibold text-white shadow-sm hover:bg-orange-600"
                    >
                      Edit Profile
                    </button>
                    <ProfileDropdown
                      open={dropdownOpen}
                      onToggle={setDropdownOpen}
                      onSelect={(action) => {
                        setDropdownOpen(false);
                        if (action === 'rename') {
                          setEditing(true);
                          return;
                        }
                        if (action === 'avatar') {
                          fileInputRef.current?.click();
                          return;
                        }
                        if (action === 'address') {
                          setAddressModalOpen(true);
                          return;
                        }
                      }}
                    />
                  </div>
                </>
              )}
            </div>

            <div className="bg-white rounded-3xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-orange-500" />
                  <h2 className="text-2xl font-bold text-gray-900">Addresses</h2>
                </div>
                <button
                  onClick={() => {
                    setEditingAddress(null);
                    setAddressModalOpen(true);
                  }}
                  className="px-4 py-2 text-sm font-semibold bg-orange-50 text-orange-600 rounded-lg hover:bg-orange-100 transition"
                >
                  + Add Address
                </button>
              </div>

              {addressLoading ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-orange-500" />
                </div>
              ) : addresses.length > 0 ? (
                <div className="space-y-3">
                  {addresses.map((address) => (
                    <AddressCard 
                      key={address.id} 
                      address={address}
                      onEdit={() => setEditingAddress(address) || setAddressModalOpen(true)}
                      onDelete={() => handleDeleteAddress(address.id)}
                      onSetDefault={() => handleSetDefaultAddress(address.id)}
                      loading={deletingAddressId === address.id}
                    />
                  ))}
                </div>
              ) : (
                <div className="rounded-3xl border border-dashed border-gray-200 bg-gray-50 px-5 py-8 text-center">
                  <MapPin className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-sm text-gray-500 font-medium">No addresses saved yet</p>
                  <button
                    onClick={() => {
                      setEditingAddress(null);
                      setAddressModalOpen(true);
                    }}
                    className="mt-4 px-4 py-2 text-sm font-semibold bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition"
                  >
                    Add Your First Address
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center space-x-2 mb-6">
                <Package className="w-6 h-6 text-primary" />
                <h2 className="text-2xl font-bold text-gray-900">Order History</h2>
              </div>

              {loading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                </div>
              ) : orders.length > 0 ? (
                <div className="space-y-4">
                  {orders.map((order) => (
                    <div
                      key={order.id}
                      className="border border-gray-100 rounded-xl p-5 hover:border-primary/30 hover:shadow-lg transition-all duration-300 bg-white"
                    >
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <p className="text-xs font-mono text-primary font-bold uppercase tracking-wider mb-1">
                            Order #{order.id.slice(0, 8)}
                          </p>
                          <p className="text-sm text-gray-500">
                            {new Date(order.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-xl font-black text-gray-900">
                            {formatPrice(Number(order.total_amount || 0))}
                          </p>
                          <span
                            className={`inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tight ${
                              order.status === 'delivered'
                                ? 'bg-green-100 text-green-700'
                                : order.status === 'cancelled'
                                ? 'bg-red-100 text-red-700'
                                : 'bg-primary/10 text-primary'
                            }`}
                          >
                            {ORDER_STATUS_LABELS[order.status]}
                          </span>
                          {order.shipping_method && (
                            <p className="text-[10px] text-gray-400 mt-1">
                              {SHIPPING_METHOD_LABELS[order.shipping_method] || order.shipping_method}
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="space-y-3 pt-3 border-t border-gray-50">
                        {order.items?.map((item) => (
                          <div
                            key={item.id}
                            className="flex justify-between text-sm items-center"
                          >
                            <span className="text-gray-700">
                              <span className="font-semibold text-gray-900">{item.quantity}x</span> {item.product?.name}
                            </span>
                            <span className="font-medium text-gray-600">{formatPrice(Number(item.price || 0) * Number(item.quantity || 0))}</span>
                          </div>
                        ))}
                      </div>

                      <div className="flex justify-end pt-4 border-t border-gray-50">
                        <Link
                          to={`/order/${order.id}/tracking`}
                          className="inline-flex items-center px-4 py-2 text-sm font-medium text-primary hover:text-orange-600 border border-primary/20 rounded-lg hover:bg-primary/5 transition-colors"
                        >
                          <Package className="w-4 h-4 mr-2" />
                          Track Order
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
                  <div className="relative mb-6">
                    <div className="absolute inset-0 bg-primary/5 rounded-full blur-2xl transform scale-150"></div>
                    <div className="relative bg-white p-6 rounded-2xl shadow-sm border border-primary/10">
                      <Package className="w-20 h-20 text-primary/20 stroke-[1]" />
                    </div>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    Your history is a clean slate!
                  </h3>
                  <p className="text-gray-500 max-w-sm mx-auto mb-8">
                    Looks like you haven't made a purchase yet! Check out our electronics collection.
                  </p>
                  <button 
                    onClick={() => navigate('/products')}
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-full shadow-sm text-white bg-primary hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-all active:scale-95"
                  >
                    Start Shopping
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <AddressFormModal
        open={addressModalOpen}
        onClose={() => {
          setAddressModalOpen(false);
          setEditingAddress(null);
        }}
        onSubmit={handleAddressModalSubmit}
        initialData={editingAddress}
        title={editingAddress ? 'Edit Address' : 'Add Address'}
        submitLabel={editingAddress ? 'Update Address' : 'Add Address'}
      />
    </div>
  );
};

export default Profile;
