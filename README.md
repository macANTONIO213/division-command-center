# Division Command Center

A Flask prototype for reviewing synthetic division work and updating record statuses. It has no external data source or persistent storage.

## User

The intended user is a division leader or operations manager who needs one place to review the division's status and decide what needs attention. This is a working assumption for the prototype, to be validated before dashboard design begins.

## Business problem

Division status is often spread across separate reports and conversations. That makes it hard to see priorities and follow up consistently. A future command center should bring the relevant signals and actions into one understandable view.

## Core journey

1. Open the command center and review four KPI counts.
2. Search the records or filter by division and status.
3. Review a record's title, summary, division, and status.
4. Select a new status and save; the page reloads with recalculated KPI counts.

## Acceptance checks

- The project contains `app.py`, `Dockerfile`, `Procfile`, `requirements.txt`, `README.md`, `templates/index.html`, `templates/error.html`, `static/styles.css`, and `.gitignore`.
- After installing dependencies, `python app.py` starts the local Flask development server.
- Opening `/` renders the dashboard from `templates/index.html` and loads `static/styles.css`.
- The dashboard contains exactly 15 synthetic records across six divisions.
- Python calculates four KPI cards from the currently displayed records: visible records, on track, needs attention (at risk or blocked), and complete.
- Search checks record title, division, and summary without regard to letter case. Division and status filters can be combined with search.
- Saving a valid status updates the in-memory record and recalculates the KPIs. Invalid record IDs return 404; invalid statuses return 400.
- A visible prototype and synthetic-data warning appears on the dashboard and HTTP error pages, including after filtering or saving.
- `GET /health` returns HTTP 200 with `{"status":"ok"}`.
- The container installs Gunicorn, exposes port 8000, and runs as a non-root user with one worker.
- The Flask `app` object is importable by a WSGI runtime; the `Procfile` starts one Gunicorn worker on Elastic Beanstalk. Local launch accepts `HOST` and `PORT` environment variables.

## Synthetic-data boundary

All 15 records are invented examples and are labeled as synthetic in the interface. Do not copy production records, personal information, credentials, or confidential division details into the project.

## Prototype limitations

- Records are stored in process memory. Status changes disappear after a restart and are not shared across multiple worker processes.
- There is no authentication, database, external API, or audit history.
- The Flask development server is for local development only. The current AWS prototype runs one Docker instance behind an Application Load Balancer and serves HTTP without TLS.
- The user and workflow assumptions above have not been validated with stakeholders.

## Deferred capabilities

Drill-down views, follow-up tracking, role-based access, data ingestion, and production deployment controls are deferred until requirements and data definitions are agreed.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000/>.

## Run in a container

```sh
docker build -t division-command-center .
docker run --rm -p 8000:8000 division-command-center
```

Open <http://127.0.0.1:8000/>. The health endpoint is <http://127.0.0.1:8000/health>.

## AWS deployment status

The prototype is running in Elastic Beanstalk's Docker platform in `ap-southeast-1` as environment `division-command-center-prototype`:

<http://division-command-center-719535286257.ap-southeast-1.elasticbeanstalk.com/>

The load balancer checks `/health`. The deployed source is commit `6089ee7` (`6089ee7-docker` application version). The environment uses one instance and an Application Load Balancer, which incur AWS charges while running. In-memory status changes disappear after an instance restart or replacement. The `Procfile` remains for a separate WSGI deployment path.
