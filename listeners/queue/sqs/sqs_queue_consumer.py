import boto3, json, logging
from listeners.queue.queue_reader import QueueConsumer


class SQSQueueConsumer(QueueConsumer):
    def __init__(self, queue_url: str, max_messages: int = 50, region: str = "eu-west-2"):
        self.queue_url = queue_url
        self.max_messages = max_messages
        self.sqs = boto3.client("sqs", region_name=region)

    def read(self) -> list[dict]:
        results = []
        while len(results) < self.max_messages:
            batch_size = min(10, self.max_messages - len(results))
            resp = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=batch_size,
                WaitTimeSeconds=5,
            )
            msgs = resp.get("Messages", [])
            if not msgs:
                break
            for msg in msgs:
                item = json.loads(msg["Body"])
                item["_receipt_handle"] = msg["ReceiptHandle"]
                results.append(item)
        logging.info("SQS received %d messages", len(results))
        return results

    def mark_processed(self, items: list[dict]) -> None:
        for item in items:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=item["_receipt_handle"],
            )

    def mark_failed(self, items: list[dict]) -> None:
        for item in items:
            self.sqs.change_message_visibility(
                QueueUrl=self.queue_url,
                ReceiptHandle=item["_receipt_handle"],
                VisibilityTimeout=0,
            )
