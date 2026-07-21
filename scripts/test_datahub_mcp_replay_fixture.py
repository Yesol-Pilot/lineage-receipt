import json
import unittest
from pathlib import Path


class DataHubMcpReplayFixtureTests(unittest.TestCase):
    def test_replay_fixture_is_explicit_and_receipt_bound(self):
        replay_path = Path(__file__).resolve().parents[1] / "evidence-datahub-mcp-replay.json"
        replay = json.loads(replay_path.read_text(encoding="utf-8"))

        self.assertEqual(replay["status"], "MCP_READ_SUCCESS_WITH_WARNINGS")
        self.assertEqual(replay["source"], "official mcp-server-datahub")
        self.assertTrue(replay["liveGms"])
        self.assertEqual(replay["serverCommand"], ["uvx", "mcp-server-datahub@0.6.0"])
        self.assertEqual(replay["serverInfo"], {"name": "datahub", "version": "3.4.4"})
        self.assertEqual(
            [call["name"] for call in replay["toolCalls"]],
            ["get_entities", "get_lineage", "get_lineage"],
        )
        self.assertEqual(replay["receipt"]["receiptId"], "LR-520F80")
        self.assertTrue(all(len(call["resultSha256"]) == 64 for call in replay["toolCalls"]))
        self.assertEqual(replay["lineageFallbackFields"], ["modelDeployments"])
        self.assertIn("Live official DataHub GMS MCP readback", replay["disclosure"])
        self.assertIn("no approval is claimed", replay["disclosure"])


if __name__ == "__main__":
    unittest.main()
