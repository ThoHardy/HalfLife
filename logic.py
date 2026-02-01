import math
from datetime import datetime, timezone

def calculate_priority(created_at: datetime, half_life: float) -> float:
    now = datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    
    days_elapsed = (now - created_at).total_seconds() / 86400.0
    exponent = -days_elapsed * math.log(2) / max(0.1, half_life)
    
    if exponent < -700:
        return 100.0
    
    return 100.0 * (1.0 - math.exp(exponent))
