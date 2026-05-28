import { useState, useEffect } from 'react';
import { Plus, Trash2, LayoutTemplate, X } from 'lucide-react';
import templateService from '../../services/templateService';

const TYPE_LABELS = {
  phone:     'Điện thoại',
  laptop:    'Laptop',
  audio:     'Âm thanh / Tai nghe',
  watch:     'Đồng hồ thông minh',
  tablet:    'Máy tính bảng',
  accessory: 'Phụ kiện',
};

const TYPE_PRESETS = [
  { value: 'watch',     label: 'Đồng hồ thông minh' },
  { value: 'tablet',    label: 'Máy tính bảng' },
  { value: 'accessory', label: 'Phụ kiện' },
  { value: 'audio',     label: 'Âm thanh / Tai nghe' },
  { value: 'phone',     label: 'Điện thoại' },
  { value: 'laptop',    label: 'Laptop' },
];

export default function SpecTemplates() {
  const [types, setTypes]               = useState([]);
  const [selectedType, setSelectedType] = useState('');
  const [templates, setTemplates]       = useState([]);
  const [loading, setLoading]           = useState(false);
  const [loadingTypes, setLoadingTypes] = useState(true);

  const [form, setForm] = useState({ group_name: '', spec_key: '' });
  const [formError, setFormError] = useState('');

  const [showAddTypeDialog, setShowAddTypeDialog] = useState(false);
  const [newTypeName, setNewTypeName]             = useState('');
  const [newTypeError, setNewTypeError]           = useState('');
  const [savingType, setSavingType]               = useState(false);

  const loadTypes = async () => {
    setLoadingTypes(true);
    try {
      const data = await templateService.adminListTypes();
      setTypes(data);
      if (data.length > 0 && !selectedType) {
        setSelectedType(data[0]);
      }
      if (selectedType && !data.includes(selectedType)) {
        setSelectedType(data[0] || '');
      }
    } catch {
      setTypes([]);
    } finally {
      setLoadingTypes(false);
    }
  };

  useEffect(() => { loadTypes(); }, []);

  const loadTemplates = async () => {
    if (!selectedType) { setTemplates([]); return; }
    setLoading(true);
    const data = await templateService.adminList(selectedType);
    setTemplates(data);
    setLoading(false);
  };

  useEffect(() => { loadTemplates(); }, [selectedType]);

  const handleAddSpec = async () => {
    if (!form.group_name.trim() || !form.spec_key.trim()) {
      setFormError('Vui lòng nhập đủ Group và Spec Key.');
      return;
    }
    setFormError('');
    try {
      await templateService.adminCreate({
        product_type:  selectedType,
        group_name:    form.group_name.trim(),
        spec_key:      form.spec_key.trim(),
        default_order: templates.length,
      });
      setForm({ group_name: '', spec_key: '' });
      loadTemplates();
    } catch {
      setFormError('Spec này đã tồn tại trong template.');
    }
  };

  const handleDeleteSpec = async (id) => {
    if (!window.confirm('Xóa spec này khỏi template?')) return;
    await templateService.adminDelete(id);
    loadTemplates();
  };

  const handleAddType = async () => {
    const trimmed = newTypeName.trim().toLowerCase().replace(/\s+/g, '-');
    if (!trimmed) {
      setNewTypeError('Vui lòng nhập tên loại sản phẩm.');
      return;
    }
    if (types.includes(trimmed)) {
      setNewTypeError(`Template "${trimmed}" đã tồn tại.`);
      return;
    }
    setNewTypeError('');
    setSavingType(true);
    try {
      await templateService.adminCreate({
        product_type:  trimmed,
        group_name:    'Thông số chung',
        spec_key:      'Thông số 1',
        default_order: 0,
      });
      await loadTypes();
      setSelectedType(trimmed);
      setShowAddTypeDialog(false);
      setNewTypeName('');
    } catch {
      setNewTypeError('Không thể tạo template. Vui lòng thử lại.');
    } finally {
      setSavingType(false);
    }
  };

  const handleDeleteType = async () => {
    if (!window.confirm(
      `Xóa toàn bộ template "${selectedType}"?\n` +
      `Thao tác này sẽ xóa TẤT CẢ ${templates.length} spec rows của loại này.`
    )) return;
    try {
      await templateService.adminDeleteType(selectedType);
      await loadTypes();
    } catch {
      alert('Không thể xóa template type.');
    }
  };

  const grouped = templates.reduce((acc, t) => {
    (acc[t.group_name] = acc[t.group_name] || []).push(t);
    return acc;
  }, {});

  return (
    <div className="p-6 max-w-4xl mx-auto">

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <LayoutTemplate className="w-6 h-6 text-primary" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Quản lý Spec Template</h1>
            <p className="text-xs text-gray-400 mt-0.5">
              Mỗi template là tập hợp các trường thông số cho một loại sản phẩm.
            </p>
          </div>
        </div>
        <button
          onClick={() => { setShowAddTypeDialog(true); setNewTypeName(''); setNewTypeError(''); }}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-xl text-sm font-semibold hover:bg-primary/90 transition shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Thêm Template
        </button>
      </div>

      {/* Tab bar (dynamic) */}
      {loadingTypes ? (
        <div className="flex gap-2 mb-6">
          {[1,2,3,4].map(i => (
            <div key={i} className="h-9 w-24 bg-gray-100 rounded-full animate-pulse" />
          ))}
        </div>
      ) : types.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <LayoutTemplate className="w-14 h-14 mx-auto mb-3 opacity-20" />
          <p className="font-medium">Chưa có template nào.</p>
          <p className="text-sm mt-1">Nhấn <strong>+ Thêm Template</strong> để bắt đầu.</p>
        </div>
      ) : (
        <>
          {/* Tabs */}
          <div className="flex gap-2 mb-6 flex-wrap items-center">
            {types.map((type) => (
              <button
                key={type}
                onClick={() => setSelectedType(type)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition border ${
                  selectedType === type
                    ? 'bg-primary text-white border-primary shadow-sm'
                    : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                {TYPE_LABELS[type] || type}
              </button>
            ))}
          </div>

          {/* Add spec row */}
          <div className="bg-white border border-gray-200 rounded-2xl p-5 mb-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-gray-700">
                Thêm spec vào template{' '}
                <span className="text-primary font-bold">
                  {TYPE_LABELS[selectedType] || selectedType}
                </span>
              </h2>
              <button
                onClick={handleDeleteType}
                className="flex items-center gap-1.5 text-xs text-red-400 hover:text-red-600 border border-red-100 hover:border-red-300 px-3 py-1.5 rounded-lg transition"
                title={`Xóa toàn bộ template "${selectedType}"`}
              >
                <Trash2 className="w-3.5 h-3.5" />
                Xóa template này
              </button>
            </div>
            <div className="flex gap-3 flex-wrap">
              <input
                type="text"
                placeholder="Group (VD: Màn hình, Hiệu năng…)"
                value={form.group_name}
                onChange={(e) => setForm({ ...form, group_name: e.target.value })}
                onKeyDown={(e) => e.key === 'Enter' && handleAddSpec()}
                className="flex-1 min-w-40 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
              />
              <input
                type="text"
                placeholder="Spec key (VD: CPU, RAM, Pin…)"
                value={form.spec_key}
                onChange={(e) => setForm({ ...form, spec_key: e.target.value })}
                onKeyDown={(e) => e.key === 'Enter' && handleAddSpec()}
                className="flex-1 min-w-40 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
              />
              <button
                onClick={handleAddSpec}
                className="flex items-center gap-1.5 px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary/90 transition"
              >
                <Plus className="w-4 h-4" /> Thêm
              </button>
            </div>
            {formError && <p className="text-red-500 text-xs mt-2">{formError}</p>}
          </div>

          {/* Spec rows grouped */}
          {loading ? (
            <p className="text-gray-400 text-sm py-4">Đang tải...</p>
          ) : templates.length === 0 ? (
            <div className="text-center py-12 text-gray-400 border-2 border-dashed border-gray-200 rounded-2xl">
              <LayoutTemplate className="w-10 h-10 mx-auto mb-2 opacity-30" />
              <p className="text-sm">Template trống. Thêm spec đầu tiên ở trên.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {Object.entries(grouped).map(([groupName, items]) => (
                <div key={groupName} className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
                  <div className="px-4 py-2.5 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
                    <span className="text-sm font-semibold text-gray-700">{groupName}</span>
                    <span className="text-xs text-gray-400">{items.length} trường</span>
                  </div>
                  <ul className="divide-y divide-gray-50">
                    {items.map((tpl) => (
                      <li key={tpl.id} className="flex items-center justify-between px-4 py-2.5 hover:bg-gray-50 group">
                        <span className="text-sm text-gray-700">{tpl.spec_key}</span>
                        <button
                          onClick={() => handleDeleteSpec(tpl.id)}
                          className="text-gray-300 group-hover:text-red-400 hover:text-red-600 transition"
                          title="Xóa spec này"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Dialog: Thêm template type mới */}
      {showAddTypeDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-gray-900">Thêm Template mới</h2>
                <p className="text-xs text-gray-400 mt-0.5">
                  Tạo tập thông số kỹ thuật cho loại sản phẩm mới.
                </p>
              </div>
              <button
                onClick={() => setShowAddTypeDialog(false)}
                className="text-gray-400 hover:text-gray-600 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                Tên loại sản phẩm (product_type)
              </label>
              <input
                type="text"
                value={newTypeName}
                onChange={(e) => { setNewTypeName(e.target.value); setNewTypeError(''); }}
                onKeyDown={(e) => e.key === 'Enter' && handleAddType()}
                placeholder="VD: watch, tablet, phu-kien…"
                autoFocus
                className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              />
              <p className="text-xs text-gray-400 mt-1.5">
                Chữ thường, không dấu, dùng dấu gạch ngang. VD: <code>dong-ho</code>, <code>tablet</code>
              </p>
              {newTypeError && (
                <p className="text-red-500 text-xs mt-1.5 font-medium">{newTypeError}</p>
              )}
            </div>

            <div>
              <p className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wider">
                Gợi ý nhanh
              </p>
              <div className="flex flex-wrap gap-2">
                {TYPE_PRESETS
                  .filter((p) => !types.includes(p.value))
                  .map((p) => (
                    <button
                      key={p.value}
                      type="button"
                      onClick={() => { setNewTypeName(p.value); setNewTypeError(''); }}
                      className={`px-3 py-1.5 rounded-full text-xs font-medium border transition ${
                        newTypeName === p.value
                          ? 'bg-primary text-white border-primary'
                          : 'bg-gray-50 text-gray-600 border-gray-200 hover:border-primary hover:text-primary'
                      }`}
                    >
                      {p.label}
                    </button>
                  ))
                }
              </div>
              {TYPE_PRESETS.every((p) => types.includes(p.value)) && (
                <p className="text-xs text-gray-400 mt-1">Tất cả loại gợi ý đã được tạo.</p>
              )}
            </div>

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowAddTypeDialog(false)}
                className="flex-1 px-4 py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition"
              >
                Huỷ
              </button>
              <button
                type="button"
                onClick={handleAddType}
                disabled={savingType || !newTypeName.trim()}
                className="flex-1 px-4 py-2.5 rounded-xl bg-primary text-white text-sm font-bold hover:bg-primary/90 transition disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {savingType ? 'Đang tạo...' : 'Tạo Template'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
