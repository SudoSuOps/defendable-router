import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from defendable_router.core.config import get_settings
from defendable_router.db.models import Base, ComputeNode, Dataset, Member
from defendable_router.db.session import get_db
from defendable_router.main import app
from defendable_router.services.members import activate_member


@pytest.fixture
def client(monkeypatch):
    tmpdir = tempfile.TemporaryDirectory()
    settings = get_settings()
    monkeypatch.setattr(settings, "receipts_dir", Path(tmpdir.name) / "receipts")
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db:
        db.add_all([
            Member(id="mem_active", email="active@example.com", name="Active Member"),
            Member(id="mem_inactive", email="inactive@example.com", name="Inactive Member"),
            Dataset(id="ds_gold", title="Gold Dataset", domain="finance", description="Test dataset", object_uri="s3://datasets/ds_gold", license_type="member", quality_tier="gold", checksum_sha256="a" * 64, size_bytes=100, row_count=10),
            ComputeNode(id="node_6000", hostname="rails-6000-01", gpu_type="rtx6000_blackwell_96gb", gpu_name="RTX PRO 6000 Blackwell Workstation 96GB", vram_gb=96, hourly_rate_usd=5.0, max_concurrent_jobs=1, tags=["test"]),
            ComputeNode(id="node_5090", hostname="smash-5090-01", gpu_type="rog_astral_5090_32gb", gpu_name="ASUS ROG Astral RTX 5090 32GB", vram_gb=32, hourly_rate_usd=2.0, max_concurrent_jobs=1, tags=["test"]),
        ])
        db.commit()
        activate_member(db, "mem_active")

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.state.testing_session_local = TestingSessionLocal
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        if hasattr(app.state, "testing_session_local"):
            delattr(app.state, "testing_session_local")
        tmpdir.cleanup()
