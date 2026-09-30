import os

from flask import Flask, abort, redirect, render_template, request, url_for
from werkzeug.exceptions import HTTPException


app = Flask(__name__)

DIVISIONS = ("Operations", "Finance", "People", "Technology", "Customer Service", "Logistics")
STATUSES = ("On track", "At risk", "Blocked", "Complete")

# Invented examples only. Changes live in this process's memory until it restarts.
RECORDS = [
    {"id": 1, "title": "Shift handover checklist", "division": "Operations", "status": "On track", "summary": "Standardize daily handovers."},
    {"id": 2, "title": "Service capacity review", "division": "Operations", "status": "At risk", "summary": "Review staffing against demand."},
    {"id": 3, "title": "Incident response drill", "division": "Operations", "status": "Complete", "summary": "Run a sample response exercise."},
    {"id": 4, "title": "Budget forecast refresh", "division": "Finance", "status": "On track", "summary": "Update an illustrative forecast."},
    {"id": 5, "title": "Expense review workflow", "division": "Finance", "status": "Blocked", "summary": "Clarify sample approval steps."},
    {"id": 6, "title": "Hiring plan review", "division": "People", "status": "At risk", "summary": "Compare planned roles with capacity."},
    {"id": 7, "title": "New starter guide", "division": "People", "status": "Complete", "summary": "Prepare a sample onboarding guide."},
    {"id": 8, "title": "Skills coverage map", "division": "People", "status": "On track", "summary": "Map illustrative skills and gaps."},
    {"id": 9, "title": "Device lifecycle review", "division": "Technology", "status": "On track", "summary": "Review a sample replacement plan."},
    {"id": 10, "title": "Access request cleanup", "division": "Technology", "status": "Blocked", "summary": "Simplify the example request flow."},
    {"id": 11, "title": "Support response guide", "division": "Customer Service", "status": "Complete", "summary": "Draft responses for common requests."},
    {"id": 12, "title": "Feedback theme review", "division": "Customer Service", "status": "At risk", "summary": "Group fictional feedback themes."},
    {"id": 13, "title": "Delivery route review", "division": "Logistics", "status": "On track", "summary": "Compare illustrative route options."},
    {"id": 14, "title": "Stock count rehearsal", "division": "Logistics", "status": "Complete", "summary": "Practice a sample inventory count."},
    {"id": 15, "title": "Supplier contingency plan", "division": "Logistics", "status": "Blocked", "summary": "Document an alternative scenario."},
]


def filtered_records(query, division, status):
    query = query.casefold()
    return [
        record for record in RECORDS
        if (not query or query in " ".join((record["title"], record["division"], record["summary"])).casefold())
        and (not division or record["division"] == division)
        and (not status or record["status"] == status)
    ]


def calculate_kpis(records):
    return {
        "total": len(records),
        "on_track": sum(record["status"] == "On track" for record in records),
        "needs_attention": sum(record["status"] in ("At risk", "Blocked") for record in records),
        "complete": sum(record["status"] == "Complete" for record in records),
    }


@app.get("/")
def index():
    query = request.args.get("q", "").strip()
    division = request.args.get("division", "")
    status = request.args.get("status", "")
    division = division if division in DIVISIONS else ""
    status = status if status in STATUSES else ""
    records = filtered_records(query, division, status)
    return render_template(
        "index.html", records=records, kpis=calculate_kpis(records),
        divisions=DIVISIONS, statuses=STATUSES,
        query=query, division=division, status=status,
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/records/<int:record_id>/status")
def update_status(record_id):
    record = next((item for item in RECORDS if item["id"] == record_id), None)
    if record is None:
        abort(404)
    new_status = request.form.get("new_status", "")
    if new_status not in STATUSES:
        abort(400)
    record["status"] = new_status
    return redirect(url_for(
        "index", q=request.form.get("q", ""),
        division=request.form.get("division", ""),
        status=request.form.get("status", ""),
    ))


@app.errorhandler(HTTPException)
def show_http_error(error):
    return render_template("error.html", code=error.code, message=error.description), error.code


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "5000")))
