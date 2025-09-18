from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from starlette.applications import Starlette
from starlette.routing import Route

requests_total = Counter("app_requests_total", "Total HTTP requests")

async def metrics_endpoint(request):
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

metrics_app = Starlette(routes=[Route("/", endpoint=metrics_endpoint)])
