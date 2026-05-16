const ProductCardSkeleton = () => (
  <div className="bg-white dark:bg-slate-800 rounded-lg overflow-hidden shadow-md animate-pulse">
    {/* Image skeleton */}
    <div className="w-full h-48 bg-slate-300 dark:bg-slate-700"></div>

    <div className="p-4">
      {/* Category skeleton */}
      <div className="h-3 bg-slate-300 dark:bg-slate-700 rounded w-20 mb-3"></div>

      {/* Title skeleton */}
      <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded mb-2"></div>
      <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-5/6 mb-3"></div>

      {/* Description skeleton */}
      <div className="h-3 bg-slate-300 dark:bg-slate-700 rounded w-4/5 mb-4"></div>

      {/* Rating skeleton */}
      <div className="flex items-center gap-2 mb-3">
        <div className="h-4 w-16 bg-slate-300 dark:bg-slate-700 rounded"></div>
        <div className="h-3 w-12 bg-slate-300 dark:bg-slate-700 rounded"></div>
      </div>

      {/* Price skeleton */}
      <div className="flex justify-between items-center mb-4">
        <div className="h-6 w-24 bg-slate-300 dark:bg-slate-700 rounded"></div>
        <div className="h-5 w-20 bg-slate-300 dark:bg-slate-700 rounded"></div>
      </div>

      {/* Button skeleton */}
      <div className="h-10 bg-slate-300 dark:bg-slate-700 rounded w-full"></div>
    </div>
  </div>
);

const ProductCardSkeletonGrid = ({ count = 4 }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    {Array.from({ length: count }).map((_, i) => (
      <ProductCardSkeleton key={i} />
    ))}
  </div>
);

export { ProductCardSkeleton, ProductCardSkeletonGrid };
