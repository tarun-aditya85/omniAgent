"""
FastAPI Dependencies: Authentication, Authorization, Database
"""
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.rbac import Permission, require_permission
from app.core.security import decode_token
from app.core.tenant import TenantContext
from app.db.session import get_db

security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    """
    Extract current user ID from JWT token

    Raises:
        HTTPException: If token is invalid or missing
    """
    try:
        token = credentials.credentials
        payload = decode_token(token)

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token: missing user_id")

        return UUID(user_id)

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Extract full user context from JWT token and set in request state

    Returns:
        dict: User context with user_id, organization_id, role
    """
    try:
        token = credentials.credentials
        payload = decode_token(token)

        user_id = payload.get("sub")
        organization_id = payload.get("organization_id")
        role = payload.get("role")
        email = payload.get("email")

        if not user_id or not organization_id or not role:
            raise AuthenticationError("Invalid token: missing required fields")

        # Set tenant context in request state
        request.state.user_id = UUID(user_id)
        request.state.organization_id = UUID(organization_id)
        request.state.role = role

        # Also set in context vars for middleware
        TenantContext.set_user_id(UUID(user_id))
        TenantContext.set_organization_id(UUID(organization_id))

        return {
            "user_id": UUID(user_id),
            "organization_id": UUID(organization_id),
            "role": role,
            "email": email,
        }

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionChecker:
    """Dependency class for checking user permissions"""

    def __init__(self, required_permission: Permission):
        self.required_permission = required_permission

    async def __call__(self, current_user: dict = Depends(get_current_user)) -> dict:
        """
        Check if current user has the required permission

        Args:
            current_user: User context from get_current_user

        Returns:
            User context if authorized

        Raises:
            HTTPException: If user doesn't have the required permission
        """
        try:
            require_permission(current_user["role"], self.required_permission)
            return current_user

        except AuthorizationError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e.detail),
            )


def require_perm(permission: Permission):
    """
    Convenience function to create a permission checker dependency

    Usage:
        @app.get("/campaigns", dependencies=[Depends(require_perm(Permission.CAMPAIGN_VIEW))])
        async def get_campaigns():
            ...
    """
    return PermissionChecker(permission)


async def get_current_organization_id(
    current_user: dict = Depends(get_current_user),
) -> UUID:
    """Get current organization ID from user context"""
    return current_user["organization_id"]


async def get_user_role(
    current_user: dict = Depends(get_current_user),
) -> str:
    """Get current user's role"""
    return current_user["role"]
