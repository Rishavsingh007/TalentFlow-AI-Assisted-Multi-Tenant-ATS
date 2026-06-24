import type { AuditLog } from "../types/api";

function formatMetadata(metadata: Record<string, unknown>): string {
  const entries = Object.entries(metadata);
  if (entries.length === 0) return "—";
  return entries.map(([key, value]) => `${key}: ${JSON.stringify(value)}`).join(", ");
}

export function AuditLogRow({ log }: { log: AuditLog }) {
  return (
    <tr className="border-b border-slate-100 hover:bg-slate-50">
      <td className="whitespace-nowrap px-3 py-2 text-xs text-slate-600">
        {new Date(log.timestamp).toLocaleString()}
      </td>
      <td className="px-3 py-2 text-xs font-medium text-slate-800">{log.action}</td>
      <td className="px-3 py-2 text-xs text-slate-600">{log.actor_email ?? "—"}</td>
      <td className="px-3 py-2 text-xs text-slate-600">
        {log.object_type} #{log.object_id}
      </td>
      <td className="max-w-md truncate px-3 py-2 text-xs text-slate-500">
        {formatMetadata(log.metadata)}
      </td>
    </tr>
  );
}
