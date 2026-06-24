import boto3

from .config import settings
from .events import EventType, NotificationEvent

_ses = boto3.client("ses", region_name=settings.aws_region)

_SUBJECTS = {
    EventType.APPOINTMENT_BOOKED: "Your LabLumen appointment is confirmed",
    EventType.APPOINTMENT_CANCELLED: "Your LabLumen appointment was cancelled",
    EventType.REPORT_READY: "Your LabLumen lab report is ready",
}


def _render_body(event: NotificationEvent) -> str:
    lines = [f"Notification: {event.type}", ""]
    lines += [f"{k}: {v}" for k, v in event.data.items()]
    lines += ["", "— LabLumen"]
    return "\n".join(lines)


def send_for_event(event: NotificationEvent) -> None:
    _ses.send_email(
        Source=settings.ses_sender_email,
        Destination={"ToAddresses": [event.to_email]},
        Message={
            "Subject": {"Data": _SUBJECTS.get(event.type, "LabLumen notification")},
            "Body": {"Text": {"Data": _render_body(event)}},
        },
    )
