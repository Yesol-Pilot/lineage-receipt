"""Seed and verify a small ML lineage graph in a local DataHub instance.

The script intentionally keeps credentials outside the repository.  It uses the
official acryl-datahub SDK and ~/.datahubenv (or DATAHUB_GMS_URL /
DATAHUB_GMS_TOKEN) for both writes and reads.
"""

from __future__ import annotations

import argparse
import json
import warnings
from datetime import datetime, timezone
from typing import Any

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.mce_builder import make_ml_model_deployment_urn
from datahub.metadata.schema_classes import (
    AuditStampClass,
    DataProcessInstanceInputClass,
    DataProcessInstanceOutputClass,
    DataProcessInstancePropertiesClass,
    DeploymentStatusClass,
    MLModelDeploymentPropertiesClass,
    MLTrainingRunPropertiesClass,
    VersionTagClass,
)
from datahub.metadata.urns import DataProcessInstanceUrn
from datahub.sdk import DataFlow, DataHubClient, DataJob, Dataset, MLModel

warnings.filterwarnings("ignore", category=Warning)


PLATFORM = "snowflake"
ENV = "PROD"
INPUT_NAME = "lineage-receipt/churn-training"
FEATURE_NAME = "lineage-receipt/churn-features"
MODEL_ID = "lineage-receipt-churn-risk"
FLOW_NAME = "lineage-receipt-serving"
JOB_NAME = "lineage-receipt-prod-deployment"
RUN_ID = "lineage-receipt-training-20260719"


def stable_fingerprint(value: str) -> str:
    """Match engine/release-audit.mjs for the ASCII receipt payload."""
    hash_value = 0x811C9DC5
    for char in value:
        hash_value ^= ord(char)
        hash_value = (hash_value * 0x01000193) & 0xFFFFFFFF
    return f"{hash_value:08x}" * 8


def days_between(start: str, end: str) -> int:
    first = datetime.fromisoformat(start).date()
    last = datetime.fromisoformat(end).date()
    return (last - first).days


def make_assets() -> tuple[Dataset, Dataset, MLModel, DataFlow, DataJob, str]:
    input_dataset = Dataset(
        platform=PLATFORM,
        name=INPUT_NAME,
        env=ENV,
        display_name="Churn training dataset",
        description="Synthetic, non-sensitive fixture for the LineageReceipt demo.",
        schema=[("customer_id", "string"), ("tenure_months", "number"), ("churned", "boolean")],
        custom_properties={
            "lineage_receipt_fixture": "true",
            "owner": "platform-data",
            "freshness_date": "2026-07-18",
        },
    )
    feature_dataset = Dataset(
        platform=PLATFORM,
        name=FEATURE_NAME,
        env=ENV,
        display_name="Churn feature set",
        description="Feature view used by the model release fixture.",
        schema=[("customer_id", "string"), ("risk_score", "number")],
        custom_properties={
            "lineage_receipt_fixture": "true",
            "owner": "data-science",
            "freshness_date": "2026-06-29",
        },
    )
    flow = DataFlow(
        platform="airflow",
        name=FLOW_NAME,
        display_name="LineageReceipt serving flow",
        description="Synthetic deployment flow for the hackathon proof.",
        custom_properties={"lineage_receipt_fixture": "true", "environment": "production"},
    )
    job = DataJob(
        name=JOB_NAME,
        flow=flow,
        display_name="Churn risk production deployment",
        description="Deployment node represented as a DataHub DataJob.",
        custom_properties={
            "lineage_receipt_fixture": "true",
            "rollback_runbook": "",
            "environment": "production",
        },
        inlets=[str(feature_dataset.urn)],
    )
    deployment_urn = make_ml_model_deployment_urn("kubernetes", "lineage-receipt-prod", ENV)
    model = MLModel(
        id=MODEL_ID,
        platform="mlflow",
        version="1.2.0",
        name="Churn risk model",
        description="Synthetic model used to demonstrate evidence-first release gating.",
        custom_properties={
            "lineage_receipt_fixture": "true",
            "freshness_date": "2026-07-18",
            "deployment_urn": deployment_urn,
        },
        training_metrics={"roc_auc": "0.91"},
    )
    model.add_deployment(deployment_urn)
    return input_dataset, feature_dataset, model, flow, job, deployment_urn


