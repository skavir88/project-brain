"""Run the synthetic Certified Knowledge → Qdrant → Dify vertical slice.

This program is executed inside the existing Dify API runtime. It never reads
raw ingestion records or provider credentials: it receives knowledge only from
the loopback Enterprise AI retrieval service and resolves already configured
Dify models through Dify's normal runtime.
"""

from __future__ import annotations

import json
import sys
import uuid
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

sys.path.insert(0, "/app/api")

from app_factory import create_app
from core.entities.embedding_type import EmbeddingInputType
from core.model_manager import ModelManager
from extensions.ext_database import db
from graphon.model_runtime.entities.message_entities import SystemPromptMessage, UserPromptMessage
from graphon.model_runtime.entities.model_entities import ModelType
from models.provider import ProviderModel
from sqlalchemy import select


KNOWLEDGE_SERVICE = "http://ingestion-service:8080"
QDRANT_URL = "http://rdvector:6333"
COLLECTION = "enterprise_ai_certified_knowledge_v1"
MIN_CERTIFIED_EVIDENCE_SCORE = 0.70
REQUIRED_FIELDS = {
    "knowledge_id",
    "source_fingerprint",
    "source_record_id",
    "certification_event_id",
    "knowledge_text",
    "provenance",
    "certifying_actor",
    "certification_timestamp",
    "certification_policy_version",
}


def http_json(url: str, method: str = "GET", payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=30) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def certified_knowledge(query: str = "") -> list[dict[str, Any]]:
    status, payload = http_json(f"{KNOWLEDGE_SERVICE}/v1/knowledge?query={quote(query)}")
    if status != 200:
        raise RuntimeError("controlled Certified Knowledge retrieval failed")
    items = payload.get("items", [])
    if not isinstance(items, list) or any(set(item) != REQUIRED_FIELDS for item in items):
        raise RuntimeError("Certified Knowledge contract mismatch")
    return items


def model_instances() -> tuple[Any, Any]:
    app = create_app()[1]
    with app.app_context():
        embedding = db.session.scalar(
            select(ProviderModel).where(
                ProviderModel.is_valid.is_(True), ProviderModel.model_type == ModelType.TEXT_EMBEDDING
            ).limit(1)
        )
        llm = db.session.scalar(
            select(ProviderModel).where(
                ProviderModel.is_valid.is_(True), ProviderModel.model_type == ModelType.LLM
            ).limit(1)
        )
        if embedding is None or llm is None:
            raise RuntimeError("configured Dify model capability is unavailable")
        manager = ModelManager.for_tenant(embedding.tenant_id)
        embedding_instance = manager.get_model_instance(
            embedding.tenant_id, embedding.provider_name, ModelType.TEXT_EMBEDDING, embedding.model_name
        )
        llm_instance = ModelManager.for_tenant(llm.tenant_id).get_model_instance(
            llm.tenant_id, llm.provider_name, ModelType.LLM, llm.model_name
        )
        return embedding_instance, llm_instance


def vectorize(model: Any, texts: list[str], input_type: EmbeddingInputType) -> list[list[float]]:
    result = model.invoke_text_embedding(texts, input_type)
    return [[float(value) for value in vector] for vector in result.embeddings]


def point_id(knowledge_id: str) -> str:
    return str(uuid.UUID(knowledge_id[:32]))


def ensure_collection(vector_size: int) -> bool:
    status, payload = http_json(f"{QDRANT_URL}/collections/{COLLECTION}")
    if status == 404:
        create_status, _ = http_json(
            f"{QDRANT_URL}/collections/{COLLECTION}",
            "PUT",
            {"vectors": {"size": vector_size, "distance": "Cosine"}},
        )
        if create_status not in (200, 201):
            raise RuntimeError("isolated Qdrant collection creation failed")
        return True
    if status != 200:
        raise RuntimeError("isolated Qdrant collection preflight failed")
    existing_size = payload["result"]["config"]["params"]["vectors"]["size"]
    if existing_size != vector_size:
        raise RuntimeError("existing collection embedding dimension mismatch")
    return False


def index() -> None:
    items = certified_knowledge()
    if not items:
        raise RuntimeError("no Certified Knowledge is available to index")
    embedding, _ = model_instances()
    vectors = vectorize(embedding, [item["knowledge_text"] for item in items], EmbeddingInputType.DOCUMENT)
    if len(vectors) != len(items) or not vectors or any(len(vector) != len(vectors[0]) for vector in vectors):
        raise RuntimeError("embedding result is incompatible with Certified Knowledge")
    collection_created = ensure_collection(len(vectors[0]))
    points = []
    for item, vector in zip(items, vectors, strict=True):
        payload = {field: item[field] for field in REQUIRED_FIELDS}
        points.append({"id": point_id(item["knowledge_id"]), "vector": vector, "payload": payload})
    status, _ = http_json(f"{QDRANT_URL}/collections/{COLLECTION}/points?wait=true", "PUT", {"points": points})
    if status != 200:
        raise RuntimeError("Qdrant Certified Knowledge upsert failed")
    print(json.dumps({
        "operation": "index", "certified_knowledge_items": len(items), "vector_dimension": len(vectors[0]),
        "collection_created": collection_created, "raw_ingestion_records_read": False,
    }, separators=(",", ":")))


def answer(question: str) -> None:
    embedding, llm = model_instances()
    query_vector = vectorize(embedding, [question], EmbeddingInputType.QUERY)[0]
    status, payload = http_json(
        f"{QDRANT_URL}/collections/{COLLECTION}/points/query",
        "POST",
        {"query": query_vector, "limit": 3, "with_payload": True},
    )
    if status != 200:
        raise RuntimeError("Qdrant Certified Knowledge query failed")
    points = [
        point for point in payload.get("result", {}).get("points", [])
        if float(point.get("score", 0.0)) >= MIN_CERTIFIED_EVIDENCE_SCORE
    ]
    if not points:
        print(json.dumps({"status": "insufficient_certified_evidence", "provenance": []}, separators=(",", ":")))
        return
    provenance = []
    context_parts = []
    for point in points:
        item = point.get("payload", {})
        if set(item) != REQUIRED_FIELDS:
            raise RuntimeError("Qdrant payload is not a Certified Knowledge item")
        provenance.append({
            "knowledge_id": item["knowledge_id"], "source_record_id": item["source_record_id"],
            "source_fingerprint": item["source_fingerprint"], "certification_event_id": item["certification_event_id"],
            "certification_timestamp": item["certification_timestamp"],
            "certification_policy_version": item["certification_policy_version"],
            "retrieval_score": round(float(point["score"]), 6),
        })
        context_parts.append(item["knowledge_text"])
    messages = [
        SystemPromptMessage(content="Answer only from the supplied Certified Knowledge context. If it is insufficient, reply exactly insufficient_certified_evidence."),
        UserPromptMessage(content=f"Certified Knowledge context:\n{'\n'.join(context_parts)}\n\nQuestion: {question}"),
    ]
    result = llm.invoke_llm(messages, model_parameters={"max_tokens": 120}, stream=False)
    text = (result.message.get_text_content() or "").strip()
    if not text:
        raise RuntimeError("Dify generation returned no answer")
    print(json.dumps({
        "status": "grounded_answer", "answer": text, "provenance": provenance,
        "raw_ingestion_records_read": False,
    }, separators=(",", ":")))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "index":
        index()
    elif len(sys.argv) == 3 and sys.argv[1] == "answer":
        answer(sys.argv[2])
    else:
        raise SystemExit("usage: run_certified_rag.py index | answer <synthetic-question>")
