export const DEFAULT_PIPELINE_STAGES = [
  "Applied",
  "Screening",
  "Interview",
  "Offer",
  "Hired",
  "Rejected",
] as const;

export const TERMINAL_STAGES = ["Hired", "Rejected"] as const;

export type EmploymentType = "full_time" | "part_time" | "contract" | "internship";
export type JobStatus = "draft" | "open" | "closed" | "archived";
export type ApplicationStatus = "active" | "rejected" | "withdrawn" | "hired";

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface WsTicketResponse {
  ticket: string;
  expires_in: number;
}

export interface Company {
  id: number;
  name: string;
  slug: string;
  industry: string;
  is_active: boolean;
  created_at: string;
}

export interface PublicJob {
  id: number;
  title: string;
  description: string;
  department: string;
  location: string;
  employment_type: EmploymentType;
  company_name: string;
  company_slug: string;
  created_at: string;
}

export interface Job {
  id: number;
  title: string;
  description: string;
  department: string;
  location: string;
  employment_type: EmploymentType;
  status: JobStatus;
  pipeline_stages: string[];
  created_at: string;
  updated_at: string;
}

export interface ApplicantSnapshot {
  full_name: string;
  email: string;
  phone: string;
}

export interface JobSummary {
  id: number;
  title: string;
}

export interface ApplicationListItem {
  id: number;
  candidate: ApplicantSnapshot;
  job: JobSummary;
  current_stage: string;
  status: ApplicationStatus;
  ai_score: number | null;
  applied_at: string;
  ai_summary?: string;
}

export interface ApplicationDetail extends ApplicationListItem {
  ai_summary: string;
  pipeline_stages: string[];
}

export interface ApplicationCreated {
  id: number;
  job_id: number;
  current_stage: string;
  applied_at: string;
}

export interface AuditLog {
  id: number;
  action: string;
  object_type: string;
  object_id: number;
  metadata: Record<string, unknown>;
  actor_email: string | null;
  timestamp: string;
}

export interface ApplicationReceivedEvent {
  event: "application.received";
  application_id: number;
  job_id: number;
  job_title: string;
  candidate_name: string;
  candidate_email: string;
  current_stage: string;
  timestamp: string;
}

export interface ApplicationScoredEvent {
  event: "application.scored";
  application_id: number;
  ai_score: number | null;
  ai_summary: string;
  timestamp: string;
}

export interface ApplicationStageChangedEvent {
  event: "application.stage_changed";
  application_id: number;
  from_stage: string;
  to_stage: string;
  actor: string | null;
  timestamp: string;
}

export type DashboardEvent =
  | ApplicationReceivedEvent
  | ApplicationScoredEvent
  | ApplicationStageChangedEvent;

export type WsConnectionStatus = "connected" | "reconnecting" | "offline";
