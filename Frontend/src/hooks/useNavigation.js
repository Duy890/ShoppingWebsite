import { useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setNavTree, setNavLoading } from '../store/navigationSlice';
import { productService } from '../services/productService';

export const useNavigation = () => {
  const dispatch = useDispatch();
  const navTree = useSelector((state) => state.navigation.navTree);
  const navLoading = useSelector((state) => state.navigation.navLoading);
  const fetchedRef = useRef(false);

  useEffect(() => {
    if (navTree.length > 0) return;
    if (fetchedRef.current) return;
    fetchedRef.current = true;

    const loadNavTree = async () => {
      try {
        dispatch(setNavLoading(true));
        const data = await productService.getNavigationTree();
        dispatch(setNavTree(data));
      } catch (err) {
        console.error('Failed to load nav tree:', err);
      } finally {
        dispatch(setNavLoading(false));
      }
    };

    loadNavTree();
  }, [dispatch, navTree.length]);

  return { navTree, navLoading };
};
