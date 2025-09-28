from models.rbac import PermissionActions, SystemRole

system_roles = [
    {"name": SystemRole.owner.value},
    {"name": SystemRole.admin.value},
    {"name": SystemRole.user.value},
]
# Create system permissions
system_permissions = [
    {
        "action": PermissionActions.read.value,
        "service": "auth",
        "resource": "user",
        "slug": "auth.user.read",
        "description": "Read user details",
    },
    {
        "action": PermissionActions.write.value,
        "service": "auth",
        "resource": "user",
        "slug": "auth.user.write",
        "description": "Update user details",
    },
    {
        "action": PermissionActions.delete.value,
        "service": "auth",
        "resource": "user",
        "slug": "auth.user.delete",
        "description": "Delete user",
    },
    {
        "action": PermissionActions.all.value,
        "service": "auth",
        "resource": "user",
        "slug": "auth.user.all",
        "description": "All user actions",
    },
    {
        "action": PermissionActions.read.value,
        "service": "auth",
        "resource": "role",
        "slug": "auth.role.read",
        "description": "Read roles",
    },
    {
        "action": PermissionActions.write.value,
        "service": "auth",
        "resource": "role",
        "slug": "auth.role.write",
        "description": "Update role",
    },
    {
        "action": PermissionActions.delete.value,
        "service": "auth",
        "resource": "role",
        "slug": "auth.role.delete",
        "description": "Delete role",
    },
    {
        "action": PermissionActions.all.value,
        "service": "auth",
        "resource": "role",
        "slug": "auth.role.all",
        "description": "All role actions",
    },
    {
        "action": PermissionActions.read.value,
        "service": "auth",
        "resource": "permission",
        "slug": "auth.permission.read",
        "description": "Read permissions",
    },
    {
        "action": PermissionActions.write.value,
        "service": "auth",
        "resource": "permission",
        "slug": "auth.permission.write",
        "description": "Update permission",
    },
    {
        "action": PermissionActions.delete.value,
        "service": "auth",
        "resource": "permission",
        "slug": "auth.permission.delete",
        "description": "Delete permission",
    },
    {
        "action": PermissionActions.all.value,
        "service": "auth",
        "resource": "permission",
        "slug": "auth.permission.all",
        "description": "All permission actions",
    }
]

# Create system role permissions assignments
role_permission = [
    {"role_id": 1, "permission_id": 1},
    {"role_id": 1, "permission_id": 2},
    {"role_id": 1, "permission_id": 3},
    {"role_id": 1, "permission_id": 4},
    {"role_id": 1, "permission_id": 5},
    {"role_id": 1, "permission_id": 6},
    {"role_id": 1, "permission_id": 7},
    {"role_id": 1, "permission_id": 8},
    {"role_id": 1, "permission_id": 9},
    {"role_id": 1, "permission_id": 10},
    {"role_id": 1, "permission_id": 11},
    {"role_id": 1, "permission_id": 12},
    {"role_id": 2, "permission_id": 1},
    {"role_id": 2, "permission_id": 2},
    {"role_id": 2, "permission_id": 3},
    {"role_id": 2, "permission_id": 4},
    {"role_id": 2, "permission_id": 5},
    {"role_id": 2, "permission_id": 9},
    {"role_id": 3, "permission_id": 1},
]
