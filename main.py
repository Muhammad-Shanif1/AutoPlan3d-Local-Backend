from fastapi import FastAPI

app = FastAPI()

# include routers
from services.user_router import router as user_router
from services.project_router import router as project_router
app.include_router(user_router)
app.include_router(project_router)
