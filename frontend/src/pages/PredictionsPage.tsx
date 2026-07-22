import { useQuery } from '@tanstack/react-query';
import { predictionService } from '@/services/prediction.service';
import { motion } from 'framer-motion';

export default function PredictionsPage() {
  const { data: dashboard } = useQuery({ queryKey: ['predictionDashboard'], queryFn: predictionService.getDashboard });
  const { data: warnings } = useQuery({ queryKey: ['warnings'], queryFn: () => predictionService.getWarnings() });

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-sky-400">Predictive intelligence</p>
        <h2 className="text-2xl font-semibold">Forecasting and early warnings</h2>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <h3 className="text-lg font-semibold">Prediction dashboard</h3>
          <p className="mt-3 text-sm text-slate-400">{dashboard?.explanation ?? 'No forecast data available right now.'}</p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <h3 className="text-lg font-semibold">Early warnings</h3>
          <div className="mt-4 space-y-3">
            {(warnings?.warnings ?? []).slice(0, 4).map((item: any, index: number) => (
              <div key={`${item.title}-${index}`} className="rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{item.title}</span>
                  <span className="text-rose-300">{item.severity}</span>
                </div>
                <p className="mt-2 text-slate-400">{item.reason}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
