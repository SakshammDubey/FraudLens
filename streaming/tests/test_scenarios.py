import unittest

from streaming.scenarios import generate_scenario_event
from streaming.simulator import FEATURES, TransactionSimulator


class TestTransactionScenarios(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simulator = TransactionSimulator(seed=42)

    def test_historical_sample_preserves_original_data(self):
        event = generate_scenario_event(
            self.simulator,
            "historical_sample",
        )

        self.assertEqual(event.simulation_mode, "historical_sample")
        self.assertIn(event.simulation_label, [0, 1])
        self.assertEqual(set(event.features.keys()), set(FEATURES))

    def test_high_amount_scenario_is_modified(self):
        event = generate_scenario_event(
            self.simulator,
            "high_amount",
        )

        historical_99th_percentile = float(
            self.simulator.source_data["TransactionAmt"].quantile(0.99)
        )

        self.assertEqual(event.simulation_mode, "high_amount")
        self.assertGreater(
            event.features["TransactionAmt"],
            historical_99th_percentile,
        )
        self.assertIsNone(event.simulation_label)

    def test_unseen_email_domain_scenario(self):
        event = generate_scenario_event(
            self.simulator,
            "unseen_email_domain",
        )

        self.assertEqual(
            event.features["P_emaildomain"],
            "synthetic-unseen-domain.invalid",
        )
        self.assertEqual(
            event.simulation_mode,
            "unseen_email_domain",
        )
        self.assertIsNone(event.simulation_label)

    def test_each_event_has_a_unique_id(self):
        first = generate_scenario_event(
            self.simulator,
            "historical_sample",
        )
        second = generate_scenario_event(
            self.simulator,
            "historical_sample",
        )

        self.assertNotEqual(first.event_id, second.event_id)

    def test_invalid_scenario_is_rejected(self):
        with self.assertRaises(ValueError):
            generate_scenario_event(
                self.simulator,
                "unknown_scenario",
            )


if __name__ == "__main__":
    unittest.main()