
from google.cloud import pubsub_v1

from streaming.schemas import TransactionEvent


PROJECT_ID = "fraudlens-local"
TOPIC_ID = "fraudlens-transactions"


class TransactionPublisher:
    """Publishes FraudLens transaction events to Google Cloud Pub/Sub."""

    def __init__(self):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(
            PROJECT_ID,
            TOPIC_ID,
        )

    def publish_event(self, event: TransactionEvent) -> str:
        """Publish one transaction event and return its message ID."""

        message_data = event.model_dump_json().encode("utf-8")

        future = self.publisher.publish(
            self.topic_path,
            message_data,
            event_id=str(event.event_id),
            simulation_mode=event.simulation_mode,
            source_transaction_id=str(event.source_transaction_id),
        )

        message_id = future.result(timeout=30)

        return message_id

    def close(self):
        """Release publisher resources."""
        self.publisher.transport.close()
