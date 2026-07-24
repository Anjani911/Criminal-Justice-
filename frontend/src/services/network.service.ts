import api from '@/api/client';
import type { NetworkGraph, NetworkMetricsResponse } from '@/types';

export const networkService = {
  async getFullNetwork(): Promise<NetworkGraph> {
    const { data } = await api.get<NetworkGraph>('/network');
    return data;
  },

  async getMetrics(): Promise<NetworkMetricsResponse> {
    const { data } = await api.get<NetworkMetricsResponse>('/network/metrics');
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
