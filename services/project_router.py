from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from schema.project import ProjectSchema
import services.controller as controller
from services.db import get_db
from services.models import UserModel

# All routes in this router will be prefixed with /projects
router = APIRouter(prefix="/projects", tags=["projects"])


# Create a project for a user -> POST /projects/create_project/for_user/{user_id}
@router.post("/create_project/for_user/{user_id}", status_code=status.HTTP_201_CREATED, response_model=ProjectSchema)
def create_project_endpoint(user_id: int, project: ProjectSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return controller.create_project(user_id, project, db)


# List all projects for a user -> GET /projects/list_projects/for_user/{user_id}
@router.get("/list_projects/for_user/{user_id}", status_code=status.HTTP_200_OK)
def get_projects_endpoint(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return controller.get_projects(user_id, db)



# Delete a project -> DELETE /projects/delete_project/{project_id}
@router.delete("/delete_project/{project_id}", status_code=status.HTTP_200_OK)
def delete_project_endpoint(project_id: int, password: str, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
    return controller.delete_project(project_id, password, current_user.id, db)


# Update a project -> PUT /projects/update_project/{project_id}
@router.put("/update_project/{project_id}", status_code=status.HTTP_200_OK, response_model=ProjectSchema)
def update_project_endpoint(project_id: int, project: ProjectSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
    return controller.update_project(project_id, project, current_user.id, db)


