import { useAuth } from '@/context/AuthContext';
import { motion } from 'framer-motion';

export default function ProfilePage() {
  const { employee } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-sky-400">User profile</p>
        <h2 className="text-2xl font-semibold">Account and unit details</h2>
      </div>

      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
            <p className="text-sm text-slate-400">Name</p>
            <p className="mt-2 text-lg font-semibold">{employee?.name}</p>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
            <p className="text-sm text-slate-400">Role</p>
            <p className="mt-2 text-lg font-semibold">{employee?.role}</p>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
            <p className="text-sm text-slate-400">Badge number</p>
            <p className="mt-2 text-lg font-semibold">{employee?.badge_number}</p>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
            <p className="text-sm text-slate-400">Unit</p>
            <p className="mt-2 text-lg font-semibold">{employee?.unit_name}</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
