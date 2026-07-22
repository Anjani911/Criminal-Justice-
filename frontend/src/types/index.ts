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
  count: number;
}

export interface AccusedStatusItem {
  status: string;
  count: number;
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

export interface Person {
  id: number;
  name: string;
  status?: string;
  [key: string]: unknown;
}

export interface Victim {
  id: number;
  name: string;
  injury_type?: string;
  [key: string]: unknown;
}

export interface HealthStatus {
  status: string;
  environment?: string;
  database?: string;
}

export interface VersionInfo {
  project: string;
  version: string;
  api_version: string;
}

export interface NetworkGraph {
  nodes?: Array<Record<string, unknown>>;
  edges?: Array<Record<string, unknown>>;
  [key: string]: unknown;
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
