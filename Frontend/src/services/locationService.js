import api from './api';

export const locationService = {
  async getProvinces() {
    const { data } = await api.get('/api/locations/provinces');
    return data.data || [];
  },

  async getDistricts(provinceCode) {
    if (!provinceCode) return [];
    const { data } = await api.get(`/api/locations/districts/${provinceCode}`);
    return data.data || [];
  },

  async getWards(districtCode) {
    if (!districtCode) return [];
    const { data } = await api.get(`/api/locations/wards/${districtCode}`);
    return data.data || [];
  },

  async searchLocation(query, type = 'all') {
    if (!query.trim()) return {};
    const { data } = await api.get('/api/locations/search', {
      params: { q: query, type },
    });
    return data.data || {};
  },
};
