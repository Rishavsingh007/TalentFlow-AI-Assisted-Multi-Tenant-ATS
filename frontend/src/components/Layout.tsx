import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function Layout() {
  const { auth, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <Link to="/" className="text-lg font-semibold text-slate-900">
            TalentFlow
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <Link to="/apply" className="text-slate-600 hover:text-slate-900">
              Apply
            </Link>
            {isAuthenticated && auth && (
              <>
                <Link
                  to={`/pipeline/${auth.companySlug}`}
                  className="text-slate-600 hover:text-slate-900"
                >
                  Pipeline
                </Link>
                <Link
                  to={`/audit/${auth.companySlug}`}
                  className="text-slate-600 hover:text-slate-900"
                >
                  Audit
                </Link>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="rounded-md border border-slate-300 px-3 py-1 text-slate-700 hover:bg-slate-50"
                >
                  Logout
                </button>
              </>
            )}
            {!isAuthenticated && (
              <Link
                to="/login"
                className="rounded-md bg-slate-900 px-3 py-1 text-white hover:bg-slate-800"
              >
                Recruiter login
              </Link>
            )}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
