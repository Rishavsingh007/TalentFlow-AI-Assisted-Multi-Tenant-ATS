import { apiRequest } from "./client";
import type { Company } from "../types/api";

export function fetchCompany(slug: string): Promise<Company> {
  return apiRequest<Company>(`/api/v1/companies/${slug}/`, { auth: true });
}
