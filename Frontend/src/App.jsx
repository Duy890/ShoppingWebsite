import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { Toaster } from 'react-hot-toast';
import { store } from './store';
import AppRoutes from './routes/AppRoutes';
import Chatbot from './components/Chatbot';
import OfflineBanner from './components/OfflineBanner';

function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <OfflineBanner />
        <AppRoutes />
        <Chatbot />
        <Toaster
          position="top-right"
          reverseOrder={false}
          gutter={8}
          toastOptions={{
            duration: 4000,
            style: {
              background: '#fff',
              color: '#333',
              borderRadius: '0.5rem',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            },
            success: {
              style: {
                background: '#10b981',
                color: '#fff',
              },
            },
            error: {
              style: {
                background: '#ef4444',
                color: '#fff',
              },
            },
          }}
        />
      </BrowserRouter>
    </Provider>
  );
}

export default App;
