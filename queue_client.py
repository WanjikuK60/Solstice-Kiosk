import uuid

def publish_print_request(attendee_id):
    job_id = str(uuid.uuid4())
    # Simulate publishing to vendor queue
    print(f"Published job {job_id} for attendee {attendee_id}")
    return job_id
