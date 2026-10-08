# Division Command Center prototype

## User
A division leader or operations colleague reviewing work across divisions in a synthetic prototype.

## Problem
The team needs a single view of operations records, their status, and summary counts without connecting real business systems.

## Core journey
1. Set up the Python environment in this folder.
2. Start Flask locally.
3. Open http://127.0.0.1:5000/ and review 15 invented records across six divisions.
4. Search by ID, title, division, or status; combine division and status filters and apply them.
5. Select a record's new status and press Save. The page reloads with the current filters preserved and Python recalculates the KPIs. A record can leave the current results if its new status no longer matches the filters.
6. Clear filters to return to all records. Review the uncommitted files with Git.

## Acceptance checks
- The project includes the Flask app, templates, stylesheet, requirements, README, AGENTS, tests, and `.gitignore`, plus the existing `Dockerfile` and `Procfile` runtime files.
- The root route renders `index.html` with 15 synthetic records across six divisions and a visible prototype warning. Error pages also retain the warning.
- Python calculates four KPI cards for the current results: total records, Open, In progress, and Completed. Initial unfiltered counts are 15, 5, 5, and 5 respectively.
- Search is case-insensitive; division and status filters combine with search. No matches produces an empty state with four zero KPIs.
- Valid status updates use POST, persist in this process, and redirect to recalculated results. Invalid status or filter values return 400 without mutation; a missing record returns 404.
- The root route returns HTTP 200 and loads the local stylesheet.
- `GET /health` returns HTTP 200 with `{"status":"ok"}` for the existing load-balancer check.
- Flask starts bound to localhost by default, with debug mode disabled. Existing `HOST` and `PORT` overrides are supported.
- `.venv`, `.env`, caches, and common secret files are ignored by Git.
- Git review excludes local environments, caches, and secrets. Commit or push only when explicitly requested.
- Records stay in memory. No database, authentication, external APIs, secrets, or real business data are added.

## Synthetic-data boundary
All 15 records and division assignments are invented demonstration data, clearly labeled synthetic. They contain no real customer, employee, financial, confidential, or operational records. Do not add credentials, tokens, or secrets to source files or Git.

## Windows PowerShell commands
Run commands from the `division-command-center` folder. Python 3.10 or newer is required. Creating the local environment is a filesystem operation; dependency installation requires approved network/package access. If access is denied, stop the installation and report it.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000/ in a browser. Press Ctrl+C in the server terminal to stop it. Using the environment's executable directly avoids changing PowerShell's execution policy.

With the server running, check it from a second PowerShell terminal:

```powershell
(Invoke-WebRequest -Uri http://127.0.0.1:5000/ -UseBasicParsing).StatusCode
(Invoke-WebRequest -Uri http://127.0.0.1:5000/static/styles.css -UseBasicParsing).StatusCode
```

Both commands should print `200`.

Run the available automated checks:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

The standard-library tests use Flask's test client and restore in-memory records after each test. They cover the synthetic dataset, KPI counts, combined filters, empty results, escaped input, status updates, filter preservation, rejected requests, error warnings, and the stylesheet.

Initialize and review Git without committing:

```powershell
git status --short
git diff
```

Untracked files do not appear in ordinary `git diff`. Use `git diff --no-index -- NUL path` to review a new file; it returns 1 when differences exist. Commit or push only when explicitly requested.

## Limitations
This is an unauthenticated synthetic prototype. Flask's development server is unsuitable for production. Updates reset on process restart and are not shared across separate workers or instances. A process-local lock prevents simultaneous reads and writes from producing partial snapshots; it does not synchronize AWS workers. There is no durable persistence or concurrent-edit conflict handling. No JavaScript is needed: native HTML forms submit filters and updates. Dependencies are bounded by major version rather than captured in a full reproducible lockfile.

## Runtime compatibility
The existing importable WSGI entry point remains `app:app`. The existing Dockerfile uses Python 3.13 Alpine, a non-root user, and one Gunicorn worker on port 8000. The Procfile retains the same one-worker WSGI entry point. Gunicorn is installed on non-Windows platforms; Windows uses the local Flask development server. Direct launch defaults to localhost:5000 with debug disabled and supports the existing `HOST`/`PORT` overrides. The application uses standard Flask/Jinja and Python, with no Windows-specific application code.

The remote repository already includes an AWS runtime and `/health` contract. Those are preserved. Docker execution and AWS deployment of this update have not been verified.

## Existing container and AWS setup

```powershell
docker build -t division-command-center .
docker run --rm -p 8000:8000 division-command-center
```

Open http://127.0.0.1:8000/ and check http://127.0.0.1:8000/health.

The repository's previous README records an Elastic Beanstalk Docker environment in `ap-southeast-1`, named `division-command-center-prototype`, with one instance and an Application Load Balancer checking `/health`. It records commit `6089ee7` as application version `6089ee7-docker`. This is historical repository information, not a live deployment verification. Pushing to GitHub does not itself verify or perform an AWS deployment.

## Deferred capabilities
Charts, additional KPIs, workflows, uploads, exports, APIs, live data integrations, user accounts, database storage, production hosting, and deployment remain deferred until separately requested.
