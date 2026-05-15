from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import blog, plan, countdown, files, music, ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Personal Learning Hub", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(blog.router)
app.include_router(plan.router)
app.include_router(countdown.router)
app.include_router(files.router)
app.include_router(music.router)
app.include_router(ai.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
