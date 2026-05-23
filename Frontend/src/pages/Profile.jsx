import { useNavigate, Link } from 'react-router-dom';
import { formatPrice } from '../utils/formatPrice';
import { ORDER_STATUS_LABELS, SHIPPING_METHOD_LABELS } from '../utils/constants';
import { Package, MapPin, User } from 'lucide-react';
import AddressCard from '../components/AddressCard';
import AddressFormModal from '../components/AddressFormModal';
import { useProfile } from '../hooks/useProfile';

const Profile = () => {
  const navigate = useNavigate();

  const {
    profile,
    orders,
    loading,
    addresses,
    addressLoading,
    addressModalOpen,
    setAddressModalOpen,
    editingAddress,
    setEditingAddress,
    deletingAddressId,
    confirmDialog,
    setConfirmDialog,
    handleAddressModalSubmit,
    handleDeleteAddress,
    deleteAddress,
    handleSetDefaultAddress,
  } = useProfile();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">My Profile</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex flex-col items-center justify-center mb-6">
                <div className="relative inline-flex">
                  <div className="w-28 h-28 rounded-full overflow-hidden border-2 border-primary/20 bg-white shadow-sm">
                    {profile?.avatar_url ? (
                      <img
                        src={profile.avatar_url}
                        alt="Avatar"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-primary/5 text-primary">
                        <User className="w-10 h-10" />
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <h2 className="text-2xl font-bold text-gray-900 text-center mb-2">
                {profile?.full_name || 'User'}
              </h2>
              <p className="text-gray-600 text-center mb-6">{profile?.email}</p>

              <div className="flex justify-center mt-2">
                <button
                  type="button"
                  onClick={() => navigate('/edit-profile')}
                  className="rounded-full bg-primary px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-orange-600 transition-colors active:scale-[0.98]"
                >
                  Edit Profile
                </button>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
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

      {confirmDialog.open && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-2xl p-8 max-w-sm w-full shadow-2xl">
            <p className="text-sm font-semibold text-gray-700 mb-6">{confirmDialog.message}</p>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={async () => {
                  await confirmDialog.onConfirm?.();
                  setConfirmDialog({ open: false, message: '', onConfirm: null });
                }}
                className="flex-1 bg-red-500 text-white py-2 rounded-lg font-bold hover:bg-red-600"
              >
                Confirm
              </button>
              <button
                type="button"
                onClick={() => setConfirmDialog({ open: false, message: '', onConfirm: null })}
                className="flex-1 bg-gray-100 text-gray-700 py-2 rounded-lg font-bold hover:bg-gray-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
