from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./satsangee.db")

if DATABASE_URL.startswith("postgres"):
    if "?" in DATABASE_URL and "sslmode=" in DATABASE_URL:
        base, params = DATABASE_URL.split("?", 1)
        params_list = [p for p in params.split("&") if not p.startswith("sslmode=")]
        DATABASE_URL = base + ("?" + "&".join(params_list) if params_list else "")
    
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif not DATABASE_URL.startswith("postgresql+asyncpg://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Configure engine differently for SQLite vs Postgres
if DATABASE_URL.startswith('sqlite'):
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={},
        pool_pre_ping=True
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={
            'server_settings': {'jit': 'off'},
            'command_timeout': 60,
        }
    )
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with async_session_maker() as session:
        yield session
