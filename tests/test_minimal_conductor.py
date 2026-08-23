import unittest

from conductor.minimal import MinimalConductor


class FakeMemory:
    def __init__(self):
        self.turns = []

    def search(self, query):
        return ["John uses speech because typing is painful."]

    def add_turn(self, user_text, assistant_text, provider):
        self.turns.append((user_text, assistant_text, provider))
        return True


class FakeWebSearch:
    def search(self, query):
        return [
            {
                "title": "Current source",
                "url": "https://example.com/current",
                "description": "Current verified details",
            }
        ]


class FakeCabinet:
    enabled = True

    def search(self, query):
        return [
            {
                "title": "CCG AI Business Plan",
                "path": "/private/CCG_AI_Business_Plan.html",
                "content": "The plan prioritizes a voice-first Conductor.",
                "score": -1.0,
            }
        ]


class MinimalConductorTests(unittest.TestCase):
    def test_chat_uses_and_persists_memory(self):
        conductor = MinimalConductor()
        conductor.provider = "openai"
        conductor.model = "test-model"
        conductor.memory = FakeMemory()
        conductor.web_search = FakeWebSearch()
        captured = {}

        def fake_openai(query):
            captured["query"] = query
            return "Voice path ready."

        conductor._call_openai = fake_openai
        result = conductor.chat("How should I interact?")

        self.assertIn("typing is painful", captured["query"])
        self.assertEqual(result["response"], "Voice path ready.")
        self.assertEqual(result["sources"][0]["platform"], "mem0")
        self.assertEqual(
            conductor.memory.turns[0],
            ("How should I interact?", "Voice path ready.", "openai:test-model"),
        )

    def test_explicit_web_request_adds_firecrawl_context(self):
        conductor = MinimalConductor()
        conductor.provider = "openai"
        conductor.model = "test-model"
        conductor.memory = FakeMemory()
        conductor.web_search = FakeWebSearch()
        captured = {}

        def fake_openai(query):
            captured["query"] = query
            return "Current answer."

        conductor._call_openai = fake_openai
        result = conductor.chat("Search the web for current details")

        self.assertIn("Current web-search results", captured["query"])
        self.assertTrue(any(source["platform"] == "firecrawl" for source in result["sources"]))

    def test_file_request_adds_local_cabinet_context(self):
        conductor = MinimalConductor()
        conductor.provider = "openai"
        conductor.model = "test-model"
        conductor.memory = FakeMemory()
        conductor.web_search = FakeWebSearch()
        conductor.cabinet = FakeCabinet()
        captured = {}

        def fake_openai(query):
            captured["query"] = query
            return "Cabinet answer."

        conductor._call_openai = fake_openai
        result = conductor.chat("What does my business plan say?")

        self.assertIn("Relevant local filing-cabinet excerpts", captured["query"])
        self.assertTrue(any(source["platform"] == "cabinet" for source in result["sources"]))


if __name__ == "__main__":
    unittest.main()
