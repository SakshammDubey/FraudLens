from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class TransactionEvent(BaseModel):
    """Standard event contract for FraudLens streaming transactions."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(default_factory=uuid4)

    source_transaction_id: int

    event_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    features: dict[str, Any]

    simulation_label: int | None = Field(
        default=None,
        description="Ground-truth label for offline testing only; never model input.",
    )

    simulation_mode: str = "historical_sample"