# Agentic AI Deployment Hub

An Agentic AI-powered deployment platform that accepts a Git repository URL, analyzes the project, determines its technology and deployment requirements, creates a deployment plan, generates Docker artifacts, validates them, builds and runs the application, performs health checks, and provides the deployed application URL.

---

# 1. Project Overview

The Agentic AI Deployment Hub automates the software deployment process using a combination of deterministic services and Agentic AI.

The user only needs to provide a Git repository URL.

The system then performs the deployment workflow automatically:

```text
Git Repository URL
        |
        v
Repository Clone
        |
        v
Project Scanning
        |
        v
Framework Detection
        |
        v
Application Detection
        |
        v
AI Project Analysis
        |
        v
Deployment Planning
        |
        v
Docker Artifact Generation
        |
        v
Validation
        |
        v
Docker Image Build
        |
        v
Docker Container Run
        |
        v
Health Check
        |
        +----------------+
        |                |
     Healthy           Failed
        |                |
        |                v
        |          Recovery Agent
        |                |
        |              Retry
        |                |
        +--------<-------+
        |
        v
Deployed Application URL
```

---

# 2. Prerequisites

- Python 3.11 or later
- Node.js 20 or later and npm 10 or later
- Docker Desktop running for Docker build, run, and health-check workflow steps
- Ollama running at `http://localhost:11434` with the `llama3.2` model for AI analysis and deployment planning

# 3. Run the Backend

Open a terminal at the repository root, then create and activate a virtual environment (only needed once):

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the FastAPI backend:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The API is now available at `http://127.0.0.1:8000`. Keep this terminal running while using the frontend.

# 4. Run the Frontend

Open a second terminal at the repository root and install dependencies (only needed once):

```powershell
cd frontend
npm install
```

Start the Vite development server:

```powershell
npm run dev
```

Open `http://127.0.0.1:5173/` in a browser. The frontend sends `/api` requests to the backend at `http://127.0.0.1:8000`.

# 5. Run the Full Application

1. Start Docker Desktop and Ollama, if you need the Docker and AI workflow steps.
2. Start the backend using the commands in section 3.
3. Start the frontend using the commands in section 4.
4. Open `http://127.0.0.1:5173/`, submit a Git repository URL, and run the desired deployment workflow steps.

## Create a production frontend build

```powershell
cd frontend
npm run build
```

The static build is written to `frontend/dist`.
