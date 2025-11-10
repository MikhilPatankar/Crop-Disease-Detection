from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from . import model
from . import caching
from .database import connect_to_mongo, close_mongo_connection
from .routers import authentication, prediction, schemes, weather

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    print("Starting up...")
    await connect_to_mongo()
    model.load_model()
    caching_task = asyncio.create_task(caching.run_scheme_caching_task())
    yield
    
    print("Shutting down...")
    caching_task.cancel()
    await close_mongo_connection()

app = FastAPI(
    title="Crop Disease Detection API",
    description="A FastAPI backend for crop disease prediction.",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
def root():
    """Root endpoint."""
    return {'message': 'Welcome to the Crop Disease Detection API!'}

app.include_router(authentication.router)
app.include_router(prediction.router)
app.include_router(schemes.router)
app.include_router(weather.router)