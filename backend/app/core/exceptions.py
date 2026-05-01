"""
Custom Exception Classes
"""
from typing import Any, Optional


class OmniGrowthException(Exception):
    """Base exception for OmniGrowth OS"""

    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        **kwargs: Any,
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        super().__init__(detail)


class AuthenticationError(OmniGrowthException):
    """Authentication failed"""

    def __init__(self, detail: str = "Authentication failed", **kwargs: Any):
        super().__init__(detail, status_code=401, error_code="AUTH_FAILED", **kwargs)


class AuthorizationError(OmniGrowthException):
    """Authorization failed"""

    def __init__(self, detail: str = "Permission denied", **kwargs: Any):
        super().__init__(detail, status_code=403, error_code="PERMISSION_DENIED", **kwargs)


class ResourceNotFoundError(OmniGrowthException):
    """Resource not found"""

    def __init__(self, resource: str, identifier: str, **kwargs: Any):
        detail = f"{resource} with identifier '{identifier}' not found"
        super().__init__(detail, status_code=404, error_code="NOT_FOUND", **kwargs)


class ValidationError(OmniGrowthException):
    """Validation error"""

    def __init__(self, detail: str, **kwargs: Any):
        super().__init__(detail, status_code=422, error_code="VALIDATION_ERROR", **kwargs)


class TenantIsolationError(OmniGrowthException):
    """Tenant isolation violation"""

    def __init__(self, detail: str = "Tenant isolation violation", **kwargs: Any):
        super().__init__(
            detail, status_code=403, error_code="TENANT_ISOLATION_VIOLATION", **kwargs
        )


class IntegrationError(OmniGrowthException):
    """External integration error"""

    def __init__(self, platform: str, detail: str, **kwargs: Any):
        full_detail = f"{platform} integration error: {detail}"
        super().__init__(full_detail, status_code=502, error_code="INTEGRATION_ERROR", **kwargs)


class RateLimitError(OmniGrowthException):
    """Rate limit exceeded"""

    def __init__(self, detail: str = "Rate limit exceeded", **kwargs: Any):
        super().__init__(detail, status_code=429, error_code="RATE_LIMIT_EXCEEDED", **kwargs)
