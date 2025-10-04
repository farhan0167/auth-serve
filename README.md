# auth-serve

Auth Serve is a lightweight starter template for spinning up your own authentication and authorization server with OAuth2.0 baked in.

Let’s be real: nobody starts a new project excited about building an auth system. You just want to ship your SaaS idea or CRUD app, and suddenly you’re knee-deep in tokens, scopes, and role management.

Auth-Serve gives you a ready-made auth server with Role-Based Access Control (RBAC) built in. Drop it into your stack, wire it up to your services, and you’re good to go. Less boilerplate, more building.

## Getting Started

1. Auth-serve uses `uv` package manager, so make sure you have it [installed](https://docs.astral.sh/uv/).
2. After cloning the repo, simply run `make server` and get started!
3. Go to `http://localhost:8000/docs` and start exploring.
4. You can use the example provided to see how you can structure your microservice for auth-serve in [example](https://github.com/farhan0167/auth-serve/tree/main/example).

---


## Concepts  

- **Services**  
  A logical part of your system, usually representing a domain or microservice.  
  Examples: `auth`, `billing`, `projects`.  

- **Resources**  
  The specific objects within a service that users interact with.  
  Examples: `user`, `invoice`, `project`.  

- **Users**  
  The people (or systems) interacting with your system. Users are authenticated, and their permissions determine what they can or cannot do.  

- **Roles**  
  Collections of permissions that can be assigned to users. Roles let you group common access patterns together. For Auth-Serve, system defined roles include: `owner`, `admin`, `user`. 

- **Permissions**  
  Fine-grained access rules that follow a `{service}.{resource}.{action}` pattern attached to each role.  
  Examples:  
  - `auth.user.read` (can read user info)  
  - `billing.invoice.create` (can create invoices)  
  - `projects.project.delete` (can delete a project)  

Together, these concepts let you enforce **Role-Based Access Control (RBAC)** across your entire system in a consistent and predictable way.  

Using these concepts, in **Auth Serve**, the following resources are available:

- **User** – Handles signups, logins, and user invitations (e.g. `user-add`).  
- **Role** – Allows creating and managing roles, including attaching permissions to them.  
- **Permission** – Lets you create and manage the set of permissions available in the system.  

---

#### Signup flow
When a new user signs up, an **organization** is automatically created for them. The first user in that organization becomes a **super user** with the role `owner`.  

The `owner` role comes preloaded with system-level permissions:

- `auth.user.{read,write,delete,all}` – Full control over managing users.  
- `auth.role.{read,write,delete,all}` – Full control over roles, including creating and deleting them.  
- `auth.permission.{read,write,delete,all}` – Full control over system permissions.  

With these, the `owner` can:  
- Add or remove users from their organization.  
- Assign roles to users (either existing roles or new ones they create).  
- Manage which permissions are attached to which roles.  

---

#### Admin role
Users with the `admin` role start with a more limited permission set:  

- `auth.user.{read,write,delete,all}`  
- `auth.role.read`  
- `auth.permission.read`  

This means:  
- Admins can fully manage users (add, update, delete).  
- They can **view** all roles and permissions in the system.  
- But they **cannot create or delete roles/permissions** — those actions are reserved for the `owner`.
- This can only be changed by a user with the `owner` role by assigning them those privilleged permissions.

---

In short:  
- **Owner** = full control over users, roles, and permissions.  
- **Admin** = full control over users, but only read access to roles and permissions, unless altered by Owner.  


## Work in Progress

- [ ] Implement caching for faster reads. You can check it out [here](https://github.com/farhan0167/auth-serve/tree/caching).
- [ ] Implement more fine-grained access controls.