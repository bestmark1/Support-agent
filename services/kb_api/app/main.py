from fastapi import FastAPI

from services.kb_api.app.api.routes import router

app = FastAPI(title="FitMentor KB API")
app.include_router(router)
