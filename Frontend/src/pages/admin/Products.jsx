import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Filter, Plus, Search, Trash2, X } from 'lucide-react';
import { useProducts } from '../../hooks/useProducts';
import { useAuth } from '../../hooks/useAuth';
import { formatPrice } from '../../utils/formatPrice';
import { productService } from '../../services/productService';
import SpecificationEditor from '../../components/SpecificationEditor';

const makeEmptySpec = () => ({
  local_id: crypto.randomUUID(),
  group_name: '',
  spec_key: '',
  spec_value: '',
  display_order: 0,
});

const flattenGroupedSpecifications = (groupedSpecs) => {
  const rows = Object.entries(groupedSpecs || {}).flatMap(([groupName, specs]) =>
    specs.map((spec, index) => ({
      local_id: spec.id || crypto.randomUUID(),
      id: spec.id,
      group_name: groupName,
      spec_key: spec.key || spec.spec_key || '',
      spec_value: spec.value || spec.spec_value || '',
      display_order: spec.display_order ?? index,
    }))
  );
  return rows.length ? rows : [makeEmptySpec()];
};

const Products = () => {
  const navigate = useNavigate();
  const { profile } = useAuth();
  const { categories, createProduct, updateProduct, deleteProduct } = useProducts();
  const [products, setProducts] = useState([]);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total_items: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    product_type: '',
    brand: '',
  });
  const [searchInput, setSearchInput] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    category_id: '',
    image_url: '',
    stock: '',
    product_type: '',
    featured: false,
  });
  const [specifications, setSpecifications] = useState([makeEmptySpec()]);

  const hasActiveFilters = Boolean(
    filters.search || filters.category || filters.product_type || filters.brand
  );

  const pageNumbers = useMemo(() => {
    const totalPages = pagination.total_pages || 1;
    const start = Math.max(1, page - 2);
    const end = Math.min(totalPages, page + 2);
    return Array.from({ length: end - start + 1 }, (_, index) => start + index);
  }, [page, pagination.total_pages]);

  const loadAdminProducts = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await productService.getProducts({
        search: filters.search.trim() || undefined,
        category: filters.category || undefined,
        type: filters.product_type || undefined,
        brand: filters.brand.trim() || undefined,
        sortBy: 'created_at',
        page,
        limit: pageSize,
      });

      const nextProducts = Array.isArray(data) ? data : data.items || [];
      const nextPagination = data.pagination || {
        page,
        limit: pageSize,
        total_items: nextProducts.length,
        total_pages: 1,
        has_next: false,
        has_prev: false,
      };

      if (nextPagination.total_pages > 0 && page > nextPagination.total_pages) {
        setPage(nextPagination.total_pages);
        return;
      }

      setProducts(nextProducts);
      setPagination(nextPagination);
    } catch (err) {
      console.error('Admin products load error:', err);
      setError(err?.response?.data?.detail || err.message || 'Failed to load products');
      setProducts([]);
    } finally {
      setLoading(false);
    }
  }, [filters.brand, filters.category, filters.product_type, filters.search, page, pageSize]);

  useEffect(() => {
    loadAdminProducts();
  }, [loadAdminProducts]);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setFilters((prev) => ({ ...prev, search: searchInput }));
      setPage(1);
    }, 350);

    return () => window.clearTimeout(timeoutId);
  }, [searchInput]);

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({
      ...formData,
      [e.target.name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const productData = {
        ...formData,
        price: parseFloat(formData.price),
        stock: parseInt(formData.stock),
        product_type: formData.product_type || null,
      };
      const specPayload = specifications
        .filter((spec) => spec.spec_key)
        .map((spec, index) => ({
          group_name: spec.group_name || 'Thông số khác',
          spec_key: spec.spec_key,
          spec_value: spec.spec_value,
          display_order: index,
        }));

      if (editingProduct) {
        const product = await updateProduct(editingProduct.id, productData);
        await productService.saveProductSpecifications(product.id, specPayload);
      } else {
        const product = await createProduct(productData);
        await productService.saveProductSpecifications(product.id, specPayload);
      }

      setShowModal(false);
      resetForm();
      await loadAdminProducts();
      alert('Product saved successfully!');
    } catch (error) {
      alert(error.message);
    }
  };

  const handleEdit = async (product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name,
      description: product.description || '',
      price: product.price,
      category_id: product.category_id || '',
      image_url: product.image_url || '',
      stock: product.stock,
      product_type: product.product_type || '',
      featured: product.featured,
    });
    try {
      const groupedSpecs = await productService.getProductSpecifications(product.id);
      setSpecifications(flattenGroupedSpecifications(groupedSpecs));
    } catch (error) {
      console.error('Error loading product specifications:', error);
      setSpecifications([makeEmptySpec()]);
    }
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await deleteProduct(id);
        await loadAdminProducts();
        alert('Product deleted successfully!');
      } catch (error) {
        alert(error.message);
      }
    }
  };

  const resetForm = () => {
    setEditingProduct(null);
    setFormData({
      name: '',
      description: '',
      price: '',
      category_id: '',
      image_url: '',
      stock: '',
      product_type: '',
      featured: false,
    });
    setSpecifications([makeEmptySpec()]);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    resetForm();
  };

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const clearFilters = () => {
    setSearchInput('');
    setFilters({
      search: '',
      category: '',
      product_type: '',
      brand: '',
    });
    setPage(1);
  };

  const firstItem = pagination.total_items === 0 ? 0 : (pagination.page - 1) * pagination.limit + 1;
  const lastItem = Math.min(pagination.page * pagination.limit, pagination.total_items);

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div className="space-y-2">
          <div className="flex items-center space-x-2 text-primary">
            <div className="h-1 w-8 bg-primary rounded-full" />
            <span className="text-xs font-black uppercase tracking-widest">Catalog</span>
          </div>
          <h1 className="text-4xl font-black text-gray-900 tracking-tight">Products</h1>
        </div>
        {profile?.is_admin && (
          <Link
            to="/admin/products/add"
            className="bg-primary text-white px-6 py-3 rounded-lg font-bold uppercase tracking-widest text-xs hover:bg-gray-900 transition-colors flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Add Product</span>
          </Link>
        )}
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 mb-6">
        <div className="flex items-center gap-2 text-gray-900 font-semibold mb-4">
          <Filter className="w-5 h-5 text-gray-500" />
          <span>Filter products</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4">
          <div className="xl:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="search"
                value={searchInput}
                onChange={(event) => setSearchInput(event.target.value)}
                placeholder="Search by product name..."
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <select
              value={filters.category}
              onChange={(event) => handleFilterChange('category', event.target.value)}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">All categories</option>
              {categories.map((category) => (
                <option key={category.id} value={category.slug || category.id}>
                  {category.level ? `${'-- '.repeat(category.level)}${category.name}` : category.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type
            </label>
            <select
              value={filters.product_type}
              onChange={(event) => handleFilterChange('product_type', event.target.value)}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">All types</option>
              <option value="phone">Phone</option>
              <option value="laptop">Laptop</option>
              <option value="audio">Audio</option>
              <option value="tablet">Tablet</option>
              <option value="accessory">Accessory</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Brand
            </label>
            <input
              type="text"
              value={filters.brand}
              onChange={(event) => handleFilterChange('brand', event.target.value)}
              placeholder="Apple, Samsung..."
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mt-4">
          <div className="flex items-center gap-3">
            <label className="text-sm text-gray-600" htmlFor="admin-product-page-size">
              Show
            </label>
            <select
              id="admin-product-page-size"
              value={pageSize}
              onChange={(event) => {
                setPageSize(Number(event.target.value));
                setPage(1);
              }}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value={10}>10 products</option>
              <option value={20}>20 products</option>
            </select>
          </div>

          {hasActiveFilters && (
            <button
              type="button"
              onClick={clearFilters}
              className="inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-semibold text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <X className="w-4 h-4" />
              Clear filters
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-5">
          {error}
        </div>
      ) : (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <p className="text-sm text-gray-600">
              Showing <span className="font-semibold text-gray-900">{firstItem}</span>-
              <span className="font-semibold text-gray-900">{lastItem}</span> of{' '}
              <span className="font-semibold text-gray-900">{pagination.total_items}</span> products
            </p>
            <p className="text-sm text-gray-500">
              Page {pagination.page || 1} / {Math.max(pagination.total_pages || 1, 1)}
            </p>
          </div>

          {products.length === 0 ? (
            <div className="text-center text-gray-500 py-16">
              No products found. Try changing the search or filters.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Product
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Category
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stock
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {products.map((product) => (
                    <tr key={product.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="h-10 w-10 flex-shrink-0 bg-gray-200 rounded">
                            {product.image_url && (
                              <img
                                src={product.image_url}
                                alt={product.name}
                                className="h-10 w-10 rounded object-cover"
                              />
                            )}
                          </div>
                          <div className="ml-4 min-w-0">
                            <div className="text-sm font-medium text-gray-900 truncate max-w-xs">
                              {product.name}
                            </div>
                            {product.brand && (
                              <div className="text-xs text-gray-500 truncate max-w-xs">
                                {product.brand}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600">
                          {product.category?.name || '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600">
                          {product.product_type || '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">
                          {formatPrice(product.price)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">{product.stock}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => navigate(`/admin/products/edit/${product.id}`)}
                          className="text-xs font-bold bg-primary/5 text-primary border border-primary/20 px-3 py-1.5 rounded-lg hover:bg-primary/10 transition-colors mr-3"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(product.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="px-6 py-4 border-t border-gray-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <button
              type="button"
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              disabled={!pagination.has_prev}
              className="inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-semibold border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </button>

            <div className="flex items-center justify-center gap-2">
              {pageNumbers.map((pageNumber) => (
                <button
                  key={pageNumber}
                  type="button"
                  onClick={() => setPage(pageNumber)}
                  className={`w-9 h-9 rounded-lg text-sm font-semibold transition-colors ${
                    pageNumber === pagination.page
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {pageNumber}
                </button>
              ))}
            </div>

            <button
              type="button"
              onClick={() => setPage((current) => current + 1)}
              disabled={!pagination.has_next}
              className="inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-semibold border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-100 shadow-2xl">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              {editingProduct ? 'Edit Product' : 'Add New Product'}
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Product Name *
                </label>
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
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Price *
                  </label>
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
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Stock *
                  </label>
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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <select
                  name="category_id"
                  value={formData.category_id}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">Select a category</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Image URL
                </label>
                <input
                  type="url"
                  name="image_url"
                  value={formData.image_url}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Product Type
                </label>
                <select
                  name="product_type"
                  value={formData.product_type}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">Custom</option>
                  <option value="phone">Phone</option>
                  <option value="laptop">Laptop</option>
                  <option value="audio">Audio</option>
                </select>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="featured"
                  checked={formData.featured}
                  onChange={handleChange}
                  className="w-4 h-4 text-primary rounded focus:ring-primary"
                />
                <label className="ml-2 text-sm text-gray-700">
                  Featured Product
                </label>
              </div>

              <SpecificationEditor
                productType={formData.product_type}
                onProductTypeChange={(productType) => setFormData({ ...formData, product_type: productType })}
                specifications={specifications}
                onChange={setSpecifications}
              />

              <div className="flex space-x-4 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-primary text-white py-3 rounded-lg font-semibold hover:bg-gray-900 transition-colors"
                >
                  {editingProduct ? 'Update Product' : 'Add Product'}
                </button>
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Products;


