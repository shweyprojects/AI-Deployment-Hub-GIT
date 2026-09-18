import { useState } from "react";

const steps = [
  ["scan", "Scan project"],
  ["detect-framework", "Detect framework"],
  ["detect-application", "Detect application"],
  ["analyze", "Analyze with AI"],
  ["create-deployment-plan", "Create deployment plan"],
  ["generate-docker", "Generate Docker files"],
  ["validate", "Validate deployment"],
  ["build-docker", "Build Docker image"],
  ["run-docker", "Run container"],
  ["health-check", "Health check"],
];

const pretty = (value) => JSON.stringify(value, null, 2);

export default function App() {
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [projectId, setProjectId] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState("");

  async function request(path, options = {}) {
    setError("");
    setLoading(path);

    try {
      const response = await fetch(`/api/git/${path}`, options);

      const body = await response.json();

      if (!response.ok) {
        throw new Error(body.detail || pretty(body));
      }

      setResult(body);

      return body;
    } catch (err) {
      setError(err.message || "The request failed.");
      throw err;
    } finally {
      setLoading("");
    }
  }

  async function clone(event) {
    event.preventDefault();

    try {
      const body = await request("clone", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repository_url: repositoryUrl.trim(),
        }),
      });

      if (body.project_id) {
        setProjectId(body.project_id);
      }
    } catch {
      // Error is shown in the result panel.
    }
  }

  async function run(endpoint) {
    if (!projectId.trim()) {
      setError(
        "Clone a repository first, or enter an existing project ID."
      );
      return;
    }

    try {
      await request(
        `${endpoint}/${encodeURIComponent(projectId.trim())}`,
        {
          method: "POST",
        }
      );
    } catch {
      // Error is shown in the result panel.
    }
  }

  async function deployLocal() {
    if (!repositoryUrl.trim()) {
      setError(
        "Enter a Git repository URL before starting a local deployment."
      );
      return;
    }

    const deploymentProjectId = crypto.randomUUID();

    setProjectId(deploymentProjectId);

    try {
      await request(
        `deploy/${encodeURIComponent(deploymentProjectId)}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            repository_url: repositoryUrl.trim(),
          }),
        }
      );
    } catch {
      // Error is shown in the result panel.
    }
  }

  async function deployToRender() {
    if (!repositoryUrl.trim()) {
      setError(
        "Enter a Git repository URL before deploying to Render."
      );
      return;
    }

    const deploymentProjectId = crypto.randomUUID();

    setProjectId(deploymentProjectId);

    try {
      await request(
        `deploy-to-render/${encodeURIComponent(
          deploymentProjectId
        )}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            repository_url: repositoryUrl.trim(),
          }),
        }
      );
    } catch {
      // Error is shown in the result panel.
    }
  }

  const isBusy = Boolean(loading);

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">Agentic AI Deployment Hub</p>

        <h1>From repository to running service.</h1>

        <p className="lede">
          Clone a project, inspect its stack, generate deployment
          artifacts, and deploy it locally or to the cloud.
        </p>
      </section>

      <section className="panel">
        <h2>1. Select a repository</h2>

        <form onSubmit={clone}>
          <label htmlFor="repo">Git repository URL</label>

          <div className="inputRow">
            <input
              id="repo"
              type="url"
              required
              placeholder="https://github.com/owner/repository.git"
              value={repositoryUrl}
              onChange={(e) =>
                setRepositoryUrl(e.target.value)
              }
            />

            <button disabled={isBusy}>
              {loading === "clone"
                ? "Cloning…"
                : "Clone repository"}
            </button>
          </div>
        </form>

        <label htmlFor="project">Project ID</label>

        <input
          id="project"
          value={projectId}
          placeholder="Filled after cloning"
          onChange={(e) =>
            setProjectId(e.target.value)
          }
        />
      </section>

      <section className="panel">
        <h2>2. Deployment workflow</h2>

        <div className="steps">
          {steps.map(([endpoint, label], index) => (
            <button
              className="step"
              key={endpoint}
              onClick={() => run(endpoint)}
              disabled={isBusy}
            >
              <span>
                {String(index + 1).padStart(2, "0")}
              </span>

              {loading === endpoint
                ? "Working…"
                : label}
            </button>
          ))}
        </div>

        <div className="deploymentActions">
          <button
            className="deployAll"
            onClick={deployLocal}
            disabled={isBusy}
          >
            {loading.startsWith("deploy/")
              ? "Deploying locally…"
              : "Deploy locally"}
          </button>

          <button
            className="deployRender"
            onClick={deployToRender}
            disabled={isBusy}
          >
            {loading.startsWith("deploy-to-render/")
              ? "Deploying to Render…"
              : "Deploy to Render"}
          </button>
        </div>
      </section>

      {(error || result) && (
        <section
          className="panel result"
          aria-live="polite"
        >
          <h2>
            {error ? "Request failed" : "Latest result"}
          </h2>

          {error ? (
            <p className="error">{error}</p>
          ) : (
            <>
              {result?.url && (
                <p className="deploymentLink">
                  Deployment ready:{" "}
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Open deployed application
                  </a>
                </p>
              )}

              {result?.service_url && (
                <p className="deploymentLink">
                  Render deployment ready:{" "}
                  <a
                    href={result.service_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Open Render application
                  </a>
                </p>
              )}

              <pre>{pretty(result)}</pre>
            </>
          )}
        </section>
      )}
    </main>
  );
}