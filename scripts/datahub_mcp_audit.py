"""Read DataHub lineage through the official DataHub MCP server.

This adapter is deliberately read-first: the official ``mcp-server-datahub``
process is launched over MCP stdio, ``get_entities`` and ``get_lineage`` are
called, and only that returned metadata is converted into the deterministic
LineageReceipt evidence shape.  No token is written to stdout or persisted in
the repository.

The default judge command follows DataHub's documented self-hosted setup::

    uvx mcp-server-datahub@0.6.0

Use ``--server-command mcp-server-datahub`` when the package is installed in a
virtual environment instead of being launched by uvx.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import shlex
from pathlib import Path
from typing import Any, Iterable

from datahub_roundtrip import build_receipt

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError as exc:  # pragma: no cover - exercised by cold-start setup
    raise SystemExit(
        "The MCP client is missing. Install requirements.txt before running "
        "scripts/datahub_mcp_audit.py."
    ) from exc


DEFAULT_SERVER_COMMAND = "uvx"
DEFAULT_SERVER_ARGS = ["mcp-server-datahub@0.6.0"]
REQUIRED_TOOLS = ("get_entities", "get_lineage")
DEFAULT_FIXTURE = Path(__file__).resolve().parents[1] / "evidence-datahub-roundtrip.json"


def to_jsonable(value: Any) -> Any:
    """Convert MCP SDK models into stable JSON-safe values."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return to_jsonable(model_dump(mode="json"))
    if hasattr(value, "__dict__"):
        return to_jsonable(vars(value))
    return str(value)


