"""
Multi-tenant context and middleware
"""
import logging
from contextvars import ContextVar
from typing import Optional
from uuid import UUID

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import TenantIsolationError

logger = logging.getLogger(__name__)

# Context variables for tenant isolation
_tenant_context: ContextVar[Optional[UUID]] = ContextVar("tenant_context", default=None)
_user_context: ContextVar[Optional[UUID]] = ContextVar("user_context", default=None)


class TenantContext:
    """Tenant context manager"""

    @staticmethod
    def get_organization_id() -> Optional[UUID]:
        """Get current organization ID from context"""
        return _tenant_context.get()

    @staticmethod
    def set_organization_id(organization_id: UUID) -> None:
        """Set organization ID in context"""
        _tenant_context.set(organization_id)

    @staticmethod
    def get_user_id() -> Optional[UUID]:
        """Get current user ID from context"""
        return _user_context.get()

    @staticmethod
    def set_user_id(user_id: UUID) -> None:
        """Set user ID in context"""
        _user_context.set(user_id)

    @staticmethod
    def clear() -> None:
        """Clear tenant context"""
        _tenant_context.set(None)
        _user_context.set(None)

    @staticmethod
    def validate_access(resource_organization_id: UUID) -> None:
        """Validate that current user has access to resource"""
        current_org_id = TenantContext.get_organization_id()

        if current_org_id is None:
            raise TenantIsolationError("No tenant context set")

        if current_org_id != resource_organization_id:
            logger.warning(
                f"Tenant isolation violation: User from org {current_org_id} "
                f"attempted to access resource from org {resource_organization_id}"
            )
            raise TenantIsolationError("Access denied: tenant mismatch")


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and set tenant context from JWT"""

    async def dispatch(self, request: Request, call_next):
        # Clear context at start of request
        TenantContext.clear()

        # Skip tenant context for public endpoints
        public_paths = ["/health", "/docs", "/redoc", "/openapi.json", "/api/v1/auth/login", "/api/v1/auth/register"]

        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        # Extract tenant context from request state (set by auth dependency)
        if hasattr(request.state, "organization_id"):
            TenantContext.set_organization_id(request.state.organization_id)

        if hasattr(request.state, "user_id"):
            TenantContext.set_user_id(request.state.user_id)

        response = await call_next(request)
        return response
