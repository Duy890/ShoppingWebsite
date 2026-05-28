import { useEffect, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useCart } from './useCart';
import { useAuth } from './useAuth';
import { formatStorage } from '../utils/formatStorage';
import { productService } from '../services/productService';

const buildVariantSearchParams = (variant) => {
  const params = new URLSearchParams();

  if (variant.color_code) {
    params.set('color', variant.color_code);
  }

  if (variant.version_name) {
    params.set('version', variant.version_name);
  } else if (variant.ram || variant.storage) {
    params.set('version', `${variant.ram}|${formatStorage(variant.storage)}`);
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
  const [baseSpecifications, setBaseSpecifications] = useState({});
  const [activeTab, setActiveTab] = useState('specifications');
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: '' });
  const [submittingReview, setSubmittingReview] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [displayPrice, setDisplayPrice] = useState(null);
  const [displayDescription, setDisplayDescription] = useState('');

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

  // Sync specs & description whenever selected variant or base specs change
  useEffect(() => {
    if (selectedVariant && Object.keys(baseSpecifications).length > 0) {
      setSpecifications(mergeVariantIntoSpecs(baseSpecifications, selectedVariant));
    }
    setDisplayDescription(buildDisplayDescription(product, selectedVariant));
  }, [selectedVariant, baseSpecifications, product]);

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
            const versionStrFormatted = `${v.ram}|${formatStorage(v.storage)}`;
            const matchVersion = !versionParam || v.version_name === versionParam || versionStr === versionParam || versionStrFormatted === versionParam;
            return matchColor && matchVersion;
          });
        }

        variant = variant || data.variants.find((v) => v.is_default) || data.variants[0];
        setSelectedVariant(variant);
        setDisplayPrice(variant.price || data.price);
        setDisplayDescription(buildDisplayDescription(data, variant));
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
      setBaseSpecifications(data);
      setSpecifications(data);
    } catch (error) {
      console.error('Error loading specifications:', error);
      setBaseSpecifications({});
      setSpecifications({});
    }
  };

  // Map variant fields to common spec key patterns (case-insensitive)
  const RAM_KEYS = ['ram', 'bộ nhớ ram', 'memory', 'bộ nhớ trong'];
  const STORAGE_KEYS = ['storage', 'ổ cứng', 'ssd', 'hdd', 'lưu trữ', 'bộ nhớ lưu trữ', 'ổ lưu trữ'];

  const buildDisplayDescription = (product, variant) => {
    if (!product) return '';
    let desc = product.description || '';
    if (variant && (variant.ram || variant.storage)) {
      const parts = [];
      if (variant.ram) parts.push(`${variant.ram} RAM`);
      if (variant.storage) parts.push(formatStorage(variant.storage));
      if (parts.length > 0) {
        desc += `\n\nPhien ban nay: ${parts.join(' — ')}.`;
      }
    }
    return desc;
  };

  const mergeVariantIntoSpecs = (baseSpecs, variant) => {
    if (!variant || (!variant.ram && !variant.storage)) return baseSpecs;

    // Deep clone
    const merged = {};
    for (const [groupName, specs] of Object.entries(baseSpecs)) {
      merged[groupName] = specs.map((spec) => {
        const keyLower = (spec.key || spec.spec_key || '').toLowerCase();
        if (variant.ram && RAM_KEYS.some((k) => keyLower.includes(k))) {
          return { ...spec, value: variant.ram, _variantHighlight: true };
        }
        if (variant.storage && STORAGE_KEYS.some((k) => keyLower.includes(k))) {
          return { ...spec, value: formatStorage(variant.storage), _variantHighlight: true };
        }
        return spec;
      });
    }
    return merged;
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
    // Sync specifications with selected variant values
    setSpecifications(mergeVariantIntoSpecs(baseSpecifications, variant));
  };

  return {
    navigate,
    product,
    reviews,
    specifications,
    baseSpecifications,
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
    displayDescription,
    handleReviewSubmit,
    handleAddToCart,
    handleVariantChange,
    setProduct,
    setSpecifications,
    setReviews,
    isAuthenticated,
  };
};