import { useState, useEffect } from 'react';
import { LayoutTemplate, ChevronDown, Check } from 'lucide-react';
import templateService from '../services/templateService';

export default function ApplyTemplateBar({ productType, onApply }) {
  const [templates, setTemplates] = useState([]);
  const [open, setOpen] = useState(false);
  const [applied, setApplied] = useState(false);

  useEffect(() => {
    if (!productType) { setTemplates([]); return; }
    templateService.getTemplatesByType(productType)
      .then(setTemplates)
      .catch(() => setTemplates([]));
    setApplied(false);
  }, [productType]);

  if (!productType || templates.length === 0) return null;

  const handleApply = () => {
    const groups = {};
    templates.forEach((tpl) => {
      if (!groups[tpl.group_name]) groups[tpl.group_name] = [];
      groups[tpl.group_name].push(tpl);
    });

    const rows = [];
    Object.entries(groups).forEach(([groupName, items], gi) => {
      rows.push({ isGroup: true,  group_name: groupName, display_order: gi * 100 });
      items.forEach((tpl, ii) => {
        rows.push({
          isGroup:       false,
          local_id:      crypto.randomUUID(),
          group_name:    groupName,
          spec_key:      tpl.spec_key,
          spec_value:    '',
          display_order: gi * 100 + ii + 1,
        });
      });
    });

    onApply(rows);
    setApplied(true);
    setOpen(false);
  };

  return (
    <div className="flex items-center gap-3 mb-4 p-3 bg-blue-50 border border-blue-100 rounded-xl">
      <LayoutTemplate className="w-4 h-4 text-blue-500 flex-shrink-0" />
      <span className="text-sm text-blue-700 font-medium flex-1">
        Có {templates.length} trường spec từ template <strong>{productType}</strong>
      </span>

      <div className="relative">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border border-blue-300 bg-white text-blue-700 hover:bg-blue-50 transition"
        >
          Xem trước <ChevronDown className="w-3.5 h-3.5" />
        </button>

        {open && (
          <div className="absolute right-0 top-full mt-1 z-50 w-72 bg-white border border-gray-200 rounded-xl shadow-xl p-3 max-h-64 overflow-y-auto">
            <p className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
              Các trường sẽ được tạo
            </p>
            {Object.entries(
              templates.reduce((acc, t) => {
                (acc[t.group_name] = acc[t.group_name] || []).push(t.spec_key);
                return acc;
              }, {})
            ).map(([group, keys]) => (
              <div key={group} className="mb-2">
                <p className="text-xs font-bold text-gray-700">{group}</p>
                {keys.map((k) => (
                  <p key={k} className="text-xs text-gray-500 ml-2">· {k}</p>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>

      <button
        type="button"
        onClick={handleApply}
        className={`flex items-center gap-1.5 text-sm px-4 py-1.5 rounded-lg font-medium transition ${
          applied
            ? 'bg-green-100 text-green-700 border border-green-300'
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {applied ? <><Check className="w-3.5 h-3.5" /> Đã áp dụng</> : 'Áp dụng'}
      </button>
    </div>
  );
}
