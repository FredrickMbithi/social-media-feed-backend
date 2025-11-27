import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        start = getattr(request, "_start_time", None)
        if start:
            duration = time.time() - start
            if duration > 1.0:
                logger.warning("Slow request: %s %s took %.2fs", request.method, request.path, duration)
            response["X-Response-Time"] = f"{duration:.3f}s"
        return response
