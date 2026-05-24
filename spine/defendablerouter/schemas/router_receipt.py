from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Classification = Literal["UNCLASSIFIED", "INTERNAL", "PRIVILEGED", "RESTRICTED"]
DeedStatus = Literal["STUB_CREATED", "PENDING_TRIBUNAL", "ANCHORED", "REJECTED"]


class ReceiptInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    input_hash: str
    input_bytes: int = 0
    input_ref: str = "input.json"


class ReceiptOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    output_hash: Optional[str] = None
    output_bytes: int = 0
    output_ref: Optional[str] = None


class ObjectStorage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    bucket: str = "streetledger"
    prefix: str
    uri: str


class TribunalBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    verdict_id: Optional[str] = None
    classification: Classification = "UNCLASSIFIED"
    assignment_success: Optional[bool] = None
    evidence_strength: Optional[float] = None
    risk_temperature: Optional[float] = None
    validator_confidence: Optional[float] = None


class DDEEDBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    deed_id: Optional[str] = None
    deed_status: DeedStatus = "STUB_CREATED"
    deed_ref: str = "ddeed_stub.json"


class ReceiptHashes(BaseModel):
    model_config = ConfigDict(extra="forbid")
    receipt_sha256: Optional[str] = None
    canonical_receipt_sha256: Optional[str] = None


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    issued_by: str = "DefendableRouter"
    host: str = "smash"
    gpu: str = "RTX 5090"
    cuda: str = "13.1"


class RouterReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    receipt_type: Literal["DEFENDABLE_ROUTER_RECEIPT"] = "DEFENDABLE_ROUTER_RECEIPT"
    schema_version: str = "v0.1"
    receipt_id: str
    created_at: str

    client_id: str
    app_id: str
    agent_id: str

    edge_device_id: Optional[str] = None
    conversation_id: Optional[str] = None

    assignment_id: str
    route: str
    source_type: str

    input: ReceiptInput
    output: ReceiptOutput = Field(default_factory=ReceiptOutput)

    classification: Classification = "UNCLASSIFIED"

    object_storage: ObjectStorage
    tribunal: TribunalBlock = Field(default_factory=TribunalBlock)
    ddeed: DDEEDBlock = Field(default_factory=DDEEDBlock)

    hashes: ReceiptHashes = Field(default_factory=ReceiptHashes)
    provenance: Provenance = Field(default_factory=Provenance)
