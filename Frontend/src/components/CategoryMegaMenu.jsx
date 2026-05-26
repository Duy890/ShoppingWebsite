import { useState, useEffect, useRef, memo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ChevronRight, LayoutGrid } from 'lucide-react';
import { useNavigation } from '../hooks/useNavigation';

const CategoryMegaMenu = memo(({ isOpen, onDismiss }) => {
  const navigate = useNavigate();
  const { i18n } = useTranslation();
  const { navTree, navLoading } = useNavigation();
  const [activeL1Index, setActiveL1Index] = useState(0);
  const closeTimeoutRef = useRef(null);

  const getItemName = (item) => {
    const isEnglish = typeof i18n.language === 'string' && i18n.language.toLowerCase().startsWith('en');
    if (isEnglish && item.name_en) {
      return item.name_en;
    }
    return item.name;
  };

  useEffect(() => {
    console.count("CategoryMegaMenu render");
  }, [isOpen]);

  useEffect(() => {
    return () => {
      if (closeTimeoutRef.current) {
        clearTimeout(closeTimeoutRef.current);
      }
    };
  }, []);

  const handleMouseEnter = useCallback(() => {
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
    }
  }, []);

  const handleMouseLeave = useCallback(() => {
    closeTimeoutRef.current = setTimeout(() => {
      onDismiss();
    }, 200);
  }, [onDismiss]);

  const handleCategoryClick = useCallback((slug) => {
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
    }
    onDismiss();
    navigate(`/products?category=${slug}`);
  }, [navigate, onDismiss]);

  if (!isOpen) return null;

  const activeL1 = navTree[activeL1Index];

  return (
    <div 
      className="absolute left-0 right-0 top-full z-50 pt-2"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className="mx-auto max-w-7xl px-4">
        <div className="flex overflow-hidden rounded-2xl bg-white shadow-2xl border border-gray-100 min-h-[500px] max-h-[75vh]">
          <div className="w-[260px] bg-gray-50 border-r border-gray-100 overflow-y-auto custom-scrollbar sticky top-0">
            <div className="py-2">
              {navTree.map((item, index) => (
                <button
                  key={item.slug}
                  onMouseEnter={() => setActiveL1Index(index)}
                  onClick={() => handleCategoryClick(item.slug)}
                  className={`w-full flex items-center justify-between px-6 py-4 text-left transition-all relative ${
                    activeL1Index === index 
                      ? 'bg-white text-primary font-bold shadow-sm' 
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {activeL1Index === index && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary" />
                  )}
                  <span className="text-sm font-semibold">{getItemName(item)}</span>
                  <ChevronRight className={`w-4 h-4 transition-transform ${activeL1Index === index ? 'translate-x-1 opacity-100 text-primary' : 'opacity-0'}`} />
                </button>
              ))}
              
              {navLoading && navTree.length === 0 && (
                <div className="p-6 space-y-4">
                  {[1,2,3,4,5,6,7,8].map(i => (
                    <div key={i} className="h-4 bg-gray-200 rounded animate-pulse w-3/4"></div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="flex-1 bg-white overflow-y-auto custom-scrollbar p-8">
            {activeL1 ? (
              <div key={activeL1.slug} className="animate-in fade-in slide-in-from-left-4 duration-300">
                <div className="mb-8 border-b border-gray-100 pb-4 flex items-center justify-between">
                  <h3 className="text-xl font-black text-gray-900 tracking-tight flex items-center gap-2">
                    <LayoutGrid className="w-5 h-5 text-primary" />
                    Tất cả {getItemName(activeL1)}
                  </h3>
                  <button 
                    onClick={() => handleCategoryClick(activeL1.slug)}
                    className="text-xs font-bold text-primary hover:underline uppercase tracking-wider"
                  >
                    Xem tất cả
                  </button>
                </div>
                
                {activeL1.children && activeL1.children.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-12 gap-y-10">
                    {activeL1.children.map((l2) => (
                      <div key={l2.slug} className="space-y-4">
                        <button 
                          onClick={() => handleCategoryClick(l2.slug)}
                          className="text-sm font-black text-gray-900 hover:text-primary transition-colors uppercase tracking-tight"
                        >
                          {getItemName(l2)}
                        </button>
                        
                        {l2.children && l2.children.length > 0 ? (
                          <div className="flex flex-col space-y-2">
                            {l2.children.map((l3) => (
                              <button
                                key={l3.slug}
                                onClick={() => handleCategoryClick(l3.slug)}
                                className="text-sm text-gray-500 hover:text-primary text-left transition-colors flex items-center group"
                              >
                                <div className="w-1.5 h-1.5 rounded-full bg-gray-200 mr-2 group-hover:bg-primary transition-colors"></div>
                                {getItemName(l3)}
                              </button>
                            ))}
                          </div>
                        ) : (
                          <div className="text-xs text-gray-300 italic">Xem chi tiết sản phẩm</div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex h-48 flex-col items-center justify-center text-gray-400">
                    <p className="italic text-sm">Chưa có phân loại chi tiết.</p>
                  </div>
                )}
              </div>
            ) : !navLoading && (
              <div className="flex h-full items-center justify-center text-gray-400 italic">
                Chọn một danh mục để xem chi tiết.
              </div>
            )}
            
            {navLoading && navTree.length === 0 && (
              <div className="space-y-8 animate-pulse">
                <div className="h-6 w-48 bg-gray-100 rounded"></div>
                <div className="grid grid-cols-3 gap-12">
                  {[1,2,3,4,5,6].map(i => (
                    <div key={i} className="space-y-4">
                      <div className="h-4 w-32 bg-gray-100 rounded"></div>
                      <div className="space-y-2">
                        <div className="h-3 w-24 bg-gray-50 rounded"></div>
                        <div className="h-3 w-28 bg-gray-50 rounded"></div>
                        <div className="h-3 w-20 bg-gray-50 rounded"></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});

CategoryMegaMenu.displayName = 'CategoryMegaMenu';

export default CategoryMegaMenu;
