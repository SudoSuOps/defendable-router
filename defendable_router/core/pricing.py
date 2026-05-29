from decimal import Decimal

ANNUAL_MEMBERSHIP_PRICE_USD = Decimal("100.00")

GPU_PRICING = {
    "rtx6000_blackwell_96gb": {
        "display_name": "RTX PRO 6000 Blackwell Workstation 96GB",
        "hourly_rate_usd": Decimal("5.00"),
        "vram_gb": 96,
        "default_use": ["fine_tune", "inference", "evals", "dataset_generation"],
    },
    "rog_astral_5090_32gb": {
        "display_name": "ASUS ROG Astral RTX 5090 32GB",
        "hourly_rate_usd": Decimal("2.00"),
        "vram_gb": 32,
        "default_use": ["inference", "smaller_fine_tunes", "evals", "dev_jobs"],
    },
}


def supported_gpu_skus() -> list[str]:
    return list(GPU_PRICING.keys())


def get_gpu_price(sku: str) -> Decimal:
    try:
        return GPU_PRICING[sku]["hourly_rate_usd"]
    except KeyError as exc:
        raise ValueError(f"Unsupported GPU SKU: {sku}") from exc


def estimate_compute_cost(sku: str, hours: float | Decimal) -> Decimal:
    hour_value = Decimal(str(hours))
    if hour_value <= 0:
        raise ValueError("estimated hours must be greater than zero")
    return (get_gpu_price(sku) * hour_value).quantize(Decimal("0.01"))
