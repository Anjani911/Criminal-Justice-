import { useQuery } from '@tanstack/react-query';
import api from '@/api/client';

export default function AuditPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['audit'],
    queryFn: async () => {
      const { data } = await api.get('/audit');
      return data;
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-sky-400">Audit trail</p>
        <h2 className="text-2xl font-semibold">Administrative activity history</h2>
      </div>
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
        {isLoading ? <p className="text-slate-400">Loading audit history…</p> : (data?.logs ?? []).map((item: any, index: number) => (
          <div key={`${item.action}-${index}`} className="mb-3 rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="font-medium">{item.action}</span>
              <span className="text-sky-300">{item.status}</span>
            </div>
            <p className="mt-2 text-slate-400">{item.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
