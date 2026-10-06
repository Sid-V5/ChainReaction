# ChainReaction

> **Real-Time Software Supply Chain & Transitive Blast Radius Telemetry Engine**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18_%2B_Vite-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![Docker](https://img.shields.io/badge/Orchestration-Docker_Compose-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

---

## Overview

Modern software repositories depend on hundreds of direct and transitive open-source packages layered multiple hops deep. When critical vulnerabilities emerge (e.g., **Log4Shell**, **XZ Utils**, malicious npm typosquats) or packages are deprecated:

1. **The Blast Radius Problem**: *Where across our microservices and repositories is a compromised package running transitively, and which user-facing applications are exposed?*
2. **The Breaking-Change Problem**: *If a package is upgraded or removed, which downstream services will experience breaking failures, and what safe alternative versions exist?*

**ChainReaction** provides an interactive telemetry engine that maps deep dependency topologies, computes transitive blast radii in sub-5ms, simulates zero-day exploits in real time, and analyzes upgrade impact before production releases.

---

## Key Features

- **Interactive Topology Visualizer**: Full-screen force-directed graph canvas supporting Organic Force, Concentric Radial, and Hierarchical dependency layouts with live node inspection.
- **Transitive Blast Radius Computation**: Trace upstream repositories impacted across 1 to 5 degrees of separation with sub-millisecond response caching.
- **Breaking Change Simulator**: Select any library to view downstream dependents, risk differentials, and safe upgrade targets.
- **Live Zero-Day Streaming**: Real-time push alerts and live risk leaderboard updates delivered via streaming WebSockets.
- **Ecosystem Vulnerability Analytics**: Multi-dimensional risk scoring, CVE severity breakdowns, and language ecosystem exposure metrics.
- **Live Repository Scanning**: Ingest any GitHub repository on demand to extract dependency manifests and resolve OSV.dev advisories.

---

## System Architecture

```
┌────────────────────────────────────────────────────────┐
│         React 18 + Vite + Tailwind + Cytoscape         │
│          (Interactive Supply Chain Dashboard)          │
└───────────────────────────▲────────────────────────────┘
                            │ REST APIs & WebSockets
                            ▼
┌────────────────────────────────────────────────────────┐
│                 FastAPI Backend Engine                 │
└────────────┬──────────────┼───────────────┬────────────┘
             │              │               │
  Graph Path │   Semi-Structured Metadata   │ Pub/Sub Alerts &
  Traversal  │   & Severity Aggregation     │ In-Memory Caching
             ▼              ▼               ▼
        ┌─────────┐    ┌─────────┐     ┌─────────┐
        │  Graph  │    │Document │     │In-Memory│
        │ Topology│    │  Store  │     │  Cache  │
        └─────────┘    └─────────┘     └─────────┘
```

- **Graph Topology**: High-performance variable-length path traversal (`[:DEPENDS_ON*1..5]`) mapping dependency relationships across projects.
- **Document Store**: Schematized storage of repository manifests, metadata, and raw OSV advisory payloads.
- **In-Memory Cache & Message Broker**: Caches repeated graph traversal queries and streams zero-day alert notifications over pub/sub channels.

---

## Quickstart Guide

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (v20+)
- [Python](https://www.python.org/) (v3.10+)
- [Node.js](https://nodejs.org/) (v18+)

---

### Step 1: Start Infrastructure Containers

```bash
docker compose up -d
```

This launches the database containers configured in `docker-compose.yml`:
- **Document Store** on port `27017`
- **Graph Database** on ports `7474` (HTTP) and `7687` (Bolt)
- **In-Memory Cache** on port `6379`

---

### Step 2: Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` if you wish to configure custom database credentials or supply an optional GitHub API token for higher ingestion rate limits.

---

### Step 3: Start the Backend Service

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Verify database connectivity and auto-seed initial repositories
python -m backend.test_connections

# Start FastAPI server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

- API Server: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`

---

### Step 4: Start the Frontend Interface

```bash
cd frontend
npm install
npm run dev
```

- Web Dashboard: `http://localhost:5173`

---

## Interactive Feature Walkthrough

1. **Transitive Blast Radius Explorer**:
   - In the sidebar or top controls, select a library (e.g., `log4j-core`) and trigger **Trace Blast Radius**.
   - Observe direct and transitive connections highlighting upstream dependencies at risk.
2. **Breaking Change Simulator**:
   - Switch to the **Breaking Changes** view, select a package, and view affected repositories, dependency chains, and remediation versions.
3. **Real-Time Zero-Day Simulation**:
   - Trigger the simulated zero-day broadcast to observe immediate WebSocket alert dispatching and risk re-ranking.
4. **On-Demand Repository Scanning**:
   - Enter any public repository slug (e.g., `tiangolo/fastapi`) into the ingest bar to fetch its dependency manifest and query current vulnerability databases.

---

## Project Structure

```
ChainReaction/
├── backend/
│   ├── db/            # Database connectors & aggregation pipelines
│   ├── routers/       # REST and WebSocket endpoints
│   ├── services/      # Ingestion, scanner, and seeders
│   ├── config.py      # App configuration & environment loader
│   ├── main.py        # FastAPI entrypoint
│   └── requirements.txt
├── frontend/
│   ├── public/        # Static assets and icons
│   ├── src/
│   │   ├── components/# Graph canvas, analytics panels, controls
│   │   ├── api.js     # API & WebSocket client
│   │   ├── App.jsx    # Main layout & view switching
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml # Container orchestration
├── .env.example       # Sample environment configuration
├── .gitignore
└── README.md
```

---

## License

This project is licensed under the [MIT License](LICENSE).
