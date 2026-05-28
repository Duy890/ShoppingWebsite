import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProducts } from '../../hooks/useProducts';
import { productService } from '../../services/productService';
import SpecificationEditor from '../../components/SpecificationEditor';
import AdminVariantManager from '../../components/AdminVariantManager';
import AIDescriptionGenerator from '../../components/AIDescriptionGenerator';
import SkuInput from '../../components/SkuInput';
import ApplyTemplateBar from '../../components/ApplyTemplateBar';
import { AlertTriangle, CheckCircle2, Info } from 'lucide-react';

const CATEGORY_TYPE_MAP = {
  'dien-thoai':        ['phone'],
  'iphone':            ['phone'],
  'android-cao-cap':   ['phone'],
  'android-pho-thong': ['phone'],
  'laptop':            ['laptop'],
  'laptop-gaming':     ['laptop'],
  'laptop-van-phong':  ['laptop'],
  'laptop-sinh-vien':  ['laptop'],
  'macbook':           ['laptop'],
  'tai-nghe-am-thanh': ['audio'],
  'tai-nghe-chong-on': ['audio'],
  'tai-nghe-gaming':   ['audio'],
  'tai-nghe-tws':      ['audio'],
  'phu-kien':          ['accessory'],
  'sac-pin-du-phong':  ['accessory'],
  'op-lung-bao-ve':    ['accessory'],
  'hub-adapter':       ['accessory'],
  'chuot-gaming':      ['accessory'],
  'tablet':            ['tablet'],
  'dong-ho-thong-minh':['watch'],
};

const PRODUCT_TYPE_LABELS = {
  phone:     'Điện thoại',
  laptop:    'Laptop',
  audio:     'Tai nghe / Âm thanh',
  watch:     'Đồng hồ thông minh',
  tablet:    'Máy tính bảng',
  accessory: 'Phụ kiện',
};

const ALL_PRODUCT_TYPES = [
  { value: 'phone',     label: 'Phone — Điện thoại' },
  { value: 'laptop',    label: 'Laptop' },
  { value: 'audio',     label: 'Audio — Tai nghe / Loa' },
  { value: 'watch',     label: 'Watch — Đồng hồ thông minh' },
  { value: 'tablet',    label: 'Tablet — Máy tính bảng' },
  { value: 'accessory', label: 'Accessory — Phụ kiện' },
];

function getConflictInfo(categoryId, productType, categories) {
  if (!categoryId || !productType) return null;
  const cat = categories.find((c) => c.id === categoryId);
  if (!cat || !cat.slug) return null;
  const allowed = CATEGORY_TYPE_MAP[cat.slug];
  if (!allowed) return null;
  if (allowed.includes(productType)) return null;
  return {
    category: cat.name,
    chosen: PRODUCT_TYPE_LABELS[productType] ?? productType,
    allowed: allowed.map((t) => PRODUCT_TYPE_LABELS[t] ?? t).join(', '),
    allowedTypes: allowed,
  };
}

function suggestTypeForCategory(slug) {
  const allowed = CATEGORY_TYPE_MAP[slug];
  return allowed ? allowed[0] : '';
}

const makeEmptySpec = () => ({
  local_id: crypto.randomUUID(),
  group_name: '',
  spec_key: '',
  spec_value: '',
  display_order: 0,
});

