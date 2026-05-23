import { useTranslation } from 'react-i18next';
import SearchSuggestionItem from './SearchSuggestionItem';
import { Search } from 'lucide-react';

const SearchSuggestions = ({ suggestions, query, activeIndex, loading, isOpen, onSelect, onClear }) => {
  const { t } = useTranslation();
  if (!isOpen) {
    return null;
  }

  const hasQuery = query.trim().length > 0;
  const hasResults = suggestions.length > 0;

  return (
    <div className="absolute inset-x-0 top-full mt-2 rounded-3xl bg-white shadow-2xl border border-gray-200 text-gray-900 overflow-hidden z-30">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <div className="flex items-center gap-2 text-xs uppercase tracking-[0.25em] text-gray-500 font-semibold">
          <Search className="w-4 h-4" />
          {t('search_suggestions.title')}
        </div>
        <button type="button" className="text-xs text-gray-400 hover:text-gray-700" onClick={onClear}>
          {t('search_suggestions.close')}
        </button>
      </div>

      <div className="max-h-72 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center py-10 text-sm text-gray-500">{t('search_suggestions.loading')}</div>
        ) : hasResults ? (
          suggestions.map((suggestion, index) => (
            <SearchSuggestionItem
              key={`${suggestion.type}-${suggestion.id}`}
              suggestion={suggestion}
              active={index === activeIndex}
              onSelect={onSelect}
            />
          ))
        ) : hasQuery ? (
          <div className="px-6 py-10 text-center text-sm text-gray-500 space-y-3">
            <p className="font-semibold text-gray-900">{t('search_suggestions.no_suggestions')}</p>
            <p>{t('search_suggestions.no_suggestions_help')}</p>
            <div className="inline-flex items-center gap-2 rounded-full border border-gray-200 px-4 py-2 text-xs text-gray-500">
              <span>{t('search_suggestions.no_suggestions_action')}</span>
            </div>
          </div>
        ) : (
          <div className="px-6 py-10 text-center text-sm text-gray-500 space-y-3">
            <p className="font-semibold text-gray-900">{t('search_suggestions.start_typing_title')}</p>
            <p>{t('search_suggestions.start_typing_desc')}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchSuggestions;
