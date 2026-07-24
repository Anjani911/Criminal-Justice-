export interface Employee {
  id: number;
  name: string;
  rank: string;
  role: string;
  badge_number: string;
  unit_name: string;
  username: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  employee: Employee;
}

export interface CaseSummary {
  id: number;
  fir_number: string;
  status: string;
  district: string;
  unit_name: string;
  incident_date?: string;
  registered_date?: string;
  crime_head_id: number;
  crime_subhead_id: number;
}

export interface CaseDetail extends CaseSummary {
  brief_facts?: string;
  crime_head?: { id: number; name?: string };
  crime_sub_head?: { id: number; name?: string };
  investigating_officer?: Employee;
  accused_list: Array<{ id: number; name: string; status: string }>;
  victims: Array<{ id: number; name: string; injury_type?: string }>;
  arrests: Array<{ id: number; arrest_type: string }>;
}

export interface DashboardSummary {
  total_cases: number;
  total_accused: number;
  total_victims: number;
  total_arrests: number;
  absconding_accused: number;
  cases_under_investigation: number;
}

export interface MonthlyTrend {
  year: number;
  month: number;
  month_name: string;
  case_count: number;
}

export interface MonthlyStatisticsItem {
  year: number;
  month: number;
  month_name: string;
  case_count: number;
  under_investigation_count: number;
  chargesheeted_count: number;
  closed_count: number;
}

export interface CrimeDistributionItem {
  crime_head?: string;
  crime_subhead?: string;
  case_count: number;
}

export interface YearlySummaryItem {
  year: number;
  case_count: number;
}

export interface StatusBreakdownItem {
  status: string;
  case_count?: number;
  count?: number;
}

export interface AccusedStatusItem {
  status: string;
  count: number;
  case_count?: number;
}

export interface DistrictHotspot {
  district: string;
  case_count: number;
}

export interface UnitHotspot {
  unit: string;
  district: string;
  case_count: number;
}

export interface PoliceStationStats {
  district: string;
  unit: string;
  case_count: number;
  under_investigation_count: number;
  chargesheeted_count: number;
  closed_count: number;
}

export interface NetworkNodeData {
  id: string;
  node_type: 'case' | 'accused' | 'arrest';
  label: string;
  status?: string;
  district?: string;
  unit?: string;
  accused_id?: number;
  case_id?: number;
  arrest_id?: number;
  age?: number;
  gender?: string;
  arrest_date?: string;
  court_name?: string;
}

export interface NetworkNode {
  data: NetworkNodeData;
}

export interface NetworkEdgeData {
  id: string;
  source: string;
  target: string;
  relationship?: string;
  [key: string]: unknown;
}

export interface NetworkEdge {
  data: NetworkEdgeData;
}

export interface NetworkGraph {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  metadata?: {
    node_count: number;
    edge_count: number;
    node_types: Record<string, number>;
  };
}

export interface NetworkMetricNode {
  node_id: string;
  label: string;
  node_type: string;
  degree_centrality: number;
  betweenness_centrality?: number;
}

export interface NetworkMetricsResponse {
  total_nodes: number;
  total_edges: number;
  top_cases: NetworkMetricNode[];
  top_accused: NetworkMetricNode[];
  top_arrests: NetworkMetricNode[];
}

export interface HistoricalSummary {
  total_records: number;
  start_date?: string;
  end_date?: string;
  recent_7d: number;
  previous_7d: number;
  growth_pct: number;
  average_daily_count: number;
}

export interface HotspotPredictionItem {
  district: string;
  police_station: string;
  crime_type: string;
  predicted_hotspot: string;
  expected_crime_count: number;
  risk_percentage: number;
  confidence: number;
  model_name: string;
  explanation: string;
  historical_data_summary?: HistoricalSummary;
}

export interface HotspotPredictionResponse {
  status: string;
  generated_at: string;
  prediction?: HotspotPredictionItem;
  predictions?: HotspotPredictionItem[];
  explanation?: string;
}

export interface TrendPredictionItem {
  period: 'next_week' | 'next_month';
  predicted_value: number;
  trend_direction: 'upward' | 'downward' | 'stable';
  confidence: number;
  model_name: string;
  explanation: string;
  historical_data_summary?: HistoricalSummary;
}

export interface TrendPredictionResponse {
  status: string;
  generated_at: string;
  prediction?: TrendPredictionItem;
  explanation?: string;
}

export interface StationRiskItem {
  district: string;
  police_station: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence: number;
  model_name: string;
  explanation: string;
  historical_data_summary?: HistoricalSummary;
}

export interface StationRiskResponse {
  status: string;
  generated_at: string;
  prediction?: StationRiskItem;
  predictions?: StationRiskItem[];
  explanation?: string;
}

export interface WarningItem {
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  title: string;
  category: string;
  district?: string;
  police_station?: string;
  reason: string;
  timestamp: string;
  confidence: number;
}

export interface WarningResponse {
  status: string;
  generated_at: string;
  warnings: WarningItem[];
  explanation?: string;
}

export interface PredictionDashboardResponse {
  status: string;
  generated_at: string;
  hotspot_forecast?: HotspotPredictionResponse;
  trend_forecast?: TrendPredictionResponse;
  station_risk?: StationRiskResponse;
  warnings?: WarningResponse;
}

export interface ReportResponse {
  report_type: string;
  generated_at: string;
  storage_provider: string;
  storage_key: string;
  file_name: string;
  download_url?: string;
  metadata?: Record<string, unknown>;
}
