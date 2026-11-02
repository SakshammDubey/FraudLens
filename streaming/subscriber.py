
from google.cloud import pubsub_v1


PROJECT_ID = "fraudlens-local"
SUBSCRIPTION_ID = "fraudlens-transactions-sub"


class TransactionSubscriber:
    """Consumes transaction events from Google Cloud Pub/Sub."""

    def __init__(self):
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            PROJECT_ID,
            SUBSCRIPTION_ID,
        )

    def pull_messages(self, max_messages: int = 5):
        """Pull messages without acknowledging them."""

        response = self.subscriber.pull(
            request={
                "subscription": self.subscription_path,
                "max_messages": max_messages,
            },
            timeout=30,
        )

        return response.received_messages

    def acknowledge_messages(self, received_messages):
        """Acknowledge successfully processed messages."""

        if not received_messages:
            return

        ack_ids = [
            message.ack_id
            for message in received_messages
        ]

        self.subscriber.acknowledge(
            request={
                "subscription": self.subscription_path,
                "ack_ids": ack_ids,
            }
        )

    def close(self):
        self.subscriber.close()
