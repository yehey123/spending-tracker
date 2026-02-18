import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic_settings import SettingsConfigDict, BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import functools
import hashlib
import pickle
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from src.domain.models.transaction import Transaction
from src.domain.services.eligibility_service import EligibilityService


# Cache configuration for multi-worker support
# Uses filesystem-based cache which is process-safe
CACHE_DIR = "/tmp/budget-tracker-cache"
os.makedirs(CACHE_DIR, exist_ok=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/budget_tracker"
    
    # Database pool configuration for multi-worker support
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Cache configuration - can be switched to Redis later
    cache_backend: str = "file"  # Options: "file", "redis"
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    cache_ttl_seconds: int = 300  # 5 minutes default TTL


def get_engine():
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/budget_tracker")
    engine = create_async_engine(db_url, pool_size=10, max_overflow=20)
    return engine


def get_settings() -> Settings:
    """Lazy load settings to ensure proper initialization in multiprocessing contexts."""
    return Settings()


class FileCache:
    """Simple file-based caching implementation for multi-worker environments."""
    
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _generate_key(self, func_name: str, *args, **kwargs) -> str:
        data = {"func": func_name, "args": args, "kwargs": kwargs}
        key_data = pickle.dumps(data)
        return hashlib.md5(key_data).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"cache_{key}.pkl")
    
    def get(self, func_name: str, *args, **kwargs) -> Any | None:
        key = self._generate_key(func_name, *args, **kwargs)
        cache_path = self._get_cache_path(key)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "rb") as f:
                    cached_data = pickle.load(f)
                
                if datetime.now() < cached_data["expires_at"]:
                    return cached_data["value"]
                else:
                    os.remove(cache_path)
            except Exception:
                pass
        
        return None
    
    def set(self, value: Any, func_name: str, *args, **kwargs) -> None:
        key = self._generate_key(func_name, *args, **kwargs)
        cache_path = self._get_cache_path(key)
        
        cached_data = {
            "value": value,
            "expires_at": datetime.now() + __import__("datetime").timedelta(seconds=300),
        }
        
        with open(cache_path, "wb") as f:
            pickle.dump(cached_data, f)
    
    def clear(self) -> None:
        for filename in os.listdir(self.cache_dir):
            if filename.startswith("cache_"):
                os.remove(os.path.join(self.cache_dir, filename))


file_cache = FileCache()


def get_cache(settings: Settings = Depends(get_settings)):
    """Get the appropriate cache based on settings."""
    if settings.cache_backend == "redis":
        raise NotImplementedError("Redis caching not yet implemented")
    return file_cache


def cached_result(ttl_seconds: int = 300):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cached_value = file_cache.get(func.__name__, *args, **kwargs)
            if cached_value is not None:
                return cached_value
            
            result = await func(*args, **kwargs)
            file_cache.set(result, func.__name__, *args, **kwargs)
            return result
        
        return wrapper
    return decorator


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Budget Tracker API",
    description="Financial tracker with AI optimization",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "Budget Tracker API", "version": "0.1.0"}


@app.get("/health")
async def health_check(engine=Depends(get_engine)):
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {str(e)}")


@app.post("/transactions", response_model=Transaction)
async def create_transaction(
    transaction: Transaction,
    settings: Settings = Depends(get_settings),
):
    transaction.is_naffl_eligible = EligibilityService.check_unionbank_naffl(transaction)
    return transaction


@app.get("/transactions", response_model=list[Transaction])
async def list_transactions(
    settings: Settings = Depends(get_settings),
):
    return []


@app.get("/eligibility/check")
@cached_result(ttl_seconds=300)
async def check_eligibility(
    description: str,
    amount: float,
    category: str,
    settings: Settings = Depends(get_settings),
):
    try:
        from decimal import Decimal

        transaction = Transaction(
            description=description,
            amount=Decimal(str(amount)),
            category=category,
            date=datetime.now(),
        )
        
        is_eligible = EligibilityService.check_unionbank_naffl(transaction)
        
        return {
            "transaction": transaction,
            "is_eligible": is_eligible,
            "eligible_categories": ["Not Quasi-cash", "Not Cash-in"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/cache/clear")
async def clear_cache():
    file_cache.clear()
    return {"message": "Cache cleared successfully"}


@app.get("/cache/stats")
async def cache_stats():
    cache_dir = CACHE_DIR
    files = [f for f in os.listdir(cache_dir) if f.startswith("cache_")]
    
    total_size = 0
    for file in files:
        path = os.path.join(cache_dir, file)
        total_size += os.path.getsize(path)
    
    return {
        "backend": "file",
        "cache_directory": cache_dir,
        "total_entries": len(files),
        "total_size_bytes": total_size,
        "redis_configured": False,
    }