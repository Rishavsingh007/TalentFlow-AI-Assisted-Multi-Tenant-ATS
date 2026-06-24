import { useState } from "react";
import { ApiError } from "../api/client";
import { moveApplicationStage } from "../api/applications";
import type { ApplicationListItem } from "../types/api";

interface ApplicationCardProps {
  application: ApplicationListItem;
  companySlug: string;
  pipelineStages: readonly string[];
  readOnly: boolean;
  onStageChanged: (application: ApplicationListItem) => void;
  onReadOnly: () => void;
}

export function ApplicationCard({
  application,
  companySlug,
  pipelineStages,
  readOnly,
  onStageChanged,
  onReadOnly,
}: ApplicationCardProps) {
  const [moving, setMoving] = useState(false);
  const [pendingStage, setPendingStage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const displayStage = pendingStage ?? application.current_stage;

  const handleStageChange = async (newStage: string) => {
    if (newStage === application.current_stage || readOnly) return;

    setError(null);
    setPendingStage(newStage);
    setMoving(true);
    try {
      const updated = await moveApplicationStage(
        companySlug,
        application.id,
        newStage,
      );
      onStageChanged({
        ...application,
        current_stage: updated.current_stage,
        status: updated.status,
        ai_score: updated.ai_score,
        ai_summary: updated.ai_summary,
      });
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        onReadOnly();
        setError("Read-only — your role cannot move stages.");
      } else {
        setError(err instanceof ApiError ? err.message : "Failed to move stage.");
      }
    } finally {
      setPendingStage(null);
      setMoving(false);
    }
  };

  return (
    <div className="rounded-md border border-slate-200 bg-white p-3 shadow-sm">
      <div className="mb-1 font-medium text-slate-900">{application.candidate.full_name}</div>
      <div className="mb-1 text-xs text-slate-500">{application.candidate.email}</div>
      <div className="mb-2 text-xs text-slate-600">{application.job.title}</div>
      <div className="mb-2 flex items-center justify-between text-xs">
        <span className="text-slate-500">AI score</span>
        <span className="font-medium text-slate-800">
          {application.ai_score !== null ? application.ai_score : "Scoring…"}
        </span>
      </div>
      {application.ai_summary && (
        <p className="mb-2 line-clamp-2 text-xs text-slate-500">{application.ai_summary}</p>
      )}
      <select
        value={displayStage}
        disabled={moving || readOnly}
        onChange={(e) => void handleStageChange(e.target.value)}
        className="w-full rounded border border-slate-300 px-2 py-1 text-xs disabled:opacity-50"
      >
        {pipelineStages.map((stage) => (
          <option key={stage} value={stage}>
            {stage}
          </option>
        ))}
      </select>
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}
