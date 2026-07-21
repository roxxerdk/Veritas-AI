import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Login } from "../pages/Login";
import { Register } from "../pages/Register";
import { Dashboard } from "../pages/Dashboard";
import { ChatConsole } from "../pages/ChatConsole";
import { Settings } from "../pages/Settings";

// Route protection decorator
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();
  const token = localStorage.getItem("veritas_token");

  if (loading) {
    return (
      <div className="bg-slate-950 min-h-screen flex items-center justify-center text-sm text-slate-500 font-mono">
        Authenticating Veritas AI session...
      </div>
    );
  }

  // If no token or user profile found, redirect to Login
  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Route protection decorator for Auth Pages (Login/Register)
const AuthRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();
  const token = localStorage.getItem("veritas_token");

  if (loading) return null;

  // If already authenticated, redirect straight to dashboard
  if (token && user) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

export const AppRouter: React.FC = () => {
  return (
    <Routes>
      {/* Public/Auth Routes */}
      <Route
        path="/login"
        element={
          <AuthRoute>
            <Login />
          </AuthRoute>
        }
      />
      <Route
        path="/register"
        element={
          <AuthRoute>
            <Register />
          </AuthRoute>
        }
      />

      {/* Protected Control Views */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <ChatConsole />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Settings />
          </ProtectedRoute>
        }
      />

      {/* Redirect Root to Dashboard */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Fallback 404 Routing redirects to root */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
