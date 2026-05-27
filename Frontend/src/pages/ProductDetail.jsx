import { useState } from 'react';
import { useProductDetail } from '../hooks/useProductDetail';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
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
import { useRecommend } from '../hooks/useRecommend';
import { formatPrice } from '../utils/formatPrice';
import StarRating from '../components/StarRating';
import ProductSpecifications from '../components/ProductSpecifications';
import VariantSelector from '../components/VariantSelector';
import ProductCard from '../components/ProductCard';

const ProductDetail = () => {
  const { t } = useTranslation();
  const { id } = useParams();
  const { recommendations: similarProducts, loading: similarLoading } = useRecommend(id);
  const {
    navigate,
    product,
    reviews,
    specifications,
    activeTab,
    setActiveTab,
    loading,
    quantity,
    setQuantity,
    reviewForm,
    setReviewForm,
    submittingReview,
    selectedVariant,
    setSelectedVariant,
    displayPrice,
    displayDescription,
    handleReviewSubmit,
    handleAddToCart,
    handleVariantChange,
    isAuthenticated,
  } = useProductDetail();

  const [selectedImageIndex, setSelectedImageIndex] = useState(0);

  const allImages = product?.product_images?.length
    ? product.product_images
    : product?.image_url
    ? [{ url: product.image_url, alt_text: product.name }]
    : [];

  const mainImage = allImages[selectedImageIndex] || allImages[0] || null;

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
          <p className="text-2xl font-black text-gray-900">{t('product_detail.product_not_found')}</p>
          <button
            onClick={() => navigate('/products')}
            className="bg-primary text-white px-8 py-3 rounded-xl font-bold uppercase tracking-widest text-xs"
          >
            {t('product_detail.back_to_catalog')}
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
          <span>{t('product_detail.back_to_products')}</span>
        </button>
      </div>

      <div className="max-w-7xl mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
          
          {/* Product Image Gallery */}
          <div className="space-y-6">
            <div className="aspect-square bg-gray-50 rounded-3xl overflow-hidden border border-gray-100 flex items-center justify-center p-12">
              {mainImage ? (
                <img
                  src={mainImage.url}
                  alt={mainImage.alt_text || product.name}
                  className="w-full h-full object-contain hover:scale-105 transition-transform duration-700"
                />
              ) : (
                <div className="text-gray-300 italic">{t('product_detail.no_image')}</div>
              )}
            </div>
            
            {allImages.length > 1 && (
              <div className="grid grid-cols-4 gap-4">
                {allImages.map((img, i) => (
                  <div
                    key={i}
                    onClick={() => setSelectedImageIndex(i)}
                    className={`aspect-square bg-gray-50 rounded-xl border cursor-pointer transition-colors p-2 ${
                      i === selectedImageIndex ? 'border-primary ring-1 ring-primary' : 'border-gray-100 hover:border-primary'
                    }`}
                  >
                    <img src={img.url} alt={img.alt_text || ''} className="w-full h-full object-contain" />
                  </div>
                ))}
              </div>
            )}
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
                <span className="text-sm font-bold text-gray-400">({product.review_count || 0} {t('product_detail.reviews_count')})</span>
              </div>

              <div className="text-5xl font-black text-primary tracking-tighter">
                {formatPrice(displayPrice || product.price)}
              </div>

              <p className="text-gray-500 leading-relaxed text-lg whitespace-pre-line">
                {displayDescription || product.description}
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
                  <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{t('product_detail.quantity')}</label>
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
                  <div className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{t('product_detail.availability')}</div>
                  <div className={`text-sm font-bold ${product.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {product.stock > 0
                      ? `${t('product_detail.in_stock')} (${product.stock} ${t('product_detail.units_available')})`
                      : t('product_detail.out_of_stock')}
                  </div>
                </div>
              </div>

              <button
                onClick={handleAddToCart}
                disabled={product.stock === 0}
                className="w-full bg-gray-900 text-white py-6 rounded-2xl text-lg font-black uppercase tracking-widest hover:bg-primary transition-all duration-300 disabled:bg-gray-200 shadow-2xl shadow-gray-900/10 flex items-center justify-center space-x-3 group"
              >
                <ShoppingCart className="w-6 h-6 group-hover:scale-110 transition-transform" />
                <span>{product.stock === 0 ? t('product_detail.out_of_stock') : t('product_detail.add_to_cart')}</span>
              </button>
            </div>

            {/* Features Info */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-8 border-t border-gray-100">
              <div className="flex items-center space-x-3">
                <div className="bg-gray-50 p-2 rounded-lg text-primary"><ShieldCheck className="w-5 h-5" /></div>
                <div className="text-[10px] font-bold uppercase tracking-tight text-gray-900">{t('product_detail.warranty')}</div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="bg-gray-50 p-2 rounded-lg text-primary"><Truck className="w-5 h-5" /></div>
                <div className="text-[10px] font-bold uppercase tracking-tight text-gray-900">{t('product_detail.free_delivery')}</div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="bg-gray-50 p-2 rounded-lg text-primary"><RefreshCcw className="w-5 h-5" /></div>
                <div className="text-[10px] font-bold uppercase tracking-tight text-gray-900">{t('product_detail.returns_policy')}</div>
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
              {t('product_detail.description_tab')}
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
              {t('product_detail.specifications')}
            </button>
          </div>

          {activeTab === 'description' ? (
            <div className="rounded-2xl bg-gray-50 p-8 text-gray-600 leading-8 whitespace-pre-line">
              {displayDescription || product.description || t('product_detail.description_missing')}
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
              <span className="text-xs font-bold uppercase tracking-widest">{t('product_detail.customer_feedback')}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-16">
            {/* Review Form */}
            <div className="lg:col-span-1 space-y-8">
              <div className="bg-gray-50 rounded-3xl p-8 space-y-6">
                <h3 className="text-2xl font-black text-gray-900 tracking-tight">{t('product_detail.write_review')}</h3>
                {isAuthenticated ? (
                  <form onSubmit={handleReviewSubmit} className="space-y-4">
                    <div className="space-y-2">
                      <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{t('product_detail.rating')}</label>
                      <StarRating
                        rating={reviewForm.rating}
                        interactive={true}
                        onRatingChange={(r) => setReviewForm({ ...reviewForm, rating: r })}
                        size={6}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{t('product_detail.comment')}</label>
                      <textarea
                        value={reviewForm.comment}
                        onChange={(e) => setReviewForm({ ...reviewForm, comment: e.target.value })}
                        placeholder={t('product_detail.comment_placeholder')}
                        rows={4}
                        className="w-full bg-white border border-gray-100 px-4 py-4 rounded-2xl text-sm font-semibold text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={submittingReview}
                      className="w-full bg-gray-900 text-white py-4 rounded-xl font-black uppercase tracking-widest text-[10px] hover:bg-primary transition-all disabled:bg-gray-200"
                    >
                      {submittingReview ? t('product_detail.submitting') : t('product_detail.post_review')}
                    </button>
                  </form>
                ) : (
                  <div className="space-y-4">
                    <p className="text-sm text-gray-500 font-medium">{t('product_detail.sign_in_review')}</p>
                    <button
                      onClick={() => navigate('/login')}
                      className="w-full bg-primary text-white py-4 rounded-xl font-black uppercase tracking-widest text-[10px] hover:bg-gray-900 transition-all"
                    >
                      {t('product_detail.sign_in')}
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
                            <p className="text-sm font-black text-gray-900">{review.user?.full_name || t('product_detail.anonymous_user')}</p>
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
                  <p className="text-gray-400 font-bold uppercase tracking-widest text-xs">{t('product_detail.no_reviews')}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {(similarLoading || similarProducts.length > 0) && (
        <section className="mt-16 max-w-7xl mx-auto px-4">
          <h2 className="text-2xl font-black text-gray-900 mb-6">
            Similar Products
          </h2>
          {similarLoading ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-gray-100 rounded-xl aspect-[3/4] animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {similarProducts.map(p => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
};

export default ProductDetail;
