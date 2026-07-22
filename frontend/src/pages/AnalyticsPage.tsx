import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '@/services/analytics.service';
import { motion } from 'framer-motion';

export default function AnalyticsPage() {
  const { data: trends } = useQuery({ queryKey: ['crimeTrends'], queryFn: () => analyticsService.getCrimeTrends() });
  const { data: statistics } = useQuery({ queryKey: ['monthlyStatistics'], queryFn: () => analyticsService.getMonthlyStatistics() });
  const { data: crimeTypes } = useQuery({ queryKey: ['crimeTypes'], queryFn: analyticsService.getCrimeTypes });
  const { data: yearlySummary } = useQuery({ queryKey: ['yearlySummary'], queryFn: analyticsService.getYearlySummary });
  const { data: policeStations } = useQuery({ queryKey: ['policeStations'], queryFn: () => analyticsService.getPoliceStations() });
  const { data: accusedStatus } = useQuery({ queryKey: ['accusedStatus'], queryFn: analyticsService.getAccusedStatusBreakdown });

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-sky-400">Operational analytics</p>
        <h2 className="text-2xl font-semibold">Crime trends and distributions</h2>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <h3 className="text-lg font-semibold">Monthly crime trend</h3>
          <div className="mt-4 space-y-3">
            {Array.isArray(trends) ? trends.slice(0, 6).map((item: any, index: number) => (
              <div key={`${item.month}-${index}`} className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm">
                <span>{item.month_name ?? item.month ?? 'Point'}</span>
                <span className="text-sky-300">{item.case_count ?? 0}</span>
              </div>
            )) : <p className="text-sm text-slate-400">No trend data available.</p>}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <h3 className="text-lg font-semibold">Crime category distribution</h3>
          <div className="mt-4 space-y-3">
            {Array.isArray(crimeTypes) ? crimeTypes.slice(0, 6).map((item: any, index: number) => (
              <div key={`${item.crime_head ?? item.crime_subhead}-${index}`} className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm">
                <span>{item.crime_head ?? item.crime_subhead ?? 'Category'}</span>
                <span className="text-sky-300">{item.case_count ?? 0}</span>
              </div>
            )) : <p className="text-sm text-slate-400">No category data available.</p>}
          </div>
        </motion.div>
      </div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
        <h3 className="text-lg font-semibold">Monthly operational statistics</h3>
        <div className="mt-4 space-y-3">
          {Array.isArray(statistics) ? statistics.slice(0, 6).map((item: any, index: number) => (
            <div key={`${item.month}-${index}`} className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm">
              <span>{item.month_name ?? item.month ?? 'Month'}</span>
              <span className="text-slate-300">Cases: {item.case_count ?? 0} · Investigating: {item.under_investigation_count ?? 0}</span>
            </div>
          )) : <p className="text-sm text-slate-400">No monthly statistics available.</p>}
        </div>
      </motion.div>

      <div className="grid gap-6 xl:grid-cols-2">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <h3 className="text-lg font-semibold">Yearly summary</h3>
          <div className="mt-4 space-y-3">
            {Array.isArray(yearlySummary) ? yearlySummary.slice(0, 6).map((item: any) => (
              <div key={item.year} className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm">
                <span>{item.year}</span>
                <span className="text-sky-300">{item.case_count}</span>
              </div>
            )) : <p className="text-sm text-slate-400">No yearly summary available.</p>}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <h3 className="text-lg font-semibold">Police station stats</h3>
          <div className="mt-4 space-y-3">
            {Array.isArray(policeStations) ? policeStations.slice(0, 6).map((item: any) => (
              <div key={`${item.district}-${item.unit}`} className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm">
                <span>{item.unit} · {item.district}</span>
                <span className="text-sky-300">{item.case_count}</span>
              </div>
            )) : <p className="text-sm text-slate-400">No police station data available.</p>}
          </div>
        </motion.div>
      </div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
        <h3 className="text-lg font-semibold">Accused status breakdown</h3>
        <div className="mt-4 space-y-3">
          {Array.isArray(accusedStatus) ? accusedStatus.slice(0, 6).map((item: any) => (
            <div key={item.status} className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm">
              <span>{item.status}</span>
              <span className="text-sky-300">{item.count}</span>
            </div>
          )) : <p className="text-sm text-slate-400">No accused status data available.</p>}
        </div>
      </motion.div>
    </div>
  );
}
