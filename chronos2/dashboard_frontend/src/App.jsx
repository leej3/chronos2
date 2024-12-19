import React, { Suspense } from 'react';
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Containers
const Layout = React.lazy(() => import('./pages/Layout/LayoutDasdboard'));
// Lazy load the Login component
const Login = React.lazy(() => import('./pages/Login/Login'));
const Home = React.lazy(() => import('./pages/Home/Home'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Layout />}>
            <Route path="" element={<Home />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
