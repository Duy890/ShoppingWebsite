const CategoryMegaMenu = ({ categories, isOpen, onSelect, onDismiss }) => {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="absolute left-0 right-0 top-full z-20 mt-2 px-4">
      <div
        className="rounded-[2rem] bg-white text-gray-900 shadow-2xl border border-gray-200 p-6 grid gap-6 lg:grid-cols-[280px_1fr]"
        onMouseLeave={onDismiss}
      >
        <div className="space-y-6">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-primary">Explore categories</p>
            <h2 className="mt-2 text-2xl font-black">Shop by aisle</h2>
            <p className="mt-3 text-sm text-gray-500">Browse curated collections, trending electronics, and the fastest routes to what you want.</p>
          </div>
          <button
            type="button"
            onClick={() => onSelect(null)}
            className="inline-flex items-center justify-center rounded-full border border-gray-200 px-5 py-3 text-sm font-semibold text-gray-700 hover:border-primary hover:text-primary transition"
          >
            All products
          </button>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categories.length > 0 ? (
            categories.map((category) => (
              <div key={category.id} className="rounded-3xl border border-gray-100 p-4 hover:border-primary transition">
                <button
                  type="button"
                  onClick={() => onSelect(category.id)}
                  className="text-left w-full"
                >
                  <p className="text-sm font-semibold text-gray-900">{category.name}</p>
                  <p className="mt-2 text-sm text-gray-500 line-clamp-2">{category.description || 'Explore the latest products in this collection.'}</p>
                </button>
                {category.children?.length ? (
                  <div className="mt-4 space-y-2">
                    {category.children.map((child) => (
                      <button
                        key={child.id}
                        type="button"
                        onClick={() => onSelect(child.id)}
                        className="block text-sm text-gray-500 hover:text-primary"
                      >
                        {child.name}
                      </button>
                    ))}
                  </div>
                ) : null}
              </div>
            ))
          ) : (
            <div className="rounded-3xl border border-gray-100 p-6 text-center text-sm text-gray-500">
              No categories available yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CategoryMegaMenu;
