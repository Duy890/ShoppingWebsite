import { useEffect, useState } from 'react';
import { toast } from 'react-hot-toast';
import { useAuth } from './useAuth';
import { orderService } from '../services/orderService';
import { authService } from '../services/authService';
import { addressService } from '../services/addressService';

export const useProfile = () => {
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
  const [confirmDialog, setConfirmDialog] = useState({ open: false, message: '', onConfirm: null });

  useEffect(() => {
    if (profile) {
      setFormData({
        full_name: profile.full_name || '',
        avatar_url: profile.avatar_url || '',
      });
    }
  }, [profile]);

  useEffect(() => {
    const init = async () => {
      await loadOrders();
      await loadAddresses().catch(() => {});
    };

    if (user) {
      init();
    }
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
      toast.success('Profile updated successfully!');
    } catch (error) {
      toast.error(error.message || 'Unable to update profile.');
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
      toast.success(editingAddress ? 'Address updated successfully!' : 'Address added successfully!');
      return result;
    } catch (error) {
      toast.error(error.message || 'Unable to save address.');
      console.error('Unable to save address.', error);
      throw error;
    }
  };

  const handleDeleteAddress = async (addressId) => {
    setConfirmDialog({
      open: true,
      message: 'Are you sure you want to delete this address?',
      onConfirm: () => deleteAddress(addressId),
    });
  };

  const deleteAddress = async (addressId) => {
    setDeletingAddressId(addressId);
    try {
      await addressService.deleteAddress(addressId);
      await loadAddresses();
      toast.success('Address deleted successfully!');
    } catch (error) {
      console.error('Unable to delete address.', error);
      toast.error(error.message || 'Unable to delete address.');
    } finally {
      setDeletingAddressId(null);
    }
  };

  const handleSetDefaultAddress = async (addressId) => {
    try {
      await addressService.setDefaultAddress(addressId);
      await loadAddresses();
    } catch (error) {
      console.error('Unable to set default address.', error);
      toast.error(error.message || 'Unable to set default address.');
    }
  };

  return {
    profile,
    user,
    updateProfile,
    orders,
    loading,
    editing,
    setEditing,
    formData,
    setFormData,
    avatarPreview,
    setAvatarPreview,
    selectedAvatarFile,
    setSelectedAvatarFile,
    addresses,
    addressLoading,
    dropdownOpen,
    setDropdownOpen,
    addressModalOpen,
    setAddressModalOpen,
    editingAddress,
    setEditingAddress,
    deletingAddressId,
    confirmDialog,
    setConfirmDialog,
    loadOrders,
    loadAddresses,
    handleChange,
    handleAvatarSelect,
    handleSubmit,
    handleAddressModalSubmit,
    handleDeleteAddress,
    deleteAddress,
    handleSetDefaultAddress,
  };
};
