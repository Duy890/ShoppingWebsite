import { useEffect, useState } from 'react';
import { Heart } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useAuth } from '../hooks/useAuth';
import { productService } from '../services/productService';

const WishlistButton = ({ productId, className = '' }) => {
  const { isAuthenticated } = useAuth();
  const [isSaved, setIsSaved] = useState(false);
  const [loading, setLoading] = useState(false);
  const [checkingStatus, setCheckingStatus] = useState(false);

  useEffect(() => {
    if (!isAuthenticated || !productId) return;
    let cancelled = false;

    const checkStatus = async () => {
      setCheckingStatus(true);
      try {
        const ids = await productService.getWishlistIds();
        if (!cancelled) setIsSaved(ids.includes(productId));
      } catch (err) {
        console.error('Error checking wishlist status:', err);
      } finally {
        if (!cancelled) setCheckingStatus(false);
      }
    };

    checkStatus();
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, productId]);

  const handleWishlist = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      toast.error('Please sign in to save items');
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
      toast.error('Error updating wishlist');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleWishlist}
      disabled={loading || checkingStatus}
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
