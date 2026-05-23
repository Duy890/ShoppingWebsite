import { useEffect, useRef, useState } from 'react';
import { MessageCircle, X, Send, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useChatbot } from '../hooks/useChatbot';
import { formatPrice } from '../utils/formatPrice';

const formatTime = (value) =>
  new Intl.DateTimeFormat('en', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));

const TypingIndicator = () => (
  <div className="flex justify-start">
    <div className="rounded-2xl rounded-bl-md bg-gray-100 px-4 py-3">
      <div className="flex items-center gap-1.5">
        <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:120ms]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:240ms]" />
      </div>
    </div>
  </div>
);

const ChatProductCard = ({ product, onOpen }) => (
  <button
    type="button"
    onClick={() => onOpen(product.id)}
    className="flex w-full gap-3 rounded-2xl border border-gray-100 bg-white p-3 text-left shadow-sm transition hover:border-orange-200 hover:shadow-md"
  >
    <div className="h-16 w-16 shrink-0 overflow-hidden rounded-xl bg-gray-50">
      {product.image_url ? (
        <img src={product.image_url} alt={product.name} className="h-full w-full object-cover" />
      ) : (
        <div className="h-full w-full bg-gray-100" />
      )}
    </div>
    <div className="min-w-0 flex-1">
      <p className="line-clamp-2 text-xs font-black text-gray-900">{product.name}</p>
      <p className="mt-1 text-[10px] font-bold uppercase tracking-wide text-gray-400">
        {[product.brand, product.category].filter(Boolean).join(' - ') || 'Product'}
      </p>
      <p className="mt-2 text-sm font-black text-primary">{formatPrice(product.price)}</p>
    </div>
  </button>
);

