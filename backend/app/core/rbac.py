"""
Role-Based Access Control (RBAC)
"""
from enum import Enum
from typing import List

from app.core.exceptions import AuthorizationError


class Role(str, Enum):
    """User roles with hierarchical permissions"""

    SUPER_ADMIN = "super_admin"
    AGENCY_ADMIN = "agency_admin"
    TRADER = "trader"
    ANALYST = "analyst"
    VIEWER = "viewer"


class Permission(str, Enum):
    """Granular permissions"""

    # Campaign permissions
    CAMPAIGN_VIEW = "campaign:view"
    CAMPAIGN_CREATE = "campaign:create"
    CAMPAIGN_EDIT = "campaign:edit"
    CAMPAIGN_DELETE = "campaign:delete"
    CAMPAIGN_EXECUTE = "campaign:execute"  # Apply recommendations

    # Client permissions
    CLIENT_VIEW = "client:view"
    CLIENT_CREATE = "client:create"
    CLIENT_EDIT = "client:edit"
    CLIENT_DELETE = "client:delete"

    # Integration permissions
    INTEGRATION_VIEW = "integration:view"
    INTEGRATION_CONNECT = "integration:connect"
    INTEGRATION_DISCONNECT = "integration:disconnect"

    # Recommendation permissions
    RECOMMENDATION_VIEW = "recommendation:view"
    RECOMMENDATION_APPLY = "recommendation:apply"
    RECOMMENDATION_DISMISS = "recommendation:dismiss"

    # Report permissions
    REPORT_VIEW = "report:view"
    REPORT_EXPORT = "report:export"

    # User management
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_EDIT = "user:edit"
    USER_DELETE = "user:delete"

    # Organization settings
    ORG_VIEW = "org:view"
    ORG_EDIT = "org:edit"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[Role, List[Permission]] = {
    Role.SUPER_ADMIN: [p for p in Permission],  # All permissions
    Role.AGENCY_ADMIN: [
        Permission.CAMPAIGN_VIEW,
        Permission.CAMPAIGN_CREATE,
        Permission.CAMPAIGN_EDIT,
        Permission.CAMPAIGN_DELETE,
        Permission.CAMPAIGN_EXECUTE,
        Permission.CLIENT_VIEW,
        Permission.CLIENT_CREATE,
        Permission.CLIENT_EDIT,
        Permission.CLIENT_DELETE,
        Permission.INTEGRATION_VIEW,
        Permission.INTEGRATION_CONNECT,
        Permission.INTEGRATION_DISCONNECT,
        Permission.RECOMMENDATION_VIEW,
        Permission.RECOMMENDATION_APPLY,
        Permission.RECOMMENDATION_DISMISS,
        Permission.REPORT_VIEW,
        Permission.REPORT_EXPORT,
        Permission.USER_VIEW,
        Permission.USER_CREATE,
        Permission.USER_EDIT,
        Permission.ORG_VIEW,
        Permission.ORG_EDIT,
    ],
    Role.TRADER: [
        Permission.CAMPAIGN_VIEW,
        Permission.CAMPAIGN_CREATE,
        Permission.CAMPAIGN_EDIT,
        Permission.CAMPAIGN_EXECUTE,
        Permission.CLIENT_VIEW,
        Permission.INTEGRATION_VIEW,
        Permission.RECOMMENDATION_VIEW,
        Permission.RECOMMENDATION_APPLY,
        Permission.RECOMMENDATION_DISMISS,
        Permission.REPORT_VIEW,
        Permission.REPORT_EXPORT,
    ],
    Role.ANALYST: [
        Permission.CAMPAIGN_VIEW,
        Permission.CLIENT_VIEW,
        Permission.INTEGRATION_VIEW,
        Permission.RECOMMENDATION_VIEW,
        Permission.REPORT_VIEW,
        Permission.REPORT_EXPORT,
    ],
    Role.VIEWER: [
        Permission.CAMPAIGN_VIEW,
        Permission.CLIENT_VIEW,
        Permission.RECOMMENDATION_VIEW,
        Permission.REPORT_VIEW,
    ],
}


def has_permission(role: Role, permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    return permission in ROLE_PERMISSIONS.get(role, [])


def require_permission(user_role: str, required_permission: Permission) -> None:
    """
    Require a specific permission, raise AuthorizationError if not present

    Args:
        user_role: User's role string
        required_permission: Required permission

    Raises:
        AuthorizationError: If user doesn't have the required permission
    """
    try:
        role = Role(user_role)
    except ValueError:
        raise AuthorizationError(f"Invalid role: {user_role}")

    if not has_permission(role, required_permission):
        raise AuthorizationError(
            f"Permission denied: {required_permission.value} required (your role: {user_role})"
        )


def require_any_permission(user_role: str, required_permissions: List[Permission]) -> None:
    """
    Require at least one of the specified permissions

    Args:
        user_role: User's role string
        required_permissions: List of acceptable permissions

    Raises:
        AuthorizationError: If user doesn't have any of the required permissions
    """
    try:
        role = Role(user_role)
    except ValueError:
        raise AuthorizationError(f"Invalid role: {user_role}")

    if not any(has_permission(role, perm) for perm in required_permissions):
        perm_names = ", ".join([p.value for p in required_permissions])
        raise AuthorizationError(
            f"Permission denied: One of ({perm_names}) required (your role: {user_role})"
        )