def emit_deployment(client: DataHubClient, deployment_urn: str) -> None:
    graph = client._graph
    # MLModelDeployment is a first-class DataHub entity, but the SDK does not
    # expose an entity wrapper yet. Emit its key and properties directly.
    from datahub.metadata.schema_classes import MLModelDeploymentKeyClass

    key = MLModelDeploymentKeyClass(platform="kubernetes", name="lineage-receipt-prod", origin=ENV)
    props = MLModelDeploymentPropertiesClass(
        description="Synthetic production deployment for the LineageReceipt demo.",
        customProperties={"lineage_receipt_fixture": "true", "rollback_runbook": ""},
        version=VersionTagClass(versionTag="1.2.0"),
        status=DeploymentStatusClass.IN_SERVICE,
    )
    mcps = []
    if not graph.exists(deployment_urn):
        mcps.append(MetadataChangeProposalWrapper(entityUrn=deployment_urn, aspect=key, changeType="CREATE_ENTITY"))
    mcps.extend(MetadataChangeProposalWrapper.construct_many(deployment_urn, [props]))
    graph.emit_mcps(mcps)


def emit_training_run(client: DataHubClient, input_dataset: Dataset, feature_dataset: Dataset, model: MLModel) -> str:
    run_urn = DataProcessInstanceUrn(RUN_ID)
    graph = client._graph
    now_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    actor = "urn:li:corpuser:datahub"
    aspects = [
        DataProcessInstancePropertiesClass(
            name="LineageReceipt churn training run",
            created=AuditStampClass(time=now_ms, actor=actor),
            customProperties={"lineage_receipt_fixture": "true", "model_version": "1.2.0"},
        ),
        DataProcessInstanceInputClass(inputs=[str(input_dataset.urn), str(feature_dataset.urn)]),
        DataProcessInstanceOutputClass(outputs=[str(model.urn)]),
        MLTrainingRunPropertiesClass(
            id=RUN_ID,
            trainingMetrics=[],
            hyperParams=[],
            customProperties={"lineage_receipt_fixture": "true"},
        ),
    ]
    mcps = []
    if not graph.exists(str(run_urn)):
        mcps.append(
            MetadataChangeProposalWrapper(
                entityUrn=str(run_urn),
                aspect=run_urn.to_key_aspect(),
                changeType="CREATE_ENTITY",
            )
        )
    mcps.extend(MetadataChangeProposalWrapper.construct_many(str(run_urn), aspects))
    graph.emit_mcps(mcps)
    model.add_training_job(run_urn)
    client.entities.upsert(model)
    return str(run_urn)


def read_evidence(client: DataHubClient, input_dataset: Dataset, feature_dataset: Dataset, model: MLModel, job: DataJob, run_urn: str) -> dict[str, Any]:
    graph = client._graph
    input_entity = client.entities.get(input_dataset.urn)
    feature_entity = client.entities.get(feature_dataset.urn)
    model_entity = client.entities.get(model.urn)
    run_inputs = graph.get_aspect(run_urn, DataProcessInstanceInputClass)
    run_outputs = graph.get_aspect(run_urn, DataProcessInstanceOutputClass)
    input_props = input_entity.custom_properties or {}
    feature_props = feature_entity.custom_properties or {}
    model_props = model_entity.custom_properties or {}
    return {
        "model": f"{MODEL_ID}@1.2.0",
        "nodes": [
            {"kind": "Dataset", "name": input_entity.display_name or INPUT_NAME, "urn": str(input_entity.urn), "owner": input_props.get("owner"), "freshness": input_props.get("freshness_date"), "state": "OK"},
            {"kind": "FeatureSet", "name": feature_entity.display_name or FEATURE_NAME, "urn": str(feature_entity.urn), "owner": feature_props.get("owner"), "freshness": feature_props.get("freshness_date"), "state": "WARN"},
            {"kind": "MLModel", "name": model_entity.name or MODEL_ID, "urn": str(model_entity.urn), "owner": None, "freshness": model_props.get("freshness_date"), "state": "REPAIR"},
            {"kind": "Deployment", "name": job.display_name or JOB_NAME, "urn": str(job.urn), "owner": "ml-platform", "freshness": "2026-07-18", "state": "OK"},
        ],
        "rollbackRunbook": None,
        "lineage": {
            "runUrn": run_urn,
            "inputs": list(run_inputs.inputs) if run_inputs else [],
            "outputs": list(run_outputs.outputs) if run_outputs else [],
            "modelTrainingJobs": list(model_entity.training_jobs or []),
            "modelDeployments": list(model_entity.deployments or []),
        },
    }


