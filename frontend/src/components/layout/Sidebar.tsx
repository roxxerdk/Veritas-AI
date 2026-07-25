import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { LayoutDashboard, MessageSquare, Settings, LogOut, Terminal } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user } = useAuth();

  const menuItems = [
    {
      name: "Dashboard",
      icon: LayoutDashboard,
      path: "/dashboard",
    },
    {
      name: "Agent Chat",
      icon: MessageSquare,
      path: "/chat",
    },
    {
      name: "Settings",
      icon: Settings,
      path: "/settings",
    },
  ];

  return (
    <aside className="w-64 bg-slate-900/60 backdrop-blur-md border-r border-slate-800 flex flex-col justify-between h-screen sticky top-0">
      <div>
        {/* Brand Logo Header */}
        <div className="p-6 border-b border-slate-800 flex items-center gap-3">
          <Terminal className="h-6 w-6 text-indigo-500" />
          <span className="font-bold text-xl tracking-tight text-gradient">Veritas AI</span>
        </div>

        {/* Menu Items */}
        <nav className="p-4 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <button
                key={item.name}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-gradient-to-r from-indigo-500/10 to-purple-500/10 text-indigo-400 border-l-2 border-indigo-500"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <Icon className={`h-5 w-5 ${isActive ? "text-indigo-400" : ""}`} />
                {item.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* User Session Info */}
      <div className="p-4 border-t border-slate-800">
        {user && (
          <div className="px-4 py-2 bg-slate-800/20 border border-slate-800/50 rounded-lg">
            <p className="text-xs text-slate-500">Logged in as</p>
            <p className="text-sm font-semibold text-slate-300 truncate">{user.email}</p>
          </div>
        )}
      </div>
    </aside>
  );
};
