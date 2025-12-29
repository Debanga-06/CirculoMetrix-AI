"""
MongoDB Atlas configuration for CirculoMetrix AI
Render-safe, async-only, non-blocking
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from core.config import settings

logger = logging.getLogger(__name__)

async_client: AsyncIOMotorClient | None = None
async_db = None
_indexes_created = False


# ==========================
# Initialization (NON-BLOCKING)
# ==========================

async def init_db():
    """
    Initialize MongoDB lazily.
    Never blocks app startup on Render.
    """
    global async_client, async_db

    if async_client is not None:
        return

    try:
        async_client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
        )

        async_db = async_client[settings.DATABASE_NAME]

        # Fire-and-forget index creation
        await _safe_create_indexes()

        logger.info("🍃 MongoDB Atlas connected")

    except Exception as e:
        logger.warning(f"MongoDB not ready (will retry lazily): {e}")


# ==========================
# Indexes (SAFE)
# ==========================

async def _safe_create_indexes():
    global _indexes_created

    if _indexes_created:
        return

    try:
        collections = await async_db.list_collection_names()

        if "users" not in collections:
            await async_db.create_collection("users")

        await async_db.users.create_index("email", unique=True)
        await async_db.users.create_index("username", unique=True)
        await async_db.users.create_index("created_at")

        _indexes_created = True
        logger.info("📌 MongoDB indexes ready")

    except Exception as e:
        logger.warning(f"Index creation skipped: {e}")


# ==========================
# Dependency
# ==========================

async def get_async_db():
    if async_db is None:
        await init_db()
    return async_db

# ==========================
# Transactions
# ==========================

@asynccontextmanager
async def async_transaction():
    if async_client is None:
        await init_db()

    async with await async_client.start_session() as session:
        async with session.start_transaction():
            yield session


# ==========================
# Health Check
# ==========================

async def database_health_check():
    try:
        if async_client is None:
            await init_db()

        await async_client.admin.command("ping")
        return {"status": "healthy"}

    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# ==========================
# Shutdown
# ==========================

def close_db_connections():
    if async_client is not None:
        async_client.close()
        logger.info("🔌 MongoDB connections closed")
