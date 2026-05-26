import { useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { setNavTree, setNavLoading } from '../store/navigationSlice';
import { productService } from '../services/productService';

export const useNavigation = () => {
  const dispatch = useDispatch();
  const { i18n } = useTranslation();
  const navTree = useSelector((state) => state.navigation.navTree);
  const navLoading = useSelector((state) => state.navigation.navLoading);
  const fetchedRef = useRef(false);
  const lastLanguageRef = useRef(i18n.language);

  useEffect(() => {
    if (lastLanguageRef.current !== i18n.language) {
      lastLanguageRef.current = i18n.language;
      fetchedRef.current = false;
      dispatch(setNavTree([]));
      productService.clearNavigationCache();
    }

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
  }, [dispatch, navTree.length, i18n.language]);

  return { navTree, navLoading };
};
