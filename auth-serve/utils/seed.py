import uuid

from models.rbac import PermissionActions, SystemRole


def get_system_roles(org_id: uuid.UUID):
    system_roles = [
        {"name": SystemRole.owner.value, "org_id": org_id},
        {"name": SystemRole.admin.value, "org_id": org_id},
        {"name": SystemRole.user.value, "org_id": org_id},
    ]

    return system_roles


def get_system_permissions(org_id: uuid.UUID = None):
    # Create system permissions
    system_permissions = [
        {
            "action": PermissionActions.read.value,
            "service": "auth",
            "resource": "user",
            "slug": "auth.user.read",
            "description": "Read user details",
            "org_id": org_id,
        },
        {
            "action": PermissionActions.write.value,
            "service": "auth",
            "resource": "user",
            "slug": "auth.user.write",
            "description": "Update user details",
            "org_id": org_id,
        },
        {
            "action": PermissionActions.delete.value,
            "service": "auth",
            "resource": "user",
            "slug": "auth.user.delete",
            "description": "Delete user",
            "org_id": org_id,
        },
        {
            "action": PermissionActions.all.value,
            "service": "auth",
            "resource": "user",
            "slug": "auth.user.all",
            "description": "All user actions",
            "org_id": org_id,
        },
        {
            "action": PermissionActions.read.value,
            "service": "auth",
            "resource": "role",
            "slug": "auth.role.read",
            "description": "Read roles",
            "org_id": org_id,
        },
        {
            "action": PermissionActions.write.value,
            "service": "auth",
            "resource": "role",
            "slug": "auth.role.write",
            "description": "Update role",
            "org_id": org_id,
        },
        {
            "action": PermissionActions.delete.value,
            "service": "auth",
            "resource": "role",
            "slug": "auth.role.delete",
            "description": "Delete role",
            "org_id": org_id,
        },
        {
            "action": PermissionActions.all.value,
            "service": "auth",
            "resource": "role",
            "slug": "auth.role.all",
            "description": "All role actions",
            "org_id": org_id,
        },
        {
            "action": PermissionActions.read.value,
            "service": "auth",
            "resource": "permission",
            "slug": "auth.permission.read",
            "description": "Read permissions",
            "org_id": org_id,
        },
        {
            "action": PermissionActions.write.value,
            "service": "auth",
            "resource": "permission",
            "slug": "auth.permission.write",
            "description": "Update permission",
            "org_id": org_id,
        },
        {
            "action": PermissionActions.delete.value,
            "service": "auth",
            "resource": "permission",
            "slug": "auth.permission.delete",
            "description": "Delete permission",
            "org_id": org_id,
        },
        {
            "action": PermissionActions.all.value,
            "service": "auth",
            "resource": "permission",
            "slug": "auth.permission.all",
            "description": "All permission actions",
            "org_id": org_id,
        },
    ]

    return system_permissions


ROLE_PERMISSION_MAP = {
    SystemRole.owner.value: [
        "auth.user.read",
        "auth.user.write",
        "auth.user.delete",
        "auth.user.all",
        "auth.role.read",
        "auth.role.write",
        "auth.role.delete",
        "auth.role.all",
        "auth.permission.read",
        "auth.permission.write",
        "auth.permission.delete",
        "auth.permission.all",
    ],
    SystemRole.admin.value: [
        "auth.user.read",
        "auth.user.write",
        "auth.user.delete",
        "auth.user.all",
        "auth.role.read",
        "auth.permission.read",
    ],
    SystemRole.user.value: [
        "auth.user.read",
    ],
}
