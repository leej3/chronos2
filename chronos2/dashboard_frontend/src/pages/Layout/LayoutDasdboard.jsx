import React, { useEffect } from 'react';
import { AppFooter, AppHeader } from '../../components/Header/index';
import { useNavigate, Outlet } from 'react-router-dom';
import { useSelector } from 'react-redux';

const Layout = () => {
  const navigate = useNavigate();
  const { isLoggedIn } = useSelector((state) => state.auth);

  useEffect(() => {
    if (isLoggedIn) {
      navigate('/');
    } else {
      navigate('/login');
    }
  }, [isLoggedIn, navigate]);
  return (
    <div>
      <div className="wrapper d-flex flex-column min-vh-100">
        <AppHeader />
        <Outlet />
        <AppFooter />
      </div>
    </div>
  );
};

export default Layout;
