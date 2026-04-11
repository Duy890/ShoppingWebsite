import { Link, useNavigate } from 'react-router-dom';
import { ShoppingCart, Star } from 'lucide-react';
import { formatPrice } from '../utils/formatPrice';
import { useCart } from '../hooks/useCart';
import { useAuth } from '../hooks/useAuth';

const ProductCard = ({ product }) => {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { isAuthenticated } = useAuth();

  const handleAddToCart = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      alert('Please sign in to add items to cart');
      navigate('/login');
      return;
    }
    try {
      await addToCart(product.id, 1);
      // Redirect to cart for the "Happy Path" prototype experience
      navigate('/cart');
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <div className="group bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 overflow-hidden flex flex-col h-full">
      {/* Image Container */}
      <Link to={`/product/${product.id}`} className="relative aspect-[4/3] overflow-hidden bg-gray-50">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-full object-contain p-4 group-hover:scale-110 transition-transform duration-500"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-300 italic text-sm">
            No Image
          </div>
        )}
        
        {/* Category Tag */}
        {product.category && (
          <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm text-primary text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-widest shadow-sm">
            {product.category.name}
          </div>
        )}

        {/* Stock Status Overlay */}
        {product.stock === 0 && (
          <div className="absolute inset-0 bg-white/60 backdrop-blur-[2px] flex items-center justify-center">
            <span className="bg-gray-900 text-white text-xs font-bold px-4 py-2 rounded-lg uppercase tracking-widest">
              Out of Stock
            </span>
          </div>
        )}
      </Link>

      {/* Content */}
      <div className="p-5 flex flex-col flex-1">
        {/* Rating & Brand */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-1 text-yellow-400">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className={`w-3 h-3 ${i < Math.floor(product.rating || 5) ? 'fill-current' : 'text-gray-200'}`} />
            ))}
            <span className="text-gray-400 text-[10px] ml-1">({product.review_count || 0})</span>
          </div>
          {product.brand && (
            <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">{product.brand}</span>
          )}
        </div>

        {/* Name */}
        <Link to={`/product/${product.id}`} className="mb-3 flex-1">
          <h3 className="text-sm font-bold text-gray-800 line-clamp-2 hover:text-primary transition-colors">
            {product.name}
          </h3>
        </Link>

        {/* Price & Action */}
        <div className="flex items-center justify-between mt-auto pt-4 border-t border-gray-50">
          <div className="flex flex-col">
            <span className="text-lg font-black text-primary">
              {formatPrice(product.price)}
            </span>
          </div>
          
          <button
            onClick={handleAddToCart}
            disabled={product.stock === 0}
            className="bg-gray-900 text-white p-2.5 rounded-lg hover:bg-primary transition-all duration-300 disabled:bg-gray-200 disabled:cursor-not-allowed group-hover:shadow-lg group-hover:shadow-primary/20"
            title="Add to Cart"
          >
            <ShoppingCart className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
