import { useEffect, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useCart } from './useCart';
import { useAuth } from './useAuth';
import { productService } from '../services/productService';

const buildVariantSearchParams = (variant) => {
  const params = new URLSearchParams();

  if (variant.color_code) {
    params.set('color', variant.color_code);
  }

  if (variant.version_name) {
    params.set('version', variant.version_name);
  } else if (variant.ram || variant.storage) {
    params.set('version', `${variant.ram}|${variant.storage}`);
  }

  return params;
};

export const useProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { addToCart } = useCart();
  const { isAuthenticated } = useAuth();

  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [specifications, setSpecifications] = useState({});
  const [activeTab, setActiveTab] = useState('specifications');
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: '' });
  const [submittingReview, setSubmittingReview] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [displayPrice, setDisplayPrice] = useState(null);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await Promise.allSettled([loadProduct(), loadReviews(), loadSpecifications()]);
      window.scrollTo(0, 0);
      setLoading(false);
    };

    if (id) {
      init();
    }
  }, [id]);

  const applyVariantParams = (variant) => {
    const newParams = buildVariantSearchParams(variant);
    setSearchParams(newParams, { replace: true });
  };

  const loadProduct = async () => {
    try {
      const data = await productService.getProductById(id);
      if (!data) {
        navigate('/404', { replace: true });
        return;
      }

      setProduct(data);
      setDisplayPrice(data.price);

      if (data.variants && data.variants.length > 0) {
        const colorParam = searchParams.get('color');
        const versionParam = searchParams.get('version');
        let variant = null;

        if (colorParam || versionParam) {
          variant = data.variants.find((v) => {
            const matchColor = !colorParam || v.color_code === colorParam;
            const versionStr = `${v.ram}|${v.storage}`;
            const matchVersion = !versionParam || v.version_name === versionParam || versionStr === versionParam;
            return matchColor && matchVersion;
          });
        }

        variant = variant || data.variants.find((v) => v.is_default) || data.variants[0];
        setSelectedVariant(variant);
        setDisplayPrice(variant.price || data.price);
        applyVariantParams(variant);
      }
    } catch (error) {
      console.error('Error loading product:', error);
      if (error.response?.status === 404) {
        navigate('/404', { replace: true });
      }
    }
  };

  const loadReviews = async () => {
    try {
      const data = await productService.getProductReviews(id);
      setReviews(data);
    } catch (error) {
      console.error('Error loading reviews:', error);
    }
  };

  const loadSpecifications = async () => {
    try {
      const data = await productService.getProductSpecifications(id);
      setSpecifications(data);
    } catch (error) {
      console.error('Error loading specifications:', error);
      setSpecifications({});
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();

    if (!isAuthenticated) {
      alert('Please sign in to leave a review');
      return;
    }

    setSubmittingReview(true);
    try {
      await productService.addProductReview(id, reviewForm);
      setReviewForm({ rating: 5, comment: '' });
      await loadReviews();
      await loadProduct();
      alert('Review submitted successfully!');
    } catch (error) {
      alert(error.message || 'Error submitting review');
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      alert('Please sign in to add items to cart');
      navigate('/login');
      return;
    }

    try {
      await addToCart(product.id, quantity, selectedVariant?.id);
      navigate('/cart');
    } catch (error) {
      alert(error.message);
    }
  };

  const handleVariantChange = (variant) => {
    setSelectedVariant(variant);
    setDisplayPrice(variant.price || product.price);
    setQuantity(1);
    applyVariantParams(variant);
  };

  return {
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
    setDisplayPrice,
    handleReviewSubmit,
    handleAddToCart,
    handleVariantChange,
    setProduct,
    setSpecifications,
    setReviews,
    isAuthenticated,
  };
};
