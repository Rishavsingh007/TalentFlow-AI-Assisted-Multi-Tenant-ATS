import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchAuditLogs } from "../api/audit";
import { AuditLogRow } from "../components/AuditLogRow";
import type { AuditLog } from "../types/api";

const ACTION_FILTERS = [
  { value: "", label: "All actions" },
  { value: "application.submitted", label: "application.submitted" },
  { value: "application.stage_changed", label: "application.stage_changed" },
  { value: "application.scored", label: "application.scored" },
  { value: "application.scoring_failed", label: "application.scoring_failed" },
  { value: "job.published", label: "job.published" },
];

export function AuditPage() {
  const { companySlug = "" } = useParams();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [actionFilter, setActionFilter] = useState("");
  const [page, setPage] = useState(1);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadLogs = useCallback(async () => {
    if (!companySlug) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAuditLogs(companySlug, {
        action: actionFilter || undefined,
        page,
      });
      setLogs(data.results);
      setCount(data.count);
    } catch {
      setError("Failed to load audit logs.");
    } finally {
      setLoading(false);
    }
  }, [companySlug, actionFilter, page]);

  useEffect(() => {
    void loadLogs();
  }, [loadLogs]);

  const pageSize = 20;
  const totalPages = Math.max(1, Math.ceil(count / pageSize));

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Audit trail</h1>
          <p className="text-sm text-slate-600">{companySlug}</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={actionFilter}
            onChange={(e) => {
              setActionFilter(e.target.value);
              setPage(1);
            }}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm"
          >
            {ACTION_FILTERS.map((filter) => (
              <option key={filter.value} value={filter.value}>
                {filter.label}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => void loadLogs()}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
          >
            Refresh
          </button>
        </div>
      </div>

      {loading && <p className="text-sm text-slate-500">Loading audit logs…</p>}
      {error && (
        <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
      )}

      {!loading && !error && (
        <>
          <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
            <table className="min-w-full text-left">
              <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-3 py-2">Timestamp</th>
                  <th className="px-3 py-2">Action</th>
                  <th className="px-3 py-2">Actor</th>
                  <th className="px-3 py-2">Object</th>
                  <th className="px-3 py-2">Metadata</th>
                </tr>
              </thead>
              <tbody>
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-3 py-6 text-center text-sm text-slate-500">
                      No audit logs found.
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => <AuditLogRow key={log.id} log={log} />)
                )}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-between text-sm text-slate-600">
            <span>
              Page {page} of {totalPages} ({count} total)
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="rounded-md border border-slate-300 px-3 py-1 disabled:opacity-40"
              >
                Previous
              </button>
              <button
                type="button"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="rounded-md border border-slate-300 px-3 py-1 disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
