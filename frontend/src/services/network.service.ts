import api from '@/api/client';
import type { NetworkGraph } from '@/types';

export const networkService = {
  async getFullNetwork(): Promise<NetworkGraph> {
    const { data } = await api.get<NetworkGraph>('/network');
    return data;
  },

  async getMetrics() {
    const { data } = await api.get('/network/metrics');
    return data;
  },

  async getCaseNetwork(caseId: number): Promise<NetworkGraph> {
    const { data } = await api.get<NetworkGraph>(`/network/case/${caseId}`);
    return data;
  },

  async getAccusedNetwork(accusedId: number): Promise<NetworkGraph> {
    const { data } = await api.get<NetworkGraph>(`/network/accused/${accusedId}`);
    return data;
  },
};
