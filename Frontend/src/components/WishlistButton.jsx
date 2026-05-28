import { Heart } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useAuth } from '../hooks/useAuth';
import { useWishlist } from '../hooks/useWishlist';

const WishlistButton = ({ productId, className = '' }) => {
  const { isAuthenticated } = useAuth();
  const { isInWishlist, addToWishlist, removeFromWishlist } = useWishlist();
  const isSaved = isInWishlist(productId);

  const handleWishlist = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      toast.error('Please sign in to save items');
      return;
    }

    try {
      if (isSaved) {
        await removeFromWishlist(productId);
      } else {
        await addToWishlist(productId);
      }
    } catch (error) {
      console.error('Error updating wishlist:', error);
      toast.error('Error updating wishlist');
    }
  };

  return (
    <button
      onClick={handleWishlist}
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
