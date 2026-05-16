import { Search, Tag, ArrowRight } from 'lucide-react';

const SearchSuggestionItem = ({ suggestion, active, onSelect }) => {
  return (
    <button
      type="button"
      onClick={() => onSelect(suggestion)}
      className={`w-full text-left px-4 py-3 flex items-center justify-between gap-4 transition ${
        active ? 'bg-primary/10 text-primary' : 'hover:bg-gray-100'
      }`}
    >
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-2xl grid place-items-center ${active ? 'bg-primary text-white' : 'bg-gray-100 text-gray-500'}`}>
          {suggestion.type === 'product' ? <Search className="w-4 h-4" /> : <Tag className="w-4 h-4" />}
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold truncate">{suggestion.label}</p>
          {suggestion.subtitle && <p className="text-xs text-gray-500 truncate">{suggestion.subtitle}</p>}
          {suggestion.category && <p className="text-[11px] uppercase tracking-[0.18em] text-gray-400 mt-1">{suggestion.category}</p>}
        </div>
      </div>
      <ArrowRight className="w-4 h-4 text-gray-400" />
    </button>
  );
};

export default SearchSuggestionItem;
