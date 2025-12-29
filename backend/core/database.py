"""
MongoDB Atlas configuration for CirculoMetrix AI
Safe FastAPI lifecycle + async-first design
"""

import logging
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from contextlib import asynccontextmanager
from functools import wraps

from core.config import settings

logger = logging.getLogger(__name__)

mongo_client: MongoClient | None = None
async_mongo_client: AsyncIOMotorClient | None = None
db = None
async_db = None


# ==========================
# Initialization
# ==========================

def init_db():
    global mongo_client, async_mongo_client, db, async_db

    try:
        mongo_client = MongoClient(settings.database_url)
        async_mongo_client = AsyncIOMotorClient(settings.database_url)

        config = settings.model_dump()
        db_name = config.get("DATABASE_NAME")

        if not db_name:
          raise RuntimeError("DATABASE_NAME is not configured")

        db = mongo_client[db_name]

        async_db = async_mongo_client[settings.DATABASE_NAME]

        # Ping test
        mongo_client.admin.command("ping")
        logger.info("🍃 MongoDB Atlas connected")

        _create_indexes()

    except Exception as e:
        logger.error(f"MongoDB init failed: {e}")
        raise


def _create_indexes():
    collections = db.list_collection_names()

    if "users" not in collections:
        db.create_collection("users")

    db.users.create_index("email", unique=True)
    db.users.create_index("username", unique=True)
    db.users.create_index("created_at")

    logger.info("📌 MongoDB indexes ready")


# ==========================
# Dependencies
# ==========================

async def get_async_db():
    return async_db


def get_db():
    return db


# ==========================
# Transactions
# ==========================

@asynccontextmanager
async def async_transaction():
    async with await async_mongo_client.start_session() as session:
        async with session.start_transaction():
            yield session


# ==========================
# Health Check
# ==========================

async def database_health_check():
    try:
        await async_mongo_client.admin.command("ping")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# ==========================
# Shutdown
# ==========================

def close_db_connections():
    if mongo_client:
        mongo_client.close()
    if async_mongo_client:
        async_mongo_client.close()

    logger.info("🔌 MongoDB connections closed")
