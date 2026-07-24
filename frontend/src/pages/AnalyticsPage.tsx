import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '@/services/analytics.service';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, PieChart, Building2, UserCheck, ShieldCheck } from 'lucide-react';
import type {
  MonthlyTrend,
  MonthlyStatisticsItem,
  CrimeDistributionItem,
  YearlySummaryItem,
  PoliceStationStats,
  StatusBreakdownItem,
  AccusedStatusItem,
} from '@/types';

export default function AnalyticsPage() {
  const { data: trends, isLoading: isTrendsLoading } = useQuery<MonthlyTrend[]>({
    queryKey: ['crimeTrends'],
    queryFn: () => analyticsService.getCrimeTrends(),
  });

  const { data: statistics, isLoading: isStatsLoading } = useQuery<MonthlyStatisticsItem[]>({
    queryKey: ['monthlyStatistics'],
    queryFn: () => analyticsService.getMonthlyStatistics(),
  });

  const { data: crimeTypes, isLoading: isCrimeTypesLoading } = useQuery<CrimeDistributionItem[]>({
    queryKey: ['crimeTypes'],
    queryFn: analyticsService.getCrimeTypes,
  });

  const { data: yearlySummary } = useQuery<YearlySummaryItem[]>({
    queryKey: ['yearlySummary'],
    queryFn: analyticsService.getYearlySummary,
  });

  const { data: policeStations } = useQuery<PoliceStationStats[]>({
    queryKey: ['policeStations'],
    queryFn: () => analyticsService.getPoliceStations(),
  });

  const { data: caseStatus } = useQuery<StatusBreakdownItem[]>({
    queryKey: ['caseStatus'],
    queryFn: analyticsService.getStatusBreakdown,
  });

  const { data: accusedStatus } = useQuery<AccusedStatusItem[]>({
    queryKey: ['accusedStatus'],
    queryFn: analyticsService.getAccusedStatusBreakdown,
  });

  const maxTrend = Math.max(...(trends?.map((t) => t.case_count) ?? [1]), 1);
  const maxCategory = Math.max(...(crimeTypes?.map((c) => c.case_count) ?? [1]), 1);

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm font-medium text-sky-400">Operational Analytics</p>
        <h2 className="text-2xl font-semibold tracking-tight">FIR Statistics & Crime Distribution</h2>
      </div>

      {/* MONTHLY TRENDS & CATEGORY DISTRIBUTION */}
      <div className="grid gap-6 xl:grid-cols-2">
        {/* Monthly Trend Chart */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl"
        >
          <div className="flex items-center gap-2 text-sky-400 mb-4">
            <TrendingUp size={20} />
            <h3 className="text-lg font-semibold text-slate-100">Monthly Crime Trend</h3>
          </div>
          {isTrendsLoading ? (
            <p className="text-xs text-slate-400">Loading trend data...</p>
          ) : Array.isArray(trends) && trends.length > 0 ? (
            <div className="space-y-3">
              {trends.map((item, index) => {
                const pct = Math.round((item.case_count / maxTrend) * 100);
                return (
                  <div key={`${item.month}-${index}`} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-medium text-slate-200">{item.month_name || `Month ${item.month}`} ({item.year})</span>
                      <span className="text-sky-400 font-semibold">{item.case_count} cases</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-950 overflow-hidden border border-slate-800">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${pct}%` }}
                        transition={{ duration: 0.5, delay: index * 0.05 }}
                        className="h-full rounded-full bg-gradient-to-r from-sky-500 to-blue-600"
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-slate-400">No trend data available.</p>
          )}
        </motion.div>

        {/* Crime Category Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl"
        >
          <div className="flex items-center gap-2 text-sky-400 mb-4">
            <PieChart size={20} />
            <h3 className="text-lg font-semibold text-slate-100">Crime Category Distribution</h3>
          </div>
          {isCrimeTypesLoading ? (
            <p className="text-xs text-slate-400">Loading crime categories...</p>
          ) : Array.isArray(crimeTypes) && crimeTypes.length > 0 ? (
            <div className="space-y-3">
              {crimeTypes.map((item, index) => {
                const label = item.crime_head || item.crime_subhead || 'Other Category';
                const pct = Math.round((item.case_count / maxCategory) * 100);
                return (
                  <div key={`${label}-${index}`} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-medium text-slate-200">{label}</span>
                      <span className="text-sky-400 font-semibold">{item.case_count} cases</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-950 overflow-hidden border border-slate-800">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${pct}%` }}
                        transition={{ duration: 0.5, delay: index * 0.05 }}
                        className="h-full rounded-full bg-gradient-to-r from-amber-500 to-rose-500"
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-slate-400">No category data available.</p>
          )}
        </motion.div>
      </div>

      {/* MONTHLY OPERATIONAL STATISTICS TABLE */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl"
      >
        <div className="flex items-center gap-2 text-sky-400 mb-4">
          <BarChart3 size={20} />
          <h3 className="text-lg font-semibold text-slate-100">Monthly Operational Clearance Breakdown</h3>
        </div>
        {isStatsLoading ? (
          <p className="text-xs text-slate-400">Loading monthly statistics...</p>
        ) : Array.isArray(statistics) && statistics.length > 0 ? (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {statistics.map((item, index) => (
              <div
                key={`${item.year}-${item.month}-${index}`}
                className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 text-xs space-y-2"
              >
                <div className="flex justify-between items-center border-b border-slate-800/80 pb-2">
                  <span className="font-semibold text-slate-200 text-sm">{item.month_name} {item.year}</span>
                  <span className="rounded-full bg-sky-500/10 px-2 py-0.5 text-sky-300 font-semibold">
                    {item.case_count} Total
                  </span>
                </div>
                <div className="space-y-1 text-slate-300">
                  <div className="flex justify-between">
                    <span className="text-amber-400">Under Investigation:</span>
                    <span className="font-semibold">{item.under_investigation_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-emerald-400">Chargesheeted:</span>
                    <span className="font-semibold">{item.chargesheeted_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Closed:</span>
                    <span className="font-semibold">{item.closed_count}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-400">No monthly statistics available.</p>
        )}
      </motion.div>

      {/* STATUS BREAKDOWNS & POLICE STATIONS */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Case Status Summary */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl"
        >
          <div className="flex items-center gap-2 text-sky-400 mb-4">
            <ShieldCheck size={18} />
            <h3 className="text-base font-semibold text-slate-100">Case Status Summary</h3>
          </div>
          <div className="space-y-2">
            {Array.isArray(caseStatus) && caseStatus.length > 0 ? (
              caseStatus.map((item, idx) => (
                <div
                  key={`${item.status}-${idx}`}
                  className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-xs"
                >
                  <span className="font-medium text-slate-200">{item.status}</span>
                  <span className="font-bold text-sky-400">{item.case_count ?? item.count ?? 0} cases</span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400">No status data available.</p>
            )}
          </div>
        </motion.div>

        {/* Accused Status Summary */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl"
        >
          <div className="flex items-center gap-2 text-amber-400 mb-4">
            <UserCheck size={18} />
            <h3 className="text-base font-semibold text-slate-100">Accused Status Breakdown</h3>
          </div>
          <div className="space-y-2">
            {Array.isArray(accusedStatus) && accusedStatus.length > 0 ? (
              accusedStatus.map((item, idx) => (
                <div
                  key={`${item.status}-${idx}`}
                  className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-xs"
                >
                  <span className="font-medium text-slate-200">{item.status}</span>
                  <span className="font-bold text-amber-400">{item.count ?? item.case_count ?? 0} persons</span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400">No accused status data available.</p>
            )}
          </div>
        </motion.div>

        {/* Police Station Workload */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl"
        >
          <div className="flex items-center gap-2 text-emerald-400 mb-4">
            <Building2 size={18} />
            <h3 className="text-base font-semibold text-slate-100">Police Station Workload</h3>
          </div>
          <div className="space-y-2">
            {Array.isArray(policeStations) && policeStations.length > 0 ? (
              policeStations.slice(0, 6).map((item, idx) => (
                <div
                  key={`${item.district}-${item.unit}-${idx}`}
                  className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-xs"
                >
                  <div>
                    <p className="font-medium text-slate-200">{item.unit}</p>
                    <p className="text-[10px] text-slate-500">{item.district}</p>
                  </div>
                  <span className="font-bold text-emerald-400">{item.case_count} cases</span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400">No station workload data available.</p>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
