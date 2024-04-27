import uvicorn
import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.routes import contacts, auth
from src.conf.config import settings

app = FastAPI()

origins = settings.allow_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')


@asynccontextmanager
async def lifespan():
    r = await redis.Redis(host=settings.redis_host,
                          port=settings.redis_port,
                          db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
