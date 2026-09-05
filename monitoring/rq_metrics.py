from rq.registry import (
    FailedJobRegistry,
    FinishedJobRegistry,
    StartedJobRegistry,
)

from monitoring.metrics import (
    RQ_FAILED_JOBS,
    RQ_FINISHED_JOBS,
    RQ_QUEUED_JOBS,
    RQ_STARTED_JOBS,
)
from workers.queue import document_queue


def update_rq_metrics() -> None:
    connection = document_queue.connection
    queue_name = document_queue.name

    started_registry = StartedJobRegistry(
        name=queue_name,
        connection=connection,
    )

    failed_registry = FailedJobRegistry(
        name=queue_name,
        connection=connection,
    )

    finished_registry = FinishedJobRegistry(
        name=queue_name,
        connection=connection,
    )

    RQ_QUEUED_JOBS.set(len(document_queue))
    RQ_STARTED_JOBS.set(started_registry.count)
    RQ_FAILED_JOBS.set(failed_registry.count)
    RQ_FINISHED_JOBS.set(finished_registry.count)