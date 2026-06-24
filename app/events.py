"""Event contract consumed off SQS.

Producers (currently appointment-service and the AI Lambda) publish JSON matching
`NotificationEvent`. This contract is the gap-fill: the blueprint defined the consumer but not
the messages it consumes.
"""

from enum import StrEnum

from pydantic import BaseModel


class EventType(StrEnum):
    APPOINTMENT_BOOKED = "appointment.booked"
    APPOINTMENT_CANCELLED = "appointment.cancelled"
    REPORT_READY = "report.ready"


class NotificationEvent(BaseModel):
    type: EventType
    to_email: str
    # Free-form, type-specific context for templating (e.g. appointment_date, test_name).
    data: dict = {}
