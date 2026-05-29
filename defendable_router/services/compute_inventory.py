import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from defendable_router.core.pricing import GPU_PRICING
from defendable_router.db.models import ComputeNode, ComputeNodeStatus
from defendable_router.schemas.compute import ComputeNodeCreate


def list_nodes(db: Session) -> list[ComputeNode]:
    """Return all registered compute nodes."""
    return list(db.scalars(select(ComputeNode)).all())


def register_node(db: Session, payload: ComputeNodeCreate) -> ComputeNode:
    """Register a compute node using central GPU SKU pricing metadata."""
    if payload.gpu_type not in GPU_PRICING:
        raise ValueError("unsupported GPU SKU")
    price = GPU_PRICING[payload.gpu_type]
    node = ComputeNode(id=payload.id or f"node_{uuid.uuid4().hex}", hostname=payload.hostname, gpu_type=payload.gpu_type, gpu_name=price["display_name"], vram_gb=price["vram_gb"], hourly_rate_usd=float(price["hourly_rate_usd"]), max_concurrent_jobs=payload.max_concurrent_jobs, tags=payload.tags)
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def assign_available_node(db: Session, gpu_sku: str) -> ComputeNode | None:
    """Reserve capacity on the first available node for a GPU SKU."""
    stmt = select(ComputeNode).where(ComputeNode.gpu_type == gpu_sku, ComputeNode.status == ComputeNodeStatus.available.value, ComputeNode.current_jobs < ComputeNode.max_concurrent_jobs)
    node = db.scalars(stmt).first()
    if node is None:
        return None
    node.current_jobs += 1
    if node.current_jobs >= node.max_concurrent_jobs:
        node.status = ComputeNodeStatus.busy.value
    db.flush()
    return node


def release_node_capacity(db: Session, node_id: str | None) -> None:
    """Release one job slot from a node after completion or cancellation."""
    if not node_id:
        return
    node = db.get(ComputeNode, node_id)
    if node is None:
        return
    node.current_jobs = max(0, node.current_jobs - 1)
    if node.status == ComputeNodeStatus.busy.value and node.current_jobs < node.max_concurrent_jobs:
        node.status = ComputeNodeStatus.available.value
    db.flush()
