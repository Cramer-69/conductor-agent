import unittest

from conductor.firecrawl_tool import FirecrawlTool


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "data": {
                "web": [
                    {
                        "title": "Official result",
                        "url": "https://example.com/result",
                        "description": "Current information",
                    }
                ]
            }
        }


class FakeClient:
    def __init__(self):
        self.calls = []

    def post(self, url, headers, json):
        self.calls.append((url, headers, json))
        return FakeResponse()


class FirecrawlToolTests(unittest.TestCase):
    def test_search_uses_v2_and_returns_compact_results(self):
        client = FakeClient()
        tool = FirecrawlTool(api_key="test-key", client=client)

        results = tool.search("latest information")

        self.assertEqual(results[0]["title"], "Official result")
        self.assertTrue(client.calls[0][0].endswith("/v2/search"))
        self.assertNotEqual(client.calls[0][1]["Authorization"], "Bearer ")

    def test_disabled_search_is_safe(self):
        tool = FirecrawlTool(api_key=None, client=None)
        tool.api_key = None

        self.assertEqual(tool.search("anything"), [])


if __name__ == "__main__":
    unittest.main()
