from decimal import Decimal
from defendable_router.core.pricing import estimate_compute_cost, get_gpu_price


def quote_compute(gpu_sku: str, estimated_hours: float) -> tuple[Decimal, Decimal]:
    """Return hourly rate and estimated cost for a supported GPU SKU."""
    hourly_rate = get_gpu_price(gpu_sku)
    estimated_cost = estimate_compute_cost(gpu_sku, estimated_hours)
    return hourly_rate, estimated_cost


def actual_compute_cost(gpu_sku: str, actual_hours: float) -> Decimal:
    """Calculate final compute cost from measured runtime hours."""
    return estimate_compute_cost(gpu_sku, actual_hours)
