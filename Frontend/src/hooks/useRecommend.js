import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { productService } from '../services/productService';

export const useRecommend = (productId = null) => {
  const [recommendations, setRecommendations] = useState([]);
  const [strategy, setStrategy] = useState('popular');
  const [loading, setLoading] = useState(true);
  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        let data;
        if (productId) {
          data = await productService.getSimilarProducts(productId);
        } else {
          data = await productService.getRecommendations(8);
        }
        if (!cancelled) {
          setRecommendations(data.items || []);
          setStrategy(data.strategy || 'popular');
        }
      } catch (err) {
        console.error('Recommendation error:', err);
        if (!cancelled) setRecommendations([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, [user?.id, productId]);

  return { recommendations, strategy, loading };
};
