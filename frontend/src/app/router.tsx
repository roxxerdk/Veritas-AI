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
  const { user, loading, checkAuth } = useAuth();
  const token = localStorage.getItem("veritas_token");

  if (loading) {
    return (
      <div className="bg-slate-950 min-h-screen flex items-center justify-center text-sm text-slate-500 font-mono">
        Authenticating Veritas AI session...
      </div>
    );
  }

  // If no token or user profile found, display a connecting screen and trigger auto-retry
  if (!token || !user) {
    // Auto-retry checkAuth after a short delay if it fails
    setTimeout(() => {
      checkAuth();
    }, 2000);

    return (
      <div className="bg-slate-950 min-h-screen flex items-center justify-center text-sm text-slate-500 font-mono flex-col gap-2">
        <span className="animate-pulse">Establishing connection to Veritas AI services...</span>
      </div>
    );
  }

  return <>{children}</>;
};

export const AppRouter: React.FC = () => {
  return (
    <Routes>
      {/* Redirect Auth routes to Dashboard root */}
      <Route path="/login" element={<Navigate to="/" replace />} />
      <Route path="/register" element={<Navigate to="/" replace />} />

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
