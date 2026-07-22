import { motion } from 'framer-motion';
import { AlertTriangle, Gavel, UserRound, FileSearch2, TrendingUp } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '@/services/analytics.service';

const statCards = [
  { key: 'total_cases', label: 'Crime Count', icon: FileSearch2, tone: 'from-sky-500/20 to-sky-600/10' },
  { key: 'cases_under_investigation', label: 'Open Cases', icon: AlertTriangle, tone: 'from-amber-500/20 to-amber-600/10' },
  { key: 'total_accused', label: 'Accused', icon: Gavel, tone: 'from-rose-500/20 to-rose-600/10' },
  { key: 'total_victims', label: 'Victims', icon: UserRound, tone: 'from-emerald-500/20 to-emerald-600/10' },
];

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboardSummary'],
    queryFn: analyticsService.getDashboardSummary,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-sky-400">Mission overview</p>
          <h2 className="text-2xl font-semibold">Intelligence dashboard</h2>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {statCards.map(({ key, label, icon: Icon, tone }) => (
          <motion.div key={key} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className={`rounded-2xl border border-slate-800 bg-gradient-to-br ${tone} p-5`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-300">{label}</p>
                <p className="mt-3 text-3xl font-semibold">{isLoading ? '—' : (data?.[key as keyof typeof data] ?? 0)}</p>
              </div>
              <div className="rounded-2xl border border-slate-700 bg-slate-900/80 p-2 text-sky-300">
                <Icon size={22} />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-sm text-sky-400">Operational insight</p>
              <h3 className="text-xl font-semibold">Recent analytical indicators</h3>
            </div>
            <div className="rounded-full border border-sky-500/20 bg-sky-500/10 px-3 py-1 text-sm text-sky-300">
              Live
            </div>
          </div>
          <div className="space-y-4">
            {[{ title: 'Prediction confidence', value: 'High', detail: 'Hotspot forecasting remains stable across district clusters.' }, { title: 'Case workflow', value: 'Accelerated', detail: 'Investigation pipelines are moving efficiently.' }].map((item) => (
              <div key={item.title} className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
                <div className="flex items-center justify-between">
                  <p className="font-medium">{item.title}</p>
                  <span className="text-sm text-sky-300">{item.value}</span>
                </div>
                <p className="mt-2 text-sm text-slate-400">{item.detail}</p>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <div className="flex items-center gap-2 text-sky-400">
            <TrendingUp size={18} />
            <p className="text-sm">Quick actions</p>
          </div>
          <div className="mt-6 space-y-3">
            {['Review high-risk cases', 'Inspect predictive warnings', 'Open AI investigator chat'].map((item) => (
              <div key={item} className="rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm text-slate-300">
                {item}
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
