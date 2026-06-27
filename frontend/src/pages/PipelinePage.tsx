import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchAllApplications } from "../api/applications";
import { fetchCompanyJobs } from "../api/jobs";
import { PipelineColumn } from "../components/PipelineColumn";
import { useWebSocket } from "../hooks/useWebSocket";
import type { ApplicationListItem, DashboardEvent, Job } from "../types/api";
import { DEFAULT_PIPELINE_STAGES } from "../types/api";

function statusLabel(status: string): string {
  if (status === "connected") return "Connected";
  if (status === "reconnecting") return "Reconnecting…";
  return "Offline";
}

function statusColor(status: string): string {
  if (status === "connected") return "bg-green-100 text-green-800";
  if (status === "reconnecting") return "bg-amber-100 text-amber-800";
  return "bg-slate-200 text-slate-700";
}

function buildJobStagesMap(jobs: Job[]): Map<number, string[]> {
  const map = new Map<number, string[]>();
  for (const job of jobs) {
    map.set(job.id, job.pipeline_stages);
  }
  return map;
}

function buildColumnStages(jobs: Job[]): string[] {
  const seen = new Set<string>();
  const stages: string[] = [];
  for (const job of jobs) {
    for (const stage of job.pipeline_stages) {
      if (!seen.has(stage)) {
        seen.add(stage);
        stages.push(stage);
      }
    }
  }
  return stages.length > 0 ? stages : [...DEFAULT_PIPELINE_STAGES];
}

export function PipelinePage() {
  const { companySlug = "" } = useParams();
  const [applications, setApplications] = useState<ApplicationListItem[]>([]);
  const [jobStages, setJobStages] = useState<Map<number, string[]>>(new Map());
  const [columnStages, setColumnStages] = useState<string[]>([
    ...DEFAULT_PIPELINE_STAGES,
  ]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [readOnly, setReadOnly] = useState(false);

  const loadPipeline = useCallback(async () => {
    if (!companySlug) return;
    setLoading(true);
    setError(null);
    try {
      const [apps, jobsData] = await Promise.all([
        fetchAllApplications(companySlug),
        fetchCompanyJobs(companySlug),
      ]);
      setApplications(apps);
      setJobStages(buildJobStagesMap(jobsData.results));
      setColumnStages(buildColumnStages(jobsData.results));
    } catch {
      setError("Failed to load applications.");
    } finally {
      setLoading(false);
    }
  }, [companySlug]);

  useEffect(() => {
    void loadPipeline();
  }, [loadPipeline]);

  const handleDashboardEvent = useCallback((event: DashboardEvent) => {
    setApplications((prev) => {
      if (event.event === "application.received") {
        if (prev.some((app) => app.id === event.application_id)) return prev;
        const newApp: ApplicationListItem = {
          id: event.application_id,
          candidate: {
            full_name: event.candidate_name,
            email: event.candidate_email,
            phone: "",
          },
          job: { id: event.job_id, title: event.job_title },
          current_stage: event.current_stage,
          status: "active",
          ai_score: null,
          applied_at: event.timestamp,
        };
        return [newApp, ...prev];
      }

      if (event.event === "application.scored") {
        return prev.map((app) =>
          app.id === event.application_id
            ? { ...app, ai_score: event.ai_score, ai_summary: event.ai_summary }
            : app,
        );
      }

      if (event.event === "application.stage_changed") {
        return prev.map((app) =>
          app.id === event.application_id
            ? { ...app, current_stage: event.to_stage }
            : app,
        );
      }

      return prev;
    });
  }, []);

  const wsStatus = useWebSocket({
    companySlug,
    enabled: Boolean(companySlug),
    onEvent: handleDashboardEvent,
  });

  const grouped = useMemo(() => {
    const map = new Map<string, ApplicationListItem[]>();
    for (const stage of columnStages) {
      map.set(stage, []);
    }
    for (const app of applications) {
      const list = map.get(app.current_stage);
      if (list) {
        list.push(app);
      } else {
        map.set(app.current_stage, [app]);
      }
    }
    return map;
  }, [applications, columnStages]);

  const handleStageChanged = (updated: ApplicationListItem) => {
    setApplications((prev) =>
      prev.map((app) => (app.id === updated.id ? updated : app)),
    );
  };

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Recruiter pipeline</h1>
          <p className="text-sm text-slate-600">{companySlug}</p>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`rounded-full px-2.5 py-1 text-xs font-medium ${statusColor(wsStatus)}`}
          >
            {statusLabel(wsStatus)}
          </span>
          <button
            type="button"
            onClick={() => void loadPipeline()}
            className="rounded-md border border-slate-300 px-3 py-1 text-sm hover:bg-slate-50"
          >
            Refresh
          </button>
        </div>
      </div>

      {loading && <p className="text-sm text-slate-500">Loading pipeline…</p>}
      {error && (
        <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
      )}

      {!loading && !error && (
        <div className="flex gap-3 overflow-x-auto pb-4">
          {columnStages.map((stage) => (
            <PipelineColumn
              key={stage}
              stage={stage}
              applications={grouped.get(stage) ?? []}
              companySlug={companySlug}
              jobStages={jobStages}
              readOnly={readOnly}
              onStageChanged={handleStageChanged}
              onReadOnly={() => setReadOnly(true)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
