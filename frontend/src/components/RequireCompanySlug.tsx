import { Navigate, Outlet, useParams } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

interface RequireCompanySlugProps {
  basePath: "pipeline" | "audit";
}

export function RequireCompanySlug({ basePath }: RequireCompanySlugProps) {
  const { companySlug } = useParams();
  const { auth } = useAuth();

  if (!auth) {
    return <Outlet />;
  }

  if (companySlug && companySlug !== auth.companySlug) {
    return <Navigate to={`/${basePath}/${auth.companySlug}`} replace />;
  }

  return <Outlet />;
}
