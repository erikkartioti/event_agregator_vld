import os
import unittest

DAGS_DIR = os.path.join(os.path.dirname(__file__), "..", "dags")

try:
    from airflow.models import DagBag
except ImportError:  # локально без Airflow тест пропускается; в контейнере выполняется
    DagBag = None


@unittest.skipIf(DagBag is None, "apache-airflow не установлен")
class DagIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dagbag = DagBag(dag_folder=DAGS_DIR, include_examples=False)

    def test_no_import_errors(self):
        self.assertEqual(self.dagbag.import_errors, {})

    def test_dag_structure(self):
        dag = self.dagbag.get_dag("event_aggregator_etl")
        self.assertIsNotNone(dag)
        self.assertEqual(
            dag.get_task("load_events").upstream_task_ids,
            {"extract_russian_theater", "extract_mariinsky"},
        )
        self.assertEqual(dag.get_task("cleanup_outdated_events").upstream_task_ids, {"load_events"})
        self.assertEqual(dag.get_task("assert_sources_healthy").upstream_task_ids, {"cleanup_outdated_events"})
        self.assertFalse(dag.catchup)


if __name__ == "__main__":
    unittest.main()
