import { apiRequest } from "./client";
import type { ApplicationCreated, Paginated, PublicJob } from "../types/api";

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
