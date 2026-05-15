import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, ChevronLeft } from 'lucide-react';
import { formatPrice } from '../utils/formatPrice';
import { productService } from '../services/productService';
import { useAuth } from '../hooks/useAuth';
import StarRating from '../components/StarRating';

const CompareProducts = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const [compareList, setCompareList] = useState(null);
  const [products, setProducts] = useState([]);
  const [specs, setSpecs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    loadCompareList();
  }, [isAuthenticated]);

  const loadCompareList = async () => {
    try {
      // Get the first compare list or create one
      const lists = await productService.getCompareLists();
      if (lists.length > 0) {
        const list = await productService.getCompareList(lists[0].id);
        setCompareList(list);
        extractSpecs(list.items.map((item) => item.product));
      }
    } catch (error) {
      console.error('Error loading compare list:', error);
    } finally {
      setLoading(false);
    }
  };

  const extractSpecs = (productList) => {
    const specMap = {};
    
    productList.forEach((product) => {
      if (product.specs) {
        product.specs.forEach((spec) => {
          if (!specMap[spec.key]) {
            specMap[spec.key] = [];
          }
          specMap[spec.key].push({ product_id: product.id, value: spec.value, unit: spec.unit });
        });
      }
    });

    setSpecs(Object.entries(specMap).map(([key, values]) => ({ key, values })));
  };

  const removeProduct = async (productId) => {
    if (compareList) {
      try {
        await productService.removeFromCompareList(compareList.id, productId);
        await loadCompareList();
      } catch (error) {
        console.error('Error removing product:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!compareList || compareList.items.length === 0) {
    return (
      <div className="min-h-screen bg-white">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-blue-600 mb-8 hover:text-blue-700"
          >
            <ChevronLeft className="w-5 h-5" />
            Back
          </button>
          <div className="text-center space-y-4">
            <h1 className="text-3xl font-bold text-gray-900">Compare Products</h1>
            <p className="text-gray-600">No products added to compare yet</p>
            <button
              onClick={() => navigate('/products')}
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700"
            >
              Browse Products
            </button>
          </div>
        </div>
      </div>
    );
  }

  const compareProducts = compareList.items.map((item) => item.product);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-blue-600 mb-4 hover:text-blue-700"
          >
            <ChevronLeft className="w-5 h-5" />
            Back
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Compare Products</h1>
          <p className="text-gray-600 mt-2">{compareProducts.length} products selected</p>
        </div>

        {/* Comparison Table */}
        <div className="bg-white rounded-lg overflow-hidden shadow-lg">
          <div className="overflow-x-auto">
            <table className="w-full">
              <tbody>
                {/* Product Cards */}
                <tr className="border-b border-gray-200">
                  <td className="p-4 font-semibold text-gray-900 min-w-[150px]">Product</td>
                  {compareProducts.map((product) => (
                    <td key={product.id} className="p-4 min-w-[300px] border-l border-gray-200">
                      <div className="space-y-4">
                        <div className="relative">
                          {product.image_url && (
                            <img
                              src={product.image_url}
                              alt={product.name}
                              className="w-full h-40 object-cover rounded-lg"
                            />
                          )}
                          <button
                            onClick={() => removeProduct(product.id)}
                            className="absolute top-2 right-2 bg-red-500 text-white p-1 rounded hover:bg-red-600"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900 line-clamp-2">{product.name}</h3>
                          <p className="text-blue-600 font-bold mt-1">{formatPrice(product.price)}</p>
                          <div className="mt-2">
                            <StarRating rating={product.rating} size={3} />
                            <p className="text-xs text-gray-500 mt-1">({product.review_count} reviews)</p>
                          </div>
                        </div>
                        <button
                          onClick={() => navigate(`/products/${product.id}`)}
                          className="w-full bg-blue-600 text-white py-2 rounded font-semibold hover:bg-blue-700 text-sm"
                        >
                          View Details
                        </button>
                      </div>
                    </td>
                  ))}
                </tr>

                {/* Specifications */}
                {specs.map((spec) => (
                  <tr key={spec.key} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="p-4 font-semibold text-gray-900 bg-gray-100">{spec.key}</td>
                    {compareProducts.map((product) => {
                      const value = spec.values.find((v) => v.product_id === product.id);
                      return (
                        <td
                          key={`${spec.key}-${product.id}`}
                          className="p-4 text-gray-700 border-l border-gray-200"
                        >
                          {value ? `${value.value} ${value.unit || ''}` : 'N/A'}
                        </td>
                      );
                    })}
                  </tr>
                ))}

                {/* Stock Status */}
                <tr className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="p-4 font-semibold text-gray-900 bg-gray-100">Availability</td>
                  {compareProducts.map((product) => (
                    <td
                      key={`stock-${product.id}`}
                      className="p-4 text-gray-700 border-l border-gray-200"
                    >
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          product.stock > 0
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {product.stock > 0 ? `In Stock (${product.stock})` : 'Out of Stock'}
                      </span>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompareProducts;
