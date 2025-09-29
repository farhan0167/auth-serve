from .jwks import jkws_router
from .permission import permission_router
from .project import project_router
from .role import role_router
from .user import user_router

__all__ = [
    "user_router",
    "project_router",
    "role_router",
    "permission_router",
    "jkws_router",
]
