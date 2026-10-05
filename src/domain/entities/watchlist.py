from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class Watchlist(BaseModel):
    id: int
    user_id: int
    name: str = Field(..., min_length=1, max_length=50)
    symbols: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
