import unittest

from conductor.mem0_store import Mem0Store


class FakeMem0Client:
    def __init__(self):
        self.add_calls = []

    def search(self, query, filters):
        return {
            "results": [
                {"memory": "John prefers voice-first operation."},
                {"memory": "OpenAI is the council lead."},
            ]
        }

    def add(self, **kwargs):
        self.add_calls.append(kwargs)


class Mem0StoreTests(unittest.TestCase):
    def test_search_and_add_turn(self):
        client = FakeMem0Client()
        store = Mem0Store(user_id="john", client=client)

        self.assertEqual(
            store.search("How should I interact?"),
            [
                "John prefers voice-first operation.",
                "OpenAI is the council lead.",
            ],
        )
        self.assertTrue(store.add_turn("Hello", "Hi John", "openai:test"))
        self.assertEqual(client.add_calls[0]["user_id"], "john")
        self.assertEqual(client.add_calls[0]["metadata"]["source"], "conductor-voice")

    def test_disabled_store_is_safe(self):
        store = Mem0Store(api_key=None, client=None)
        store._client = None

        self.assertEqual(store.search("anything"), [])
        self.assertFalse(store.add_turn("Hello", "Hi", "openai:test"))


if __name__ == "__main__":
    unittest.main()
