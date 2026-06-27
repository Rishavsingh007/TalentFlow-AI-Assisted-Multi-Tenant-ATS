import { apiRequest } from "./client";
import type { ApplicationDetail, ApplicationListItem, Paginated } from "../types/api";

export function fetchApplications(
  companySlug: string,
  page = 1,
): Promise<Paginated<ApplicationListItem>> {
  const query = page > 1 ? `?page=${page}` : "";
  return apiRequest<Paginated<ApplicationListItem>>(
    `/api/v1/companies/${companySlug}/applications/${query}`,
    { auth: true },
  );
}

export async function fetchAllApplications(
  companySlug: string,
): Promise<ApplicationListItem[]> {
  const all: ApplicationListItem[] = [];
  let page = 1;
  for (;;) {
    const data = await fetchApplications(companySlug, page);
    all.push(...data.results);
    if (!data.next) break;
    page += 1;
  }
  return all;
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
