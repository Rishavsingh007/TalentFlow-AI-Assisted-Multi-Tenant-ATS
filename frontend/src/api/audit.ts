import { apiRequest } from "./client";
import type { AuditLog, Paginated } from "../types/api";

export interface AuditLogFilters {
  action?: string;
  page?: number;
}

export function fetchAuditLogs(
  companySlug: string,
  filters: AuditLogFilters = {},
): Promise<Paginated<AuditLog>> {
  const params = new URLSearchParams();
  if (filters.action) params.set("action", filters.action);
  if (filters.page) params.set("page", String(filters.page));
  const query = params.toString();
  const path = `/api/v1/companies/${companySlug}/audit-logs/${query ? `?${query}` : ""}`;
  return apiRequest<Paginated<AuditLog>>(path, { auth: true });
}
