import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError } from "../api/client";
import { applyToJob, fetchPublicJobs } from "../api/jobs";
import type { ApplicationCreated, PublicJob } from "../types/api";

export function ApplyPage() {
  const [jobs, setJobs] = useState<PublicJob[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | "">("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [resume, setResume] = useState<File | null>(null);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<ApplicationCreated | null>(null);
  const [formKey, setFormKey] = useState(0);

  useEffect(() => {
    fetchPublicJobs()
      .then((data) => {
        setJobs(data.results);
        if (data.results.length > 0) {
          setSelectedJobId(data.results[0].id);
        }
      })
      .catch(() => setError("Failed to load open jobs."))
      .finally(() => setLoadingJobs(false));
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!selectedJobId || !resume) return;

    setError(null);
    setSuccess(null);
    setSubmitting(true);

    const formData = new FormData();
    formData.append("full_name", fullName);
    formData.append("email", email);
    if (phone) formData.append("phone", phone);
    formData.append("resume", resume);

    try {
      const result = await applyToJob(selectedJobId, formData);
      setSuccess(result);
      setFullName("");
      setEmail("");
      setPhone("");
      setResume(null);
      setFormKey((k) => k + 1);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Application failed.");
    } finally {
      setSubmitting(false);
    }
  };

  const selectedJob = jobs.find((job) => job.id === selectedJobId);

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-2 text-2xl font-semibold">Apply for a job</h1>
      <p className="mb-6 text-sm text-slate-600">
        Submit your resume — parsing and AI scoring run asynchronously after you apply.
      </p>

      {loadingJobs && <p className="text-sm text-slate-500">Loading open jobs…</p>}

      {!loadingJobs && jobs.length === 0 && (
        <p className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          No open jobs found. Run <code>scripts/seed_demo.py</code> to create demo jobs.
        </p>
      )}

      {jobs.length > 0 && (
        <form
          key={formKey}
          onSubmit={handleSubmit}
          className="space-y-4 rounded-lg border border-slate-200 bg-white p-6"
        >
          <label className="block text-sm">
            <span className="mb-1 block font-medium">Job</span>
            <select
              value={selectedJobId}
              onChange={(e) =>
                setSelectedJobId(e.target.value ? Number(e.target.value) : "")
              }
              className="w-full rounded-md border border-slate-300 px-3 py-2"
              required
            >
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title} — {job.company_name}
                </option>
              ))}
            </select>
          </label>

          {selectedJob && (
            <p className="text-sm text-slate-600">{selectedJob.description}</p>
          )}

          <label className="block text-sm">
            <span className="mb-1 block font-medium">Full name</span>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2"
            />
          </label>

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
            <span className="mb-1 block font-medium">Phone (optional)</span>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2"
            />
          </label>

          <label className="block text-sm">
            <span className="mb-1 block font-medium">Resume (PDF or DOCX)</span>
            <input
              type="file"
              required
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={(e) => setResume(e.target.files?.[0] ?? null)}
              className="w-full text-sm"
            />
          </label>

          {error && (
            <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
          )}

          {success && (
            <div className="rounded-md bg-green-50 px-3 py-3 text-sm text-green-800">
              <p className="font-medium">Application submitted!</p>
              <p className="mt-1">
                Application #{success.id} is in stage &quot;{success.current_stage}&quot;. AI
                scoring will complete shortly.
              </p>
              <p className="mt-2">
                <Link to="/login" className="underline">
                  Log in as recruiter
                </Link>{" "}
                to watch it appear on the pipeline in real time.
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={submitting || !resume}
            className="w-full rounded-md bg-slate-900 px-4 py-2 text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {submitting ? "Submitting…" : "Submit application"}
          </button>
        </form>
      )}
    </div>
  );
}
