from fastapi import APIRouter, Depends, Security, HTTPException, status
from sqlmodel import Session, select

from api.dependency import oauth2_scheme,get_current_user
from db.engine import get_session
from db.tables import Project
from models import ProjectBase

project_router = APIRouter(prefix="/project", tags=["project"])

READ = "auth.project.read"
WRITE = "auth.project.write"
DELETE = "auth.project.delete"
ALL = "auth.project.all"


@project_router.post("/")
async def create_project(
    request: ProjectBase,
    current_user = Security(get_current_user, scopes=[WRITE, ALL]),
    db: Session = Depends(get_session),
):
    project = Project.model_validate(request)
    db.add(project)
    db.commit()
    return project


@project_router.get("/")
async def get_projects(
    current_user: str = Security(get_current_user, scopes=[READ, ALL]),
    db: Session = Depends(get_session),
):
    projects = db.exec(select(Project)).all()
    return projects


@project_router.get("/{project_id}")
async def get_project(
    project_id, 
    current_user: str = Security(get_current_user, scopes=[READ, ALL]),
    db: Session = Depends(get_session),
):
    project = db.exec(select(Project).where(Project.id == project_id)).one_or_none()
    return project
    


@project_router.delete("/{project_id}")
async def delete_project(
    project_id,
    current_user = Security(get_current_user, scopes=[DELETE, ALL]),
    db: Session = Depends(get_session),
):
    project = db.exec(select(Project).where(Project.id == project_id)).one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    db.delete(project)
    db.commit()
    return project


@project_router.put("/{project_id}/apikey")
async def update_project(project_id):
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
