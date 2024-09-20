import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
from limits import storage, RateLimitItemPerMinute
from limits.strategies import FixedWindowRateLimiter
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from .config import config
from .stats import Stats
from .utils import setup_logging

logger = setup_logging(config.log_level)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limiter, rate_limit, error_message):
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.rate_limit = rate_limit
        self.error_message = error_message

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        client_ip = request.client.host
        if not self.rate_limiter.hit(self.rate_limit, client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "message": self.error_message,
                        "type": "rate_limit_error",
                        "param": None,
                        "code": "rate_limit_exceeded",
                    }
                }
            )
        response = await call_next(request)
        return response

@asynccontextmanager
async def print_stats_periodically(app: "MiniServer"):
    # Startup: Start the background task to print stats periodically
    stats_task = asyncio.create_task(app.stats.print_stats_periodically())
    yield
    # Shutdown: Cancel the background task
    stats_task.cancel()
    try:
        await stats_task
    except asyncio.CancelledError:
        pass

class MiniServer(FastAPI):
    """
    A minimal FastAPI server with rate limiting and logging.
    """
    def __init__(
        self,
        *args,
        **kwargs
    ):
        # Extract custom arguments from kwargs with defaults
        rate_limit_requests_per_minute = kwargs.pop('rate_limit_requests_per_minute', config.rate_limit_requests_per_minute)
        rate_limit_error_message = kwargs.pop('rate_limit_error_message', config.rate_limit_error_message)
        max_concurrent_requests = kwargs.pop('max_concurrent_requests', config.max_concurrent_requests)
        stats_window_size = kwargs.pop('stats_window_size', config.stats_window_size)
        stats_print_interval = kwargs.pop('stats_print_interval', config.stats_print_interval)
        
        # Initialize the parent class with the remaining args and kwargs
        super().__init__(*args, **kwargs, lifespan=print_stats_periodically)
        
        self.stats = Stats(stats_window_size, stats_print_interval)
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

        # Set up rate limiter
        mem_storage = storage.MemoryStorage()
        rate_limiter = FixedWindowRateLimiter(mem_storage)
        rate_limit = RateLimitItemPerMinute(rate_limit_requests_per_minute)

        logger.info(f"Rate limit: {rate_limit_requests_per_minute} requests per minute")
        logger.info(f"Max concurrent requests: {max_concurrent_requests}")
        logger.info(f"Stats print interval: {stats_print_interval} seconds")

        # Add rate limiting middleware
        self.add_middleware(
            RateLimitMiddleware,
            rate_limiter=rate_limiter,
            rate_limit=rate_limit,
            error_message=rate_limit_error_message + f" (Current rate limit: {rate_limit_requests_per_minute} requests per minute)"
        )

        # Add a middleware to record requests for stats
        @self.middleware("http")
        async def record_request_stats(request: Request, call_next):
            self.stats.record_request(request.client.host)
            response = await call_next(request)
            return response
