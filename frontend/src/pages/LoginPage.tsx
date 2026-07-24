import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShieldCheck, UserCheck, KeyRound } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(username, password);
      navigate('/');
    } catch (err: unknown) {
      setError(
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ??
          'Unable to sign in. Please verify credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleQuickFill = (user: string, pass: string) => {
    setUsername(user);
    setPassword(pass);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(37,99,235,0.2),_transparent_45%),linear-gradient(135deg,_#020617,_#0f172a)] px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md rounded-3xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl shadow-slate-950/50 backdrop-blur"
      >
        <div className="mb-6 flex items-center gap-3">
          <div className="rounded-2xl bg-sky-500/15 p-3 text-sky-400">
            <ShieldCheck size={28} />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-sky-400">Karnataka SCRB</p>
            <h1 className="text-xl font-bold tracking-tight text-slate-100">AI Crime Intelligence</h1>
          </div>
        </div>

        <p className="mb-6 text-xs text-slate-400">
          Secure authentication portal for SCRB investigators, police officers, and system administrators.
        </p>

        {/* DEMO ACCOUNTS HELPER BADGES */}
        <div className="mb-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-3.5 space-y-2">
          <div className="flex items-center gap-1.5 text-xs text-sky-400 font-semibold">
            <UserCheck size={14} /> Demo Accounts (Click to quick-fill):
          </div>
          <div className="flex flex-wrap gap-1.5">
            <button
              type="button"
              onClick={() => handleQuickFill('admin', 'admin123')}
              className="rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1 text-[11px] text-slate-300 hover:border-sky-500 hover:text-sky-300"
            >
              admin <span className="text-slate-500">(Admin)</span>
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('officer', 'officer123')}
              className="rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1 text-[11px] text-slate-300 hover:border-sky-500 hover:text-sky-300"
            >
              officer <span className="text-slate-500">(Officer)</span>
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('investigator', 'investigator123')}
              className="rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1 text-[11px] text-slate-300 hover:border-sky-500 hover:text-sky-300"
            >
              investigator <span className="text-slate-500">(Investigator)</span>
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-slate-300">Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-3.5 py-2.5 text-sm text-slate-100 outline-none focus:border-sky-500"
              placeholder="Enter username"
              required
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-slate-300">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-3.5 py-2.5 text-sm text-slate-100 outline-none focus:border-sky-500"
              placeholder="Enter password"
              required
            />
          </div>

          {error && <p className="text-xs text-rose-400 bg-rose-950/30 p-2.5 rounded-xl border border-rose-800/40">{error}</p>}

          <button
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-sky-600 px-4 py-3 font-semibold text-xs text-white shadow-lg transition hover:bg-sky-500 disabled:opacity-70"
          >
            <KeyRound size={16} />
            {loading ? 'Authenticating...' : 'Sign In to Command Portal'}
          </button>
        </form>
      </motion.div>
    </div>
  );
}
