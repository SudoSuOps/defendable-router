from sqlalchemy.orm import Session

from defendable_router.core.pricing import GPU_PRICING
from defendable_router.db.models import Base, ComputeNode, Dataset, Member
from defendable_router.db.session import engine
from defendable_router.services.members import activate_member


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def seed_demo(db: Session) -> None:
    init_db()
    members = [
        Member(id="mem_demo_active_1", email="ada@defendable.cloud", name="Ada Member"),
        Member(id="mem_demo_active_2", email="grace@defendable.cloud", name="Grace Member"),
        Member(id="mem_demo_inactive_1", email="inactive@defendable.cloud", name="Inactive Member"),
    ]
    for member in members:
        if db.get(Member, member.id) is None:
            db.add(member)
    db.commit()
    activate_member(db, "mem_demo_active_1")
    activate_member(db, "mem_demo_active_2")
    datasets = [
        Dataset(id="ds_finance_gold", title="Curated Finance Signals", domain="finance", description="Validated market signal records.", object_uri="s3://defendable-datasets/finance/gold", license_type="member", quality_tier="gold", checksum_sha256="0" * 64, size_bytes=2048, row_count=1000),
        Dataset(id="ds_health_silver", title="Healthcare Claims Sample", domain="healthcare", description="De-identified claims sample metadata.", object_uri="s3://defendable-datasets/healthcare/silver", license_type="member", quality_tier="silver", checksum_sha256="1" * 64, size_bytes=4096, row_count=2500),
        Dataset(id="ds_legal_platinum", title="Legal Contract Clauses", domain="legal", description="Curated clause extraction corpus.", object_uri="s3://defendable-datasets/legal/platinum", license_type="member", quality_tier="platinum", checksum_sha256="2" * 64, size_bytes=8192, row_count=5000),
        Dataset(id="ds_security_royal", title="Security Incident Royal Jelly", domain="security", description="High-trust incident classification records.", object_uri="s3://defendable-datasets/security/royal", license_type="member", quality_tier="royal_jelly", checksum_sha256="3" * 64, size_bytes=16384, row_count=12000),
        Dataset(id="ds_general_bronze", title="General Web Bronze", domain="general", description="Broad crawl metadata sample.", object_uri="s3://defendable-datasets/general/bronze", license_type="member", quality_tier="bronze", checksum_sha256="4" * 64, size_bytes=1024, row_count=500),
    ]
    for dataset in datasets:
        if db.get(Dataset, dataset.id) is None:
            db.add(dataset)
    nodes = [("node_rails_6000_01", "rails-6000-01", "rtx6000_blackwell_96gb"), ("node_smash_5090_01", "smash-5090-01", "rog_astral_5090_32gb")]
    for node_id, hostname, sku in nodes:
        if db.get(ComputeNode, node_id) is None:
            price = GPU_PRICING[sku]
            db.add(ComputeNode(id=node_id, hostname=hostname, gpu_type=sku, gpu_name=price["display_name"], vram_gb=price["vram_gb"], hourly_rate_usd=float(price["hourly_rate_usd"]), tags=["demo", "defendablecloud"]))
    db.commit()
