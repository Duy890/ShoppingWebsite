import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { productService } from '../services/productService';

export const useEditProduct = () => {
  const { id } = useParams();
  const navigate = useNavigate();
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

  useEffect(() => {
    const fetchProduct = async () => {
      if (!id) return;

      try {
        setLoading(true);
        const product = await productService.getProductById(id);
        const specs = [];
        const groupedSpecs = {};

        if (product.product_specs && product.product_specs.length > 0) {
          product.product_specs.forEach((spec) => {
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
              id: spec.id,
            });
          });

          Object.keys(groupedSpecs).forEach((groupName, groupIndex) => {
            if (groupName !== 'Ungrouped') {
              specs.push({
                isGroup: true,
                group_name: groupName,
                display_order: groupIndex * 100,
              });
            }
            groupedSpecs[groupName].forEach((spec) => specs.push(spec));
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
          specs,
          product_specs: product.product_specs || [],
          images: product.images || [],
        });
      } catch (err) {
        setError(err.message || 'Failed to load product');
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [id]);

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({
      ...formData,
      [e.target.name]: value,
      ...(e.target.name === 'name' && !formData.slug ? { slug: generateSlug(value) } : {}),
    });
  };

  const generateSlug = (name) => {
    return name
      .toLowerCase()
    .replace(/[^\w\s-]/g, '')
      .replace(/[\s_-]+/g, '-')
      .replace(/^-+|-+$/g, '');
  };

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

  const addSpecGroup = () => {
    setFormData({
      ...formData,
      specs: [
        ...formData.specs,
        {
          isGroup: true,
          group_name: '',
          display_order: formData.specs.length,
        },
      ],
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
      display_order: groupIndex + 1,
    });
    newSpecs.forEach((spec, idx) => {
      spec.display_order = idx;
    });
    setFormData({ ...formData, specs: newSpecs });
  };

  const addSpecItem = () => {
    setFormData({
      ...formData,
      specs: [
        ...formData.specs,
        {
          isGroup: false,
          group_name: '',
          spec_key: '',
          spec_value: '',
          unit: '',
          display_order: formData.specs.length,
        },
      ],
    });
  };

  const addSpecTemplates = (templates) => {
    setFormData({
      ...formData,
      specs: [...formData.specs, ...templates],
    });
  };

  const setVariants = (variants) => {
    setFormData({ ...formData, variants });
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

    newSpecs.forEach((spec, idx) => {
      spec.display_order = idx;
    });
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
        .filter((spec) => !spec.isGroup)
        .map((spec) => ({
          group_name: spec.group_name || null,
          spec_key: spec.spec_key,
          spec_value: spec.spec_value,
          unit: spec.unit || null,
          display_order: spec.display_order,
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

  return {
    activeTab,
    setActiveTab,
    formData,
    setFormData,
    loading,
    error,
    selectedImageIndex,
    setSelectedImageIndex,
    currentImage,
    handleChange,
    generateSlug,
    addVariant,
    updateVariant,
    removeVariant,
    setVariants,
    addSpecGroup,
    addSpecRow,
    removeSpecItem,
    updateSpecField,
    addSpecItem,
    addSpecTemplates,
    addImage,
    removeImage,
    updateImage,
    addHotspot,
    updateHotspot,
    removeHotspot,
    handleSubmit,
  };
};
