from redis import Redis
from rq import Queue

from config.settings import settings


redis_connection = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=False,
)

document_queue = Queue(
    name="document-processing",
    connection=redis_connection,
    default_timeout=1800,
)