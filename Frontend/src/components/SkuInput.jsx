import { useState, useEffect, useRef } from 'react';
import { AlertCircle } from 'lucide-react';
import api from '../services/api';

/**
 * Props:
 *   value        – string, giá trị SKU hiện tại
 *   onChange     – (newVal: string) => void
 *   currentId    – string | null, id sản phẩm đang edit (null khi Add)
 *   className    – string, class bổ sung cho wrapper
 */
export default function SkuInput({ value, onChange, currentId = null, className = '' }) {
  const [status, setStatus] = useState('idle');
  const [showTip, setShowTip] = useState(false);
  const debounceRef = useRef(null);
  const tipRef = useRef(null);

  const SKU_REGEX = /^[A-Za-z0-9\-_]{3,50}$/;

  useEffect(() => {
    if (!value || value.trim() === '') {
      setStatus('idle');
      return;
    }

    if (!SKU_REGEX.test(value.trim())) {
      setStatus('invalid');
      return;
    }

    clearTimeout(debounceRef.current);
    setStatus('checking');
    debounceRef.current = setTimeout(async () => {
      try {
        const params = new URLSearchParams({ sku: value.trim() });
        if (currentId) params.append('exclude_id', currentId);
        const { data } = await api.get(`/admin/check-sku?${params}`);
        setStatus(data.exists ? 'duplicate' : 'ok');
      } catch {
        setStatus('idle');
      }
    }, 500);

    return () => clearTimeout(debounceRef.current);
  }, [value, currentId]);

  useEffect(() => {
    const handler = (e) => {
      if (tipRef.current && !tipRef.current.contains(e.target)) setShowTip(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const messages = {
    idle:      { color: 'text-gray-400', tip: 'SKU phải từ 3–50 ký tự, chỉ dùng chữ cái, số, dấu gạch ngang (-) và gạch dưới (_). Mỗi sản phẩm phải có SKU duy nhất.' },
    checking:  { color: 'text-yellow-500', tip: 'Đang kiểm tra SKU...' },
    ok:        { color: 'text-green-500', tip: 'SKU hợp lệ và chưa được sử dụng.' },
    duplicate: { color: 'text-red-500', tip: 'SKU này đã tồn tại. Vui lòng dùng SKU khác.' },
    invalid:   { color: 'text-red-500', tip: 'SKU không hợp lệ. Chỉ dùng A-Z, 0-9, dấu - và _, tối thiểu 3 ký tự.' },
  };

  const borderColor =
    status === 'ok'        ? 'border-green-400 focus:ring-green-400' :
    status === 'duplicate' ? 'border-red-400 focus:ring-red-400' :
    status === 'invalid'   ? 'border-red-400 focus:ring-red-400' :
    status === 'checking'  ? 'border-yellow-400 focus:ring-yellow-400' :
    'border-gray-300 focus:ring-primary';

  const { color, tip } = messages[status];

  return (
    <div className={`relative ${className}`}>
      <div className="relative flex items-center">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="VD: LAPTOP-DELL-001"
          className={`w-full px-4 py-2 pr-10 border rounded-md focus:outline-none focus:ring-2 transition-colors ${borderColor}`}
        />

        <div ref={tipRef} className="absolute right-3 flex items-center">
          <button
            type="button"
            onClick={() => setShowTip((v) => !v)}
            className={`focus:outline-none ${color} hover:opacity-80 transition-opacity`}
            tabIndex={-1}
            aria-label="SKU hint"
          >
            <AlertCircle className="w-4 h-4" />
          </button>

          {showTip && (
            <div className="absolute right-6 top-1/2 -translate-y-1/2 z-50 w-64 bg-gray-900 text-white text-xs rounded-lg px-3 py-2 shadow-xl leading-relaxed">
              {tip}
              <span className="absolute right-[-6px] top-1/2 -translate-y-1/2 border-4 border-transparent border-l-gray-900" />
            </div>
          )}
        </div>
      </div>

      {status === 'duplicate' && (
        <p className="mt-1 text-xs text-red-500">SKU đã tồn tại, vui lòng chọn SKU khác.</p>
      )}
      {status === 'invalid' && (
        <p className="mt-1 text-xs text-red-500">Chỉ dùng A-Z, 0-9, dấu - và _. Tối thiểu 3 ký tự.</p>
      )}
      {status === 'ok' && (
        <p className="mt-1 text-xs text-green-500">SKU hợp lệ ✓</p>
      )}
    </div>
  );
}
