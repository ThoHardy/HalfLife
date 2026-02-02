from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Task(BaseModel):
    id: str
    name: str
    half_life: float = 1.0
    difficulty: int = 1
    is_recurrent: bool = False
    created_at: datetime
    priority: float = 0.0
    hashtag: Optional[str] = None

class DailyStat(BaseModel):
    date: str
    total: int