def build_receipt(evidence: dict[str, Any], today: str) -> dict[str, Any]:
    gaps: list[dict[str, str]] = []
    model = next(node for node in evidence["nodes"] if node["kind"] == "MLModel")
    feature = next(node for node in evidence["nodes"] if node["kind"] == "FeatureSet")
    if not model.get("owner"):
        gaps.append({"id": "missing-owner", "title": "Missing owner", "detail": f"{evidence['model']} has no owner recorded in DataHub."})
    if feature.get("freshness") and days_between(feature["freshness"], today) > 7:
        gaps.append({"id": "stale-feature", "title": "Stale feature freshness", "detail": f"Feature set freshness is {feature['freshness']}; it is older than 7 days."})
    if not evidence.get("rollbackRunbook"):
        gaps.append({"id": "no-rollback", "title": "No rollback runbook", "detail": "No rollback runbook is linked to the production deployment."})
    canonical = json.dumps({"model": evidence["model"], "gaps": [gap["id"] for gap in gaps]}, separators=(",", ":"))
    digest = stable_fingerprint(canonical)
    return {"verdict": "REPAIR" if gaps else "APPROVE", "gaps": gaps, "digest": digest, "receiptId": f"LR-{digest[:6].upper()}"}


def write_decision(client: DataHubClient, model: MLModel, receipt: dict[str, Any]) -> None:
    current = dict(model.custom_properties or {})
    current.update(
        {
            "lineage_receipt_verdict": receipt["verdict"],
            "lineage_receipt_id": receipt["receiptId"],
            "lineage_receipt_digest": receipt["digest"],
            "lineage_receipt_gaps": ",".join(gap["id"] for gap in receipt["gaps"]),
            "lineage_receipt_recorded_at": datetime.now(tz=timezone.utc).isoformat(),
        }
    )
    model.set_custom_properties(current)
    client.entities.upsert(model)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-decision", action="store_true", help="persist the computed receipt on the MLModel custom properties")
    parser.add_argument("--today", default="2026-07-19", help="date used by the deterministic freshness rule")
    args = parser.parse_args()
    client = DataHubClient.from_env()
    client.test_connection()
    input_dataset, feature_dataset, model, flow, job, deployment_urn = make_assets()
    emit_deployment(client, deployment_urn)
    for entity in (input_dataset, feature_dataset, flow, job, model):
        client.entities.upsert(entity)
    run_urn = emit_training_run(client, input_dataset, feature_dataset, model)
    evidence = read_evidence(client, input_dataset, feature_dataset, model, job, run_urn)
    receipt = build_receipt(evidence, args.today)
    if args.write_decision:
        write_decision(client, model, receipt)
        persisted_model = client.entities.get(model.urn)
        persisted_properties = persisted_model.custom_properties or {}
        evidence["decisionWrite"] = {
            "entityUrn": str(model.urn),
            "customProperty": "lineage_receipt_verdict",
            "readbackVerdict": persisted_properties.get("lineage_receipt_verdict"),
            "readbackReceiptId": persisted_properties.get("lineage_receipt_id"),
        }
    print(json.dumps({"evidence": evidence, "receipt": receipt}, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
