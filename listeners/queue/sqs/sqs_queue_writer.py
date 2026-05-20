import boto3, json, logging
from listeners.queue.queue_writer import QueueWriter


class SQSQueueWriter(QueueWriter):
    def __init__(self, queue_url: str, region: str = "eu-west-2"):
        self.queue_url = queue_url
        self.sqs = boto3.client("sqs", region_name=region)

    def write(self, rows: list[dict]) -> None:
        if not rows:
            return
        for i in range(0, len(rows), 10):
            batch = rows[i:i + 10]
            entries = [
                {"Id": str(j), "MessageBody": json.dumps(row, default=str)}
                for j, row in enumerate(batch)
            ]
            self.sqs.send_message_batch(QueueUrl=self.queue_url, Entries=entries)
        logging.info("SQS published %d messages", len(rows))
