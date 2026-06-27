import { ApplicationCard } from "./ApplicationCard";
import type { ApplicationListItem } from "../types/api";

interface PipelineColumnProps {
  stage: string;
  applications: ApplicationListItem[];
  companySlug: string;
  jobStages: Map<number, string[]>;
  readOnly: boolean;
  onStageChanged: (application: ApplicationListItem) => void;
  onReadOnly: () => void;
}

export function PipelineColumn({
  stage,
  applications,
  companySlug,
  jobStages,
  readOnly,
  onStageChanged,
  onReadOnly,
}: PipelineColumnProps) {
  return (
    <div className="min-w-[220px] flex-1 rounded-lg border border-slate-200 bg-slate-100/80 p-3">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-800">{stage}</h3>
        <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs text-slate-600">
          {applications.length}
        </span>
      </div>
      <div className="space-y-2">
        {applications.map((application) => (
          <ApplicationCard
            key={application.id}
            application={application}
            companySlug={companySlug}
            jobStages={jobStages}
            readOnly={readOnly}
            onStageChanged={onStageChanged}
            onReadOnly={onReadOnly}
          />
        ))}
      </div>
    </div>
  );
}
