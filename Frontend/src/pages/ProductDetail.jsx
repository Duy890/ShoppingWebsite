import { useEffect, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import {
  ShoppingCart,
  ArrowLeft,
  Star,
  ShieldCheck,
  Truck,
  RefreshCcw,
  Plus,
  Minus
} from 'lucide-react';
import { formatPrice } from '../utils/formatPrice';
import { useCart } from '../hooks/useCart';
import { useAuth } from '../hooks/useAuth';
import { productService } from '../services/productService';
import StarRating from '../components/StarRating';
import ProductSpecifications from '../components/ProductSpecifications';
import VariantSelector from '../components/VariantSelector';

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { addToCart } = useCart();
  const { isAuthenticated, user } = useAuth();
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [specifications, setSpecifications] = useState({});
  const [activeTab, setActiveTab] = useState('specifications');
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: '' });
  const [submittingReview, setSubmittingReview] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [displayPrice, setDisplayPrice] = useState(null);

  useEffect(() => {
    loadProduct();
    loadReviews();
    loadSpecifications();
    window.scrollTo(0, 0);
  }, [id]);

  const loadProduct = async () => {
    try {
      const data = await productService.getProductById(id);
      if (!data) {
        navigate('/404', { replace: true });
        return;
      }
      setProduct(data);
      setDisplayPrice(data.price);

      if (data.variants && data.variants.length > 0) {
        const colorParam = searchParams.get('color');
        const versionParam = searchParams.get('version');
        let variant = null;

        if (colorParam || versionParam) {
          variant = data.variants.find(v => {
            const matchColor = !colorParam || v.color_code === colorParam;
            const versionStr = `${v.ram}|${v.storage}`;
            const matchVersion = !versionParam || v.version_name === versionParam || versionStr === versionParam;
            return matchColor && matchVersion;
          });
        }

        variant = variant || data.variants.find(v => v.is_default) || data.variants[0];
        setSelectedVariant(variant);
        setDisplayPrice(variant.price || data.price);

        const newParams = new URLSearchParams();
        if (variant.color_code) {
          newParams.set('color', variant.color_code);
        }
        if (variant.version_name) {
          newParams.set('version', variant.version_name);
        } else if (variant.ram || variant.storage) {
          newParams.set('version', `${variant.ram}|${variant.storage}`);
        }
        setSearchParams(newParams);
      }
    } catch (error) {
      console.error('Error loading product:', error);
      if (error.response?.status === 404) {
        navigate('/404', { replace: true });
      }
    } finally {
      setLoading(false);
    }
  };

  const loadReviews = async () => {
    try {
      const data = await productService.getProductReviews(id);
      setReviews(data);
    } catch (error) {
      console.error('Error loading reviews:', error);
    }
  };

  const loadSpecifications = async () => {
    try {
      const data = await productService.getProductSpecifications(id);
      setSpecifications(data);
    } catch (error) {
      console.error('Error loading specifications:', error);
      setSpecifications({});
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      alert('Please sign in to leave a review');
      return;
    }

    setSubmittingReview(true);
    try {
      await productService.addProductReview(id, reviewForm);
      setReviewForm({ rating: 5, comment: '' });
      await loadReviews();
      await loadProduct(); // Reload to get updated average rating
      alert('Review submitted successfully!');
    } catch (error) {
      alert(error.message || 'Error submitting review');
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      alert('Please sign in to add items to cart');
      navigate('/login');
      return;
    }
    try {
      await addToCart(product.id, quantity, selectedVariant?.id);
      navigate('/cart');
    } catch (error) {
      alert(error.message);
    }
  };

  const handleVariantChange = (variant) => {
    setSelectedVariant(variant);
    setDisplayPrice(variant.price || product.price);
    setQuantity(1);

    const newParams = new URLSearchParams();
    if (variant.color_code) {
      newParams.set('color', variant.color_code);
    }
    if (variant.version_name) {
      newParams.set('version', variant.version_name);
    } else if (variant.ram || variant.storage) {
      newParams.set('version', `${variant.ram}|${variant.storage}`);
    }
    setSearchParams(newParams);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center space-y-4">
          <p className="text-2xl font-black text-gray-900">Product Not Found</p>
          <button
            onClick={() => navigate('/products')}
            className="bg-primary text-white px-8 py-3 rounded-xl font-bold uppercase tracking-widest text-xs"
          >
            Back to Catalog
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white pb-20">
      {/* Breadcrumb / Navigation */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center space-x-2 text-gray-400 hover:text-primary transition-colors font-bold uppercase tracking-widest text-[10px]"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to products</span>
        </button>
      </div>

      <div className="max-w-7xl mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
          
          {/* Product Image Gallery */}
          <div className="space-y-6">
            <div className="aspect-square bg-gray-50 rounded-3xl overflow-hidden border border-gray-100 flex items-center justify-center p-12">
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="w-full h-full object-contain hover:scale-105 transition-transform duration-700"
                />
              ) : (
                <div className="text-gray-300 italic">No image available</div>
              )}
            </div>
            
            {/* Small Thumbnails (Mockup) */}
            <div className="grid grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="aspect-square bg-gray-50 rounded-xl border border-gray-100 cursor-pointer hover:border-primary transition-colors p-2">
                   {product.image_url && <img src={product.image_url} alt="thumbnail" className="w-full h-full object-contain opacity-50" />}
                </div>
              ))}
            </div>
          </div>

          {/* Product Info */}
          <div className="flex flex-col">
            <div className="space-y-6 border-b border-gray-100 pb-8">
              <div className="flex items-center space-x-2">
                 <span className="bg-primary/10 text-primary px-4 py-1 rounded-full text-[10px] font-black uppercase tracking-widest">
                  {product.category?.name || 'Electronic'}
                </span>
                {product.brand && (
                  <span className="text-gray-400 text-[10px] font-bold uppercase tracking-widest px-4 py-1 border border-gray-100 rounded-full">
                    {product.brand}
                  </span>
                )}
              </div>

              <h1 className="text-5xl font-black text-gray-900 leading-tight tracking-tighter">
                {product.name}
              </h1>

              <div className="flex items-center space-x-4">
                <div className="flex items-center text-yellow-400">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className={`w-4 h-4 ${i < Math.floor(product.rating || 5) ? 'fill-current' : 'text-gray-200'}`} />
                  ))}
                </div>
                <span className="text-sm font-bold text-gray-400">({product.review_count || 0} Professional Reviews)</span>
              </div>

              <div className="text-5xl font-black text-primary tracking-tighter">
                {formatPrice(displayPrice || product.price)}
              </div>

              <p className="text-gray-500 leading-relaxed text-lg">
                {product.description}
              </p>
            </div>

            {/* Variant Selection */}
            {product.variants && product.variants.length > 0 && (
              <VariantSelector
                variants={product.variants}
                currentVariant={selectedVariant}
                onVariantChange={handleVariantChange}
              />
            )}

            {/* Selection & Actions */}
            <div className="py-8 space-y-8">
              <div className="flex flex-col sm:flex-row sm:items-center gap-8">
                <div className="space-y-3">
                  <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Quantity</label>
                  <div className="flex items-center bg-gray-50 rounded-xl border border-gray-100 p-1 w-fit">
                    <button
                      onClick={() => setQuantity(Math.max(1, quantity - 1))}
                      className="p-3 text-gray-600 hover:text-primary transition-colors"
                    >
                      <Minus className="w-4 h-4" />
                    </button>
                    <span className="w-12 text-center font-black text-gray-900">{quantity}</span>
                    <button
                      onClick={() => setQuantity(Math.min(product.stock || 99, quantity + 1))}
                      className="p-3 text-gray-600 hover:text-primary transition-colors"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="flex-1 space-y-3 pt-6 sm:pt-0">
                  <div className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Availability</div>
                  <div className={`text-sm font-bold ${product.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {product.stock > 0 ? `In Stock (${product.stock} units available)` : 'Currently Out of Stock'}
                  </div>
                </div>
              </div>

              <button
                onClick={handleAddToCart}
                disabled={product.stock === 0}
                className="w-full bg-gray-900 text-white py-6 rounded-2xl text-lg font-black uppercase tracking-widest hover:bg-primary transition-all duration-300 disabled:bg-gray-200 shadow-2xl shadow-gray-900/10 flex items-center justify-center space-x-3 group"
              >
                <ShoppingCart className="w-6 h-6 group-hover:scale-110 transition-transform" />
                <span>{product.stock === 0 ? 'Out of Stock' : 'Add to Shopping Cart'}</span>
              </button>
            </div>

            {/* Features Info */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-8 border-t border-gray-100">
              <div className="flex items-center space-x-3">
                <div className="bg-gray-50 p-2 rounded-lg text-primary"><ShieldCheck className="w-5 h-5" /></div>
                <div className="text-[10px] font-bold uppercase tracking-tight text-gray-900">1 Year Warranty</div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="bg-gray-50 p-2 rounded-lg text-primary"><Truck className="w-5 h-5" /></div>
                <div className="text-[10px] font-bold uppercase tracking-tight text-gray-900">Free Delivery</div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="bg-gray-50 p-2 rounded-lg text-primary"><RefreshCcw className="w-5 h-5" /></div>
                <div className="text-[10px] font-bold uppercase tracking-tight text-gray-900">30 Day Returns</div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-24 space-y-8">
          <div className="flex flex-wrap gap-3 border-b border-gray-100">
            <button
              type="button"
              onClick={() => setActiveTab('description')}
              className={`px-5 py-4 text-sm font-black uppercase tracking-widest transition-colors ${
                activeTab === 'description'
                  ? 'border-b-2 border-primary text-primary'
                  : 'text-gray-400 hover:text-gray-900'
              }`}
            >
              Mô tả sản phẩm
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('specifications')}
              className={`px-5 py-4 text-sm font-black uppercase tracking-widest transition-colors ${
                activeTab === 'specifications'
                  ? 'border-b-2 border-primary text-primary'
                  : 'text-gray-400 hover:text-gray-900'
              }`}
            >
              Thông số kỹ thuật
            </button>
          </div>

          {activeTab === 'description' ? (
            <div className="rounded-2xl bg-gray-50 p-8 text-gray-600 leading-8">
              {product.description || 'Chưa có mô tả chi tiết cho sản phẩm này.'}
            </div>
          ) : (
            <ProductSpecifications specifications={specifications} />
          )}
        </div>

        {/* Reviews Section */}
        <div className="mt-24 space-y-12">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-primary">
              <div className="h-1 w-8 bg-primary rounded-full" />
              <span className="text-xs font-bold uppercase tracking-widest">Customer Feedback</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-16">
            {/* Review Form */}
            <div className="lg:col-span-1 space-y-8">
              <div className="bg-gray-50 rounded-3xl p-8 space-y-6">
                <h3 className="text-2xl font-black text-gray-900 tracking-tight">Write a Review</h3>
                {isAuthenticated ? (
                  <form onSubmit={handleReviewSubmit} className="space-y-4">
                    <div className="space-y-2">
                      <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Rating</label>
                      <StarRating
                        rating={reviewForm.rating}
                        interactive={true}
                        onRatingChange={(r) => setReviewForm({ ...reviewForm, rating: r })}
                        size={6}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Comment</label>
                      <textarea
                        value={reviewForm.comment}
                        onChange={(e) => setReviewForm({ ...reviewForm, comment: e.target.value })}
                        placeholder="Share your experience with this product..."
                        rows={4}
                        className="w-full bg-white border border-gray-100 px-4 py-4 rounded-2xl text-sm font-semibold text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={submittingReview}
                      className="w-full bg-gray-900 text-white py-4 rounded-xl font-black uppercase tracking-widest text-[10px] hover:bg-primary transition-all disabled:bg-gray-200"
                    >
                      {submittingReview ? 'Submitting...' : 'Post Review'}
                    </button>
                  </form>
                ) : (
                  <div className="space-y-4">
                    <p className="text-sm text-gray-500 font-medium">Please sign in to share your thoughts about this product.</p>
                    <button
                      onClick={() => navigate('/login')}
                      className="w-full bg-primary text-white py-4 rounded-xl font-black uppercase tracking-widest text-[10px] hover:bg-gray-900 transition-all"
                    >
                      Sign In
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Reviews List */}
            <div className="lg:col-span-2 space-y-8">
              {reviews.length > 0 ? (
                <div className="space-y-8">
                  {reviews.map((review) => (
                    <div key={review.id} className="border-b border-gray-100 pb-8 space-y-4 group">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center text-primary font-black text-xs uppercase">
                            {review.user?.full_name?.charAt(0) || 'U'}
                          </div>
                          <div>
                            <p className="text-sm font-black text-gray-900">{review.user?.full_name || 'Anonymous User'}</p>
                            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                              {new Date(review.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <StarRating rating={review.rating} size={3} />
                      </div>
                      <p className="text-gray-600 leading-relaxed text-sm font-medium">
                        {review.comment}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-gray-50 rounded-3xl p-12 text-center border-2 border-dashed border-gray-200">
                  <p className="text-gray-400 font-bold uppercase tracking-widest text-xs">No reviews yet. Be the first to share your experience!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;
