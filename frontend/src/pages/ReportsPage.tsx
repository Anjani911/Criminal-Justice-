import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { reportService } from '@/services/report.service';
import { motion } from 'framer-motion';

export default function ReportsPage() {
  const [payload, setPayload] = useState({ report_type: 'dashboard', district: '', year: 2026, ai_summary: '' });
  const mutation = useMutation({
    mutationFn: (value: Record<string, unknown>) => reportService.generateReport(value),
  });
  const { data: districtReport } = useQuery({ queryKey: ['districtReport'], queryFn: () => reportService.getDistrictReport('Bengaluru', 2026) });
  const { data: dashboardReport } = useQuery({ queryKey: ['dashboardReport'], queryFn: reportService.getDashboardReport });

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-sky-400">Reporting module</p>
        <h2 className="text-2xl font-semibold">Generate and review reports</h2>
      </div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
        <div className="grid gap-4 md:grid-cols-2">
          <select value={payload.report_type} onChange={(e) => setPayload({ ...payload, report_type: e.target.value })} className="rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-3 text-sm">
            <option value="dashboard">Dashboard</option>
            <option value="district_summary">District Summary</option>
            <option value="case_investigation">Case Investigation</option>
          </select>
          <input value={payload.district} onChange={(e) => setPayload({ ...payload, district: e.target.value })} placeholder="District" className="rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-3 text-sm" />
        </div>
        <textarea value={payload.ai_summary} onChange={(e) => setPayload({ ...payload, ai_summary: e.target.value })} placeholder="Optional AI summary" className="mt-4 min-h-24 w-full rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-3 text-sm" />
        <button onClick={() => mutation.mutate(payload)} className="mt-4 rounded-xl bg-sky-600 px-4 py-3 text-sm font-semibold text-white">
          Generate report
        </button>
        {mutation.data ? <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-950/60 p-4 text-sm text-slate-300">{mutation.data.file_name}</div> : null}
      </motion.div>

      <div className="grid gap-6 xl:grid-cols-2">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <h3 className="text-lg font-semibold">District report</h3>
          <p className="mt-3 text-sm text-slate-400">{districtReport ? `Generated ${districtReport.report_type ?? 'district report'}` : 'Load a district report from the backend.'}</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
          <h3 className="text-lg font-semibold">Dashboard report</h3>
          <p className="mt-3 text-sm text-slate-400">{dashboardReport ? `Generated ${dashboardReport.report_type ?? 'dashboard report'}` : 'Load a dashboard report from the backend.'}</p>
        </motion.div>
      </div>
    </div>
  );
}
