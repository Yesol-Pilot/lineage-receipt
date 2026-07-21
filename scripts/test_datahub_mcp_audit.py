import json
import unittest

from datahub_mcp_audit import (
    build_mcp_evidence,
    flatten_custom_properties,
    lineage_process_urns,
    lineage_result_urns,
    parse_server_spec,
    stable_sha256,
    unwrap_tool_result,
)


class _Text:
    def __init__(self, text):
        self.text = text


class _ToolResult:
    def __init__(self, content, structuredContent=None):
        self.content = content
        self.structuredContent = structuredContent


class McpAdapterTests(unittest.TestCase):
    def test_server_defaults_to_pinned_official_command(self):
        self.assertEqual(parse_server_spec(None, None), ("uvx", ["mcp-server-datahub@0.6.0"]))

    def test_explicit_server_args_are_preserved(self):
        self.assertEqual(parse_server_spec("python", "-m fake_server --stdio"), ("python", ["-m", "fake_server", "--stdio"]))

    def test_tool_result_prefers_structured_content(self):
        result = _ToolResult([_Text('{"wrong": true}')], {"result": {"ok": True}})
        self.assertEqual(unwrap_tool_result(result), {"ok": True})

    def test_tool_result_parses_text_fallback(self):
        result = _ToolResult([_Text("not-json"), _Text('{"ok": true}')])
        self.assertEqual(unwrap_tool_result(result), {"ok": True})

    def test_properties_and_lineage_are_normalized(self):
        self.assertEqual(flatten_custom_properties([{"key": "owner", "value": "ml"}]), {"owner": "ml"})
        lineage = {
            "upstreams": {"searchResults": [{"entity": {"urn": "urn:input"}}]},
            "downstreams": {"searchResults": [{"entity": {"urn": "urn:output"}}]},
        }
        self.assertEqual(lineage_result_urns(lineage, "upstreams"), ["urn:input"])
        self.assertEqual(lineage_result_urns(lineage, "downstreams"), ["urn:output"])
        lineage["upstreams"]["searchResults"].append({"entity": {"urn": "urn:li:dataProcessInstance:run"}})
        self.assertEqual(lineage_process_urns(lineage), ["urn:li:dataProcessInstance:run"])

    def test_mcp_evidence_binds_readback_and_preserves_repair(self):
        fixture = {
            "model": "m@1",
            "nodes": [
                {"kind": "FeatureSet", "name": "features", "urn": "urn:feature", "state": "WARN"},
                {"kind": "MLModel", "name": "model", "urn": "urn:model", "state": "REPAIR"},
            ],
        }
        entities = [
            {
                "urn": "urn:feature",
                "properties": {"name": "Features from MCP", "customProperties": [{"key": "freshness_date", "value": "2026-07-01"}]},
            },
            {
                "urn": "urn:model",
                "properties": {"name": "Model from MCP", "customProperties": []},
            },
        ]
        evidence, diagnostics = build_mcp_evidence(fixture, fixture["nodes"], entities, {"upstreams": {"searchResults": []}})
        self.assertEqual(diagnostics["missingEntityUrns"], [])
        self.assertEqual(evidence["nodes"][0]["name"], "Features from MCP")
        self.assertTrue(all(node["mcpReadback"] for node in evidence["nodes"]))
        self.assertEqual(stable_sha256(evidence)[:8], stable_sha256(json.loads(json.dumps(evidence)))[:8])


if __name__ == "__main__":
    unittest.main()