const AddProduct = () => {
  const navigate = useNavigate();
  const { categories, createProduct, loading } = useProducts();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    stock: '',
    category_id: '',
    image_url: '',
    brand: '',
    sku: '',
    product_type: '',
    featured: false,
    status: 'active',
    variants: [],
  });
  const [variants, setVariants] = useState([]);
  const [specifications, setSpecifications] = useState([makeEmptySpec()]);
  const [imagePreview, setImagePreview] = useState('');
  const [selectedImageFile, setSelectedImageFile] = useState(null);
  const [productImages, setProductImages] = useState([]);
  const [uploadingImages, setUploadingImages] = useState(false);
  const [error, setError] = useState(null);

  const conflict = useMemo(
    () => getConflictInfo(formData.category_id, formData.product_type, categories),
    [formData.category_id, formData.product_type, categories]
  );

  const allowedTypesForCategory = useMemo(() => {
    const cat = categories.find((c) => c.id === formData.category_id);
    if (!cat) return null;
    return CATEGORY_TYPE_MAP[cat.slug] ?? null;
  }, [formData.category_id, categories]);

  const selectedCategoryName = useMemo(() => {
    return categories.find((c) => c.id === formData.category_id)?.name ?? '';
  }, [formData.category_id, categories]);

  const categoryGroups = useMemo(() => {
    const roots = categories.filter((c) => !c.parent_id);
    const children = categories.filter((c) => c.parent_id);
    return roots.map((root) => ({
      root,
      subs: children.filter((c) => c.parent_id === root.id),
    }));
  }, [categories]);

  useEffect(() => {
    if (!formData.category_id) return;
    const cat = categories.find((c) => c.id === formData.category_id);
    if (!cat) return;
    const suggested = suggestTypeForCategory(cat.slug);
    if (suggested && formData.product_type !== suggested) {
      setFormData((prev) => ({ ...prev, product_type: suggested }));
    }
  }, [formData.category_id, categories]);

  const handleApplyAI = (result) => {
    setFormData((prev) => ({
      ...prev,
      ...(result.short_description !== undefined && { description: result.full_description || result.short_description }),
    }));
  };

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: value,
    }));
  };

  const handleAutoFix = () => {
    if (!conflict) return;
    setFormData((prev) => ({ ...prev, product_type: conflict.allowedTypes[0] }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) {
      if (imagePreview) {
        URL.revokeObjectURL(imagePreview);
      }
      setFormData({ ...formData, image_url: '' });
      setImagePreview('');
      setSelectedImageFile(null);
      return;
    }

    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }

    const previewUrl = URL.createObjectURL(file);
    setSelectedImageFile(file);
    setFormData({ ...formData, image_url: '' });
    setImagePreview(previewUrl);
  };

  const handleAddImage = async () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = async (e) => {
      const file = e.target.files?.[0];
      if (!file) return;
      setUploadingImages(true);
      try {
        const result = await productService.uploadProductImage(file);
        setProductImages(prev => [...prev, {
          url: result.image_url,
          alt_text: '',
          is_primary: prev.length === 0,
          sort_order: prev.length,
        }]);
      } catch (err) {
        setError('Failed to upload image: ' + err.message);
      } finally {
        setUploadingImages(false);
      }
    };
    input.click();
  };

  const handleRemoveImage = (index) => {
    setProductImages(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      if (conflict) {
        setError(
          `Không thể lưu: Loại sản phẩm "${conflict.chosen}" không khớp với danh mục "${conflict.category}". ` +
          `Danh mục này chỉ chấp nhận: ${conflict.allowed}.`
        );
        return;
      }

      const SKU_REGEX = /^[A-Za-z0-9\-_]{3,50}$/;
      if (formData.sku && !SKU_REGEX.test(formData.sku.trim())) {
        setError('SKU không hợp lệ. Chỉ dùng A-Z, 0-9, dấu - và _, tối thiểu 3 ký tự.');
        return;
      }

      let imageUrl = formData.image_url;
      if (selectedImageFile) {
        const uploadResult = await productService.uploadProductImage(selectedImageFile);
        imageUrl = uploadResult.image_url;
      }

      const productData = {
        ...formData,
        image_url: imageUrl,
        price: parseFloat(formData.price) || 0,
        stock: parseInt(formData.stock, 10) || 0,
        category_id: formData.category_id || null,
        sku: formData.sku || null,
        brand: formData.brand || null,
        product_type: formData.product_type || null,
      };

      const product = await createProduct(productData);

      if (variants.length > 0) {
        const finalVariants = variants.map((v, i) => ({
          ...v,
          is_default: variants.some(x => x.is_default) ? v.is_default : i === 0,
        }));
        await productService.saveProductVariants(product.id, finalVariants);
      }

      const validSpecs = specifications.filter((spec) => spec.spec_key);
      if (validSpecs.length > 0) {
        await productService.saveProductSpecifications(
          product.id,
          validSpecs.map((spec, index) => ({
            group_name: spec.group_name || 'Thông số khác',
            spec_key: spec.spec_key,
            spec_value: spec.spec_value,
            display_order: index,
          }))
        );
      }

      if (productImages.length > 0) {
        await productService.saveProductImages(product.id, productImages);
      }

      navigate('/admin/products');
    } catch (err) {
      setError(err.message || 'Unable to create product');
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div className="space-y-2">
          <div className="flex items-center space-x-2 text-primary">
            <div className="h-1 w-8 bg-primary rounded-full" />
            <span className="text-xs font-black uppercase tracking-widest">Catalog</span>
          </div>
          <h1 className="text-4xl font-black text-gray-900 tracking-tight">Add Product</h1>
          <p className="text-gray-600 mt-2">Create a new product entry for the store catalog.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
        {error && <div className="text-sm text-red-600">{error}</div>}

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">SKU</label>
            <SkuInput
              value={formData.sku}
              onChange={(val) => setFormData({ ...formData, sku: val })}
              currentId={null}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Brand</label>
            <input
              type="text"
              name="brand"
              value={formData.brand}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div className="flex items-start gap-2 text-xs text-gray-500 bg-gray-50 rounded-lg px-4 py-3">
            <Info className="w-3.5 h-3.5 mt-0.5 shrink-0 text-gray-400" />
            <span>
              Khi chọn <strong>Danh mục</strong>, hệ thống sẽ tự gợi ý{' '}
              <strong>Loại sản phẩm</strong> phù hợp. Nếu chọn sai loại, sản phẩm sẽ không lưu được.
            </span>
          </div>

          {conflict && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4 space-y-3">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-bold text-red-700">Loại sản phẩm không khớp danh mục</p>
                  <p className="text-xs text-red-600 mt-1">
                    Danh mục <strong>"{conflict.category}"</strong> chỉ chấp nhận{' '}
                    <strong>{conflict.allowed}</strong>, nhưng bạn đang chọn{' '}
                    <strong>"{conflict.chosen}"</strong>.
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={handleAutoFix}
                className="text-xs font-bold text-red-700 underline underline-offset-2 hover:text-red-900"
              >
                ✓ Tự động sửa thành "{conflict.allowed}"
              </button>
            </div>
          )}

          {!conflict && formData.category_id && formData.product_type && (
            <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 bg-emerald-50 rounded-lg px-4 py-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              Danh mục & loại sản phẩm khớp nhau →{' '}
              <span className="opacity-80">
                {selectedCategoryName} → {PRODUCT_TYPE_LABELS[formData.product_type] ?? formData.product_type}
              </span>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              name="category_id"
              value={formData.category_id}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">— Chọn danh mục —</option>
              {categoryGroups.map(({ root, subs }) =>
                subs.length > 0 ? (
                  <optgroup key={root.id} label={root.name}>
                    {subs.map((cat) => (
                      <option key={cat.id} value={cat.id}>{cat.name}</option>
                    ))}
                  </optgroup>
                ) : (
                  <option key={root.id} value={root.id}>{root.name}</option>
                )
              )}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Product Type</label>
            <select
              name="product_type"
              value={formData.product_type}
              onChange={handleChange}
              className={`w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary ${conflict ? 'border-red-400 ring-1 ring-red-300' : 'border-gray-300'}`}
            >
              <option value="">Custom (không xác định)</option>
              {ALL_PRODUCT_TYPES.map(({ value, label }) => {
                const isAllowed = !allowedTypesForCategory || allowedTypesForCategory.includes(value);
                return (
                  <option key={value} value={value} disabled={!isAllowed}>
                    {!isAllowed && '✕ '}{label}
                  </option>
                );
              })}
            </select>
            {allowedTypesForCategory && (
              <p className="mt-1.5 text-xs text-gray-400">
                Danh mục "{selectedCategoryName}" chỉ cho phép:{' '}
                {allowedTypesForCategory.map((t) => PRODUCT_TYPE_LABELS[t] ?? t).join(', ')}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Price *</label>
            <input
              type="number"
              name="price"
              value={formData.price}
              onChange={handleChange}
              required
              step="1000"
              min="0"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
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
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>


        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Add Image from Devices</label>
            <input
              type="file"
              accept="image/*"
              name="image_url"
              onChange={handleImageChange}
              className="w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary/5 file:text-primary hover:file:bg-primary/10"
            />
            {imagePreview && (
              <img
                src={imagePreview}
                alt="Selected preview"
                className="mt-4 h-40 w-full object-contain rounded-md border border-gray-200"
              />
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Additional Images</label>
            <button
              type="button"
              onClick={handleAddImage}
              disabled={uploadingImages}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm hover:bg-gray-50 disabled:opacity-50"
            >
              {uploadingImages ? 'Uploading...' : '+ Add Image'}
            </button>
            {productImages.length > 0 && (
              <div className="mt-3 grid grid-cols-4 gap-2">
                {productImages.map((img, i) => (
                  <div key={i} className="relative group">
                    <img
                      src={img.url}
                      alt={img.alt_text || ''}
                      className="h-20 w-full object-cover rounded border border-gray-200"
                    />
                    <button
                      type="button"
                      onClick={() => handleRemoveImage(i)}
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            name="featured"
            id="featured"
            checked={formData.featured}
            onChange={handleChange}
            className="w-4 h-4 accent-primary"
          />
          <label htmlFor="featured" className="text-sm font-medium text-gray-700">
            Featured Product (hiển thị nổi bật trên trang chủ)
          </label>
        </div>

        <AIDescriptionGenerator
          formData={formData}
          variants={variants}
          specifications={specifications}
          onApply={handleApplyAI}
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={5}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <AdminVariantManager
          variants={variants}
          onVariantsChange={setVariants}
          productType={formData.product_type}
        />

        <div>
          <ApplyTemplateBar
            productType={formData.product_type}
            onApply={(rows) => {
              setSpecifications((prev) => {
                const hasUserData = prev.some((r) => !r.isGroup && r.spec_value?.trim());
                if (hasUserData) {
                  const confirmed = window.confirm(
                    'Áp dụng template sẽ thay thế các spec hiện tại. Tiếp tục?'
                  );
                  if (!confirmed) return prev;
                }
                return rows;
              });
            }}
          />
          <SpecificationEditor
            productType={formData.product_type}
            onProductTypeChange={(productType) => setFormData({ ...formData, product_type: productType })}
            specifications={specifications}
            onChange={setSpecifications}
          />
        </div>

        <div className="flex items-center justify-end gap-4">
          <button
            type="button"
            onClick={() => navigate('/admin/products')}
            className="px-6 py-3 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-6 py-3 rounded-lg bg-primary text-white font-bold uppercase tracking-widest text-xs hover:bg-gray-900 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            disabled={loading || !!conflict}
          >
            {loading ? 'Đang lưu...' : 'Lưu sản phẩm'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddProduct;

