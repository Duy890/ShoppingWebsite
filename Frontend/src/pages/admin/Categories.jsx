import { useEffect, useState } from 'react';
import { ChevronDown, ChevronRight, Folder, FolderOpen, Plus, Trash2 } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { productService } from '../../services/productService';

const emptyForm = { name: '', description: '', parent_id: '' };

const Categories = () => {
  const [tree, setTree] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState({});
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [flatList, setFlatList] = useState([]);
  const [confirmDialog, setConfirmDialog] = useState({ open: false, id: null, name: '' });

  useEffect(() => {
    loadTree();
  }, []);

  const loadTree = async () => {
    setLoading(true);
    try {
      const [treeData, flatData] = await Promise.all([
        productService.getCategoryTree(),
        productService.getCategories(),
      ]);
      setTree(treeData);
      setFlatList(flatData);
      setExpanded((prev) => {
        const next = { ...prev };
        treeData.forEach((node) => {
          if (node.children?.length && next[node.id] === undefined) {
            next[node.id] = true;
          }
        });
        return next;
      });
    } catch (error) {
      console.error('Unable to load categories:', error);
      toast.error('Khong tai duoc danh muc');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (id) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const requestDelete = (id, name) => {
    setConfirmDialog({ open: true, id, name });
  };

  const handleDelete = async () => {
    if (!confirmDialog.id) return;

    try {
      await productService.deleteCategory(confirmDialog.id);
      toast.success('Da xoa danh muc');
      setConfirmDialog({ open: false, id: null, name: '' });
      loadTree();
    } catch (error) {
      toast.error(error?.response?.data?.detail || 'Xoa that bai');
    }
  };

  const handleSubmit = async () => {
    if (!formData.name.trim()) {
      toast.error('Ten danh muc khong duoc de trong');
      return;
    }

    setSubmitting(true);
    try {
      await productService.createCategory({
        name: formData.name.trim(),
        description: formData.description.trim() || null,
        parent_id: formData.parent_id || null,
      });
      toast.success('Da them danh muc');
      setFormData(emptyForm);
      setShowForm(false);
      loadTree();
    } catch (error) {
      toast.error(error?.response?.data?.detail || 'Them that bai');
    } finally {
      setSubmitting(false);
    }
  };

  const CategoryNode = ({ node, depth = 0 }) => {
    const isExpanded = expanded[node.id];
    const hasChildren = node.children?.length > 0;
    const paddingLeft = depth * 24 + 16;

    return (
      <div>
        <div
          className="flex items-center justify-between py-3 px-4 hover:bg-gray-50 border-b border-gray-100 transition-colors"
          style={{ paddingLeft }}
        >
          <div className="flex items-center gap-2 flex-1 min-w-0">
            {hasChildren ? (
              <button
                type="button"
                onClick={() => toggleExpand(node.id)}
                className="p-0.5 text-gray-400 hover:text-gray-700 flex-shrink-0"
              >
                {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </button>
            ) : (
              <span className="w-5 flex-shrink-0" />
            )}

            {hasChildren ? (
              <FolderOpen className="w-4 h-4 text-orange-400 flex-shrink-0" />
            ) : (
              <Folder className="w-4 h-4 text-gray-300 flex-shrink-0" />
            )}

            <div className="min-w-0">
              <span className={`font-medium text-gray-800 truncate block ${depth === 0 ? 'text-base' : 'text-sm'}`}>
                {node.name}
              </span>
              {node.description && (
                <span className="text-xs text-gray-400 truncate block">
                  {node.description}
                </span>
              )}
            </div>

            {node.level === 0 && (
              <span className="ml-2 text-[10px] font-bold bg-orange-100 text-orange-600 px-2 py-0.5 rounded-full flex-shrink-0">
                Cha
              </span>
            )}
            {hasChildren && (
              <span className="ml-1 text-[10px] text-gray-400 flex-shrink-0">
                ({node.children.length} con)
              </span>
            )}
          </div>

          <button
            type="button"
            onClick={() => requestDelete(node.id, node.name)}
            className="p-1.5 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors flex-shrink-0 ml-2"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>

        {hasChildren && isExpanded && (
          <div>
            {node.children.map((child) => (
              <CategoryNode key={child.id} node={child} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Quan ly danh muc
        </h1>
        <button
          type="button"
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-xl font-semibold text-sm transition-colors"
        >
          <Plus className="w-4 h-4" />
          Them danh muc
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4">
            Them danh muc moi
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Ten danh muc *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(event) => setFormData((prev) => ({ ...prev, name: event.target.value }))}
                placeholder="VD: Laptop Gaming"
                className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Danh muc cha
              </label>
              <select
                value={formData.parent_id}
                onChange={(event) => setFormData((prev) => ({ ...prev, parent_id: event.target.value }))}
                className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
              >
                <option value="">-- Khong chon (tao danh muc cha) --</option>
                {flatList
                  .filter((category) => category.level === 0 || category.level == null)
                  .map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Mo ta
              </label>
              <input
                type="text"
                value={formData.description}
                onChange={(event) => setFormData((prev) => ({ ...prev, description: event.target.value }))}
                placeholder="Mo ta ngan ve danh muc..."
                className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
              />
            </div>
          </div>
          <div className="flex gap-3 mt-5">
            <button
              type="button"
              onClick={handleSubmit}
              disabled={submitting}
              className="bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white px-6 py-2.5 rounded-xl font-bold text-sm transition-colors"
            >
              {submitting ? 'Dang them...' : 'Them danh muc'}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowForm(false);
                setFormData(emptyForm);
              }}
              className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-2.5 rounded-xl font-bold text-sm transition-colors"
            >
              Huy
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-100 bg-gray-50">
          <span className="text-sm font-semibold text-gray-500">
            Danh sach danh muc
            {!loading && ` (${flatList.length} tong cong)`}
          </span>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-48">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500" />
          </div>
        ) : tree.length === 0 ? (
          <div className="text-center text-gray-400 py-16">
            Chua co danh muc nao. Them danh muc dau tien!
          </div>
        ) : (
          <div>
            {tree.map((node) => (
              <CategoryNode key={node.id} node={node} depth={0} />
            ))}
          </div>
        )}
      </div>

      {confirmDialog.open && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl">
            <p className="text-sm font-semibold text-gray-700 mb-6">
              Xoa danh muc "{confirmDialog.name}"?
            </p>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={handleDelete}
                className="flex-1 bg-red-500 text-white py-2 rounded-lg font-bold hover:bg-red-600"
              >
                Xoa
              </button>
              <button
                type="button"
                onClick={() => setConfirmDialog({ open: false, id: null, name: '' })}
                className="flex-1 bg-gray-100 text-gray-700 py-2 rounded-lg font-bold hover:bg-gray-200"
              >
                Huy
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Categories;
