"""
API v1 Router - Aggregates all endpoint routers
"""
from fastapi import APIRouter

# Import routers as they are created
# from app.api.v1 import auth, campaigns, clients, integrations, metrics
# from app.api.v1 import recommendations, optimizer, seo, aeo, influencers
# from app.api.v1 import competitors, reports, copilot

api_router = APIRouter()

# Include routers (uncomment as you create them)
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
# api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
# api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
# api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
# api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
# api_router.include_router(optimizer.router, prefix="/optimizer", tags=["optimizer"])
# api_router.include_router(seo.router, prefix="/seo", tags=["seo"])
# api_router.include_router(aeo.router, prefix="/aeo", tags=["aeo"])
# api_router.include_router(influencers.router, prefix="/influencers", tags=["influencers"])
# api_router.include_router(competitors.router, prefix="/competitors", tags=["competitors"])
# api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
# api_router.include_router(copilot.router, prefix="/copilot", tags=["copilot"])


@api_router.get("/health")
async def api_health():
    """API v1 health check"""
    return {"status": "healthy", "version": "v1"}
