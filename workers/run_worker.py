from rq import SimpleWorker

from config.logging_config import setup_logging
from workers.queue import document_queue, redis_connection


def main():
    setup_logging()

    worker = SimpleWorker(
        [document_queue],
        connection=redis_connection,
    )

    worker.work(with_scheduler=True)


if __name__ == "__main__":
    main()