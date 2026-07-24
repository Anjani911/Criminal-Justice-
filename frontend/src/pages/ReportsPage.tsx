import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { reportService } from '@/services/report.service';
import { motion } from 'framer-motion';
import { FileText, Download, Sparkles, Building, BarChart2, ShieldCheck } from 'lucide-react';
import type { ReportResponse } from '@/types';

export default function ReportsPage() {
  const [payload, setPayload] = useState({
    report_type: 'dashboard',
    district: 'Bengaluru',
    year: 2026,
    case_id: 1,
    ai_summary: '',
  });

  const mutation = useMutation<ReportResponse, Error, Record<string, unknown>>({
    mutationFn: (value) => reportService.generateReport(value),
  });

  const { data: districtReport, isLoading: isDistrictLoading } = useQuery({
    queryKey: ['districtReport', payload.district, payload.year],
    queryFn: () => reportService.getDistrictReport(payload.district || 'Bengaluru', payload.year),
  });

  const { data: dashboardReport, isLoading: isDashboardLoading } = useQuery({
    queryKey: ['dashboardReport'],
    queryFn: reportService.getDashboardReport,
  });

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm font-medium text-sky-400">Intelligence Reporting Module</p>
        <h2 className="text-2xl font-semibold tracking-tight">Generate & Export Investigation Reports</h2>
      </div>

      {/* GENERATOR CARD */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl space-y-4"
      >
        <div className="flex items-center gap-2 text-sky-400">
          <FileText size={20} />
          <h3 className="text-lg font-semibold text-slate-100">Report Generator</h3>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <div>
            <label className="text-xs text-slate-400 block mb-1">Report Type</label>
            <select
              value={payload.report_type}
              onChange={(e) => setPayload({ ...payload, report_type: e.target.value })}
              className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-3 py-2.5 text-xs text-slate-200 outline-none focus:border-sky-500"
            >
              <option value="dashboard">Dashboard Summary Report</option>
              <option value="district_summary">District Crime Report</option>
              <option value="case_investigation">Case Investigation Report</option>
            </select>
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">District Scope</label>
            <input
              value={payload.district}
              onChange={(e) => setPayload({ ...payload, district: e.target.value })}
              placeholder="e.g. Bengaluru"
              className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-3 py-2 text-xs text-slate-200 outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Calendar Year</label>
            <input
              type="number"
              value={payload.year}
              onChange={(e) => setPayload({ ...payload, year: parseInt(e.target.value) || 2026 })}
              className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-3 py-2 text-xs text-slate-200 outline-none focus:border-sky-500"
            />
          </div>

          {payload.report_type === 'case_investigation' && (
            <div>
              <label className="text-xs text-slate-400 block mb-1">FIR Case ID</label>
              <input
                type="number"
                value={payload.case_id}
                onChange={(e) => setPayload({ ...payload, case_id: parseInt(e.target.value) || 1 })}
                className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-3 py-2 text-xs text-slate-200 outline-none focus:border-sky-500"
              />
            </div>
          )}
        </div>

        <div>
          <label className="text-xs text-slate-400 block mb-1">Custom Executive Summary / Notes</label>
          <textarea
            value={payload.ai_summary}
            onChange={(e) => setPayload({ ...payload, ai_summary: e.target.value })}
            placeholder="Add optional notes or AI summary details..."
            className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-3 py-2 text-xs text-slate-200 outline-none focus:border-sky-500 min-h-[70px]"
          />
        </div>

        <button
          onClick={() => mutation.mutate(payload)}
          disabled={mutation.isPending}
          className="flex items-center gap-2 rounded-xl bg-sky-600 px-5 py-2.5 text-xs font-semibold text-white shadow-lg transition hover:bg-sky-500 disabled:opacity-50"
        >
          <Sparkles size={16} />
          {mutation.isPending ? 'Generating Report PDF...' : 'Generate Official PDF Report'}
        </button>

        {/* Mutation Result Output */}
        {mutation.data && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 rounded-2xl border border-emerald-500/30 bg-emerald-950/30 p-4 text-xs space-y-2"
          >
            <div className="flex items-center justify-between">
              <span className="font-semibold text-emerald-300 flex items-center gap-2">
                <FileText size={16} /> Report PDF Generated Successfully
              </span>
              {mutation.data.download_url && (
                <a
                  href={mutation.data.download_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1 text-sky-400 hover:underline font-semibold"
                >
                  <Download size={14} /> Download PDF
                </a>
              )}
            </div>
            <div className="grid grid-cols-2 gap-2 text-slate-300 sm:grid-cols-4 pt-1">
              <div><span className="text-slate-500 block">File Name</span>{mutation.data.file_name}</div>
              <div><span className="text-slate-500 block">Report Type</span>{mutation.data.report_type}</div>
              <div><span className="text-slate-500 block">Storage Provider</span>{mutation.data.storage_provider}</div>
              <div><span className="text-slate-500 block">Generated At</span>{new Date(mutation.data.generated_at).toLocaleString()}</div>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* REPORT PREVIEWS GRID */}
      <div className="grid gap-6 xl:grid-cols-2">
        {/* District Summary Preview */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl space-y-4"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sky-400">
              <Building size={18} />
              <h3 className="text-base font-semibold text-slate-100">District Report Data Payload</h3>
            </div>
            <span className="text-xs text-slate-400 font-mono">{payload.district} ({payload.year})</span>
          </div>

          {isDistrictLoading ? (
            <p className="text-xs text-slate-400">Loading district report data...</p>
          ) : districtReport ? (
            <div className="space-y-3 text-xs">
              <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-3.5 space-y-2">
                <p className="font-semibold text-sky-300">Executive Summary</p>
                <p className="text-slate-300 leading-relaxed">{districtReport.ai_summary || 'No AI summary generated.'}</p>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                  <span className="text-slate-500 block">Total District Cases</span>
                  <span className="text-base font-bold text-slate-100">
                    {districtReport.dashboard_kpis?.total_cases ?? 0}
                  </span>
                </div>
                <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                  <span className="text-slate-500 block">Cases Under Investigation</span>
                  <span className="text-base font-bold text-amber-400">
                    {districtReport.dashboard_kpis?.cases_under_investigation ?? 0}
                  </span>
                </div>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 flex justify-between items-center text-slate-400">
                <span>Monthly Trends Records: {districtReport.monthly_trends?.length ?? 0}</span>
                <span>Unit Hotspots: {districtReport.unit_hotspots?.length ?? 0}</span>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-400">No district report payload returned.</p>
          )}
        </motion.div>

        {/* Dashboard Summary Preview */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl space-y-4"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sky-400">
              <BarChart2 size={18} />
              <h3 className="text-base font-semibold text-slate-100">State Dashboard Report Data</h3>
            </div>
            <span className="text-xs text-emerald-400 flex items-center gap-1">
              <ShieldCheck size={14} /> Live Sync
            </span>
          </div>

          {isDashboardLoading ? (
            <p className="text-xs text-slate-400">Loading dashboard report data...</p>
          ) : dashboardReport ? (
            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                  <span className="text-slate-500 block">Total FIRs</span>
                  <span className="text-base font-bold text-slate-100">{dashboardReport.kpis?.total_cases ?? 0}</span>
                </div>
                <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                  <span className="text-slate-500 block">Accused</span>
                  <span className="text-base font-bold text-amber-400">{dashboardReport.kpis?.total_accused ?? 0}</span>
                </div>
                <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                  <span className="text-slate-500 block">Victims</span>
                  <span className="text-base font-bold text-emerald-400">{dashboardReport.kpis?.total_victims ?? 0}</span>
                </div>
                <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                  <span className="text-slate-500 block">Arrests</span>
                  <span className="text-base font-bold text-purple-400">{dashboardReport.kpis?.total_arrests ?? 0}</span>
                </div>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-slate-300 space-y-1">
                <div className="flex justify-between">
                  <span>District Hotspot Zones:</span>
                  <span className="font-semibold text-sky-400">{dashboardReport.district_hotspots?.length ?? 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>Crime Categories Tracked:</span>
                  <span className="font-semibold text-sky-400">{dashboardReport.crime_type_distribution?.length ?? 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>Network Nodes in Graph:</span>
                  <span className="font-semibold text-sky-400">{dashboardReport.network_metrics?.total_nodes ?? 0}</span>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-400">No dashboard report payload returned.</p>
          )}
        </motion.div>
      </div>
    </div>
  );
}
