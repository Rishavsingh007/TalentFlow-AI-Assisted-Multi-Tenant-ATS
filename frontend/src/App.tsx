import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { RequireAuth } from "./components/RequireAuth";
import { RequireCompanySlug } from "./components/RequireCompanySlug";
import { AuthProvider } from "./hooks/useAuth";
import { ApplyPage } from "./pages/ApplyPage";
import { AuditPage } from "./pages/AuditPage";
import { LoginPage } from "./pages/LoginPage";
import { PipelinePage } from "./pages/PipelinePage";

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Navigate to="/apply" replace />} />
            <Route path="apply" element={<ApplyPage />} />
            <Route path="login" element={<LoginPage />} />
            <Route element={<RequireAuth />}>
              <Route element={<RequireCompanySlug basePath="pipeline" />}>
                <Route path="pipeline/:companySlug" element={<PipelinePage />} />
              </Route>
              <Route element={<RequireCompanySlug basePath="audit" />}>
                <Route path="audit/:companySlug" element={<AuditPage />} />
              </Route>
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
