import { useEffect, useMemo, useState } from 'react';
import { aiService } from '../services/aiService';

const STORAGE_KEY = 'shop_chatbot_messages';

const createMessage = (role, content, metadata = {}) => ({
  id: crypto.randomUUID(),
  role,
  content,
  createdAt: new Date().toISOString(),
  ...metadata,
});

const initialMessages = [
  createMessage(
    'assistant',
    "Hello! I'm your shopping assistant. I can help with products, checkout, and order questions."
  ),
];

const loadStoredMessages = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return initialMessages;

    const parsed = JSON.parse(stored);
    return Array.isArray(parsed) && parsed.length ? parsed : initialMessages;
  } catch (error) {
    console.error('Unable to load chatbot history:', error);
    return initialMessages;
  }
};

export const useChatbot = () => {
  const [messages, setMessages] = useState(loadStoredMessages);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  const chatHistory = useMemo(
    () =>
      messages.map((message) => ({
        role: message.role,
        content: message.content,
        createdAt: message.createdAt,
      })),
    [messages]
  );

  const sendMessage = async (content) => {
    const trimmed = content.trim();
    if (!trimmed || loading) return;

    const userMessage = createMessage('user', trimmed);
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await aiService.sendChatMessage(trimmed, {
        history: [...chatHistory, userMessage],
      });

      const assistantMessage = createMessage('assistant', response.message, {
        intent: response.intent,
        entities: response.entities || {},
        products: response.products || [],
        comparison: response.comparison || {},
        gamingResult: response.gaming_result || {},
        recommendations: response.recommendations || [],
        actions: response.actions || [],
      });
      setMessages((prev) => [...prev, assistantMessage]);
      return response;
    } catch (error) {
      console.error('Chat request failed:', error);
      setMessages((prev) => [
        ...prev,
        createMessage('assistant', 'Sorry, I could not connect to the chat service. Please try again.'),
      ]);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const clearMessages = () => {
    setMessages(initialMessages);
  };

  return {
    messages,
    loading,
    sendMessage,
    clearMessages,
  };
};
