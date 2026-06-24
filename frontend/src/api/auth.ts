import { apiRequest } from "./client";
import type { LoginResponse, WsTicketResponse } from "../types/api";

export function login(email: string, password: string): Promise<LoginResponse> {
  return apiRequest<LoginResponse>("/api/v1/auth/login/", {
    method: "POST",
    body: { email, password },
  });
}

export function fetchWsTicket(): Promise<WsTicketResponse> {
  return apiRequest<WsTicketResponse>("/api/v1/auth/ws-ticket/", {
    method: "POST",
    auth: true,
  });
}
