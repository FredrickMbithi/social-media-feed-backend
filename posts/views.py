from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache


def health_check(request):
    """
    Health check endpoint for monitoring
    Returns 200 if healthy, 503 if any check fails
    """
    health_status = {"status": "healthy", "checks": {}}

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check Redis cache
    try:
        cache.set("health_check", "ok", 10)
        if cache.get("health_check") == "ok":
            health_status["checks"]["redis"] = "ok"
        else:
            health_status["checks"]["redis"] = "error: cache write/read failed"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JsonResponse(health_status, status=status_code)
