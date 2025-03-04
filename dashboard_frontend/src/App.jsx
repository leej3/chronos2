import React, { Suspense } from 'react';
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { CSpinner } from '@coreui/react';
// Containers
const Layout = React.lazy(() => import('./pages/Layout/LayoutDasdboard'));
// Lazy load the Login component
const Login = React.lazy(() => import('./pages/Login/Login'));
const Home = React.lazy(() => import('./pages/Home/Home'));

function App() {
  return (
    <BrowserRouter>
      <Suspense
        fallback={
          <div className="spinner-overlay">
            <CSpinner color="primary" />
          </div>
        }
      >
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Layout />}>
            <Route path="" element={<Home />} />
          </Route>
        </Routes>
      </Suspense>
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </BrowserRouter>
  );
}

export default App;
