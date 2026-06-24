"""Background SQS long-poll loop.

Resilient by design: any AWS/parse error is logged and the loop backs off, so the service stays
healthy locally (placeholder queue) and in the cluster.
"""

import asyncio
import functools
import logging

import boto3

from .config import settings
from .emailer import send_for_event
from .events import NotificationEvent

logger = logging.getLogger("notification.consumer")

_sqs = boto3.client("sqs", region_name=settings.aws_region)


async def consume_forever(stop: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()
    while not stop.is_set():
        try:
            resp = await loop.run_in_executor(
                None,
                functools.partial(
                    _sqs.receive_message,
                    QueueUrl=settings.notifications_queue_url,
                    MaxNumberOfMessages=settings.max_messages,
                    WaitTimeSeconds=settings.poll_wait_seconds,
                ),
            )
        except Exception:
            logger.exception("SQS poll failed; backing off")
            await asyncio.sleep(settings.error_backoff_seconds)
            continue

        for msg in resp.get("Messages", []):
            receipt = msg["ReceiptHandle"]
            try:
                event = NotificationEvent.model_validate_json(msg["Body"])
                await loop.run_in_executor(None, send_for_event, event)
            except Exception:
                logger.exception("Failed to process message %s", msg.get("MessageId"))
                continue  # leave on queue -> redrive/DLQ handles retries
            await loop.run_in_executor(
                None,
                functools.partial(
                    _sqs.delete_message,
                    QueueUrl=settings.notifications_queue_url,
                    ReceiptHandle=receipt,
                ),
            )
