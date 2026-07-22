import api from '@/api/client';
import type { AccusedStatusItem, CrimeDistributionItem, DashboardSummary, DistrictHotspot, MonthlyStatisticsItem, MonthlyTrend, PoliceStationStats, StatusBreakdownItem, UnitHotspot, YearlySummaryItem } from '@/types';

export const analyticsService = {
  async getDashboardSummary(): Promise<DashboardSummary> {
    const { data } = await api.get<DashboardSummary>('/analytics/dashboard');
    return data;
  },

  async getCrimeTrends(year?: number): Promise<MonthlyTrend[]> {
    const { data } = await api.get<MonthlyTrend[]>('/analytics/crime-trends', { params: { year } });
    return data;
  },

  async getMonthlyStatistics(year?: number): Promise<MonthlyStatisticsItem[]> {
    const { data } = await api.get<MonthlyStatisticsItem[]>('/analytics/monthly-statistics', { params: { year } });
    return data;
  },

  async getYearlySummary(): Promise<YearlySummaryItem[]> {
    const { data } = await api.get<YearlySummaryItem[]>('/analytics/yearly-summary');
    return data;
  },

  async getCrimeTypes(): Promise<CrimeDistributionItem[]> {
    const { data } = await api.get<CrimeDistributionItem[]>('/analytics/crime-types');
    return data;
  },

  async getHotspots(district?: string): Promise<{ district_hotspots: DistrictHotspot[]; unit_hotspots: UnitHotspot[] }> {
    const { data } = await api.get<{ district_hotspots: DistrictHotspot[]; unit_hotspots: UnitHotspot[] }>('/analytics/hotspots', { params: { district } });
    return data;
  },

  async getPoliceStations(district?: string): Promise<PoliceStationStats[]> {
    const { data } = await api.get<PoliceStationStats[]>('/analytics/police-stations', { params: { district } });
    return data;
  },

  async getStatusBreakdown(): Promise<StatusBreakdownItem[]> {
    const { data } = await api.get<StatusBreakdownItem[]>('/analytics/status');
    return data;
  },

  async getAccusedStatusBreakdown(): Promise<AccusedStatusItem[]> {
    const { data } = await api.get<AccusedStatusItem[]>('/analytics/accused-status');
    return data;
  },
};
