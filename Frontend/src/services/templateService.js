import api from './api';

const templateService = {
  getTemplatesByType: async (productType) => {
    const { data } = await api.get(`/spec-templates/${productType}`);
    return data;
  },

  adminList: async (productType = null) => {
    const params = productType ? `?product_type=${productType}` : '';
    const { data } = await api.get(`/admin/spec-templates${params}`);
    return data;
  },

  adminCreate: async (payload) => {
    const { data } = await api.post('/admin/spec-templates', payload);
    return data;
  },

  adminDelete: async (templateId) => {
    await api.delete(`/admin/spec-templates/${templateId}`);
  },

  adminReorder: async (productType, ids) => {
    await api.put('/admin/spec-templates/reorder', { product_type: productType, ids });
  },

  adminListTypes: async () => {
    const { data } = await api.get('/admin/spec-templates/types');
    return data;
  },

  adminDeleteType: async (productType) => {
    await api.delete(`/admin/spec-templates/type/${productType}`);
  },
};

export default templateService;
