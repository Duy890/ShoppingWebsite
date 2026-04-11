import { useEffect, useState } from 'react';
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

const Home = () => {
  const navigate = useNavigate();
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    {
      title: "Elevate Your Tech Gadget Game",
      subtitle: "Discover the next generation of smartphones and accessories.",
      image: "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=1200&auto=format&fit=crop",
      cta: "Shop Smartphones",
      category: "Smartphones"
    },
    {
      title: "Powerful Performance for Professionals",
      subtitle: "The latest laptops with cutting-edge M3 and Intel processors.",
      image: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=1200&auto=format&fit=crop",
      cta: "Browse Laptops",
      category: "Laptops"
    },
    {
      title: "Pure Sound. Zero Noise.",
      subtitle: "Experience high-fidelity audio with active noise cancellation.",
      image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1200&auto=format&fit=crop",
      cta: "Explore Audio",
      category: "Audio"
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
      const products = await productService.getProducts({ featured: true });
      setFeaturedProducts(products.slice(0, 8)); // 4x2 grid
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
              alt={slide.title} 
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 z-20 flex items-center">
              <div className="max-w-7xl mx-auto px-4 w-full">
                <div className="max-w-xl text-white space-y-6">
                  <span className="inline-block bg-primary px-4 py-1 rounded text-xs font-bold uppercase tracking-widest animate-fade-in">
                    New Arrivals 2024
                  </span>
                  <h1 className="text-5xl md:text-7xl font-black leading-tight tracking-tighter">
                    {slide.title}
                  </h1>
                  <p className="text-lg text-gray-300 max-w-md">
                    {slide.subtitle}
                  </p>
                  <div className="pt-4">
                    <button 
                      onClick={() => navigate('/products')}
                      className="bg-primary text-white px-8 py-4 rounded-lg font-bold uppercase tracking-widest hover:bg-white hover:text-primary transition-all duration-300 shadow-2xl shadow-primary/20 flex items-center space-x-2 group"
                    >
                      <span>{slide.cta}</span>
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
              <img key={i} src={brand.url} alt={brand.name} className="h-8 w-auto object-contain" />
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
                <h3 className="text-3xl font-black text-gray-900 leading-tight">Fastest Shipping in the Industry</h3>
                <p className="text-gray-600">Get your electronics delivered same-day in major metropolitan areas.</p>
                <button 
                  onClick={() => navigate('/products')}
                  className="bg-gray-900 text-white px-6 py-3 rounded-lg font-bold text-xs uppercase tracking-widest hover:bg-primary transition-colors inline-block"
                >
                  Learn More
                </button>
              </div>
              <Truck className="absolute -right-12 -bottom-12 w-64 h-64 text-gray-200/50 -rotate-12 group-hover:rotate-0 transition-transform duration-700" />
            </div>

            {/* Stacked Banners */}
            <div className="flex flex-col gap-8">
              <div className="flex-1 bg-primary text-white rounded-2xl p-8 flex items-center justify-between relative overflow-hidden group">
                <div className="relative z-10">
                  <span className="text-xs font-bold uppercase tracking-widest opacity-80">Season Sale</span>
                  <h3 className="text-2xl font-black mt-2">Black Friday<br/>Clearance</h3>
                  <button onClick={() => navigate('/products')} className="mt-4 text-xs font-bold underline underline-offset-4 hover:opacity-80 transition-opacity uppercase tracking-widest">Shop Now</button>
                </div>
                <Tag className="w-32 h-32 opacity-10 absolute right-4 top-1/2 -translate-y-1/2 rotate-12 group-hover:rotate-0 transition-transform duration-500" />
              </div>
              <div className="flex-1 bg-gray-900 text-white rounded-2xl p-8 flex items-center justify-between relative overflow-hidden group">
                <div className="relative z-10">
                  <span className="text-xs font-bold uppercase tracking-widest text-primary">Limited Offer</span>
                  <h3 className="text-2xl font-black mt-2">First Purchase<br/>20% Discount</h3>
                  <button onClick={() => navigate('/products')} className="mt-4 text-xs font-bold underline underline-offset-4 hover:opacity-80 transition-opacity uppercase tracking-widest">Claim Coupon</button>
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
                <span className="text-xs font-bold uppercase tracking-widest">Must Have</span>
              </div>
              <h2 className="text-4xl font-black text-gray-900 tracking-tight">New Arrivals</h2>
            </div>
            <Link
              to="/products"
              className="group flex items-center space-x-2 font-bold text-gray-400 hover:text-primary transition-colors uppercase tracking-widest text-xs"
            >
              <span>Explore All Products</span>
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
              <p className="text-gray-400 font-medium">No new products available at the moment.</p>
            </div>
          )}
        </div>
      </section>

      {/* Value Proposition Section */}
      <section className="py-20 px-4 border-t border-gray-100">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-12">
            <div className="space-y-4">
              <div className="w-12 h-12 bg-orange-50 text-primary flex items-center justify-center rounded-xl">
                <Truck className="w-6 h-6" />
              </div>
              <h4 className="font-black text-gray-900 uppercase tracking-tight">Free Shipping</h4>
              <p className="text-sm text-gray-500 leading-relaxed">On all orders over 5,000,000₫. Fast and secure delivery guaranteed.</p>
            </div>
            <div className="space-y-4">
              <div className="w-12 h-12 bg-blue-50 text-blue-600 flex items-center justify-center rounded-xl">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h4 className="font-black text-gray-900 uppercase tracking-tight">Secure Payment</h4>
              <p className="text-sm text-gray-500 leading-relaxed">Your data is protected with military-grade SSL encryption technology.</p>
            </div>
            <div className="space-y-4">
              <div className="w-12 h-12 bg-green-50 text-green-600 flex items-center justify-center rounded-xl">
                <Clock className="w-6 h-6" />
              </div>
              <h4 className="font-black text-gray-900 uppercase tracking-tight">24/7 Support</h4>
              <p className="text-sm text-gray-500 leading-relaxed">Round-the-clock assistance for all your inquiries and concerns.</p>
            </div>
            <div className="space-y-4">
              <div className="w-12 h-12 bg-purple-50 text-purple-600 flex items-center justify-center rounded-xl">
                <Zap className="w-6 h-6" />
              </div>
              <h4 className="font-black text-gray-900 uppercase tracking-tight">Authentic Only</h4>
              <p className="text-sm text-gray-500 leading-relaxed">We source directly from manufacturers to ensure 100% authenticity.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
