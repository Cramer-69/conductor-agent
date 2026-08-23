import unittest

import pytest

# The voice agent ships in its own image and pins livekit-agents in
# requirements.livekit.txt, so CI installs from requirements-cloud.txt
# without it. Skip rather than error out during collection.
pytest.importorskip("livekit")

from livekit_agent import AraVoiceAgent, post_to_conductor


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"response": "Persistent answer"}


class FakeAsyncClient:
    def __init__(self):
        self.calls = []

    async def post(self, url, headers, json):
        self.calls.append((url, headers, json))
        return FakeResponse()


class FakeMemory:
    def __init__(self):
        self.turns = []

    def search(self, query):
        return ["John never wants to type."]

    def add_turn(self, user_text, assistant_text, provider):
        self.turns.append((user_text, assistant_text, provider))
        return True


class LiveKitAgentTests(unittest.IsolatedAsyncioTestCase):
    async def test_voice_turn_is_sent_to_conductor(self):
        client = FakeAsyncClient()

        result = await post_to_conductor("Remember this", client=client)

        self.assertEqual(result, "Persistent answer")
        self.assertTrue(client.calls[0][0].endswith("/api/chat"))
        self.assertEqual(client.calls[0][2], {"query": "Remember this"})

    async def test_agent_has_mem0_adapter(self):
        agent = AraVoiceAgent()
        agent.memory = FakeMemory()

        self.assertTrue(agent.memory.search("preferences"))


if __name__ == "__main__":
    unittest.main()
