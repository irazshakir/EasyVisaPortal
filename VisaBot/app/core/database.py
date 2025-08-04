"""
Database connection and session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from loguru import logger

from app.core.config import settings
from app.models.database import Base

# Create async engine for Supabase PostgreSQL
engine = None
AsyncSessionLocal = None


async def init_database():
    """Initialize database connection"""
    global engine, AsyncSessionLocal
    
    # If engine already exists, dispose it first
    if engine:
        await engine.dispose()
        engine = None
        AsyncSessionLocal = None
    
    # Construct DATABASE_URL from individual components if not provided
    database_url = settings.DATABASE_URL
    if not database_url and all([settings.DB_USER, settings.DB_PASSWORD, settings.DB_HOST, settings.DB_PORT, settings.DB_NAME]):
        database_url = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        logger.info("Constructed DATABASE_URL from individual components")
    
    if not database_url:
        logger.warning("DATABASE_URL not set and individual DB components not provided, skipping database initialization")
        return
    
    try:
        # Convert sync URL to async URL for Supabase and add PgBouncer compatibility
        async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        # Add PgBouncer compatibility parameters to URL
        if "?" in async_url:
            async_url += "&statement_cache_size=0&prepared_statement_cache_size=0"
        else:
            async_url += "?statement_cache_size=0&prepared_statement_cache_size=0"
        
        engine = create_async_engine(
            async_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_recycle=300,
            # Disable prepared statements for PgBouncer compatibility
            connect_args={
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
                "server_settings": {
                    "jit": "off"
                }
            }
        )
        
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info("Database connection initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def get_db_session() -> AsyncSession:
    """Get database session"""
    if not AsyncSessionLocal:
        await init_database()
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all database tables"""
    if not engine:
        await init_database()
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise


async def close_database():
    """Close database connection"""
    if engine:
        await engine.dispose()
        logger.info("Database connection closed") 