def stable_sha256(value: Any) -> str:
    canonical = json.dumps(to_jsonable(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def parse_server_spec(command: str | None, args: str | None) -> tuple[str, list[str]]:
    """Resolve the documented uvx default or an explicit local command."""
    if command:
        return command, shlex.split(args or "", posix=False)
    return DEFAULT_SERVER_COMMAND, list(DEFAULT_SERVER_ARGS)


def load_fixture(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    evidence = payload.get("evidence")
    if not isinstance(evidence, dict):
        raise ValueError(f"Fixture does not contain an evidence object: {path}")
    nodes = [node for node in evidence.get("nodes", []) if node.get("urn")]
    if not nodes:
        raise ValueError(f"Fixture does not contain DataHub node URNs: {path}")
    return evidence, nodes


def flatten_custom_properties(value: Any) -> dict[str, str]:
    """Normalize DataHub's GraphQL key/value list or SDK-style mapping."""
    if isinstance(value, dict):
        return {str(key): str(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return {
            str(item.get("key")): str(item.get("value"))
            for item in value
            if isinstance(item, dict) and item.get("key") is not None and item.get("value") is not None
        }
    return {}


def entity_properties(entity: dict[str, Any]) -> dict[str, Any]:
    properties = entity.get("properties")
    if isinstance(properties, dict):
        return properties
    return {}


def entity_custom_properties(entity: dict[str, Any]) -> dict[str, str]:
    properties = entity_properties(entity)
    return flatten_custom_properties(properties.get("customProperties"))


def entity_owner(entity: dict[str, Any]) -> str | None:
    ownership = entity.get("ownership")
    owners = ownership.get("owners", []) if isinstance(ownership, dict) else []
    if not isinstance(owners, list) or not owners:
        return None
    first = owners[0] if isinstance(owners[0], dict) else {}
    owner = first.get("owner") if isinstance(first, dict) else None
    if isinstance(owner, dict):
        return owner.get("urn") or (owner.get("properties") or {}).get("displayName")
    return str(owner) if owner else None


def entity_display_name(entity: dict[str, Any], fallback: str) -> str:
    properties = entity_properties(entity)
    return str(properties.get("name") or entity.get("name") or fallback)


def unwrap_tool_result(result: Any) -> Any:
    """Extract FastMCP structured output or its JSON text fallback."""
    structured = getattr(result, "structuredContent", None)
    if structured is None:
        structured = getattr(result, "structured_content", None)
    if structured:
        structured = to_jsonable(structured)
        if isinstance(structured, dict) and set(structured) == {"result"}:
            return structured["result"]
        return structured

    content = getattr(result, "content", None) or []
    for item in content:
        text = getattr(item, "text", None)
        if not text:
            continue
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            continue
    raise ValueError("MCP tool returned no structured JSON content")


def as_entity_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("result"), list):
        payload = payload["result"]
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def lineage_result_urns(payload: Any, direction: str) -> list[str]:
    section = payload.get(direction, {}) if isinstance(payload, dict) else {}
    results = section.get("searchResults", []) if isinstance(section, dict) else []
    urns: list[str] = []
    for item in results if isinstance(results, list) else []:
        entity = item.get("entity", {}) if isinstance(item, dict) else {}
        urn = entity.get("urn") if isinstance(entity, dict) else None
        if urn and urn not in urns:
            urns.append(str(urn))
    return urns


def lineage_facet_urns(payload: Any, direction: str, field: str) -> list[str]:
    """Extract entity URNs from DataHub's lineage facet aggregations."""
    section = payload.get(direction, {}) if isinstance(payload, dict) else {}
    facets = section.get("facets", []) if isinstance(section, dict) else []
    urns: list[str] = []
    for facet in facets if isinstance(facets, list) else []:
        if not isinstance(facet, dict) or facet.get("field") != field:
            continue
        aggregations = facet.get("aggregations", [])
        for aggregation in aggregations if isinstance(aggregations, list) else []:
            entity = aggregation.get("entity") if isinstance(aggregation, dict) else None
            urn = entity.get("urn") if isinstance(entity, dict) else None
            if urn and urn not in urns:
                urns.append(str(urn))
    return urns


def lineage_process_urns(payload: Any) -> list[str]:
    """Extract process-instance URNs when the GMS exposes them in lineage."""
    all_urns = lineage_result_urns(payload, "upstreams") + lineage_result_urns(payload, "downstreams")
    return [urn for urn in all_urns if urn.startswith("urn:li:dataProcessInstance:")]


def build_mcp_evidence(
    fixture_evidence: dict[str, Any],
    fixture_nodes: list[dict[str, Any]],
    entities_payload: Any,
    lineage_payload: Any,
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Merge MCP readback into the evidence schema without hiding gaps.

    DataHub's MCP lineage tool does not expose every process-instance aspect on
    every server version. When that happens, the existing synthetic fixture
    context is retained for the missing field and reported in
    ``lineageFallbackFields`` instead of being silently treated as MCP data.
    """
    entity_map = {
        str(entity.get("urn")): entity
        for entity in as_entity_list(entities_payload)
        if entity.get("urn") and not entity.get("error")
    }
    missing_entity_urns: list[str] = []
    nodes: list[dict[str, Any]] = []
    for fixture_node in fixture_nodes:
        urn = str(fixture_node["urn"])
        entity = entity_map.get(urn)
        if entity is None:
            missing_entity_urns.append(urn)
            nodes.append(dict(fixture_node, source="fixture-fallback", mcpReadback=False))
            continue
        custom = entity_custom_properties(entity)
        nodes.append(
            {
                "kind": fixture_node.get("kind"),
                "name": entity_display_name(entity, str(fixture_node.get("name") or urn)),
                "urn": urn,
                "owner": entity_owner(entity) or custom.get("owner"),
                "freshness": custom.get("freshness_date"),
                "state": fixture_node.get("state"),
                "source": "datahub-mcp-server",
                "mcpReadback": True,
            }
        )

    model_node = next((node for node in nodes if node.get("kind") == "MLModel"), None)
    model_custom = entity_custom_properties(entity_map.get(str(model_node.get("urn"))) or {}) if model_node else {}
    job_node = next((node for node in nodes if node.get("kind") == "Deployment"), None)
    job_custom = entity_custom_properties(entity_map.get(str(job_node.get("urn"))) or {}) if job_node else {}
    upstreams = lineage_result_urns(lineage_payload, "upstreams")
    downstreams = lineage_result_urns(lineage_payload, "downstreams")
    process_urns = lineage_process_urns(lineage_payload)
    mcp_model_deployments = [urn for urn in downstreams if urn.startswith("urn:li:mlModelDeployment:")]
    fixture_lineage = fixture_evidence.get("lineage") or {}
    lineage_fallback_fields: list[str] = []
    facet_inputs = lineage_facet_urns(lineage_payload, "upstreams", "inputs")
    facet_outputs = lineage_facet_urns(lineage_payload, "upstreams", "outputs")
    mcp_inputs = [urn for urn in (facet_inputs or upstreams) if not urn.startswith("urn:li:dataProcessInstance:")]
    mcp_outputs = [urn for urn in (facet_outputs or downstreams) if not urn.startswith("urn:li:dataProcessInstance:")]
    inputs = mcp_inputs or list(fixture_lineage.get("inputs") or [])
    outputs = mcp_outputs or list(fixture_lineage.get("outputs") or [])
    if not mcp_inputs and fixture_lineage.get("inputs"):
        lineage_fallback_fields.append("inputs")
    if not mcp_outputs and fixture_lineage.get("outputs"):
        lineage_fallback_fields.append("outputs")
    training_jobs = process_urns or list(fixture_lineage.get("modelTrainingJobs") or [])
    run_urn = process_urns[0] if process_urns else fixture_lineage.get("runUrn")
    if not process_urns and fixture_lineage.get("runUrn"):
        lineage_fallback_fields.append("runUrn")
    if not process_urns and training_jobs:
        lineage_fallback_fields.append("modelTrainingJobs")
    model_deployments = mcp_model_deployments or ([model_custom["deployment_urn"]] if model_custom.get("deployment_urn") else list(fixture_lineage.get("modelDeployments") or []))
    if not mcp_model_deployments and not model_custom.get("deployment_urn") and fixture_lineage.get("modelDeployments"):
        lineage_fallback_fields.append("modelDeployments")
    evidence = {
        "model": fixture_evidence.get("model"),
        "nodes": nodes,
        "rollbackRunbook": job_custom.get("rollback_runbook") or None,
        "lineage": {
            "runUrn": run_urn,
            "inputs": inputs,
            "outputs": outputs,
            "modelTrainingJobs": training_jobs,
            "modelDeployments": model_deployments,
        },
    }
    return evidence, {
        "missingEntityUrns": missing_entity_urns,
        "lineageFallbackFields": lineage_fallback_fields,
    }


async def read_via_mcp(
    server_command: str,
    server_args: list[str],
    server_env: dict[str, str],
    entity_urns: list[str],
    model_urn: str,
) -> dict[str, Any]:
    server = StdioServerParameters(command=server_command, args=server_args, env=server_env)
    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            tool_list = await session.list_tools()
            tool_names = sorted(str(tool.name) for tool in tool_list.tools)
            missing_tools = [tool for tool in REQUIRED_TOOLS if tool not in tool_names]
            if missing_tools:
                raise RuntimeError(f"DataHub MCP server is missing required tools: {', '.join(missing_tools)}")
            entities_result = await session.call_tool("get_entities", {"urns": entity_urns})
            upstream_lineage_result = await session.call_tool(
                "get_lineage",
                {"urn": model_urn, "upstream": True, "max_hops": 3, "max_results": 30},
            )
            downstream_lineage_result = await session.call_tool(
                "get_lineage",
                {"urn": model_urn, "upstream": False, "max_hops": 3, "max_results": 30},
            )
            entities = unwrap_tool_result(entities_result)
            upstream_lineage = unwrap_tool_result(upstream_lineage_result)
            downstream_lineage = unwrap_tool_result(downstream_lineage_result)
            lineage = {
                "upstreams": upstream_lineage.get("upstreams", {}) if isinstance(upstream_lineage, dict) else {},
                "downstreams": downstream_lineage.get("downstreams", {}) if isinstance(downstream_lineage, dict) else {},
            }
            return {
                "serverInfo": to_jsonable(getattr(initialized, "serverInfo", None)),
                "protocolVersion": str(getattr(initialized, "protocolVersion", "unknown")),
                "tools": tool_names,
                "toolCalls": [
                    {
                        "name": "get_entities",
                        "arguments": {"urns": entity_urns},
                        "resultSha256": stable_sha256(entities),
                        "result": entities,
                    },
                    {
                        "name": "get_lineage",
                        "arguments": {"urn": model_urn, "upstream": True, "max_hops": 3, "max_results": 30},
                        "resultSha256": stable_sha256(upstream_lineage),
                        "result": upstream_lineage,
                    },
                    {
                        "name": "get_lineage",
                        "arguments": {"urn": model_urn, "upstream": False, "max_hops": 3, "max_results": 30},
                        "resultSha256": stable_sha256(downstream_lineage),
                        "result": downstream_lineage,
                    },
                ],
                "entities": entities,
                "lineage": lineage,
            }


def resolve_datahub_env() -> dict[str, str]:
    env = dict(os.environ)
    # DataHubClient.from_env also understands ~/.datahubenv, but explicitly
    # forwarding the two documented variables makes the MCP subprocess
    # reproducible and keeps all credential handling outside the repo.
    config_path = Path.home() / ".datahubenv"
    if config_path.exists():
        for raw_line in config_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if line.startswith("server:") and "DATAHUB_GMS_URL" not in env:
                env["DATAHUB_GMS_URL"] = line.split(":", 1)[1].strip()
            elif line.startswith("token:") and "DATAHUB_GMS_TOKEN" not in env:
                env["DATAHUB_GMS_TOKEN"] = line.split(":", 1)[1].strip()
    return env


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--today", default="2026-07-21")
    parser.add_argument("--server-command", help="override the MCP server executable")
    parser.add_argument("--server-args", help="quoted arguments for --server-command")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        fixture_evidence, fixture_nodes = load_fixture(args.fixture)
        server_command, server_args = parse_server_spec(args.server_command, args.server_args)
        model_node = next(node for node in fixture_nodes if node.get("kind") == "MLModel")
        entity_urns = [str(node["urn"]) for node in fixture_nodes]
        mcp_readback = asyncio.run(
            read_via_mcp(
                server_command,
                server_args,
                resolve_datahub_env(),
                entity_urns,
                str(model_node["urn"]),
            )
        )
        evidence, diagnostics = build_mcp_evidence(
            fixture_evidence,
            fixture_nodes,
            mcp_readback["entities"],
            mcp_readback["lineage"],
        )
        receipt = build_receipt(evidence, args.today)
        output = {
            "status": "MCP_READ_SUCCESS" if not any(diagnostics.values()) else "MCP_READ_SUCCESS_WITH_WARNINGS",
            "source": "official mcp-server-datahub"
            if (server_command == DEFAULT_SERVER_COMMAND and server_args == DEFAULT_SERVER_ARGS)
            or "mcp-server-datahub" in Path(server_command).name
            else "MCP transport override",
            "serverCommand": [server_command, *server_args],
            "mcp": {key: value for key, value in mcp_readback.items() if key not in {"entities", "lineage"}},
            **diagnostics,
            "evidence": evidence,
            "receipt": receipt,
        }
        print(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    except Exception as exc:  # Keep the failure machine-readable for judge readback.
        print(
            json.dumps(
                {
                    "status": "MCP_UNVERIFIED",
                    "verdict": "REPAIR",
                    "error": f"{type(exc).__name__}: {exc}",
                    "next": "Start DataHub Quickstart, export DATAHUB_GMS_URL/DATAHUB_GMS_TOKEN, and rerun the command.",
                },
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
