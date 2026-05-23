import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import { 
  ArrowRight, 
  Truck, 
  Clock, 
  Tag, 
  ChevronLeft, 
  ChevronRight,
  ShieldCheck,
  Zap
} from 'lucide-react';
import ProductCard from '../components/ProductCard';
import { productService } from '../services/productService';
import { useRecommend } from '../hooks/useRecommend';

const Home = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentSlide, setCurrentSlide] = useState(0);
  const { recommendations, loading: recommendationsLoading } = useRecommend();

  const slides = [
    {
      titleKey: 'home.hero.slide1_title',
      subtitleKey: 'home.hero.slide1_subtitle',
      image: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=1200&auto=format&fit=crop',
      ctaKey: 'home.hero.cta_smartphones',
      category: 'Smartphones'
    },
    {
      titleKey: 'home.hero.slide2_title',
      subtitleKey: 'home.hero.slide2_subtitle',
      image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=1200&auto=format&fit=crop',
      ctaKey: 'home.hero.cta_laptops',
      category: 'Laptops'
    },
    {
      titleKey: 'home.hero.slide3_title',
      subtitleKey: 'home.hero.slide3_subtitle',
      image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1200&auto=format&fit=crop',
      ctaKey: 'home.hero.cta_audio',
      category: 'Audio'
    }
  ];

  useEffect(() => {
    loadFeaturedProducts();
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  const loadFeaturedProducts = async () => {
    try {
      const response = await productService.getProducts({ featured: true, limit: 8 });
      setFeaturedProducts(response.items || []);
    } catch (error) {
      console.error('Error loading featured products:', error);
    } finally {
      setLoading(false);
    }
  };

  const nextSlide = () => setCurrentSlide((prev) => (prev + 1) % slides.length);
  const prevSlide = () => setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);

  const brandLogos = [
    { name: "Samsung", url: "https://upload.wikimedia.org/wikipedia/commons/2/24/Samsung_Logo.svg" },
    { name: "Apple", url: "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg" },
    { name: "Amazon", url: "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" },
    { name: "Sony", url: "https://upload.wikimedia.org/wikipedia/commons/c/ca/Sony_logo.svg" },
    { name: "Bose", url: "https://upload.wikimedia.org/wikipedia/commons/2/2a/Bose_logo.svg" },
    { name: "Dell", url: "https://upload.wikimedia.org/wikipedia/commons/4/48/Dell_Logo.svg" }
  ];

  const handleBrandClick = (brandName) => {
    navigate(`/products?brand=${encodeURIComponent(brandName)}`);
  };

  const handleSlideClick = (category) => {
    navigate(`/products?category=${encodeURIComponent(category)}`);
  };

  return (
    <div className="min-h-screen bg-white">
      
      {/* Hero Section Carousel */}
      <section className="relative h-[600px] bg-gray-900 overflow-hidden">
        {slides.map((slide, index) => (
          <div 
            key={index}
            className={`absolute inset-0 transition-opacity duration-1000 ease-in-out ${index === currentSlide ? 'opacity-100' : 'opacity-0'}`}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-black/80 to-transparent z-10" />
            <img 
              src={slide.image} 
              alt={t(slide.titleKey)} 
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 z-20 flex items-center">
              <div className="max-w-7xl mx-auto px-4 w-full">
                <div className="max-w-xl text-white space-y-6">
                  <span className="inline-block bg-primary px-4 py-1 rounded text-xs font-bold uppercase tracking-widest animate-fade-in">
                    {t('home.hero.new_arrivals_badge')}
                  </span>
                  <h1 className="text-5xl md:text-7xl font-black leading-tight tracking-tighter">
                    {t(slide.titleKey)}
                  </h1>
                  <p className="text-lg text-gray-300 max-w-md">
                    {t(slide.subtitleKey)}
                  </p>
                  <div className="pt-4">
                    <button 
                      onClick={() => handleSlideClick(slide.category)}
                      className="bg-primary text-white px-8 py-4 rounded-lg font-bold uppercase tracking-widest hover:bg-white hover:text-primary transition-all duration-300 shadow-2xl shadow-primary/20 flex items-center space-x-2 group"
                    >
                      <span>{t(slide.ctaKey)}</span>
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {/* Carousel Controls */}
        <button onClick={prevSlide} className="absolute left-6 top-1/2 -translate-y-1/2 z-30 p-3 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors backdrop-blur-md">
          <ChevronLeft className="w-6 h-6" />
        </button>
        <button onClick={nextSlide} className="absolute right-6 top-1/2 -translate-y-1/2 z-30 p-3 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors backdrop-blur-md">
          <ChevronRight className="w-6 h-6" />
        </button>
      </section>

      {/* Brand Logos Bar */}
      <section className="py-12 border-b border-gray-100 bg-gray-50/50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex flex-wrap items-center justify-center gap-12 opacity-40 grayscale hover:grayscale-0 transition-all duration-500">
            {brandLogos.map((brand, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleBrandClick(brand.name)}
                className="h-8 w-auto cursor-pointer overflow-hidden rounded transition hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-primary"
                aria-label={t('home.brand_logo_aria', { brand: brand.name })}
              >
                <img src={brand.url} alt={brand.name} className="h-8 w-auto object-contain" />
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Banners Grid */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Main Banner */}
            <div className="bg-gray-100 rounded-2xl p-10 flex flex-col justify-center relative overflow-hidden group min-h-[400px]">
              <div className="relative z-10 space-y-4 max-w-sm">
                <h3 className="text-3xl font-black text-gray-900 leading-tight">{t('home.shipping_banner.title')}</h3>
                <p className="text-gray-600">{t('home.shipping_banner.subtitle')}</p>
                <button 
                  onClick={() => navigate('/products')}
                  className="bg-gray-900 text-white px-6 py-3 rounded-lg font-bold text-xs uppercase tracking-widest hover:bg-primary transition-colors inline-block"
                >
                  {t('home.shipping_banner.learn_more')}
                </button>
              </div>
              <Truck className="absolute -right-12 -bottom-12 w-64 h-64 text-gray-200/50 -rotate-12 group-hover:rotate-0 transition-transform duration-700" />
            </div>

            {/* Stacked Banners */}
            <div className="flex flex-col gap-8">
              <div className="flex-1 bg-primary text-white rounded-2xl p-8 flex items-center justify-between relative overflow-hidden group">
                <div className="relative z-10">
                  <span className="text-xs font-bold uppercase tracking-widest opacity-80">{t('home.sale_banner.season_sale')}</span>
                  <h3 className="text-2xl font-black mt-2">{t('home.sale_banner.title')}</h3>
                  <button onClick={() => navigate('/products')} className="mt-4 text-xs font-bold underline underline-offset-4 hover:opacity-80 transition-opacity uppercase tracking-widest">{t('home.sale_banner.shop_now')}</button>
                </div>
                <Tag className="w-32 h-32 opacity-10 absolute right-4 top-1/2 -translate-y-1/2 rotate-12 group-hover:rotate-0 transition-transform duration-500" />
              </div>
              <div className="flex-1 bg-gray-900 text-white rounded-2xl p-8 flex items-center justify-between relative overflow-hidden group">
                <div className="relative z-10">
                  <span className="text-xs font-bold uppercase tracking-widest text-primary">{t('home.discount_banner.limited_offer')}</span>
                  <h3 className="text-2xl font-black mt-2">{t('home.discount_banner.title')}</h3>
                  <button onClick={() => navigate('/products')} className="mt-4 text-xs font-bold underline underline-offset-4 hover:opacity-80 transition-opacity uppercase tracking-widest">{t('home.discount_banner.claim_coupon')}</button>
                </div>
                <Zap className="w-32 h-32 opacity-10 absolute right-4 top-1/2 -translate-y-1/2 -rotate-12 group-hover:rotate-0 transition-transform duration-500" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* New Products Section 4x2 */}
      <section className="py-20 px-4 bg-gray-50/30">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-primary">
                <div className="h-1 w-8 bg-primary rounded-full" />
                <span className="text-xs font-bold uppercase tracking-widest">{t('home.new_arrivals.badge')}</span>
              </div>
              <h2 className="text-4xl font-black text-gray-900 tracking-tight">{t('home.new_arrivals.title')}</h2>
            </div>
            <Link
              to="/products"
              className="group flex items-center space-x-2 font-bold text-gray-400 hover:text-primary transition-colors uppercase tracking-widest text-xs"
            >
              <span>{t('home.new_arrivals.explore_all')}</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>

          {loading ? (
            <div className="flex justify-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
          ) : featuredProducts.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
              {featuredProducts.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          ) : (
            <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-gray-200">
              <p className="text-gray-400 font-medium">{t('home.new_arrivals.no_products')}</p>
            </div>
          )}
        </div>
      </section>


      {/* You May Also Like - render section always, show skeleton while loading and fallback if empty */}
      <section className="py-20 px-4 bg-white border-t border-gray-100">
        <div className="max-w-7xl mx-auto">

          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-primary">
                <div className="h-1 w-8 bg-primary rounded-full" />
                <span className="text-xs font-bold uppercase tracking-widest">
                  {t('home.personalized_badge')}
                </span>
              </div>
              <h2 className="text-4xl font-black text-gray-900 tracking-tight">
                {t('home.personalized_title')}
              </h2>
            </div>
            <Link
              to="/products"
              className="group flex items-center space-x-2 font-bold text-gray-400 hover:text-primary transition-colors uppercase tracking-widest text-xs"
            >
              <span>{t('home.view_all_products')}</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>

          {recommendationsLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden animate-pulse">
                  <div className="aspect-[4/3] bg-gray-100" />
                  <div className="p-5 space-y-3">
                    <div className="h-3 bg-gray-100 rounded w-3/4" />
                    <div className="h-3 bg-gray-100 rounded w-1/2" />
                    <div className="h-5 bg-gray-100 rounded w-1/3 mt-4" />
                  </div>
                </div>
              ))}
            </div>
          ) : recommendations.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
              {recommendations.slice(0, 8).map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          ) : (
            featuredProducts.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                {featuredProducts.slice(0, 8).map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            ) : null
          )}

        </div>
      </section>
    </div>
  );
};

export default Home;
