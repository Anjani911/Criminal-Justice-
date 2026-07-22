import { Link, NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, ShieldCheck, FolderKanban, BarChart3, BrainCircuit, Network, FileText, ScrollText, UserCircle, LogOut } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/cases', label: 'Cases', icon: FolderKanban },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/predictions', label: 'Predictive', icon: BrainCircuit },
  { to: '/network', label: 'Network', icon: Network },
  { to: '/chat', label: 'AI Chat', icon: ShieldCheck },
  { to: '/reports', label: 'Reports', icon: FileText },
  { to: '/audit', label: 'Audit', icon: ScrollText },
  { to: '/profile', label: 'Profile', icon: UserCircle },
];

export default function MainLayout() {
  const { employee, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="flex min-h-screen">
        <aside className="hidden w-72 border-r border-slate-800 bg-slate-900/80 p-6 lg:flex lg:flex-col">
          <div className="mb-10">
            <p className="text-xs uppercase tracking-[0.35em] text-sky-400">SCRB</p>
            <h1 className="mt-2 text-xl font-semibold">Crime Intelligence</h1>
          </div>
          <nav className="space-y-2">
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${isActive ? 'bg-sky-600/20 text-sky-300' : 'text-slate-300 hover:bg-slate-800'}`
                }
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="mt-auto rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
            <p className="text-sm font-semibold">{employee?.name ?? 'Operator'}</p>
            <p className="text-xs text-slate-400">{employee?.role ?? 'Investigator'}</p>
            <button onClick={logout} className="mt-4 flex items-center gap-2 text-sm text-slate-300">
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </aside>

        <div className="flex-1">
          <header className="border-b border-slate-800 bg-slate-900/70 px-6 py-4 backdrop-blur">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-sky-400">Karnataka State Crime Records Bureau</p>
                <h2 className="text-xl font-semibold">AI Command Center</h2>
              </div>
              <div className="flex items-center gap-3">
                <Link to="/profile" className="rounded-full border border-slate-700 px-3 py-2 text-sm text-slate-300">
                  {employee?.badge_number ?? 'Profile'}
                </Link>
              </div>
            </div>
          </header>

          <main className="p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
