import api from './api';

export const shippingService = {
  /**
   * Save a new shipping address to the database
   * @param {Object} addressData - The formatted address object from AddressSelector
   */
  saveAddress: async (addressData) => {
    try {
      // Mapping frontend fields to the snake_case PostgreSQL schema
      const payload = {
        full_name: addressData.fullName,
        phone_number: addressData.phoneNumber,
        province: addressData.province,
        district: addressData.district,
        ward: addressData.ward,
        street_address: addressData.streetAddress,
        address_type: addressData.addressType,
        latitude: addressData.latitude,
        longitude: addressData.longitude,
        is_default: addressData.isDefault || false
      };

      const response = await api.post('/shipping-addresses', payload);
      return response.data;
    } catch (error) {
      console.error("Error saving address:", error);
      throw error;
    }
  },

  /**
   * Get all shipping addresses for the current user
   */
  getUserAddresses: async () => {
    const response = await api.get('/shipping-addresses');
    return response.data;
  },

  /**
   * Delete an address
   */
  deleteAddress: async (id) => {
    await api.delete(`/shipping-addresses/${id}`);
  }
};

export default shippingService;
