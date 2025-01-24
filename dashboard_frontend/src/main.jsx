import { createRoot } from 'react-dom/client';

import '@coreui/coreui/dist/css/coreui.min.css';

import { Provider } from 'react-redux';
import { ToastContainer } from 'react-toastify';

import { store } from './app/store.js';
import App from './App.jsx';
import './index.css';
createRoot(document.getElementById('root')).render(
  <>
    <Provider store={store}>
      <App />
      <ToastContainer />
    </Provider>
  </>,
);
