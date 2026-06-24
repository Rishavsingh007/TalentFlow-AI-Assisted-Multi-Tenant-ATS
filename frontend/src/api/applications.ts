import { apiRequest } from "./client";
import type { ApplicationDetail, ApplicationListItem, Paginated } from "../types/api";

export function fetchApplications(
  companySlug: string,
): Promise<Paginated<ApplicationListItem>> {
  return apiRequest<Paginated<ApplicationListItem>>(
    `/api/v1/companies/${companySlug}/applications/`,
    { auth: true },
  );
}

export function moveApplicationStage(
  companySlug: string,
  applicationId: number,
  currentStage: string,
): Promise<ApplicationDetail> {
  return apiRequest<ApplicationDetail>(
    `/api/v1/companies/${companySlug}/applications/${applicationId}/stage/`,
    {
      method: "PATCH",
      auth: true,
      body: { current_stage: currentStage },
    },
  );
}
