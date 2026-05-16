import api from './api';

export const addressService = {
  async getAddresses() {
    const { data } = await api.get('/addresses');
    return data;
  },

  async createAddress(address) {
    const { data } = await api.post('/addresses', address);
    return data;
  },

  async updateAddress(addressId, address) {
    const { data } = await api.put(`/addresses/${addressId}`, address);
    return data;
  },

  async deleteAddress(addressId) {
    await api.delete(`/addresses/${addressId}`);
  },

  async setDefaultAddress(addressId) {
    const { data } = await api.patch(`/addresses/${addressId}/set-default`);
    return data;
  },
};
