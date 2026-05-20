from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from klee_web.api.jobs import router as jobs_router

app = FastAPI(
    title="KLEE Web",
    version="0.1.0",
    description="Browser-accessible KLEE symbolic execution.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(jobs_router)
