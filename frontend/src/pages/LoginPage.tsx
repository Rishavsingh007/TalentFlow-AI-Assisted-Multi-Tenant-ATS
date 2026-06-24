import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../hooks/useAuth";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("recruiter@acme.com");
  const [password, setPassword] = useState("demo-password-123");
  const [companySlug, setCompanySlug] = useState("acme-corp");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password, companySlug);
      navigate(`/pipeline/${companySlug}`);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(
          err.status === 404
            ? "You are not a member of that company."
            : err.message,
        );
      } else {
        setError("Login failed. Check your credentials and try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-md">
      <h1 className="mb-2 text-2xl font-semibold">Recruiter login</h1>
      <p className="mb-6 text-sm text-slate-600">
        Demo: <code className="text-xs">recruiter@acme.com</code> /{" "}
        <code className="text-xs">demo-password-123</code> /{" "}
        <code className="text-xs">acme-corp</code>
      </p>
      <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border border-slate-200 bg-white p-6">
        <label className="block text-sm">
          <span className="mb-1 block font-medium">Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          <span className="mb-1 block font-medium">Password</span>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          <span className="mb-1 block font-medium">Company slug</span>
          <input
            type="text"
            required
            value={companySlug}
            onChange={(e) => setCompanySlug(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2"
          />
        </label>
        {error && (
          <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
        )}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-slate-900 px-4 py-2 text-white hover:bg-slate-800 disabled:opacity-50"
        >
          {loading ? "Signing in…" : "Sign in"}
        </button>
      </form>
      <p className="mt-4 text-center text-sm text-slate-600">
        <Link to="/apply" className="text-slate-900 underline">
          Back to public apply
        </Link>
      </p>
    </div>
  );
}
