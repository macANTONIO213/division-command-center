import os
from threading import Lock

from flask import Flask, abort, redirect, render_template, request, url_for
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

DIVISIONS = ("Customer Operations", "Finance", "People", "Technology", "Commercial", "Strategy")
STATUSES = ("Open", "In progress", "Completed")

# Invented examples only. Changes live in this process and reset on restart.
records = [
    {"id": 1, "division": "Customer Operations", "title": "Review sample service queue", "status": "Open"},
    {"id": 2, "division": "Customer Operations", "title": "Draft demo response guide", "status": "In progress"},
    {"id": 3, "division": "Customer Operations", "title": "Check mock escalation flow", "status": "Completed"},
    {"id": 4, "division": "Finance", "title": "Review fictional budget worksheet", "status": "Open"},
    {"id": 5, "division": "Finance", "title": "Reconcile demo expense categories", "status": "In progress"},
    {"id": 6, "division": "Finance", "title": "Validate sample reporting checklist", "status": "Completed"},
    {"id": 7, "division": "People", "title": "Draft sample onboarding checklist", "status": "Open"},
    {"id": 8, "division": "People", "title": "Review fictional training plan", "status": "In progress"},
    {"id": 9, "division": "People", "title": "Check demo policy index", "status": "Completed"},
    {"id": 10, "division": "Technology", "title": "Review mock system inventory", "status": "Open"},
    {"id": 11, "division": "Technology", "title": "Prepare sample release checklist", "status": "In progress"},
    {"id": 12, "division": "Commercial", "title": "Review fictional campaign brief", "status": "Open"},
    {"id": 13, "division": "Commercial", "title": "Validate demo handoff guide", "status": "Completed"},
    {"id": 14, "division": "Strategy", "title": "Draft sample planning agenda", "status": "In progress"},
    {"id": 15, "division": "Strategy", "title": "Review mock priorities register", "status": "Completed"},
]
records_lock = Lock()


def filters_from(values):
    filters = {name: values.get(name, "").strip() for name in ("q", "division", "status")}
    if filters["division"] and filters["division"] not in DIVISIONS:
        abort(400, description="Choose a division from the available options.")
    if filters["status"] and filters["status"] not in STATUSES:
        abort(400, description="Choose a status from the available options.")
    return filters


def dashboard_context(filters):
    with records_lock:
        snapshot = [record.copy() for record in records]
    query = filters["q"].casefold()
    visible = [
        record for record in snapshot
        if (not filters["division"] or record["division"] == filters["division"])
        and (not filters["status"] or record["status"] == filters["status"])
        and (not query or query in f'{record["id"]} {record["title"]} {record["division"]} {record["status"]}'.casefold())
    ]
    kpis = [("Total records", len(visible))]
    kpis.extend((status, sum(record["status"] == status for record in visible)) for status in STATUSES)
    return dict(records=visible, kpis=kpis, filters=filters, divisions=DIVISIONS,
                statuses=STATUSES, total_records=len(snapshot))


@app.get("/")
def index():
    return render_template("index.html", **dashboard_context(filters_from(request.args)))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/records/<int:record_id>/status")
def update_status(record_id):
    filters = filters_from(request.form)
    new_status = request.form.get("new_status", "")
    if new_status not in STATUSES:
        abort(400, description="Choose a valid status before saving.")
    with records_lock:
        record = next((record for record in records if record["id"] == record_id), None)
        if record is None:
            abort(404, description="This synthetic record does not exist.")
        record["status"] = new_status
    return redirect(url_for("index", **{key: value for key, value in filters.items() if value}), code=303)


@app.errorhandler(HTTPException)
def http_error(error):
    # Render errors in the same shell so the prototype warning stays visible.
    response = error.get_response()
    response.data = render_template(
        "index.html", error=error,
        **dashboard_context({"q": "", "division": "", "status": ""}),
    )
    response.content_type = "text/html; charset=utf-8"
    return response


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
