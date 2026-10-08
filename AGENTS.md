# Working boundaries

- Work in this folder and follow README.md's scope and acceptance checks.
- Maintain the requested Flask/Jinja prototype: 15 synthetic in-memory records across six divisions, four Python KPI counts, search, division/status filters, and status updates. Use HTML forms and CSS; JavaScript is unnecessary for this scope.
- Keep a prototype/synthetic-data warning visible on the dashboard and error pages. Preserve filters after updates and recalculate KPIs for the current results.
- Preserve the importable `app:app` WSGI entry point, existing Dockerfile/Procfile, Gunicorn dependency on Linux, `/health` endpoint, and `HOST`/`PORT` overrides for runtime compatibility. Do not invent deployment settings.
- Do not add capabilities beyond the requested dashboard. Charts, additional KPIs, workflows, data integrations, accounts, databases, and deployment require a separate request.
- Use only clearly labeled synthetic examples if example data is later requested. Never introduce real business records or secrets.
- Keep `.venv`, `.env`, caches, and secret files out of Git. Do not commit or push unless explicitly authorized later.
- Install requirements only with approved package/network access. Respect denied access and report the limitation; do not bypass it.
- Default the development server to `127.0.0.1` with debug mode disabled; honor existing explicit `HOST`/`PORT` overrides.
- Report actual startup/check output and summarize all changed files.

## Windows PowerShell run commands

From this folder, with Python 3.10 or newer:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

From a second terminal while the server runs:

```powershell
(Invoke-WebRequest -Uri http://127.0.0.1:5000/ -UseBasicParsing).StatusCode
(Invoke-WebRequest -Uri http://127.0.0.1:5000/static/styles.css -UseBasicParsing).StatusCode
```

Expect `200` for both. Stop the server with Ctrl+C.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

Keep tests independent by restoring the synthetic records after each test. Records are process-local and reset on restart; never claim persistence or synchronization between AWS workers.

```powershell
git init
git status --short
git diff --no-index -- NUL app.py
```

Repeat the last command for each new file as needed. Untracked files require `git diff --no-index`, which returns 1 when it finds differences. Use `git diff` for tracked changes. Stage, commit, or push only when explicitly requested.
