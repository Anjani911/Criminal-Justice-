import { useQuery } from '@tanstack/react-query';
import { networkService } from '@/services/network.service';
import { motion } from 'framer-motion';

export default function NetworkPage() {
  const { data: network } = useQuery({ queryKey: ['network'], queryFn: networkService.getFullNetwork });
  const { data: metrics } = useQuery({ queryKey: ['networkMetrics'], queryFn: networkService.getMetrics });

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-sky-400">Criminal network</p>
        <h2 className="text-2xl font-semibold">Interactive graph view</h2>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <h3 className="text-lg font-semibold">Network graph</h3>
          <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-950/70 p-6 text-sm text-slate-400">
            {network ? `Loaded ${network.nodes?.length ?? 0} nodes and ${network.edges?.length ?? 0} edges.` : 'Network data will appear here.'}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <h3 className="text-lg font-semibold">Network metrics</h3>
          <div className="mt-4 space-y-3 text-sm text-slate-400">
            {metrics ? Object.entries(metrics).slice(0, 6).map(([key, value]) => (
              <div key={key} className="rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.25em] text-sky-400">{key}</p>
                <p className="mt-1 text-slate-300">{String(value)}</p>
              </div>
            )) : <p>No metrics available yet.</p>}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
