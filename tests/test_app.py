import unittest

from app import DIVISIONS, STATUSES, app, dashboard_context, records


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.original = [record.copy() for record in records]
        self.client = app.test_client()

    def tearDown(self):
        records[:] = self.original

    def context(self, **filters):
        return dashboard_context({"q": "", "division": "", "status": "", **filters})

    def assert_warning(self, response):
        self.assertIn("Prototype — synthetic data only.", response.get_data(as_text=True))

    def test_dataset_and_initial_kpis(self):
        self.assertEqual(len(records), 15)
        self.assertEqual(len({r["id"] for r in records}), 15)
        self.assertEqual({r["division"] for r in records}, set(DIVISIONS))
        self.assertEqual(len(DIVISIONS), 6)
        self.assertTrue(all(r["status"] in STATUSES for r in records))
        self.assertEqual(dict(self.context()["kpis"]),
                         {"Total records": 15, "Open": 5, "In progress": 5, "Completed": 5})

    def test_existing_health_contract(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_existing_runtime_overrides(self):
        import runpy
        from pathlib import Path
        from unittest.mock import patch

        with patch.dict("os.environ", {"HOST": "0.0.0.0", "PORT": "8000"}):
            with patch("flask.Flask.run") as run:
                runpy.run_path(str(Path(__file__).resolve().parents[1] / "app.py"), run_name="__main__")
                run.assert_called_once_with(host="0.0.0.0", port=8000, debug=False)

    def test_dashboard_and_stylesheet(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assert_warning(response)
        html = response.get_data(as_text=True)
        self.assertEqual(html.count('class="kpi"'), 4)
        self.assertEqual(html.count('class="status-form"'), 15)
        self.assertIn("Showing 15 of 15 synthetic records.", html)
        self.assertIn('/static/styles.css', html)
        css = self.client.get("/static/styles.css")
        self.assertEqual(css.status_code, 200)
        css.close()

    def test_search_and_combined_filters(self):
        self.assertEqual([r["id"] for r in self.context(q="FICTIONAL")["records"]], [4, 8, 12])
        self.assertEqual([r["id"] for r in self.context(q="15")["records"]], [15])
        context = self.context(q="demo", division="Finance", status="In progress")
        self.assertEqual([r["id"] for r in context["records"]], [5])
        self.assertEqual(dict(context["kpis"]),
                         {"Total records": 1, "Open": 0, "In progress": 1, "Completed": 0})
        response = self.client.get("/", query_string={"q": " DEMO ", "division": "Finance", "status": "In progress"})
        self.assertIn("Showing 1 of 15 synthetic records.", response.get_data(as_text=True))

    def test_each_division_and_status(self):
        for division in DIVISIONS:
            self.assertTrue(all(r["division"] == division for r in self.context(division=division)["records"]))
        for status in STATUSES:
            self.assertEqual(len(self.context(status=status)["records"]), 5)

    def test_empty_state_and_escaped_search(self):
        context = self.context(q="no-matching-record")
        self.assertEqual(context["records"], [])
        self.assertTrue(all(value == 0 for _, value in context["kpis"]))
        response = self.client.get("/", query_string={"q": '<script>alert("x")</script>'})
        html = response.get_data(as_text=True)
        self.assertIn("No records match", html)
        self.assertNotIn('<script>', html)
        self.assertIn("&lt;script&gt;", html)

    def test_update_recalculates_and_preserves_filters(self):
        response = self.client.post("/records/1/status", data={
            "new_status": "Completed", "q": "service", "division": "Customer Operations", "status": "Open",
        })
        self.assertEqual(response.status_code, 303)
        from urllib.parse import parse_qs, urlsplit
        self.assertEqual(parse_qs(urlsplit(response.location).query),
                         {"q": ["service"], "division": ["Customer Operations"], "status": ["Open"]})
        self.assertEqual(records[0]["status"], "Completed")
        self.assertEqual(dict(self.context()["kpis"]),
                         {"Total records": 15, "Open": 4, "In progress": 5, "Completed": 6})
        filtered = self.client.get(response.location)
        self.assertIn("Showing 0 of 15", filtered.get_data(as_text=True))
        self.assert_warning(filtered)
        # Saving the same status twice must not change totals again.
        self.client.post("/records/1/status", data={"new_status": "Completed"})
        self.assertEqual(dict(self.context()["kpis"])["Completed"], 6)

    def test_rejected_requests_do_not_mutate(self):
        requests = [
            ("get", "/?division=Unknown", None, 400),
            ("get", "/?status=Unknown", None, 400),
            ("post", "/records/1/status", {"new_status": "Unknown"}, 400),
            ("post", "/records/1/status", {}, 400),
            ("post", "/records/1/status", {"new_status": "Completed", "division": "Unknown"}, 400),
            ("post", "/records/999/status", {"new_status": "Completed"}, 404),
            ("get", "/records/1/status", None, 405),
            ("get", "/missing", None, 404),
        ]
        for method, path, data, expected in requests:
            with self.subTest(path=path, data=data):
                response = getattr(self.client, method)(path, data=data)
                self.assertEqual(response.status_code, expected)
                self.assert_warning(response)
                self.assertEqual(records, self.original)
                if expected == 405:
                    self.assertIn("POST", response.headers["Allow"])


if __name__ == "__main__":
    unittest.main()
