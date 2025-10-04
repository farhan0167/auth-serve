from typing import Union

from fastapi import FastAPI
from billing.router import billing_router

app = FastAPI()

app.include_router(billing_router)