import { useState } from 'react';
import { Trash2, Plus } from 'lucide-react';

const COLOR_CODES = {
  "Den": "#111111",
  "Trang": "#F7F7F7",
  "Xanh": "#2563EB",
  "Bac": "#C0C0C0",
  "Vang": "#D4AF37",
  "Hong": "#F9A8D4",
  "Xam": "#6B7280",
  "Tim": "#8B5CF6",
  "Kem": "#EADBC8",
  "Do": "#DC2626",
  "Titan Den": "#2D2D2D",
  "Titan Trang": "#E8E1D9",
  "Titan Sa Mac": "#C8A26A",
  "Titan Xam": "#8A8A8A",
};

const SWATCH_FALLBACK = 'conic-gradient(from 90deg at 50% 50%, #e0e0e0 0%, #ffffff 25%, #e0e0e0 50%, #ffffff 75%, #e0e0e0 100%)';

const isRenderableColor = (code) => {
  if (!code) return false;
  if (code.startsWith('#')) return true;
  if (code.startsWith('rgb')) return true;
  if (code.startsWith('linear-gradient')) return true;
  if (code.startsWith('conic-gradient')) return true;
  if (code.startsWith('radial-gradient')) return true;
  return false;
};

const AdminVariantManager = ({ variants = [], onVariantsChange, productType }) => {
  const [localVariants, setLocalVariants] = useState(variants.map((v, i) => ({ ...v, local_id: v.id || `new-${i}` })));

  const handleAddVariant = () => {
    const newVariant = {
      local_id: `new-${Date.now()}`,
      color_name: '',
      color_code: '#000000',
      version_name: '',
      ram: '',
      storage: '',
      price: 0,
      compare_price: null,
      stock: 0,
      image_url: '',
      is_default: localVariants.length === 0,
      status: 'active',
    };
    setLocalVariants([...localVariants, newVariant]);
  };

  const handleRemoveVariant = (localId) => {
    const updated = localVariants.filter(v => v.local_id !== localId);
    if (updated.length > 0 && !updated.some(v => v.is_default)) {
      updated[0].is_default = true;
    }
    setLocalVariants(updated);
    onVariantsChange(updated);
  };

  const handleVariantChange = (localId, field, value) => {
    let updated = localVariants.map(v =>
      v.local_id === localId ? { ...v, [field]: value } : v
    );

    if (field === 'color_name') {
      const autoCode = COLOR_CODES[value];
      if (autoCode) {
        updated = updated.map(v =>
          v.local_id === localId ? { ...v, color_name: value, color_code: autoCode } : v
        );
      }
    }

    if (field === 'price') {
      const numPrice = parseFloat(value) || 0;
      const autoCompare = Math.round(numPrice * 1.1 / 10000) * 10000;
      updated = updated.map(v =>
        v.local_id === localId
          ? { ...v, price: numPrice, compare_price: autoCompare }
          : v
      );
    }

    setLocalVariants(updated);
    onVariantsChange(updated);
  };

  const handleSetDefault = (localId) => {
    const updated = localVariants.map(v => ({
      ...v,
      is_default: v.local_id === localId
    }));
    setLocalVariants(updated);
    onVariantsChange(updated);
  };

  return (
    <div className="space-y-6 bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-gray-900">Product Variants</h3>
        <button
          onClick={handleAddVariant}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Variant</span>
        </button>
      </div>

      {localVariants.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No variants yet. Click "Add Variant" to create one.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">Color Name</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">Color Value</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">Version</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">RAM</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">Storage</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">Price</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">Giá gốc (gạch)</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">Stock</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">Default</th>
                <th className="px-4 py-3 text-center font-semibold text-gray-700">Action</th>
              </tr>
            </thead>
            <datalist id="color-suggestions">
              {Object.keys(COLOR_CODES).map(name => (
                <option key={name} value={name} />
              ))}
            </datalist>
            <tbody>
              {localVariants.map((variant) => (
                <tr key={variant.local_id} className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <input
                      type="text"
                      list="color-suggestions"
                      value={variant.color_name || ''}
                      onChange={(e) => handleVariantChange(variant.local_id, 'color_name', e.target.value)}
                      placeholder="Den, Bac, Trang..."
                      className="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-6 h-6 rounded-full border border-gray-300 shrink-0"
                        style={{
                          background: isRenderableColor(variant.color_code) ? variant.color_code : SWATCH_FALLBACK,
                        }}
                      />
                      <input
                        type="text"
                        value={variant.color_code || ''}
                        onChange={(e) => handleVariantChange(variant.local_id, 'color_code', e.target.value)}
                        placeholder="#000000 or rgba(...)"
                        className="flex-1 px-2 py-1 border border-gray-300 rounded text-xs font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="text"
                      value={variant.version_name || ''}
                      onChange={(e) => handleVariantChange(variant.local_id, 'version_name', e.target.value)}
                      placeholder="e.g., Pro Max"
                      className="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="text"
                      value={variant.ram || ''}
                      onChange={(e) => handleVariantChange(variant.local_id, 'ram', e.target.value)}
                      placeholder="e.g., 8GB"
                      className="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="text"
                      value={variant.storage || ''}
                      onChange={(e) => handleVariantChange(variant.local_id, 'storage', e.target.value)}
                      placeholder="e.g., 256GB"
                      className="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="number"
                      value={variant.price || 0}
                      onChange={(e) => handleVariantChange(variant.local_id, 'price', e.target.value)}
                      placeholder="0"
                      className="w-28 px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                      step="1000"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs text-gray-500 line-through">
                      {variant.compare_price ? variant.compare_price.toLocaleString('vi-VN') : '—'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="number"
                      value={variant.stock || 0}
                      onChange={(e) => handleVariantChange(variant.local_id, 'stock', parseInt(e.target.value))}
                      placeholder="0"
                      className="w-20 px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </td>
                  <td className="px-4 py-3 text-center">
                    <input
                      type="checkbox"
                      checked={variant.is_default || false}
                      onChange={() => handleSetDefault(variant.local_id)}
                      className="w-4 h-4 rounded accent-blue-600 cursor-pointer"
                    />
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => handleRemoveVariant(variant.local_id)}
                      className="text-red-600 hover:text-red-700 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AdminVariantManager;
