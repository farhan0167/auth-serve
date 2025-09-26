from models.rbac import PermissionActions, SystemRole

system_roles = [
    {"id": 1, "name": SystemRole.owner.value},
    {"id": 2, "name": SystemRole.admin.value},
    {"id": 3, "name": SystemRole.user.value},
]
# Create system permissions
system_permissions = [
    {
        "id": 1,
        "action": PermissionActions.read.value,
        "service": "auth",
        "resource": "user",
        "slug": "auth.user.read",
        "description": "Read user details",
    },
    {
        "id": 2,
        "action": PermissionActions.write.value,
        "service": "auth",
        "resource": "user",
        "slug": "auth.user.write",
        "description": "Update user details",
    },
    {
        "id": 3,
        "action": PermissionActions.delete.value,
        "service": "auth",
        "resource": "user",
        "slug": "auth.user.delete",
        "description": "Delete user",
    },
    {
        "id": 4,
        "action": PermissionActions.all.value,
        "service": "auth",
        "resource": "user",
        "slug": "auth.user.all",
        "description": "All user actions",
    },
]

# Create system role permissions assignments
role_permission = [
    {"role_id": 1, "permission_id": 1},
    {"role_id": 1, "permission_id": 2},
    {"role_id": 1, "permission_id": 3},
    {"role_id": 1, "permission_id": 4},
    {"role_id": 2, "permission_id": 1},
    {"role_id": 2, "permission_id": 2},
    {"role_id": 2, "permission_id": 3},
    {"role_id": 2, "permission_id": 4},
    {"role_id": 3, "permission_id": 1},
]
