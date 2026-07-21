import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Terminal, Key, Mail, AlertCircle, Loader } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const Register: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password || submitting) return;

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await register(email, password);
      navigate("/dashboard");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Account creation failed. Email might already be registered."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-slate-950 min-h-screen flex flex-col justify-center items-center p-4 relative overflow-hidden">
      
      {/* Background gradients */}
      <div className="absolute top-1/4 left-1/4 h-[300px] w-[300px] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 h-[300px] w-[300px] bg-purple-500/10 rounded-full blur-[120px] pointer-events-none"></div>

      <div className="w-full max-w-md space-y-6">
        
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center space-y-2">
          <div className="h-12 w-12 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-center text-indigo-400">
            <Terminal className="h-6 w-6" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gradient">Veritas AI</h1>
          <p className="text-xs text-slate-500">Scaffold a secure database query library</p>
        </div>

        {/* Card Panel */}
        <div className="glass-panel p-8 shadow-2xl relative">
          <form onSubmit={handleSubmit} className="space-y-4">
            
            {/* Email Field */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-400 uppercase">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full bg-slate-950 border border-slate-850 hover:border-slate-800 focus:border-indigo-500 rounded-lg py-2.5 pl-10 pr-4 text-sm text-slate-300 focus:outline-none transition-all"
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-400 uppercase">Password</label>
              <div className="relative">
                <Key className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-950 border border-slate-850 hover:border-slate-800 focus:border-indigo-500 rounded-lg py-2.5 pl-10 pr-4 text-sm text-slate-300 focus:outline-none transition-all"
                />
              </div>
            </div>

            {/* Confirm Password Field */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-400 uppercase">Confirm Password</label>
              <div className="relative">
                <Key className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-950 border border-slate-850 hover:border-slate-800 focus:border-indigo-500 rounded-lg py-2.5 pl-10 pr-4 text-sm text-slate-300 focus:outline-none transition-all"
                />
              </div>
            </div>

            {/* Error Prompt */}
            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-lg flex items-center gap-2">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submitting}
              className="w-full flex items-center justify-center gap-2 bg-indigo-500 hover:bg-indigo-600 disabled:bg-slate-800 text-slate-100 disabled:text-slate-600 py-3 rounded-lg text-sm font-semibold transition-all border border-indigo-600/30"
            >
              {submitting ? <Loader className="h-4 w-4 animate-spin" /> : "Sign Up"}
            </button>
          </form>

          {/* Redirection link */}
          <div className="text-center mt-6 text-xs text-slate-500 font-medium">
            Already have an account?{" "}
            <Link to="/login" className="text-indigo-400 hover:text-indigo-300 transition-colors">
              Sign in instead
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
