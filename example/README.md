# Demo

In this example, we'll see how we can use the Auth Server to access resources in a new microservice we create, which in this case will be the `example_service` which has a billing resource. This repo particularly hosts a demo FastAPI application mirroring the example service.

>> ⚠️ Notes
All commands assume your auth server is running locally at http://localhost:8000.
Replace placeholders like <paste access token here> and <role_id> with real values from your environment.
The code snippets are intentionally unchanged—this document only fills in descriptions and usage steps.

The example server launches a example service hosting a billing resource with the following operations: `read`, `write` and `delete`. Each resource is defined with a specific permission. If you navigate to `billing/router.py`, you'll see the following:

```python
from typing import Annotated

from fastapi import APIRouter, Security

from billing.dependency import has_access

billing_router = APIRouter(
    prefix="/billing",
    tags=["billing"],
)

# {service}.{resource}.{action}
READ = "example_service.billing.read"
WRITE = "example_service.billing.write"
DELETE = "example_service.billing.delete"


@billing_router.get("/")
async def read_billing(
    _:bool = Security(has_access, scopes=[READ])
):
    return {"message": "Read billing"}


@billing_router.post("/")
async def write_billing(
    _:bool = Security(has_access, scopes=[WRITE])
):
    return {"message": "Write billing"}


@billing_router.delete("/")
async def delete_billing(
    _:bool = Security(has_access, scopes=[DELETE])
):
    return {"message": "Delete billing"}

```

**How it works**

- FastAPI’s `Security` function is used to declare that the endpoint requires a particular authentication dependency.
In this case, it calls `has_access`, which handles token verification and scope validation.
- When a client makes a request, their access token is validated against the required scopes. If the token contains the required scope, the request proceeds. If not, FastAPI raises an automatic `403 Forbidden` error.

### Dependency to validate access tokens

```python
import httpx
import json
from typing import Annotated

import jwt
from jwt.algorithms import RSAAlgorithm
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

# Define scopes for your service
SCOPES = {
    "example_service.billing.read": "Read billing",
    "example_service.billing.write": "Write billing",
    "example_service.billing.delete": "Delete billing",
}
# Define the URL for the token endpoint
AUTH_URL = "http://localhost:8000/user/login"
JWKS_URL = "http://localhost:8000/.well-known/jwks.json"
USER_ME_URL = "http://localhost:8000/user/me"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=AUTH_URL,
    scopes=SCOPES
)

async def validate_access_token(token:str):
    unverified_header = jwt.get_unverified_header(token)
    # Fetch the public key from auth server
    async with httpx.AsyncClient() as client:
        public_key = await client.get(JWKS_URL)
        public_key = public_key.json()
    kid = unverified_header.get("kid")
    if not kid:
        raise jwt.InvalidTokenError("Token has no kid")
    matches = [k for k in public_key["keys"] if k["kid"] == kid]
    matching = matches[0] if matches else None
    if not matches:
        raise jwt.InvalidTokenError("Token has no matching kid")
    public_key = RSAAlgorithm.from_jwk(json.dumps(matching))
    # Verify the token
    return jwt.decode(token, public_key, algorithms=["RS256"])

# Define the dependency
async def has_access(
    token: Annotated[str, Depends(oauth2_scheme)],
    security_scopes: SecurityScopes
):
    try:
        validated_token = await validate_access_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get the scopes from the token
    token_scopes = set(validated_token.get("scopes"))
    # Get the scopes required by the resource being called
    required_scopes = set(security_scopes.scopes)

    has_access = token_scopes & required_scopes
    if not has_access:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return True
```


## Setup

To enable users to query the example service, we'll need to make sure that the Auth Server has the corresponding permissions required by the service. To do so, we'll create a new super user, and create the permissions that will allow that user(and it's members) to access the resources of the example service.

### Create a new user

Create a new test user. This will create a new organization account with a super user with owner role.

```bash
curl --location 'http://localhost:8000/user/signup' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--data '{
  "user": {
    "username": "test_user",
    "password": "test1234@",
    "primary_email": "example@example.com"
  },
  "org": {
    "name": "test_org",
    "domain": "example.example.come",
    "type": "teams",
    "mfa_enabled": false
  }
}'
```

### Login as the new user

Login as the new user and retrieve an access token.

```bash
curl --location 'http://localhost:8000/user/login' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Accept: application/json' \
--data-urlencode 'username=test_user' \
--data-urlencode 'password=test1234@' \
--data-urlencode 'grant_type=password' \
--data-urlencode 'scope='

```

### Create a new Permission Scope

With the access token of the super-user, you will now create a permission for the billing resource. For this example, we'll only create a permission that will grant read privillege.

```bash

curl --location 'http://localhost:8000/permission/' \
--header 'accept: application/json' \
--header 'Authorization: Bearer <paste access token here>' \
--header 'Content-Type: application/json' \
--data '{
  "service": "example_service",
  "resource": "billing",
  "action": "read",
  "description": "Example service read"
}'
```

Once we create the permission, we'll need to attach it to a role. For now, we'll simply attach it to the `owner` role that the super-user is attached to. You could create a new custom role, and attach it to that as well.

```bash
curl --location 'http://localhost:8000/role/attach-permission' \
--header 'accept: application/json' \
--header 'Authorization: Bearer <paste access token here>' \
--header 'Content-Type: application/json' \
--data '{
  "role_id": <role_id>,
  "permission_slug": "example_service.billing.read"
}'
```

To get the role id, you can query the get roles endpoint, and grab the id of the role:

```bash
curl --location 'http://localhost:8000/role/' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer <paste access token here>'
```

## Launch Example Server

Start the example service:

```bash
uv run uvicorn main:app --port 8001 --host 0.0.0.0 --reload
```

### Query the endpoints:

1. Get the access token
   ```bash
    curl --location 'http://localhost:8000/user/login' \
    --header 'Content-Type: application/x-www-form-urlencoded' \
    --header 'Accept: application/json' \
    --data-urlencode 'username=test_user' \
    --data-urlencode 'password=test1234@' \
    --data-urlencode 'grant_type=password' \
    --data-urlencode 'scope='

    ```
2. Get endpoint:
    ```bash
    curl -X 'GET' \
    'http://localhost:8001/billing/' \
    -H 'accept: application/json' \
    -H 'Authorization: Bearer <paste access token here>'
    ```

    This should return:
    ```bash
    {
        "message": "Read billing"
    }
    ```
3. Post endpoint:
    ```bash
    curl -X 'POST' \
        'http://localhost:8001/billing/' \
        -H 'accept: application/json' \
        -H 'Authorization: Bearer <paste access token here>'
    ```
    This should return:
    ```bash
    {
    "detail": "Not enough permissions"
    }
    ```
    This is because in our demo, we have not created any permission that grants any user access to the write endpoint. Specifically our test user has no permission that grants that access. In order to do so, follow the aforementioned steps to create the `example_service.billing.write` permission which is required by that endpoint, and attach it to the `owner` role.