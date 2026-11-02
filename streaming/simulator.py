
import argparse
import json
import random
import time
from pathlib import Path
from typing import Iterator

import pandas as pd

from streaming.schemas import TransactionEvent
from streaming.scenarios import generate_scenario_event, ScenarioName


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "train_transaction.csv"

NUMERIC_FEATURES = [
    "TransactionAmt",
    "card1",
    "card2",
    "card3",
    "card5",
    "addr1",
    "dist1",
    "C1",
    "C2",
    "C3",
    "C5",
    "C6",
    "C9",
    "D1",
    "D2",
    "D3",
    "D4",
    "D10",
    "D15",
]

CATEGORICAL_FEATURES = [
    "ProductCD",
    "card4",
    "card6",
    "P_emaildomain",
]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

REQUIRED_COLUMNS = [
    "TransactionID",
    "TransactionDT",
    "isFraud",
    *FEATURES,
]

SCENARIOS = [
    "historical_sample",
    "high_amount",
    "unseen_email_domain",
]


def load_source_data() -> pd.DataFrame:
    """Load the held-out chronological portion of the IEEE-CIS dataset."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    data = pd.read_csv(
        DATA_PATH,
        usecols=REQUIRED_COLUMNS,
        low_memory=False,
    )

    data = data.dropna(
        subset=["isFraud", "TransactionDT"]
    )

    data = data.sort_values(
        "TransactionDT"
    ).reset_index(drop=True)

    split_index = int(len(data) * 0.80)
    validation_data = data.iloc[split_index:].copy()

    if validation_data.empty:
        raise ValueError("The validation portion of the dataset is empty.")

    return validation_data


def clean_value(value):
    """Convert Pandas/NumPy values into JSON-compatible Python values."""

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


class TransactionSimulator:

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)
        self.source_data = load_source_data()

    def generate_event(self) -> TransactionEvent:
        """Sample one held-out transaction and create a streaming event."""

        index = self.random.randrange(len(self.source_data))
        row = self.source_data.iloc[index]

        features = {
            feature: clean_value(row[feature])
            for feature in FEATURES
        }

        return TransactionEvent(
            source_transaction_id=int(row["TransactionID"]),
            features=features,
            simulation_label=int(row["isFraud"]),
            simulation_mode="historical_sample",
        )

    def generate_scenario(self, scenario: ScenarioName) -> TransactionEvent:
        """Generate an event using a selected controlled scenario."""

        return generate_scenario_event(self, scenario)

    def stream(
        self,
        count: int | None = None,
        scenario: str = "historical_sample",
    ) -> Iterator[TransactionEvent]:
        """Yield events continuously or stop after a specified count."""

        generated = 0

        while count is None or generated < count:

            if scenario == "mixed":
                selected_scenario = self.random.choice(SCENARIOS)
            else:
                selected_scenario = scenario

            yield self.generate_scenario(selected_scenario)

            generated += 1


def run_simulator(
    rate: float,
    count: int | None,
    seed: int,
    scenario: str,
    destination: str = "console",
) -> None:
    """Generate transaction events and send them to the selected destination."""

    if rate <= 0:
        raise ValueError("Rate must be greater than zero.")

    simulator = TransactionSimulator(seed=seed)
    interval = 1.0 / rate

    publisher = None

    if destination == "pubsub":
        from streaming.publisher import TransactionPublisher

        publisher = TransactionPublisher()

    print("FraudLens transaction simulator started.")
    print(f"Source: {DATA_PATH}")
    print(f"Validation samples: {len(simulator.source_data):,}")
    print(f"Scenario: {scenario}")
    print(f"Destination: {destination}")
    print(f"Generation rate: {rate} events/second")
    print("Press Ctrl+C to stop.\n")

    generated = 0

    try:
        for event in simulator.stream(
            count=count,
            scenario=scenario,
        ):

            if destination == "console":
                print(
                    json.dumps(
                        event.model_dump(mode="json"),
                        separators=(",", ":"),
                    ),
                    flush=True,
                )

            elif destination == "pubsub":
                message_id = publisher.publish_event(event)

                print(
                    f"Published event {generated + 1}: "
                    f"message_id={message_id}, "
                    f"transaction_id={event.source_transaction_id}, "
                    f"scenario={event.simulation_mode}",
                    flush=True,
                )

            generated += 1
            time.sleep(interval)

        print(f"\nSimulation completed. Events generated: {generated}")

    except KeyboardInterrupt:
        print(f"\nSimulator stopped. Events generated: {generated}")

    finally:
        if publisher is not None:
            publisher.close()


def main():

    parser = argparse.ArgumentParser(
        description="FraudLens transaction event simulator"
    )

    parser.add_argument(
        "--rate",
        type=float,
        default=1.0,
        help="Events generated per second (default: 1)",
    )

    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of events; use 0 for continuous generation",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible sampling",
    )

    parser.add_argument(
        "--scenario",
        type=str,
        choices=[
            "historical_sample",
            "high_amount",
            "unseen_email_domain",
            "mixed",
        ],
        default="historical_sample",
        help="Transaction scenario to generate",
    )

    parser.add_argument(
        "--destination",
        type=str,
        choices=["console", "pubsub"],
        default="console",
        help="Where generated events should be sent",
    )

    args = parser.parse_args()

    if args.count < 0:
        parser.error("--count cannot be negative")

    if args.rate <= 0:
        parser.error("--rate must be greater than zero")

    run_simulator(
        rate=args.rate,
        count=None if args.count == 0 else args.count,
        seed=args.seed,
        scenario=args.scenario,
        destination=args.destination,
    )


if __name__ == "__main__":
    main()
