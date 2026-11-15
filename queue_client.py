import logging
import uuid

logger = logging.getLogger(__name__)


def publish_print_request(attendee_id: str) -> str:
    """Send a badge print job to the vendor queue and return its job id.

    This is a stand-in for the real vendor queue: it only logs the job.
    """
    job_id = str(uuid.uuid4())
    logger.info("Published print job %s for attendee %s", job_id, attendee_id)
    return job_id
