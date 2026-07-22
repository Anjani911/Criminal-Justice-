import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShieldCheck } from 'lucide-react';
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
      setError((err as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? 'Unable to sign in.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(37,99,235,0.2),_transparent_45%),linear-gradient(135deg,_#020617,_#0f172a)] px-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md rounded-3xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl shadow-slate-950/50 backdrop-blur">
        <div className="mb-6 flex items-center gap-3">
          <div className="rounded-2xl bg-sky-500/15 p-3 text-sky-400">
            <ShieldCheck size={24} />
          </div>
          <div>
            <p className="text-sm uppercase tracking-[0.3em] text-sky-400">SCRB</p>
            <h1 className="text-xl font-semibold">Investigative Command</h1>
          </div>
        </div>
        <p className="mb-8 text-sm text-slate-400">Secure access to Karnataka’s crime intelligence platform.</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-2 block text-sm text-slate-300">Username</label>
            <input value={username} onChange={(e) => setUsername(e.target.value)} className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-3 outline-none ring-0" placeholder="Enter username" />
          </div>
          <div>
            <label className="mb-2 block text-sm text-slate-300">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-3 outline-none ring-0" placeholder="Enter password" />
          </div>
          {error ? <p className="text-sm text-rose-400">{error}</p> : null}
          <button disabled={loading} className="w-full rounded-xl bg-sky-600 px-4 py-3 font-semibold text-white transition hover:bg-sky-500 disabled:opacity-70">
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </motion.div>
    </div>
  );
}
