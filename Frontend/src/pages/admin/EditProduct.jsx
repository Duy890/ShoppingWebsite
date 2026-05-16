import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useProducts } from '../../hooks/useProducts';
import { productService } from '../../services/productService';
import Breadcrumbs from '../../components/Breadcrumbs';
import AdminVariantManager from '../../components/AdminVariantManager';

const EditProduct = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { categories, products = [], loading: productsLoading } = useProducts();
  const [activeTab, setActiveTab] = useState('basic');
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    description: '',
    short_description: '',
    price: '',
    stock: '',
    category_id: '',
    brand: '',
    product_type: '',
    product_line: '',
    sku: '',
    featured: false,
    status: 'active',
    variants: [],
    specs: [],
    product_specs: [],
    images: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(null);

  const productType = formData.product_type;
  const brand = formData.brand;
  const productLine = formData.product_line;
  const productName = formData.name;

  const breadcrumbPreview = [
    { name: 'Trang chủ', url: '/' },
    ...(productType ? [{ name: productType, url: `/${productType.toLowerCase().replace(/\s+/g, '-')}` }] : []),
    ...(brand ? [{ name: brand, url: productType ? `/${productType.toLowerCase().replace(/\s+/g, '-')}/${brand.toLowerCase().replace(/\s+/g, '-')}` : null }] : []),
    ...(productLine ? [{ name: productLine, url: productType && brand ? `/${productType.toLowerCase().replace(/\s+/g, '-')}/${brand.toLowerCase().replace(/\s+/g, '-')}/${productLine.toLowerCase().replace(/\s+/g, '-')}` : null }] : []),
    ...(productName ? [{ name: productName, url: null }] : []),
  ].flat().filter(crumb => crumb && crumb.name);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        setLoading(true);
        const product = await productService.getProductById(id);
        
        // Transform product_specs to the format used in the form
        const specs = [];
        
        // Group specs by group_name
        const groupedSpecs = {};
        if (product.product_specs && product.product_specs.length > 0) {
          product.product_specs.forEach(spec => {
            const group = spec.group_name || 'Ungrouped';
            if (!groupedSpecs[group]) {
              groupedSpecs[group] = [];
            }
            groupedSpecs[group].push({
              isGroup: false,
              group_name: spec.group_name,
              spec_key: spec.spec_key,
              spec_value: spec.spec_value,
              unit: spec.unit,
              display_order: spec.display_order,
              id: spec.id
            });
          });
          
          // Create the flat structure with group headers
          Object.keys(groupedSpecs).forEach((groupName, groupIndex) => {
            if (groupName !== 'Ungrouped') {
              specs.push({
                isGroup: true,
                group_name: groupName,
                display_order: groupIndex * 100
              });
            }
            groupedSpecs[groupName].forEach(spec => specs.push(spec));
          });
        }
        
        setFormData({
          name: product.name || '',
          slug: product.slug || '',
          description: product.description || '',
          short_description: product.short_description || '',
          price: product.price || '',
          stock: product.stock || '',
          category_id: product.category_id || '',
          brand: product.brand || '',
          product_type: product.product_type || '',
          product_line: product.product_line || '',
          sku: product.sku || '',
          featured: product.featured || false,
          status: product.status || 'active',
          variants: product.variants || [],
          specs: specs,
          product_specs: product.product_specs || [],
          images: product.images || [],
        });
      } catch (err) {
        setError(err.message || 'Failed to load product');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchProduct();
    }
  }, [id]);

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({
      ...formData,
      [e.target.name]: value,
    });
  };

  const generateSlug = (name) => {
    return name
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/[\s_-]+/g, '-')
      .replace(/^-+|-+$/g, '');
  };

  // Variant Management
  const addVariant = () => {
    setFormData({
      ...formData,
      variants: [
        ...formData.variants,
        { name: '', price: '', sale_price: '', stock: '', sku: '', is_default: false, metadata: {} },
      ],
    });
  };

  const updateVariant = (index, field, value) => {
    const newVariants = [...formData.variants];
    newVariants[index] = { ...newVariants[index], [field]: value };
    setFormData({ ...formData, variants: newVariants });
  };

  const removeVariant = (index) => {
    setFormData({
      ...formData,
      variants: formData.variants.filter((_, i) => i !== index),
    });
  };

  // Specification Management - Grouped Table Editor
  const addSpecGroup = () => {
    setFormData({
      ...formData,
      specs: [...formData.specs, { 
        isGroup: true, 
        group_name: '', 
        display_order: formData.specs.length 
      }],
    });
  };

  const addSpecRow = (groupIndex) => {
    const newSpecs = [...formData.specs];
    newSpecs.splice(groupIndex + 1, 0, {
      isGroup: false,
      group_name: newSpecs[groupIndex].group_name || '',
      spec_key: '',
      spec_value: '',
      unit: '',
      display_order: groupIndex + 1
    });
    newSpecs.forEach((spec, idx) => { spec.display_order = idx; });
    setFormData({ ...formData, specs: newSpecs });
  };

  const removeSpecItem = (index) => {
    const newSpecs = [...formData.specs];
    const removedItem = newSpecs[index];
    
    if (removedItem.isGroup) {
      let endIndex = index + 1;
      while (endIndex < newSpecs.length && !newSpecs[endIndex].isGroup) {
        endIndex++;
      }
      newSpecs.splice(index, endIndex - index);
    } else {
      newSpecs.splice(index, 1);
    }
    
    newSpecs.forEach((spec, idx) => { spec.display_order = idx; });
    setFormData({ ...formData, specs: newSpecs });
  };

  const updateSpecField = (index, field, value) => {
    const newSpecs = [...formData.specs];
    newSpecs[index] = { ...newSpecs[index], [field]: value };
    
    if (field === 'group_name' && newSpecs[index].isGroup) {
      let i = index + 1;
      while (i < newSpecs.length && !newSpecs[i].isGroup) {
        newSpecs[i].group_name = value;
        i++;
      }
    }
    
    setFormData({ ...formData, specs: newSpecs });
  };

  // Image Management
  const addImage = async (file) => {
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file');
      return;
    }

    try {
      const uploadResult = await productService.uploadProductImage(file);
      setFormData({
        ...formData,
        images: [
          ...formData.images,
          {
            url: uploadResult.image_url,
            alt_text: '',
            sort_order: formData.images.length,
            is_primary: formData.images.length === 0,
            hotspots: [],
          },
        ],
      });
    } catch (err) {
      setError('Failed to upload image: ' + err.message);
    }
  };

  const removeImage = (index) => {
    setFormData({
      ...formData,
      images: formData.images.filter((_, i) => i !== index),
    });
    setSelectedImageIndex(null);
  };

  const updateImage = (index, field, value) => {
    const newImages = [...formData.images];
    newImages[index] = { ...newImages[index], [field]: value };
    setFormData({ ...formData, images: newImages });
  };

  // Hotspot Management
  const addHotspot = () => {
    if (selectedImageIndex === null) {
      setError('Please select an image first');
      return;
    }
    const newImages = [...formData.images];
    if (!newImages[selectedImageIndex].hotspots) {
      newImages[selectedImageIndex].hotspots = [];
    }
    newImages[selectedImageIndex].hotspots.push({
      x: 50,
      y: 50,
      title: '',
      description: '',
      spec_key: '',
    });
    setFormData({ ...formData, images: newImages });
  };

  const updateHotspot = (imageIndex, hotspotIndex, field, value) => {
    const newImages = [...formData.images];
    newImages[imageIndex].hotspots[hotspotIndex] = {
      ...newImages[imageIndex].hotspots[hotspotIndex],
      [field]: value,
    };
    setFormData({ ...formData, images: newImages });
  };

  const removeHotspot = (imageIndex, hotspotIndex) => {
    const newImages = [...formData.images];
    newImages[imageIndex].hotspots = newImages[imageIndex].hotspots.filter(
      (_, i) => i !== hotspotIndex
    );
    setFormData({ ...formData, images: newImages });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      const productSpecs = formData.specs
        .filter(spec => !spec.isGroup)
        .map(spec => ({
          group_name: spec.group_name || null,
          spec_key: spec.spec_key,
          spec_value: spec.spec_value,
          unit: spec.unit || null,
          display_order: spec.display_order
        }));

      const updates = {
        ...formData,
        price: parseFloat(formData.price) || 0,
        stock: parseInt(formData.stock, 10) || 0,
        category_id: formData.category_id || null,
        product_specs: productSpecs,
        variants: formData.variants.map((v) => ({
          ...v,
          price: parseFloat(v.price) || 0,
          sale_price: v.sale_price ? parseFloat(v.sale_price) : null,
          stock: parseInt(v.stock, 10) || 0,
        })),
      };

      delete updates.specs;

      await productService.updateProduct(id, updates);
      navigate('/admin/products');
    } catch (err) {
      setError(err.message || 'Unable to update product');
    }
  };

  const currentImage = selectedImageIndex !== null ? formData.images[selectedImageIndex] : null;

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Edit Product</h1>
        <p className="text-gray-600 mt-2">Update product information, variants, specifications, and images.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
            {error}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex gap-2 border-b border-gray-200">
          {['basic', 'variants', 'specs', 'images'].map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-medium text-sm border-b-2 transition ${
                activeTab === tab
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Basic Info Tab */}
        {activeTab === 'basic' && (
          <div className="bg-white rounded-lg shadow p-8 space-y-6">
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Name *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={(e) => {
                    handleChange(e);
                    if (!formData.slug) {
                      setFormData({
                        ...formData,
                        name: e.target.value,
                        slug: generateSlug(e.target.value),
                      });
                    }
                  }}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Slug</label>
                <input
                  type="text"
                  name="slug"
                  value={formData.slug}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">SKU</label>
                <input
                  type="text"
                  name="sku"
                  value={formData.sku}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Brand</label>
                <input
                  type="text"
                  name="brand"
                  value={formData.brand}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Product Type</label>
                <input
                  type="text"
                  name="product_type"
                  value={formData.product_type}
                  onChange={handleChange}
                  placeholder="e.g., Điện thoại, Laptop, Tablet"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Product Line</label>
                <input
                  type="text"
                  name="product_line"
                  value={formData.product_line}
                  onChange={handleChange}
                  placeholder="e.g., iPhone 17, ROG Strix G16"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              {breadcrumbPreview.length > 1 && (
                <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Breadcrumb Preview</p>
                  <div className="flex flex-wrap items-center gap-1 text-sm">
                    {breadcrumbPreview.map((crumb, idx) => (
                      <span key={idx} className="flex items-center text-gray-400">
                        {idx > 0 && <span className="mx-1">/</span>}
                        <span className={idx === breadcrumbPreview.length - 1 ? 'text-gray-900 font-semibold' : 'text-blue-600'}>
                          {crumb.name}
                        </span>
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Price (Base) *</label>
                <input
                  type="number"
                  name="price"
                  value={formData.price}
                  onChange={handleChange}
                  required
                  step="1000"
                  min="0"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Stock *</label>
                <input
                  type="number"
                  name="stock"
                  value={formData.stock}
                  onChange={handleChange}
                  required
                  min="0"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Short Description</label>
              <input
                type="text"
                name="short_description"
                value={formData.short_description}
                onChange={handleChange}
                maxLength="512"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Brief description for listings"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Full Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={6}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Detailed product description"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="featured"
                checked={formData.featured}
                onChange={handleChange}
                className="h-4 w-4 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
              <label className="ml-3 text-sm font-medium text-gray-700">Featured Product</label>
            </div>
          </div>
        )}

        {/* Variants Tab */}
        {activeTab === 'variants' && (
          <AdminVariantManager
            variants={formData.variants}
            onVariantsChange={(variants) => setFormData({ ...formData, variants })}
            productType={formData.product_type}
          />
        )}

        {/* Specifications Tab */}
        {activeTab === 'specs' && (
          <div className="bg-white rounded-lg shadow p-8 space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Technical Specifications</h3>
                <p className="text-sm text-gray-500 mt-1">Add grouped specifications similar to electronics product sheets</p>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={addSpecGroup}
                  className="px-4 py-2 bg-green-600 text-white rounded-md text-sm hover:bg-green-700"
                >
                  Add Group
                </button>
                <button
                  type="button"
                  onClick={() => setFormData({...formData, specs: [...formData.specs, { isGroup: false, group_name: '', spec_key: '', spec_value: '', unit: '', display_order: formData.specs.length }]})}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
                >
                  Add Spec Row
                </button>
              </div>
            </div>

            {formData.specs.length === 0 ? (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="mt-4 text-gray-500">No specifications yet. Add a group or spec row to get started.</p>
                <div className="mt-4 flex justify-center gap-2">
                  <button
                    type="button"
                    onClick={addSpecGroup}
                    className="px-4 py-2 bg-green-600 text-white rounded-md text-sm hover:bg-green-700"
                  >
                    Add Specification Group
                  </button>
                </div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-200">
                      <th className="text-left p-3 text-xs font-medium text-gray-500 uppercase w-48">Group/Section</th>
                      <th className="text-left p-3 text-xs font-medium text-gray-500 uppercase">Spec Name</th>
                      <th className="text-left p-3 text-xs font-medium text-gray-500 uppercase w-48">Value</th>
                      <th className="text-left p-3 text-xs font-medium text-gray-500 uppercase w-24">Unit</th>
                      <th className="text-left p-3 text-xs font-medium text-gray-500 uppercase w-32">Order</th>
                      <th className="text-center p-3 text-xs font-medium text-gray-500 uppercase w-24">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {formData.specs.map((spec, index) => (
                      <tr key={index} className={`border-b border-gray-100 ${spec.isGroup ? 'bg-blue-50' : 'hover:bg-gray-50'}`}>
                        {spec.isGroup ? (
                          <>
                            <td colSpan="4" className="p-3">
                              <input
                                type="text"
                                value={spec.group_name || ''}
                                onChange={(e) => updateSpecField(index, 'group_name', e.target.value)}
                                placeholder="Group Name (e.g., Display, Processor, Camera)"
                                className="w-full px-3 py-2 border border-blue-300 rounded-md text-sm font-medium"
                              />
                            </td>
                            <td className="p-3">
                              <input
                                type="number"
                                value={spec.display_order}
                                onChange={(e) => updateSpecField(index, 'display_order', parseInt(e.target.value) || 0)}
                                className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                              />
                            </td>
                            <td className="p-3 text-center">
                              <div className="flex gap-1 justify-center">
                                <button
                                  type="button"
                                  onClick={() => addSpecRow(index)}
                                  className="text-blue-600 hover:text-blue-700 text-xs"
                                  title="Add spec to this group"
                                >
                                  + Add Row
                                </button>
                                <button
                                  type="button"
                                  onClick={() => removeSpecItem(index)}
                                  className="text-red-600 hover:text-red-700 text-xs"
                                >
                                  Remove
                                </button>
                              </div>
                            </td>
                          </>
                        ) : (
                          <>
                            <td className="p-3">
                              <input
                                type="text"
                                value={spec.group_name || ''}
                                onChange={(e) => updateSpecField(index, 'group_name', e.target.value)}
                                placeholder="Group"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                              />
                            </td>
                            <td className="p-3">
                              <input
                                type="text"
                                value={spec.spec_key || ''}
                                onChange={(e) => updateSpecField(index, 'spec_key', e.target.value)}
                                placeholder="Spec name (e.g., Screen Size)"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                                required
                              />
                            </td>
                            <td className="p-3">
                              <input
                                type="text"
                                value={spec.spec_value || ''}
                                onChange={(e) => updateSpecField(index, 'spec_value', e.target.value)}
                                placeholder="Value"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                                required
                              />
                            </td>
                            <td className="p-3">
                              <input
                                type="text"
                                value={spec.unit || ''}
                                onChange={(e) => updateSpecField(index, 'unit', e.target.value)}
                                placeholder="Unit"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                              />
                            </td>
                            <td className="p-3">
                              <input
                                type="number"
                                value={spec.display_order}
                                onChange={(e) => updateSpecField(index, 'display_order', parseInt(e.target.value) || 0)}
                                className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                              />
                            </td>
                            <td className="p-3 text-center">
                              <button
                                type="button"
                                onClick={() => removeSpecItem(index)}
                                className="text-red-600 hover:text-red-700 text-xs"
                              >
                                Remove
                              </button>
                            </td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            
            {/* Spec Template Suggestions */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-sm font-medium text-gray-700 mb-3">Quick Templates:</p>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => {
                    const templates = [
                      { isGroup: true, group_name: 'Display', display_order: formData.specs.length },
                      { isGroup: false, group_name: 'Display', spec_key: 'Screen Size', spec_value: '', unit: 'inch', display_order: formData.specs.length + 1 },
                      { isGroup: false, group_name: 'Display', spec_key: 'Resolution', spec_value: '', unit: '', display_order: formData.specs.length + 2 },
                      { isGroup: false, group_name: 'Display', spec_key: 'Refresh Rate', spec_value: '', unit: 'Hz', display_order: formData.specs.length + 3 },
                    ];
                    setFormData({...formData, specs: [...formData.specs, ...templates]});
                  }}
                  className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-md text-xs hover:bg-gray-200"
                >
                  Phone Display
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const templates = [
                      { isGroup: true, group_name: 'Processor', display_order: formData.specs.length },
                      { isGroup: false, group_name: 'Processor', spec_key: 'Chipset', spec_value: '', unit: '', display_order: formData.specs.length + 1 },
                      { isGroup: false, group_name: 'Processor', spec_key: 'CPU Cores', spec_value: '', unit: '', display_order: formData.specs.length + 2 },
                      { isGroup: false, group_name: 'Processor', spec_key: 'GPU', spec_value: '', unit: '', display_order: formData.specs.length + 3 },
                    ];
                    setFormData({...formData, specs: [...formData.specs, ...templates]});
                  }}
                  className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-md text-xs hover:bg-gray-200"
                >
                  Processor
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const templates = [
                      { isGroup: true, group_name: 'Battery', display_order: formData.specs.length },
                      { isGroup: false, group_name: 'Battery', spec_key: 'Capacity', spec_value: '', unit: 'mAh', display_order: formData.specs.length + 1 },
                      { isGroup: false, group_name: 'Battery', spec_key: 'Fast Charging', spec_value: '', unit: 'W', display_order: formData.specs.length + 2 },
                    ];
                    setFormData({...formData, specs: [...formData.specs, ...templates]});
                  }}
                  className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-md text-xs hover:bg-gray-200"
                >
                  Battery
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Images Tab */}
        {activeTab === 'images' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Image List */}
            <div className="lg:col-span-1 bg-white rounded-lg shadow p-6 space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Product Images</h3>
                <label className="block">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => {
                      if (e.target.files?.[0]) {
                        addImage(e.target.files[0]);
                      }
                    }}
                    className="text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                </label>
              </div>

              <div className="space-y-2 max-h-96 overflow-y-auto">
                {formData.images.map((image, index) => (
                  <div
                    key={index}
                    onClick={() => setSelectedImageIndex(index)}
                    className={`p-3 rounded-lg cursor-pointer border-2 transition ${
                      selectedImageIndex === index
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <img
                      src={image.url}
                      alt={image.alt_text}
                      className="w-full h-24 object-cover rounded-md mb-2"
                    />
                    <p className="text-xs text-gray-600">Image {index + 1}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Image Editor */}
            {currentImage && (
              <div className="lg:col-span-2 bg-white rounded-lg shadow p-6 space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Image {selectedImageIndex + 1} Details</h3>
                  <img src={currentImage.url} alt="Current" className="w-full h-64 object-cover rounded-lg mb-4" />

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Alt Text</label>
                      <input
                        type="text"
                        value={currentImage.alt_text}
                        onChange={(e) => updateImage(selectedImageIndex, 'alt_text', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                      />
                    </div>

                    <div className="flex gap-2">
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={currentImage.is_primary}
                          onChange={(e) => updateImage(selectedImageIndex, 'is_primary', e.target.checked)}
                          className="h-4 w-4 border border-gray-300 rounded"
                        />
                        <span className="ml-2 text-sm text-gray-700">Primary Image</span>
                      </label>
                    </div>

                    <div>
                      <div className="flex justify-between items-center mb-3">
                        <h4 className="text-sm font-semibold text-gray-900">Interactive Hotspots</h4>
                        <button
                          type="button"
                          onClick={addHotspot}
                          className="text-blue-600 hover:text-blue-700 text-xs font-medium"
                        >
                          Add Hotspot
                        </button>
                      </div>

                      {!currentImage.hotspots || currentImage.hotspots.length === 0 ? (
                        <p className="text-xs text-gray-500 py-4">No hotspots yet. Click "Add Hotspot" to create interactive features.</p>
                      ) : (
                        <div className="space-y-3 max-h-48 overflow-y-auto">
                          {currentImage.hotspots.map((hotspot, hIndex) => (
                            <div key={hIndex} className="border border-gray-200 rounded-lg p-3 space-y-2 bg-gray-50">
                              <div className="flex justify-between items-start">
                                <p className="text-xs font-medium text-gray-700">Hotspot {hIndex + 1}</p>
                                <button
                                  type="button"
                                  onClick={() => removeHotspot(selectedImageIndex, hIndex)}
                                  className="text-red-600 hover:text-red-700 text-xs"
                                >
                                  Remove
                                </button>
                              </div>
                              <div className="grid grid-cols-2 gap-2">
                                <input
                                  type="number"
                                  min="0"
                                  max="100"
                                  step="1"
                                  value={hotspot.x}
                                  onChange={(e) => updateHotspot(selectedImageIndex, hIndex, 'x', parseFloat(e.target.value))}
                                  placeholder="X (%)"
                                  className="px-2 py-1 border border-gray-300 rounded text-xs"
                                />
                                <input
                                  type="number"
                                  min="0"
                                  max="100"
                                  step="1"
                                  value={hotspot.y}
                                  onChange={(e) => updateHotspot(selectedImageIndex, hIndex, 'y', parseFloat(e.target.value))}
                                  placeholder="Y (%)"
                                  className="px-2 py-1 border border-gray-300 rounded text-xs"
                                />
                              </div>
                              <input
                                type="text"
                                value={hotspot.title}
                                onChange={(e) => updateHotspot(selectedImageIndex, hIndex, 'title', e.target.value)}
                                placeholder="Title"
                                className="w-full px-2 py-1 border border-gray-300 rounded text-xs"
                              />
                              <input
                                type="text"
                                value={hotspot.description}
                                onChange={(e) => updateHotspot(selectedImageIndex, hIndex, 'description', e.target.value)}
                                placeholder="Description"
                                className="w-full px-2 py-1 border border-gray-300 rounded text-xs"
                              />
                              <input
                                type="text"
                                value={hotspot.spec_key}
                                onChange={(e) => updateHotspot(selectedImageIndex, hIndex, 'spec_key', e.target.value)}
                                placeholder="Spec Key (optional)"
                                className="w-full px-2 py-1 border border-gray-300 rounded text-xs"
                              />
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    <button
                      type="button"
                      onClick={() => removeImage(selectedImageIndex)}
                      className="w-full px-4 py-2 text-red-600 border border-red-300 rounded-md hover:bg-red-50 text-sm"
                    >
                      Delete This Image
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => navigate('/admin/products')}
            className="px-6 py-3 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 font-medium"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Saving...' : 'Update Product'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EditProduct;
