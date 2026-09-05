from prometheus_client import Counter, Gauge, Histogram


HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)


HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)


RAG_QUERIES_TOTAL = Counter(
    "rag_queries_total",
    "Total number of RAG queries",
)


DOCUMENT_UPLOADS_TOTAL = Counter(
    "document_uploads_total",
    "Total number of document uploads",
)


RQ_QUEUED_JOBS = Gauge(
    "rq_queued_jobs",
    "Number of jobs currently waiting in the document queue",
)


RQ_STARTED_JOBS = Gauge(
    "rq_started_jobs",
    "Number of document jobs currently being processed",
)


RQ_FAILED_JOBS = Gauge(
    "rq_failed_jobs",
    "Number of failed document processing jobs",
)


RQ_FINISHED_JOBS = Gauge(
    "rq_finished_jobs",
    "Number of successfully finished document processing jobs",
)