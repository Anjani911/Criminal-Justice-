import api from '@/api/client';
import type { CaseDetail, CaseSummary } from '@/types';

export const casesService = {
  async listCases(params?: Record<string, unknown>) {
    const { data } = await api.get<{ cases: CaseSummary[]; total: number; skip: number; limit: number }>('/cases', { params });
    return data;
  },

  async getCaseById(caseId: number) {
    const { data } = await api.get<CaseDetail>(`/cases/${caseId}`);
    return data;
  },

  async createCase(payload: Record<string, unknown>) {
    const { data } = await api.post<CaseDetail>('/cases', payload);
    return data;
  },

  async updateCaseStatus(caseId: number, status: string) {
    const { data } = await api.patch<CaseDetail>(`/cases/${caseId}/status`, { status });
    return data;
  },
};
