import { useQuery } from '@tanstack/react-query';
import { predictionService } from '@/services/prediction.service';
import { motion } from 'framer-motion';
import {
  BrainCircuit,
  Flame,
  TrendingUp,
  ShieldAlert,
  AlertOctagon,
  CheckCircle2,
  HelpCircle,
  BarChart3,
} from 'lucide-react';
import type {
  PredictionDashboardResponse,
  WarningResponse,
} from '@/types';

export default function PredictionsPage() {
  const { data: dashboard, isLoading: isDashboardLoading } = useQuery<PredictionDashboardResponse>({
    queryKey: ['predictionDashboard'],
    queryFn: predictionService.getDashboard,
  });

  const { data: warningsData, isLoading: isWarningsLoading } = useQuery<WarningResponse>({
    queryKey: ['warnings'],
    queryFn: () => predictionService.getWarnings(),
  });

  const hotspotPred = dashboard?.hotspot_forecast?.prediction;
  const hotspotList = dashboard?.hotspot_forecast?.predictions ?? [];

  const trendPred = dashboard?.trend_forecast?.prediction;

  const stationRiskPred = dashboard?.station_risk?.prediction;
  const stationRiskList = dashboard?.station_risk?.predictions ?? [];

  const warnings = warningsData?.warnings ?? dashboard?.warnings?.warnings ?? [];

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'border-rose-500 bg-rose-950/80 text-rose-300';
      case 'HIGH':
        return 'border-amber-500 bg-amber-950/80 text-amber-300';
      case 'MEDIUM':
        return 'border-yellow-500 bg-yellow-950/80 text-yellow-300';
      default:
        return 'border-emerald-500 bg-emerald-950/80 text-emerald-300';
    }
  };

  const getTrendBadge = (direction?: string) => {
    switch (direction) {
      case 'upward':
        return 'border-rose-500 bg-rose-500/10 text-rose-400';
      case 'downward':
        return 'border-emerald-500 bg-emerald-500/10 text-emerald-400';
      default:
        return 'border-sky-500 bg-sky-500/10 text-sky-400';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-medium text-sky-400">AI Predictive Intelligence</p>
          <h2 className="text-2xl font-semibold tracking-tight">Forecasting & Early Warning Engine</h2>
        </div>
        {dashboard?.generated_at && (
          <div className="rounded-full border border-slate-800 bg-slate-900/90 px-3 py-1 text-xs text-slate-400">
            Generated: {new Date(dashboard.generated_at).toLocaleString()}
          </div>
        )}
      </div>

      {isDashboardLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 text-center text-slate-400">
          Loading ML prediction models...
        </div>
      ) : (
        <>
          {/* TOP FORECAST SUMMARY GRID */}
          <div className="grid gap-6 lg:grid-cols-3">
            {/* 1. HOTSPOT FORECAST */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col justify-between rounded-3xl border border-slate-800 bg-gradient-to-b from-slate-900/80 to-slate-950/90 p-6 shadow-xl"
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-rose-400">
                    <Flame size={20} />
                    <h3 className="text-base font-semibold text-slate-100">Crime Hotspot Forecast</h3>
                  </div>
                  {hotspotPred && (
                    <span className="rounded-full border border-rose-500/30 bg-rose-500/10 px-2.5 py-0.5 text-xs text-rose-300 font-medium">
                      Risk: {hotspotPred.risk_percentage}%
                    </span>
                  )}
                </div>

                {hotspotPred ? (
                  <div className="mt-4 space-y-3 text-sm">
                    <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
                      <p className="text-xs text-slate-400 uppercase tracking-wider">High Risk Zone</p>
                      <p className="mt-1 text-base font-semibold text-slate-100">
                        {hotspotPred.district} · {hotspotPred.police_station}
                      </p>
                      <p className="text-xs text-slate-400 mt-0.5">{hotspotPred.crime_type}</p>
                      <div className="mt-3 flex items-center justify-between border-t border-slate-800/80 pt-2 text-xs">
                        <span className="text-slate-400">Expected Incidents</span>
                        <span className="font-semibold text-rose-400 text-sm">
                          {hotspotPred.expected_crime_count} cases
                        </span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/40 p-3 rounded-xl border border-slate-800/50">
                      {hotspotPred.explanation}
                    </p>

                    {/* Historical 7-day Breakdown */}
                    {hotspotPred.historical_data_summary && (
                      <div className="grid grid-cols-2 gap-2 text-xs rounded-xl border border-slate-800/80 bg-slate-950/60 p-3">
                        <div>
                          <span className="text-slate-500 block">Recent 7-Day</span>
                          <span className="font-semibold text-slate-200">
                            {hotspotPred.historical_data_summary.recent_7d}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 block">Previous 7-Day</span>
                          <span className="font-semibold text-slate-200">
                            {hotspotPred.historical_data_summary.previous_7d}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 block">Growth</span>
                          <span className={`font-semibold ${hotspotPred.historical_data_summary.growth_pct >= 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                            {hotspotPred.historical_data_summary.growth_pct > 0 ? '+' : ''}
                            {hotspotPred.historical_data_summary.growth_pct}%
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 block">Model Confidence</span>
                          <span className="font-semibold text-sky-400">
                            {Math.round(hotspotPred.confidence * 100)}%
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="mt-4 text-xs text-slate-400">No hotspot forecast available.</p>
                )}
              </div>
              {hotspotPred?.model_name && (
                <div className="mt-4 text-[10px] text-slate-500 flex justify-between items-center border-t border-slate-800/60 pt-2">
                  <span>Model: {hotspotPred.model_name}</span>
                </div>
              )}
            </motion.div>

            {/* 2. TREND PREDICTION */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="flex flex-col justify-between rounded-3xl border border-slate-800 bg-gradient-to-b from-slate-900/80 to-slate-950/90 p-6 shadow-xl"
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sky-400">
                    <TrendingUp size={20} />
                    <h3 className="text-base font-semibold text-slate-100">Crime Trend Forecast</h3>
                  </div>
                  {trendPred && (
                    <span className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold capitalize ${getTrendBadge(trendPred.trend_direction)}`}>
                      {trendPred.trend_direction} Trend
                    </span>
                  )}
                </div>

                {trendPred ? (
                  <div className="mt-4 space-y-3 text-sm">
                    <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
                      <p className="text-xs text-slate-400 uppercase tracking-wider">
                        Period: {trendPred.period.replace('_', ' ')}
                      </p>
                      <p className="mt-1 text-2xl font-bold text-sky-400">
                        {trendPred.predicted_value} <span className="text-sm font-normal text-slate-300">predicted incidents</span>
                      </p>
                      <div className="mt-2 text-xs text-slate-400 flex items-center gap-2">
                        <BrainCircuit size={14} className="text-sky-400" />
                        Confidence Score: <span className="font-semibold text-slate-200">{Math.round(trendPred.confidence * 100)}%</span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/40 p-3 rounded-xl border border-slate-800/50">
                      {trendPred.explanation}
                    </p>

                    {trendPred.historical_data_summary && (
                      <div className="grid grid-cols-2 gap-2 text-xs rounded-xl border border-slate-800/80 bg-slate-950/60 p-3">
                        <div>
                          <span className="text-slate-500 block">Total Records</span>
                          <span className="font-semibold text-slate-200">
                            {trendPred.historical_data_summary.total_records}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 block">Daily Average</span>
                          <span className="font-semibold text-slate-200">
                            {trendPred.historical_data_summary.average_daily_count} / day
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 block">Recent 7-Day</span>
                          <span className="font-semibold text-slate-200">
                            {trendPred.historical_data_summary.recent_7d}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 block">Growth Pct</span>
                          <span className={`font-semibold ${trendPred.historical_data_summary.growth_pct >= 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                            {trendPred.historical_data_summary.growth_pct}%
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="mt-4 text-xs text-slate-400">No trend forecast available.</p>
                )}
              </div>
              {trendPred?.model_name && (
                <div className="mt-4 text-[10px] text-slate-500 flex justify-between items-center border-t border-slate-800/60 pt-2">
                  <span>Model: {trendPred.model_name}</span>
                </div>
              )}
            </motion.div>

            {/* 3. STATION RISK */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="flex flex-col justify-between rounded-3xl border border-slate-800 bg-gradient-to-b from-slate-900/80 to-slate-950/90 p-6 shadow-xl"
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-amber-400">
                    <ShieldAlert size={20} />
                    <h3 className="text-base font-semibold text-slate-100">Police Station Risk Score</h3>
                  </div>
                  {stationRiskPred && (
                    <span className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold ${getSeverityBadge(stationRiskPred.risk_level)}`}>
                      {stationRiskPred.risk_level} RISK
                    </span>
                  )}
                </div>

                {stationRiskPred ? (
                  <div className="mt-4 space-y-3 text-sm">
                    <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
                      <p className="text-xs text-slate-400 uppercase tracking-wider">Top Risk Station</p>
                      <p className="mt-1 text-base font-semibold text-slate-100">
                        {stationRiskPred.police_station}
                      </p>
                      <p className="text-xs text-slate-400">{stationRiskPred.district}</p>
                      <div className="mt-3 flex items-center justify-between border-t border-slate-800/80 pt-2 text-xs">
                        <span className="text-slate-400">Risk Index Score</span>
                        <span className="font-bold text-amber-400 text-sm">
                          {stationRiskPred.risk_score} / 100
                        </span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/40 p-3 rounded-xl border border-slate-800/50">
                      {stationRiskPred.explanation}
                    </p>
                  </div>
                ) : (
                  <p className="mt-4 text-xs text-slate-400">No station risk assessment available.</p>
                )}
              </div>
              {stationRiskPred?.model_name && (
                <div className="mt-4 text-[10px] text-slate-500 flex justify-between items-center border-t border-slate-800/60 pt-2">
                  <span>Model: {stationRiskPred.model_name}</span>
                  <span>Confidence: {Math.round((stationRiskPred.confidence || 0) * 100)}%</span>
                </div>
              )}
            </motion.div>
          </div>

          {/* EARLY WARNING CARDS & STATION RISK LIST */}
          <div className="grid gap-6 xl:grid-cols-2">
            {/* EARLY WARNING SYSTEM */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl"
            >
              <div className="flex items-center gap-2 text-rose-400 mb-4">
                <AlertOctagon size={20} />
                <h3 className="text-lg font-semibold text-slate-100">Automated Early Warnings</h3>
              </div>

              {isWarningsLoading ? (
                <p className="text-xs text-slate-400">Checking warning triggers...</p>
              ) : warnings.length > 0 ? (
                <div className="space-y-3">
                  {warnings.map((item, index) => (
                    <div
                      key={`${item.title}-${index}`}
                      className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4 text-sm"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <span className="text-xs text-slate-400 font-mono uppercase">{item.category}</span>
                          <h4 className="font-semibold text-slate-100 mt-0.5">{item.title}</h4>
                        </div>
                        <span className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold ${getSeverityBadge(item.severity)}`}>
                          {item.severity}
                        </span>
                      </div>
                      <p className="mt-2 text-xs text-slate-300 leading-normal">{item.reason}</p>
                      <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-800/60 pt-2">
                        <span>Scope: {item.district || 'Statewide'} {item.police_station ? `· ${item.police_station}` : ''}</span>
                        <span>Confidence: {Math.round(item.confidence * 100)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-6 text-center text-sm text-slate-400 flex flex-col items-center gap-2">
                  <CheckCircle2 size={24} className="text-emerald-400" />
                  <span>No active critical early warnings at this time.</span>
                </div>
              )}
            </motion.div>

            {/* STATION RISK TABLE / RANKINGS */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl"
            >
              <div className="flex items-center gap-2 text-amber-400 mb-4">
                <BarChart3 size={20} />
                <h3 className="text-lg font-semibold text-slate-100">Police Station Risk Matrix</h3>
              </div>

              {stationRiskList.length > 0 || hotspotList.length > 0 ? (
                <div className="space-y-3">
                  {(stationRiskList.length > 0 ? stationRiskList : hotspotList).slice(0, 5).map((station: any, idx: number) => (
                    <div
                      key={`${station.police_station}-${idx}`}
                      className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/70 p-3.5 text-xs"
                    >
                      <div>
                        <p className="font-semibold text-slate-200">{station.police_station}</p>
                        <p className="text-[11px] text-slate-400">{station.district}</p>
                      </div>
                      <div className="text-right">
                        <span className={`inline-block rounded-full border px-2 py-0.5 text-[10px] font-semibold ${getSeverityBadge(station.risk_level || (station.risk_percentage > 70 ? 'HIGH' : 'MEDIUM'))}`}>
                          {station.risk_level || `${station.risk_percentage}% Risk`}
                        </span>
                        <p className="text-[10px] text-slate-500 mt-1">
                          Score: {station.risk_score ?? station.risk_percentage} / 100
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-6 text-center text-sm text-slate-400">
                  Station risk matrix data loaded from predictive model.
                </div>
              )}
            </motion.div>
          </div>
        </>
      )}
    </div>
  );
}
