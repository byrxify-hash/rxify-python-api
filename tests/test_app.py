"""Offline endpoint tests: replace only the external Croissant data source."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


class DatasetTests(unittest.TestCase):
    def load_app(self, records=(), error=None, record_sets=True):
        dataset = Mock()
        dataset.metadata.record_sets = [SimpleNamespace(id="medicines")] if record_sets else []
        dataset.records.return_value = iter(records)
        factory = Mock(return_value=dataset, side_effect=error)
        spec = importlib.util.spec_from_file_location(
            "rxify_test_app", Path(__file__).resolve().parents[1] / "app.py"
        )
        module = importlib.util.module_from_spec(spec)
        with patch.dict("sys.modules", {"mlcroissant": SimpleNamespace(Dataset=factory)}):
            with patch("flask.Flask.logger"):
                spec.loader.exec_module(module)
        module.app.config["TESTING"] = True
        return module, module.app.test_client()

    def assert_unavailable(self, client):
        for path in ("/", "/medicines", "/medicines?q=aspirin"):
            with self.subTest(path=path):
                response = client.get(path)
                self.assertEqual(response.status_code, 503)
                self.assertEqual(response.json, {
                    "status": "unavailable", "dataset_status": "failed",
                    "error": {"code": "dataset_unavailable",
                              "message": "Medicine data is unavailable. Please try again later."}
                })

    def test_success_preserves_decoding_and_search(self):
        _, client = self.load_app([
            {b"med/Product Name": b"Aspirin", "med/Uses": "Pain", "med/Dose": 10},
            {"med/Product Name": "Paracetamol", "med/Uses": "Fever"},
        ])
        self.assertEqual(client.get("/").json, {
            "status": "online", "dataset_status": "ready", "total_cached": 2,
            "dataset": "Indian Medicine Data - Full Fetch"
        })
        response = client.get("/medicines")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0], {"Product Name": "Aspirin", "Uses": "Pain", "Dose": "10"})
        self.assertEqual(client.get("/medicines?q=%20AS%20").json, response.json[:1])
        self.assertEqual(client.get("/medicines?q=fever").json, response.json[1:])
        self.assertEqual(client.get("/medicines?q=sp").json, [])
        self.assertEqual(client.get("/medicines?q=unknown").json, [])

    def test_existing_result_limits(self):
        _, client = self.load_app([{"Name": "Aspirin"}] * 120)
        self.assertEqual(len(client.get("/medicines").json), 50)
        self.assertEqual(len(client.get("/medicines?q=asp").json), 100)

    def test_successful_empty_dataset_is_ready(self):
        _, client = self.load_app()
        self.assertEqual(client.get("/").json["dataset_status"], "ready")
        self.assertEqual(client.get("/medicines").status_code, 200)
        self.assertEqual(client.get("/medicines").json, [])

    def test_constructor_failure(self):
        _, client = self.load_app(error=RuntimeError("private upstream details"))
        self.assert_unavailable(client)

    def test_missing_record_set(self):
        _, client = self.load_app(record_sets=False)
        self.assert_unavailable(client)

    def test_download_failure_discards_partial_records(self):
        def interrupted_download():
            yield {"Name": "Aspirin"}
            raise RuntimeError("download interrupted")
        module, client = self.load_app(records=interrupted_download())
        self.assertEqual(module.cached_records, [])
        self.assert_unavailable(client)

    def test_record_decoding_failure(self):
        module, client = self.load_app(records=[None])
        self.assertEqual(module.cached_records, [])
        self.assert_unavailable(client)


if __name__ == "__main__":
    unittest.main()
