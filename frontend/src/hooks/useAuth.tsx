import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { login as apiLogin } from "../api/auth";
import { fetchCompany } from "../api/companies";
import {
  ApiError,
  clearStoredAuth,
  loadStoredAuth,
  saveStoredAuth,
  setAuthExpiredHandler,
  setAuthRefreshedHandler,
  type StoredAuth,
} from "../api/client";

interface AuthContextValue {
  auth: StoredAuth | null;
  isAuthenticated: boolean;
  login: (email: string, password: string, companySlug: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<StoredAuth | null>(() => loadStoredAuth());

  const logout = useCallback(() => {
    clearStoredAuth();
    setAuth(null);
  }, []);

  useEffect(() => {
    setAuthExpiredHandler(() => {
      setAuth(null);
    });
    setAuthRefreshedHandler(() => {
      setAuth(loadStoredAuth());
    });
    return () => {
      setAuthExpiredHandler(null);
      setAuthRefreshedHandler(null);
    };
  }, []);

  const login = useCallback(
    async (email: string, password: string, companySlug: string) => {
      const tokens = await apiLogin(email, password);
      const stored: StoredAuth = {
        access: tokens.access,
        refresh: tokens.refresh,
        companySlug,
      };
      saveStoredAuth(stored);
      setAuth(stored);
      try {
        await fetchCompany(companySlug);
      } catch (err) {
        clearStoredAuth();
        setAuth(null);
        if (err instanceof ApiError && err.status === 404) {
          throw new ApiError("You are not a member of that company.", 404, null);
        }
        throw err;
      }
    },
    [],
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      auth,
      isAuthenticated: auth !== null,
      login,
      logout,
    }),
    [auth, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
