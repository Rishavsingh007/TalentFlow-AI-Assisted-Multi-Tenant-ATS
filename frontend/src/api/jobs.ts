import { apiRequest } from "./client";
import type { ApplicationCreated, Job, Paginated, PublicJob } from "../types/api";

export function fetchCompanyJobs(companySlug: string): Promise<Paginated<Job>> {
  return apiRequest<Paginated<Job>>(`/api/v1/companies/${companySlug}/jobs/`, {
    auth: true,
  });
}

export function fetchPublicJobs(): Promise<Paginated<PublicJob>> {
  return apiRequest<Paginated<PublicJob>>("/api/v1/jobs/");
}

export function applyToJob(
  jobId: number,
  formData: FormData,
): Promise<ApplicationCreated> {
  return apiRequest<ApplicationCreated>(`/api/v1/jobs/${jobId}/apply/`, {
    method: "POST",
    body: formData,
  });
}
