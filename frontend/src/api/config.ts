export function getApiBaseUrl(): string {
  return import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
}

export function getWsBaseUrl(): string {
  const url = new URL(getApiBaseUrl());
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  return url.origin;
}
