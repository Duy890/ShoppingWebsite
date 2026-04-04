import { useState } from 'react';
import { Trash2 } from 'lucide-react';
import { useProducts } from '../../hooks/useProducts';

const Categories = () => {
  const { categories, loading, createCategory, deleteCategory } = useProducts();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
  });
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      await createCategory(formData);
      setFormData({ name: '', description: '' });
      alert('Category added successfully!');
    } catch (err) {
      setError(err.message || 'Unable to create category');
    }
  };

  const handleDelete = async (categoryId) => {
    if (!window.confirm('Delete this category?')) {
      return;
    }

    try {
      await deleteCategory(categoryId);
      alert('Category deleted successfully!');
    } catch (err) {
      alert(err.message || 'Unable to delete category');
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Categories</h1>
          <p className="text-gray-600 mt-2">Manage product categories for the store.</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.3fr_1fr]">
        <section className="bg-white rounded-xl shadow p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Add Category</h2>
          {error && <div className="text-sm text-red-600 mb-4">{error}</div>}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Name *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              disabled={loading}
            >
              {loading ? 'Saving...' : '+ Add Category'}
            </button>
          </form>
        </section>

        <section className="bg-white rounded-xl shadow p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Category List</h2>
          {loading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : categories.length === 0 ? (
            <p className="text-gray-600">No categories available yet.</p>
          ) : (
            <div className="space-y-4">
              {categories.map((category) => (
                <div
                  key={category.id}
                  className="flex items-center justify-between rounded-lg border border-gray-200 p-4"
                >
                  <div>
                    <div className="font-semibold text-gray-900">{category.name}</div>
                    {category.description && (
                      <div className="text-sm text-gray-600">{category.description}</div>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => handleDelete(category.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default Categories;
