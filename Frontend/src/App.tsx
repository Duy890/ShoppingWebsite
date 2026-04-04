import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';
import AppRoutes from './routes/AppRoutes';
import Chatbot from './components/Chatbot';

function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <AppRoutes />
        <Chatbot />
      </BrowserRouter>
    </Provider>
  );
}

export default App;
