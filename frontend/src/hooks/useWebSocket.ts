import { useEffect, useRef, useState } from "react";
import { fetchWsTicket } from "../api/auth";
import { ApiError } from "../api/client";
import { getWsBaseUrl } from "../api/config";
import type { DashboardEvent, WsConnectionStatus } from "../types/api";

const MAX_BACKOFF_MS = 30_000;

interface UseWebSocketOptions {
  companySlug: string;
  enabled: boolean;
  onEvent: (event: DashboardEvent) => void;
}

export function useWebSocket({
  companySlug,
  enabled,
  onEvent,
}: UseWebSocketOptions): WsConnectionStatus {
  const [status, setStatus] = useState<WsConnectionStatus>("offline");
  const onEventRef = useRef(onEvent);
  const reconnectAttemptRef = useRef(0);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const unmountedRef = useRef(false);

  useEffect(() => {
    onEventRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    unmountedRef.current = false;

    if (!enabled || !companySlug) {
      setStatus("offline");
      return () => {
        unmountedRef.current = true;
      };
    }

    const clearReconnectTimer = () => {
      if (reconnectTimerRef.current !== null) {
        window.clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };

    const closeSocket = () => {
      if (wsRef.current) {
        wsRef.current.onopen = null;
        wsRef.current.onclose = null;
        wsRef.current.onmessage = null;
        wsRef.current.onerror = null;
        wsRef.current.close();
        wsRef.current = null;
      }
    };

    const scheduleReconnect = () => {
      if (unmountedRef.current) return;
      setStatus("reconnecting");
      const attempt = reconnectAttemptRef.current;
      const delay = Math.min(1000 * 2 ** attempt, MAX_BACKOFF_MS);
      reconnectAttemptRef.current = attempt + 1;
      clearReconnectTimer();
      reconnectTimerRef.current = window.setTimeout(() => {
        void connect();
      }, delay);
    };

    const connect = async () => {
      if (unmountedRef.current) return;
      closeSocket();
      setStatus("reconnecting");

      try {
        const { ticket } = await fetchWsTicket();
        if (unmountedRef.current) return;

        const wsUrl = `${getWsBaseUrl()}/ws/companies/${companySlug}/dashboard/?ticket=${encodeURIComponent(ticket)}`;
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          if (unmountedRef.current) return;
          reconnectAttemptRef.current = 0;
          setStatus("connected");
        };

        ws.onmessage = (message) => {
          try {
            const event = JSON.parse(message.data as string) as DashboardEvent;
            onEventRef.current(event);
          } catch {
            // ignore malformed payloads
          }
        };

        ws.onerror = () => {
          ws.close();
        };

        ws.onclose = (event) => {
          if (unmountedRef.current) return;
          wsRef.current = null;

          const fatalCodes = [4401, 4404];
          if (fatalCodes.includes(event.code)) {
            setStatus("offline");
            return;
          }

          setStatus("offline");
          scheduleReconnect();
        };
      } catch (err) {
        if (unmountedRef.current) return;
        if (err instanceof ApiError && err.status === 401) {
          setStatus("offline");
          return;
        }
        scheduleReconnect();
      }
    };

    void connect();

    return () => {
      unmountedRef.current = true;
      clearReconnectTimer();
      closeSocket();
      setStatus("offline");
    };
  }, [companySlug, enabled]);

  return status;
}
