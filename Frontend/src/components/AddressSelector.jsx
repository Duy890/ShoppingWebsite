import { useState, useEffect } from 'react';
import { Plus, AlertCircle, Loader } from 'lucide-react';
import AddressCard from './AddressCard';
import AddressFormModal from './AddressFormModal';
import { addressService } from '../services/addressService';

/**
 * Address selector component for checkout page
 * Displays saved addresses and allows selection, add, edit, delete
 */
const AddressSelector = ({ selectedAddressId, onAddressSelect, onAddressChange }) => {
  const [addresses, setAddresses] = useState([]);
  const [selectedId, setSelectedId] = useState(selectedAddressId);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingAddress, setEditingAddress] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAddresses().catch(() => {});
  }, []);

  useEffect(() => {
    setSelectedId(selectedAddressId || null);
  }, [selectedAddressId]);

  const selectFromAddresses = (addressList, preferredAddressId = null) => {
    const preferred = preferredAddressId
      ? addressList.find((address) => address.id === preferredAddressId)
      : null;
    const selected = preferred || addressList.find((address) => address.is_default) || addressList[0] || null;

    setSelectedId(selected?.id || null);
    onAddressSelect?.(selected);
    return selected;
  };

  const loadAddresses = async ({ preferredAddressId = selectedId, showLoading = true } = {}) => {
    if (showLoading) {
      setLoading(true);
    }
    setError(null);
    try {
      const data = await addressService.getAddresses();
      setAddresses(data);
      onAddressChange?.(data);

      const selectedStillExists = preferredAddressId
        ? data.some((address) => address.id === preferredAddressId)
        : false;
      if (!selectedStillExists || preferredAddressId) {
        selectFromAddresses(data, preferredAddressId);
      }

      return data;
    } catch (err) {
      console.error('Error loading addresses:', err);
      setError('Failed to load addresses');
      throw err;
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  };

  const handleSelectAddress = (address) => {
    setSelectedId(address.id);
    onAddressSelect?.(address);
  };

  const handleAddAddress = async (formData) => {
    try {
      const newAddress = await addressService.createAddress(formData);
      await loadAddresses({ preferredAddressId: newAddress.id, showLoading: false });
      setModalOpen(false);
    } catch (err) {
      alert(err.message || 'Failed to add address');
      throw err;
    }
  };

  const handleEditAddress = (address) => {
    setEditingAddress(address);
    setModalOpen(true);
  };

  const handleUpdateAddress = async (formData) => {
    if (!editingAddress) return;

    try {
      const updated = await addressService.updateAddress(editingAddress.id, formData);
      await loadAddresses({ preferredAddressId: updated.id, showLoading: false });
      
      setModalOpen(false);
      setEditingAddress(null);
    } catch (err) {
      alert(err.message || 'Failed to update address');
      throw err;
    }
  };

  const handleDeleteAddress = async (addressId) => {
    if (!window.confirm('Are you sure you want to delete this address?')) return;

    setDeleting(addressId);
    try {
      await addressService.deleteAddress(addressId);
      await loadAddresses({ preferredAddressId: selectedId === addressId ? null : selectedId, showLoading: false });
    } catch (err) {
      alert(err.message || 'Failed to delete address');
    } finally {
      setDeleting(null);
    }
  };

  const handleSetDefault = async (addressId) => {
    try {
      const updated = await addressService.setDefaultAddress(addressId);
      await loadAddresses({ preferredAddressId: updated.id, showLoading: false });
    } catch (err) {
      alert(err.message || 'Failed to set default address');
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-32 bg-gray-100 rounded-xl animate-pulse" />
        <div className="h-32 bg-gray-100 rounded-xl animate-pulse" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-gray-900">Delivery Address</h3>
        <button
          onClick={() => {
            setEditingAddress(null);
            setModalOpen(true);
          }}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-orange-50 text-orange-600 hover:bg-orange-100 transition font-medium text-sm"
        >
          <Plus className="w-4 h-4" />
          Add Address
        </button>
      </div>

      {/* Error State */}
      {error && (
        <div className="flex items-start gap-3 p-4 rounded-lg bg-red-50 border border-red-200">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-900">{error}</p>
            <button
              onClick={loadAddresses}
              className="text-xs text-red-600 hover:text-red-700 mt-2 underline"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Empty State */}
      {addresses.length === 0 ? (
        <div className="p-8 text-center border-2 border-dashed border-gray-300 rounded-xl">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600 font-medium mb-3">No addresses saved yet</p>
          <button
            onClick={() => {
              setEditingAddress(null);
              setModalOpen(true);
            }}
            className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition font-medium"
          >
            Add Your First Address
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {addresses.map(address => (
            <AddressCard
              key={address.id}
              address={address}
              selected={selectedId === address.id}
              onSelect={() => handleSelectAddress(address)}
              onEdit={() => handleEditAddress(address)}
              onDelete={() => handleDeleteAddress(address.id)}
              onSetDefault={() => handleSetDefault(address.id)}
              loading={deleting === address.id}
            />
          ))}
        </div>
      )}

      {/* Add/Edit Address Modal */}
      <AddressFormModal
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingAddress(null);
        }}
        onSubmit={editingAddress ? handleUpdateAddress : handleAddAddress}
        initialData={editingAddress}
        title={editingAddress ? 'Edit Address' : 'Add Address'}
        submitLabel={editingAddress ? 'Update Address' : 'Add Address'}
      />
    </div>
  );
};

export default AddressSelector;
