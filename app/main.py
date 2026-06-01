from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router as v1_router
from app.db.session import Base, engine
from app.models import user, task  # noqa

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskAPI", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(v1_router)

@app.get("/")
def health():
    return {"status": "ok", "docs": "/docs"}
