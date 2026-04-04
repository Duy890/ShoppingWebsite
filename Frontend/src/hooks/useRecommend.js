import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { aiService } from '../services/aiService';

export const useRecommend = (productId = null) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    if (user) {
      loadRecommendations();
    }
  }, [user, productId]);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      const data = await aiService.getRecommendations(user?.id, productId);
      setRecommendations(data);
    } catch (error) {
      console.error('Error loading recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  return {
    recommendations,
    loading,
  };
};
