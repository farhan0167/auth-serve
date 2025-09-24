
from fastapi import FastAPI

from api.routes import (
    permission_router,
    project_router,
    role_router,
    user_router,
    validate_router,
)
from db.engine import create_db_and_tables, drop_db_and_tables

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.delete("/tables")
def delete_tables():
    drop_db_and_tables()
    return {"message": "Tables deleted"}


app.include_router(user_router)
app.include_router(project_router)
app.include_router(role_router)
app.include_router(permission_router)
app.include_router(validate_router)
