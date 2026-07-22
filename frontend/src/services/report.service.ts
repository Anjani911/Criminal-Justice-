import api from '@/api/client';
import type { ReportResponse } from '@/types';

export const reportService = {
  async generateReport(payload: Record<string, unknown>) {
    const { data } = await api.post<ReportResponse>('/report', payload);
    return data;
  },

  async getCaseReport(caseId: number) {
    const { data } = await api.get(`/reports/case/${caseId}`);
    return data;
  },

  async getDistrictReport(district: string, year?: number) {
    const { data } = await api.get(`/reports/district`, { params: { district, year } });
    return data;
  },

  async getDashboardReport() {
    const { data } = await api.get('/reports/dashboard');
    return data;
  },
};
