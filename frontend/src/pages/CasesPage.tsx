import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { casesService } from '@/services/cases.service';
import { motion } from 'framer-motion';

export default function CasesPage() {
  const [statusFilter, setStatusFilter] = useState('');
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['cases', statusFilter],
    queryFn: () => casesService.listCases({ status: statusFilter || undefined, limit: 10 }),
  });

  const mutation = useMutation({
    mutationFn: ({ caseId, status }: { caseId: number; status: string }) => casesService.updateCaseStatus(caseId, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['cases'] }),
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm text-sky-400">Case operations</p>
          <h2 className="text-2xl font-semibold">FIR case workspace</h2>
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm">
          <option value="">All statuses</option>
          <option value="Under Investigation">Under Investigation</option>
          <option value="Chargesheeted">Chargesheeted</option>
          <option value="Closed">Closed</option>
        </select>
      </div>

      <div className="space-y-3">
        {isLoading ? (
          <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 text-slate-400">Loading cases…</div>
        ) : (
          data?.cases?.map((item) => (
            <motion.div key={item.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p className="text-sm text-sky-400">{item.fir_number}</p>
                  <h3 className="text-lg font-semibold">{item.district} · {item.unit_name}</h3>
                  <p className="mt-2 text-sm text-slate-400">Crime head {item.crime_head_id} / subhead {item.crime_subhead_id}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-sm text-slate-300">{item.status}</span>
                  <button onClick={() => mutation.mutate({ caseId: item.id, status: 'Chargesheeted' })} className="rounded-xl bg-sky-600 px-3 py-2 text-sm font-medium text-white">Advance status</button>
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
}
