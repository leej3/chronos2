import React, { useEffect } from "react";
import { useNavigate, Outlet } from "react-router-dom";
import UseTokenRefresh from "../../hook/UseTokenRefresh";

const Layout = () => {
  const navigate = useNavigate();
  const { refreshAccessToken } = UseTokenRefresh();

  useEffect(() => {
    const checkToken = async () => {
      const accessToken = localStorage.getItem("access_token");
      const refreshToken = localStorage.getItem("refresh_token");

      if (accessToken) {
        navigate("/");
      } else if (refreshToken) {
        try {
          const newAccessToken = await refreshAccessToken(refreshToken);
          navigate(newAccessToken ? "/" : "/login");
        } catch {
          navigate("/login");
        }
      } else {
        navigate("/login");
      }
    };

    checkToken();
  }, []);

  return (
    <div className="wrapper d-flex flex-column min-vh-100">
      <Outlet />
    </div>
  );
};

export default Layout;
