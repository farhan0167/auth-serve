from typing import Union

from fastapi import FastAPI

from db.engine import create_db_and_tables
from api.routes import (
    user_router,
    project_router,
    role_router,
    permission_router,
    validate_router
)

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    

app.include_router(user_router)
app.include_router(project_router)
app.include_router(role_router)
app.include_router(permission_router)
app.include_router(validate_router)