const CartSkeleton = () => (
  <div className="space-y-4 animate-pulse">
    {/* Cart items skeleton */}
    {[1, 2, 3].map((i) => (
      <div key={i} className="bg-white dark:bg-slate-800 rounded-lg p-4 flex gap-4">
        {/* Product image skeleton */}
        <div className="w-24 h-24 bg-slate-300 dark:bg-slate-700 rounded"></div>

        <div className="flex-1">
          {/* Product name skeleton */}
          <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-48 mb-2"></div>
          {/* Product price skeleton */}
          <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-32 mb-3"></div>
          {/* Quantity and actions skeleton */}
          <div className="flex gap-2">
            <div className="h-8 w-24 bg-slate-300 dark:bg-slate-700 rounded"></div>
            <div className="h-8 w-8 bg-slate-300 dark:bg-slate-700 rounded"></div>
          </div>
        </div>

        {/* Total price skeleton */}
        <div className="flex flex-col items-end">
          <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-28 mb-2"></div>
          <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-8"></div>
        </div>
      </div>
    ))}

    {/* Summary skeleton */}
    <div className="bg-white dark:bg-slate-800 rounded-lg p-4 mt-6">
      <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-32 mb-3"></div>
      <div className="space-y-2">
        <div className="flex justify-between">
          <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-24"></div>
          <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-20"></div>
        </div>
        <div className="flex justify-between">
          <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-24"></div>
          <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-20"></div>
        </div>
        <div className="border-t border-slate-200 dark:border-slate-700 pt-2 mt-2 flex justify-between">
          <div className="h-5 bg-slate-300 dark:bg-slate-700 rounded w-24"></div>
          <div className="h-5 bg-slate-300 dark:bg-slate-700 rounded w-20"></div>
        </div>
      </div>
      <div className="mt-4 h-10 bg-slate-300 dark:bg-slate-700 rounded w-full"></div>
    </div>
  </div>
);

export default CartSkeleton;
