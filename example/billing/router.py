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