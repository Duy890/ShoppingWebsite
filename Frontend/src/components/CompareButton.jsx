import { useState } from 'react';
import { Scale } from 'lucide-react';
import { productService } from '../services/productService';

const CompareButton = ({ productId, compareListId, onCompare, className = '' }) => {
  const [isInCompare, setIsInCompare] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleCompare = async (e) => {
    e.preventDefault();

    if (!compareListId) {
      alert('Please create a compare list first');
      return;
    }

    setLoading(true);
    try {
      if (isInCompare) {
        await productService.removeFromCompareList(compareListId, productId);
        setIsInCompare(false);
      } else {
        await productService.addToCompareList(compareListId, productId);
        setIsInCompare(true);
      }
      if (onCompare) onCompare();
    } catch (error) {
      console.error('Error updating compare list:', error);
      alert('Error updating compare list');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleCompare}
      disabled={loading}
      className={`p-2 rounded-lg border transition ${
        isInCompare
          ? 'bg-blue-50 border-blue-200 text-blue-600 hover:bg-blue-100'
          : 'border-gray-200 text-gray-600 hover:border-blue-200 hover:text-blue-600'
      } ${className}`}
      title={isInCompare ? 'Remove from compare' : 'Add to compare'}
    >
      <Scale
        className={`w-5 h-5 transition ${isInCompare ? 'fill-current' : ''}`}
      />
    </button>
  );
};

export default CompareButton;
