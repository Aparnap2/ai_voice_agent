"""
Database configuration and connection management.
"""
import asyncio
from typing import AsyncGenerator

import structlog
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

logger = structlog.get_logger()

# Database metadata and base model
metadata = MetaData()
Base = declarative_base(metadata=metadata)

# Database engines and sessions
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None


def get_database_url(async_mode: bool = False) -> str:
    """Get database URL with appropriate driver for sync/async mode."""
    settings = get_settings()
    db_url = settings.DATABASE_URL
    
    if async_mode and db_url.startswith("postgresql://"):
        # Convert to async PostgreSQL URL
        return db_url.replace("postgresql://", "postgresql+asyncpg://")
    elif async_mode and db_url.startswith("sqlite:///"):
        # Convert to async SQLite URL
        return db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    
    return db_url


async def init_db() -> None:
    """Initialize database connections and create tables."""
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    
    settings = get_settings()
    
    try:
        # Create sync engine for migrations
        engine = create_engine(
            get_database_url(async_mode=False),
            echo=settings.DEBUG,
            pool_pre_ping=True,
        )
        
        # Create async engine for application use
        async_engine = create_async_engine(
            get_database_url(async_mode=True),
            echo=settings.DEBUG,
            pool_pre_ping=True,
        )
        
        # Create session factories
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        AsyncSessionLocal = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise


async def close_db() -> None:
    """Close database connections."""
    global engine, async_engine
    
    try:
        if async_engine:
            await async_engine.dispose()
        if engine:
            engine.dispose()
        
        logger.info("Database connections closed")
        
    except Exception as e:
        logger.error("Error closing database connections", error=str(e))


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    if not AsyncSessionLocal:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session():
    """Get sync database session for migrations."""
    if not SessionLocal:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()