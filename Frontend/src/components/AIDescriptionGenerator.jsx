import { useState } from 'react';
import { Sparkles, ChevronDown, ChevronUp, Copy, Check, AlertCircle, Loader2 } from 'lucide-react';
import { adminService } from '../services/adminService';
import { toast } from 'react-hot-toast';

const AIDescriptionGenerator = ({ formData, variants, specifications, onApply }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(null);

  const handleGenerate = async () => {
    if (!formData.name?.trim()) {
      toast.error('Vui lòng nhập tên sản phẩm trước khi tạo mô tả.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const specsByGroup = specifications
        .filter((s) => s.spec_key && s.spec_value)
        .reduce((acc, s) => {
          if (!acc[s.group_name || 'Thông số']) acc[s.group_name || 'Thông số'] = {};
          acc[s.group_name || 'Thông số'][s.spec_key] = s.spec_value;
          return acc;
        }, {});

      const cleanVariants = variants
        .filter((v) => v.color_name || v.version_name || v.ram || v.storage)
        .map((v) => ({
          ...(v.color_name   && { color_name: v.color_name }),
          ...(v.version_name && { version_name: v.version_name }),
          ...(v.ram          && { ram: v.ram }),
          ...(v.storage      && { storage: v.storage }),
          ...(v.price        && { price: v.price }),
        }));

      const payload = {
        name: formData.name,
        ...(formData.brand        && { brand: formData.brand }),
        ...(formData.product_type && { product_type: formData.product_type }),
        ...(formData.price        && { price: formData.price }),
        ...(formData.sku          && { sku: formData.sku }),
        ...(cleanVariants.length  && { variants: cleanVariants }),
        ...(Object.keys(specsByGroup).length && { specifications: specsByGroup }),
      };

      const data = await adminService.generateDescription(payload);
      setResult(data);
      setExpanded(true);
      toast.success('Tạo mô tả thành công!');
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message || 'Tạo mô tả thất bại.';
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async (text, key) => {
    await navigator.clipboard.writeText(text);
    setCopied(key);
    setTimeout(() => setCopied(null), 2000);
  };

  const handleApplyField = (field, value) => {
    onApply({ [field]: value });
    toast.success(`Đã áp dụng "${field === 'short_description' ? 'Mô tả ngắn' : field}" vào form.`);
  };

  const handleApplyAll = () => {
    onApply(result);
    toast.success('Đã áp dụng toàn bộ mô tả vào form!');
  };

  return (
    <div className="border border-violet-200 rounded-xl bg-violet-50/40 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-violet-600" />
          <span className="text-sm font-black text-violet-800 uppercase tracking-widest">
            AI Tạo Mô Tả
          </span>
          <span className="text-[10px] bg-violet-200 text-violet-700 px-2 py-0.5 rounded-full font-bold">
            Gemini Flash
          </span>
        </div>
        <button
          type="button"
          onClick={handleGenerate}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 bg-violet-600 text-white text-xs font-bold rounded-lg hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Đang tạo...</>
          ) : (
            <><Sparkles className="w-3.5 h-3.5" /> Tạo mô tả tự động</>
          )}
        </button>
      </div>

      <p className="text-xs text-violet-600 leading-relaxed">
        Điền <strong>Tên sản phẩm</strong>, <strong>Thương hiệu</strong>, <strong>Loại sản phẩm</strong> và
        <strong> Thông số kỹ thuật</strong> trước để AI tạo mô tả chính xác nhất.
        AI chỉ dùng dữ liệu bạn đã nhập, không bịa thêm thông tin.
      </p>

      {error && (
        <div className="flex items-start gap-2 text-xs text-red-700 bg-red-50 border border-red-200 rounded-lg p-3">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div className="space-y-3">
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="flex items-center gap-1.5 text-xs font-bold text-violet-700 hover:text-violet-900"
          >
            {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            {expanded ? 'Ẩn kết quả' : 'Xem kết quả'}
          </button>

          {expanded && (
            <div className="space-y-3 bg-white rounded-xl border border-violet-100 p-4">
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={handleApplyAll}
                  className="text-xs font-black bg-violet-600 text-white px-4 py-1.5 rounded-lg hover:bg-violet-700 transition-colors"
                >
                  ✓ Áp dụng tất cả vào form
                </button>
              </div>

              <ResultField
                label="Mô tả ngắn"
                value={result.short_description}
                fieldKey="short_description"
                copied={copied}
                onCopy={handleCopy}
                onApply={() => handleApplyField('short_description', result.short_description)}
              />

              <div>
                <FieldHeader label="Điểm nổi bật" />
                <ul className="mt-2 space-y-1 pl-3">
                  {result.key_highlights.map((h, i) => (
                    <li key={i} className="text-xs text-gray-700 flex items-start gap-1.5">
                      <span className="text-violet-500 font-bold mt-0.5">•</span>
                      <span>{h}</span>
                    </li>
                  ))}
                </ul>
                <button
                  type="button"
                  onClick={() => handleApplyField('key_highlights', result.key_highlights)}
                  className="mt-2 text-[10px] font-bold text-violet-600 underline hover:text-violet-800"
                >
                  Áp dụng
                </button>
              </div>

              <ResultField
                label="Mô tả đầy đủ"
                value={result.full_description}
                fieldKey="full_description"
                multiline
                copied={copied}
                onCopy={handleCopy}
                onApply={() => handleApplyField('description', result.full_description)}
              />

              {result.performance_summary && (
                <ResultField
                  label="Tổng quan hiệu năng"
                  value={result.performance_summary}
                  fieldKey="performance_summary"
                  multiline
                  copied={copied}
                  onCopy={handleCopy}
                  onApply={() => handleApplyField('performance_summary', result.performance_summary)}
                />
              )}

              <ResultField
                label={`SEO Meta (${result.seo_description?.length ?? 0}/160 ký tự)`}
                value={result.seo_description}
                fieldKey="seo_description"
                copied={copied}
                onCopy={handleCopy}
                onApply={() => handleApplyField('seo_description', result.seo_description)}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

function FieldHeader({ label }) {
  return <p className="text-[10px] font-black uppercase tracking-widest text-gray-400">{label}</p>;
}

function ResultField({ label, value, fieldKey, multiline, copied, onCopy, onApply }) {
  return (
    <div>
      <FieldHeader label={label} />
      <div className="mt-1.5 relative group">
        {multiline ? (
          <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap bg-gray-50 rounded-lg p-3 pr-16">
            {value}
          </p>
        ) : (
          <p className="text-xs text-gray-700 bg-gray-50 rounded-lg p-3 pr-16">{value}</p>
        )}
        <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            type="button"
            onClick={() => onCopy(value, fieldKey)}
            className="p-1 rounded bg-white shadow-sm border border-gray-200 hover:bg-gray-50"
            title="Copy"
          >
            {copied === fieldKey
              ? <Check className="w-3 h-3 text-emerald-500" />
              : <Copy className="w-3 h-3 text-gray-400" />}
          </button>
        </div>
      </div>
      <button
        type="button"
        onClick={onApply}
        className="mt-1 text-[10px] font-bold text-violet-600 underline hover:text-violet-800"
      >
        Áp dụng vào form
      </button>
    </div>
  );
}

export default AIDescriptionGenerator;
