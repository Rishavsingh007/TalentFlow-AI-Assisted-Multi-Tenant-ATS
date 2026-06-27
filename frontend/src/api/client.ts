import { getApiBaseUrl } from "./config";
import type { AuthTokens } from "../types/api";

const AUTH_STORAGE_KEY = "talentflow_auth";

export interface StoredAuth extends AuthTokens {
  companySlug: string;
}

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

export function loadStoredAuth(): StoredAuth | null {
  const raw = sessionStorage.getItem(AUTH_STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredAuth;
  } catch {
    return null;
  }
}

export function saveStoredAuth(auth: StoredAuth): void {
  sessionStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(auth));
}

export function clearStoredAuth(): void {
  sessionStorage.removeItem(AUTH_STORAGE_KEY);
}

function parseErrorMessage(body: unknown, fallback: string): string {
  if (!body || typeof body !== "object") return fallback;
  const record = body as Record<string, unknown>;
  if (typeof record.detail === "string") return record.detail;
  if (Array.isArray(record.detail)) return record.detail.map(String).join(", ");
  const fieldMessages = Object.entries(record)
    .filter(([, value]) => value !== undefined)
    .map(([key, value]) => {
      if (Array.isArray(value)) return `${key}: ${value.join(", ")}`;
      return `${key}: ${String(value)}`;
    });
  return fieldMessages.length > 0 ? fieldMessages.join("; ") : fallback;
}

let refreshPromise: Promise<string | null> | null = null;
let authExpiredHandler: (() => void) | null = null;
let authRefreshedHandler: (() => void) | null = null;

export function setAuthExpiredHandler(handler: (() => void) | null): void {
  authExpiredHandler = handler;
}

export function setAuthRefreshedHandler(handler: (() => void) | null): void {
  authRefreshedHandler = handler;
}

function notifyAuthExpired(): void {
  clearStoredAuth();
  authExpiredHandler?.();
}

async function refreshAccessToken(refresh: string): Promise<string | null> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });
  if (!response.ok) return null;
  const data = (await response.json()) as { access: string; refresh?: string };
  const stored = loadStoredAuth();
  if (stored) {
    saveStoredAuth({
      ...stored,
      access: data.access,
      ...(data.refresh ? { refresh: data.refresh } : {}),
    });
    authRefreshedHandler?.();
  }
  return data.access;
}

async function getAccessToken(): Promise<string | null> {
  return loadStoredAuth()?.access ?? null;
}

export interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  auth?: boolean;
  retry?: boolean;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { body, auth = false, retry = true, headers, ...rest } = options;
  const requestHeaders = new Headers(headers);

  if (body !== undefined && !(body instanceof FormData)) {
    requestHeaders.set("Content-Type", "application/json");
  }

  if (auth) {
    const access = await getAccessToken();
    if (access) {
      requestHeaders.set("Authorization", `Bearer ${access}`);
    }
  }

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...rest,
    headers: requestHeaders,
    body:
      body === undefined
        ? undefined
        : body instanceof FormData
          ? body
          : JSON.stringify(body),
  });

  if (response.status === 401 && auth && retry) {
    const stored = loadStoredAuth();
    if (stored?.refresh) {
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken(stored.refresh).finally(() => {
          refreshPromise = null;
        });
      }
      const newAccess = await refreshPromise;
      if (newAccess) {
        return apiRequest<T>(path, { ...options, retry: false });
      }
    }
    notifyAuthExpired();
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const responseBody = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(
      parseErrorMessage(responseBody, response.statusText),
      response.status,
      responseBody,
    );
  }

  return responseBody as T;
}
