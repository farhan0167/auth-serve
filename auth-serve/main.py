from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import (
    jwks_router,
    permission_router,
    project_router,
    role_router,
    user_router,
)
from db.engine import create_db_and_tables, drop_db_and_tables

app = FastAPI(title="Auth Serve", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
app.include_router(jwks_router)
