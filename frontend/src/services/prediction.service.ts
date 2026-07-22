import api from '@/api/client';

export const predictionService = {
  async getDashboard() {
    const { data } = await api.get('/predictions/dashboard');
    return data;
  },

  async getHotspots(params?: Record<string, unknown>) {
    const { data } = await api.get('/predictions/hotspots', { params });
    return data;
  },

  async getTrends(params?: Record<string, unknown>) {
    const { data } = await api.get('/predictions/trends', { params });
    return data;
  },

  async getStationRisk(params?: Record<string, unknown>) {
    const { data } = await api.get('/predictions/station-risk', { params });
    return data;
  },

  async getWarnings(params?: Record<string, unknown>) {
    const { data } = await api.get('/predictions/warnings', { params });
    return data;
  },
};
