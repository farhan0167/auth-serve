from fastapi import APIRouter

project_router = APIRouter(prefix="/project", tags=["project"])

@project_router.post("/")
async def create_project():
    return

@project_router.get("/")
async def get_projects():
    return

@project_router.get("/{project_id}")
async def get_project(project_id):
    return

@project_router.delete("/{project_id}")
async def delete_project(project_id):
    return

@project_router.put("/{project_id}/apikey")
async def update_project(project_id):
    return