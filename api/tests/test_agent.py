import unittest
from types import SimpleNamespace

from helpers import FakeResponse, FakeSession
from app.agent import AgentError, DiagnosticsAgent, build_tools
from app.sources.registry import build_registry

INCIDENT = {"dag_id": "event_aggregator_etl", "task_id": "extract_mariinsky", "run_id": "manual__1"}


def tool_use(id_, name, **inp):
    return SimpleNamespace(type="tool_use", id=id_, name=name, input=inp)


class FakeMessages:
    def __init__(self, scripted):
        self.scripted, self.requests = list(scripted), []

    def create(self, **kwargs):
        self.requests.append({**kwargs, "messages": list(kwargs["messages"])})
        return SimpleNamespace(content=self.scripted.pop(0))


class FakeClient:
    def __init__(self, scripted):
        self.messages = FakeMessages(scripted)


DIAGNOSIS = dict(
    category="layout_changed", summary="Страница открывается, но карточек нет.",
    probable_cause="Сменилась вёрстка", suggested_action="Обновить селекторы", confidence="high",
)


def make_agent(scripted, html="<html>new</html>", max_steps=6):
    registry = build_registry(session=FakeSession(FakeResponse(text=html)))
    client = FakeClient(scripted)
    return DiagnosticsAgent(client, "test-model", build_tools(registry, airflow=None), max_steps), client


class AgentTests(unittest.TestCase):
    def test_probe_then_submit(self):
        agent, client = make_agent([
            [tool_use("1", "probe_source", source="mariinsky")],
            [tool_use("2", "submit_diagnosis", **DIAGNOSIS)],
        ])
        diagnosis = agent.run(INCIDENT)
        self.assertEqual(diagnosis.category, "layout_changed")
        tool_result = client.messages.requests[1]["messages"][-1]["content"][0]
        self.assertFalse(tool_result["is_error"])
        self.assertIn('"marker_found": false', tool_result["content"])

    def test_invalid_values_are_normalized(self):
        agent, _ = make_agent([[tool_use("1", "submit_diagnosis", **{**DIAGNOSIS, "category": "aliens", "confidence": "total"})]])
        diagnosis = agent.run(INCIDENT)
        self.assertEqual((diagnosis.category, diagnosis.confidence), ("unknown", "low"))

    def test_unknown_source_is_reported_to_model_not_raised(self):
        agent, client = make_agent([
            [tool_use("1", "probe_source", source="evil")],
            [tool_use("2", "submit_diagnosis", **DIAGNOSIS)],
        ])
        agent.run(INCIDENT)
        self.assertTrue(client.messages.requests[1]["messages"][-1]["content"][0]["is_error"])

    def test_unknown_tool_is_error_result(self):
        agent, client = make_agent([
            [tool_use("1", "rm_rf")],
            [tool_use("2", "submit_diagnosis", **DIAGNOSIS)],
        ])
        agent.run(INCIDENT)
        self.assertTrue(client.messages.requests[1]["messages"][-1]["content"][0]["is_error"])

    def test_step_limit(self):
        agent, _ = make_agent([[tool_use(str(i), "probe_source", source="mariinsky")] for i in range(3)], max_steps=3)
        with self.assertRaises(AgentError):
            agent.run(INCIDENT)

    def test_no_tool_call_is_error(self):
        agent, _ = make_agent([[SimpleNamespace(type="text", text="не знаю")]])
        with self.assertRaises(AgentError):
            agent.run(INCIDENT)

    def test_tool_arguments_are_validated(self):
        tools = build_tools({}, airflow=None)
        with self.assertRaises(ValueError):
            tools["get_task_log"](dag_id="../etc", run_id="x", task_id="y")
        with self.assertRaises(ValueError):
            tools["get_recent_runs"](dag_id="a/b")


if __name__ == "__main__":
    unittest.main()
