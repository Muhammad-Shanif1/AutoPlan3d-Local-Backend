from pydantic import BaseModel, ConfigDict


class ProjectSchema(BaseModel):
    title: str
    description: str
    project_data: dict | None = None

    model_config = ConfigDict(from_attributes=True)