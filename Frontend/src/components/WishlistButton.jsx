import { useState } from 'react';
import { Heart } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { productService } from '../services/productService';

const WishlistButton = ({ productId, className = '' }) => {
  const { isAuthenticated, user } = useAuth();
  const [isSaved, setIsSaved] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleWishlist = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      alert('Please sign in to save items');
      return;
    }

    setLoading(true);
    try {
      if (isSaved) {
        await productService.removeFromWishlist(productId);
        setIsSaved(false);
      } else {
        await productService.addToWishlist(productId);
        setIsSaved(true);
      }
    } catch (error) {
      console.error('Error updating wishlist:', error);
      alert('Error updating wishlist');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleWishlist}
      disabled={loading}
      className={`p-2 rounded-lg border transition ${
        isSaved
          ? 'bg-red-50 border-red-200 text-red-600 hover:bg-red-100'
          : 'border-gray-200 text-gray-600 hover:border-red-200 hover:text-red-600'
      } ${className}`}
      title={isSaved ? 'Remove from wishlist' : 'Add to wishlist'}
    >
      <Heart
        className={`w-5 h-5 transition ${isSaved ? 'fill-current' : ''}`}
      />
    </button>
  );
};

export default WishlistButton;
