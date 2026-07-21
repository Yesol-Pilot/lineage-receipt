import json
import unittest
from pathlib import Path


class DataHubMcpReplayFixtureTests(unittest.TestCase):
    def test_replay_fixture_is_explicit_and_receipt_bound(self):
        replay_path = Path(__file__).resolve().parents[1] / "evidence-datahub-mcp-replay.json"
        replay = json.loads(replay_path.read_text(encoding="utf-8"))

        self.assertEqual(replay["status"], "MCP_READ_SUCCESS")
        self.assertFalse(replay["liveGms"])
        self.assertEqual(
            [call["name"] for call in replay["toolCalls"]],
            ["get_entities", "get_lineage", "get_lineage"],
        )
        self.assertEqual(replay["receipt"]["receiptId"], "LR-4BFBA6")
        self.assertTrue(all(len(call["resultSha256"]) == 64 for call in replay["toolCalls"]))
        self.assertIn("healthy official DataHub GMS", replay["disclosure"])


if __name__ == "__main__":
    unittest.main()
