import { useState, useEffect } from 'react';
import { Check } from 'lucide-react';

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

const VariantSelector = ({ variants, onVariantChange, currentVariant }) => {
  const [selectedColor, setSelectedColor] = useState(null);
  const [selectedVersion, setSelectedVersion] = useState(null);

  const colorGroups = [];
  const seen = new Set();
  variants.forEach(v => {
    const key = v.color_code || v.color_name || 'default';
    if (!seen.has(key)) {
      seen.add(key);
      colorGroups.push({
        key,
        color_code: v.color_code,
        color_name: v.color_name || key,
      });
    }
  });

  const versionGroups = [];
  const seenV = new Set();
  variants.forEach(v => {
    const key = v.version_name || `${v.ram || ''}|${v.storage || ''}`;
    if (key && !seenV.has(key)) {
      seenV.add(key);
      versionGroups.push({ key, ram: v.ram, storage: v.storage });
    }
  });

  useEffect(() => {
    if (currentVariant) {
      setSelectedColor(currentVariant.color_code || currentVariant.color_name || null);
      setSelectedVersion(currentVariant.version_name || `${currentVariant.ram || ''}|${currentVariant.storage || ''}`);
    } else if (variants.length > 0) {
      const defaultVariant = variants.find(v => v.is_default) || variants[0];
      setSelectedColor(defaultVariant.color_code || defaultVariant.color_name || null);
      setSelectedVersion(defaultVariant.version_name || `${defaultVariant.ram || ''}|${defaultVariant.storage || ''}`);
      onVariantChange(defaultVariant);
    }
  }, [variants]);

  useEffect(() => {
    if (selectedColor !== null && selectedVersion !== null) {
      const selected = variants.find(v =>
        (v.color_code || v.color_name || null) === selectedColor &&
        (v.version_name || `${v.ram || ''}|${v.storage || ''}`) === selectedVersion
      );
      if (selected) {
        onVariantChange(selected);
      }
    }
  }, [selectedColor, selectedVersion]);

  const getAvailableVersionsForColor = (colorKey) => {
    return versionGroups.filter(vg => {
      return variants.some(v =>
        (v.color_code || v.color_name || null) === colorKey &&
        (v.version_name || `${v.ram || ''}|${v.storage || ''}`) === vg.key
      );
    });
  };

  return (
    <div className="space-y-8 border-b border-gray-100 pb-8">
      {colorGroups.length > 1 && (
        <div className="space-y-4">
          <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Màu sắc</label>
          <div className="flex flex-wrap gap-4">
            {colorGroups.map(({ key, color_code, color_name }) => (
              <button
                key={key}
                onClick={() => setSelectedColor(key)}
                className={`relative flex items-center space-x-3 px-5 py-3 rounded-xl border-2 transition-all ${
                  selectedColor === key
                    ? 'border-primary bg-primary/5'
                    : 'border-gray-100 hover:border-gray-200'
                }`}
              >
                <div
                  className="w-5 h-5 rounded-full border border-gray-300 shrink-0"
                  style={{
                    background: isRenderableColor(color_code) ? color_code : SWATCH_FALLBACK,
                  }}
                />
                <span className="font-semibold text-sm text-gray-900">{color_name}</span>
                {selectedColor === key && (
                  <Check className="w-4 h-4 text-primary absolute -top-2 -right-2 bg-primary text-white rounded-full p-0.5" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {versionGroups.length > 1 && (
        <div className="space-y-4">
          <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Phiên bản</label>
          <div className="flex flex-wrap gap-4">
            {versionGroups.map(({ key }) => {
              const availableVersions = getAvailableVersionsForColor(selectedColor);
              const isAvailable = availableVersions.some(av => av.key === key);

              return (
                <button
                  key={key}
                  onClick={() => setSelectedVersion(key)}
                  disabled={!isAvailable}
                  className={`relative px-5 py-3 rounded-xl border-2 transition-all font-semibold text-sm ${
                    selectedVersion === key && isAvailable
                      ? 'border-primary bg-primary/5 text-gray-900'
                      : isAvailable
                      ? 'border-gray-100 text-gray-900 hover:border-gray-200'
                      : 'border-gray-50 text-gray-300 cursor-not-allowed'
                  }`}
                >
                  {key}
                  {selectedVersion === key && isAvailable && (
                    <Check className="w-4 h-4 text-primary absolute -top-2 -right-2 bg-primary text-white rounded-full p-0.5" />
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default VariantSelector;