const ComparisonCard = ({ comparison }) => {
  const products = comparison?.products || [];
  const fields = comparison?.fields || {};

  if (!products.length || !Object.keys(fields).length) return null;

  return (
    <div className="overflow-hidden rounded-2xl border border-gray-100 bg-white text-xs shadow-sm">
      <div className="grid grid-cols-[88px_1fr_1fr] bg-gray-900 text-white">
        <div className="px-3 py-2 font-black">Spec</div>
        {products.slice(0, 2).map((product) => (
          <div key={product.id} className="min-w-0 px-3 py-2 font-black">
            <span className="line-clamp-2">{product.name}</span>
          </div>
        ))}
      </div>
      {Object.entries(fields).map(([field, values]) => (
        <div key={field} className="grid grid-cols-[88px_1fr_1fr] border-t border-gray-100">
          <div className="bg-gray-50 px-3 py-2 font-bold capitalize text-gray-500">{field}</div>
          {values.slice(0, 2).map((item) => (
            <div key={`${field}-${item.product_id}`} className="px-3 py-2 font-semibold text-gray-800">
              {field === 'price' && typeof item.value === 'number' ? formatPrice(item.value) : item.value}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

const capabilityStyles = {
  low: 'bg-red-50 text-red-700 border-red-100',
  medium: 'bg-yellow-50 text-yellow-700 border-yellow-100',
  high: 'bg-green-50 text-green-700 border-green-100',
  ultra: 'bg-purple-50 text-purple-700 border-purple-100',
  unknown: 'bg-gray-50 text-gray-600 border-gray-100',
};

const PerformanceBadge = ({ level }) => (
  <span className={`rounded-full border px-2.5 py-1 text-[10px] font-black uppercase tracking-wide ${capabilityStyles[level] || capabilityStyles.unknown}`}>
    {level || 'unknown'}
  </span>
);

const GamingResultCard = ({ result, onOpenProduct }) => {
  if (!result || (!result.direct_evaluation && !result.products?.length)) return null;

  return (
    <div className="space-y-3 rounded-2xl border border-gray-100 bg-white p-3 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-black text-gray-900">Gaming capability</p>
          <p className="text-[10px] font-bold text-gray-400">
            {result.game?.name || 'Internal benchmark data'}
          </p>
        </div>
        {result.direct_evaluation && <PerformanceBadge level={result.direct_evaluation.capability} />}
      </div>

      {result.direct_evaluation && (
        <GamingDetail evaluation={result.direct_evaluation} />
      )}

      {result.products?.map((item) => (
        <div key={item.product.id} className="rounded-xl border border-gray-100 bg-gray-50 p-3">
          <div className="mb-2 flex items-start justify-between gap-2">
            <button
              type="button"
              onClick={() => onOpenProduct(item.product.id)}
              className="line-clamp-2 text-left text-xs font-black text-gray-900 hover:text-primary"
            >
              {item.product.name}
            </button>
            <PerformanceBadge level={item.capability} />
          </div>
          <GamingDetail evaluation={item} />
        </div>
      ))}
    </div>
  );
};

const GamingDetail = ({ evaluation }) => (
  <div className="space-y-2 text-[11px] leading-5">
    {evaluation.strengths?.length > 0 && (
      <div>
        <p className="font-black text-green-700">Strengths</p>
        <ul className="list-disc space-y-1 pl-4 text-gray-600">
          {evaluation.strengths.map((item, index) => (
            <li key={`strength-${index}`}>{item}</li>
          ))}
        </ul>
      </div>
    )}
    {evaluation.limitations?.length > 0 && (
      <div>
        <p className="font-black text-orange-700">Limitations</p>
        <ul className="list-disc space-y-1 pl-4 text-gray-600">
          {evaluation.limitations.map((item, index) => (
            <li key={`limit-${index}`}>{item}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
);

const Chatbot = () => {
  const navigate = useNavigate();
  const { messages, loading, sendMessage, clearMessages } = useChatbot();
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [messages, loading, isOpen]);

  useEffect(() => {
    if (isOpen) {
      window.setTimeout(() => inputRef.current?.focus(), 180);
    }
  }, [isOpen]);

  const handleSend = async (event) => {
    event.preventDefault();
    const message = input.trim();
    if (!message || loading) return;

    setInput('');
    try {
      await sendMessage(message);
    } catch {
      // useChatbot already appends an error message.
    }
  };

  const handleAction = (action) => {
    const target = action.target || action.url;
    if (action.type === 'navigate' && target) {
      navigate(target);
      setIsOpen(false);
    }
  };

  const openProduct = (productId) => {
    navigate(`/product/${productId}`);
    setIsOpen(false);
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen((open) => !open)}
        className={`fixed bottom-5 right-5 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-white shadow-2xl shadow-orange-500/30 transition-all duration-300 hover:bg-orange-600 active:scale-95 md:bottom-6 md:right-6 ${
          isOpen ? 'scale-0 opacity-0' : 'scale-100 opacity-100'
        }`}
        aria-label="Open shopping assistant"
      >
        <MessageCircle className="h-6 w-6" />
      </button>

      <section
        className={`fixed inset-x-3 bottom-3 z-50 flex max-h-[calc(100vh-1.5rem)] flex-col overflow-hidden rounded-3xl bg-white shadow-2xl ring-1 ring-black/5 transition-all duration-300 sm:inset-x-auto sm:right-6 sm:bottom-6 sm:h-[620px] sm:w-[400px] ${
          isOpen
            ? 'translate-y-0 scale-100 opacity-100'
            : 'pointer-events-none translate-y-8 scale-95 opacity-0'
        }`}
        aria-hidden={!isOpen}
      >
        <header className="flex items-center justify-between bg-gray-900 px-5 py-4 text-white">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary">
              <MessageCircle className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-black uppercase tracking-wide">Shopping Assistant</h3>
              <p className="text-xs font-medium text-gray-300">AI shopping advisor</p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={clearMessages}
              className="rounded-full p-2 text-gray-300 transition hover:bg-white/10 hover:text-white"
              aria-label="Clear chat history"
            >
              <Trash2 className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="rounded-full p-2 text-gray-300 transition hover:bg-white/10 hover:text-white"
              aria-label="Close shopping assistant"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </header>

        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto bg-gray-50 px-4 py-5">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[82%] space-y-2 ${message.role === 'user' ? 'items-end' : 'items-start'}`}>
                <div
                  className={`rounded-2xl px-4 py-3 text-sm font-medium leading-6 shadow-sm ${
                    message.role === 'user'
                      ? 'rounded-br-md bg-primary text-white'
                      : 'rounded-bl-md bg-white text-gray-800 ring-1 ring-gray-100'
                  }`}
                >
                  <p className="whitespace-pre-line">{message.content}</p>
                </div>

                {message.actions?.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {message.actions.map((action, index) => (
                      <button
                        key={`${action.label}-${index}`}
                        type="button"
                        onClick={() => handleAction(action)}
                        className="rounded-full border border-orange-200 bg-orange-50 px-3 py-1.5 text-xs font-bold text-orange-700 transition hover:bg-orange-100"
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                )}

                {(message.products?.length > 0 || message.recommendations?.length > 0) && (
                  <div className="space-y-2">
                    {(message.recommendations?.length ? message.recommendations : message.products).map((product) => (
                      <ChatProductCard key={product.id} product={product} onOpen={openProduct} />
                    ))}
                  </div>
                )}

                {message.comparison && <ComparisonCard comparison={message.comparison} />}

                {message.gamingResult && (
                  <GamingResultCard result={message.gamingResult} onOpenProduct={openProduct} />
                )}

                {message.gamingResult?.alternatives?.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {message.gamingResult.alternatives.slice(0, 3).map((product) => (
                      <button
                        key={`alt-${product.id}`}
                        type="button"
                        onClick={() => openProduct(product.id)}
                        className="rounded-full border border-orange-200 bg-orange-50 px-3 py-1.5 text-[10px] font-black text-orange-700 transition hover:bg-orange-100"
                      >
                        {product.name}
                      </button>
                    ))}
                  </div>
                )}

                <p className={`text-[10px] font-bold text-gray-400 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                  {formatTime(message.createdAt)}
                </p>
              </div>
            </div>
          ))}
          {loading && <TypingIndicator />}
        </div>

        <form onSubmit={handleSend} className="border-t border-gray-100 bg-white p-4">
          <div className="flex items-end gap-2 rounded-2xl border border-gray-200 bg-gray-50 p-2 focus-within:border-primary focus-within:bg-white">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault();
                  handleSend(event);
                }
              }}
              placeholder="Ask about products, orders, or checkout..."
              rows={1}
              className="max-h-28 flex-1 resize-none bg-transparent px-2 py-2 text-sm font-medium text-gray-800 outline-none placeholder:text-gray-400"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary text-white transition hover:bg-orange-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
              aria-label="Send message"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </form>
      </section>
    </>
  );
};

export default Chatbot;
