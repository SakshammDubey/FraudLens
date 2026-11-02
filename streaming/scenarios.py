from __future__ import annotations
from typing import Literal

from streaming.schemas import TransactionEvent
from typing import TYPE_CHECKING, Literal

from streaming.schemas import TransactionEvent

if TYPE_CHECKING:
    from streaming.simulator import TransactionSimulator


ScenarioName = Literal[
    "historical_sample",
    "high_amount",
    "unseen_email_domain",
]


def generate_scenario_event(
    simulator: TransactionSimulator,
    scenario: ScenarioName,
) -> TransactionEvent:
    """
    Generate a transaction under a controlled test scenario.

    Modified events intentionally have no ground-truth fraud label.
    """

    event = simulator.generate_event()
    features = event.features.copy()

    if scenario == "historical_sample":
        return event.model_copy(
            update={"simulation_mode": "historical_sample"}
        )

    if scenario == "high_amount":
        historical_99th_percentile = float(
            simulator.source_data["TransactionAmt"].quantile(0.99)
        )

        features["TransactionAmt"] = max(
            float(features["TransactionAmt"] or 0) * 5,
            historical_99th_percentile * 1.5,
        )

    elif scenario == "unseen_email_domain":
        features["P_emaildomain"] = "synthetic-unseen-domain.invalid"

    else:
        raise ValueError(f"Unsupported scenario: {scenario}")

    return event.model_copy(
        update={
            "features": features,
            "simulation_label": None,
            "simulation_mode": scenario,
        }
    )