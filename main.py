import uvicorn
import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.routes import contacts, auth, users
from src.conf.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    The lifespan function is a coroutine that runs once when the server starts.
    It initializes the FastAPILimiter module with a connection to Redis.
    
    :param app: FastAPI: Pass the fastapi object to the lifespan function
    :return: A lifespanmanager object
    :doc-author: Trelent
    """
    r = await redis.Redis(host=settings.redis_host,
                          port=settings.redis_port,
                          db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)
    yield

app = FastAPI(lifespan=lifespan)

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
app.include_router(users.router, prefix='/api')
    

@app.get("/")
def read_root():
    """
    The read_root function is a function that returns the string &quot;Hello World&quot;
    in JSON format. This is an example of how to use FastAPI to create a ReST API.
    
    :return: A dictionary with a key &quot;message&quot; and
    :doc-author: Trelent
    """
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
