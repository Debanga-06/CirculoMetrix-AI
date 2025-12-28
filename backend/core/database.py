"""
Database configuration and session management
SQLAlchemy setup with connection pooling and session handling
"""

from sqlalchemy import create_engine, event, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool
from typing import Generator
import logging

from core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# ==========================================
# Database Engine Configuration
# ==========================================

# Determine if using SQLite
is_sqlite = settings.database_url.startswith("sqlite")

# Create appropriate connection args based on database type
if is_sqlite:
    connect_args = {"check_same_thread": False}
    poolclass = StaticPool
    pool_config = {}
else:
    connect_args = {
        "connect_timeout": 10,
        "options": "-c timezone=utc"
    }
    poolclass = QueuePool
    pool_config = {
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
    }

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    poolclass=poolclass,
    connect_args=connect_args,
    **pool_config
)


# ==========================================
# SQLAlchemy Event Listeners
# ==========================================

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Set database connection parameters on connect
    For SQLite, enable foreign keys
    """
    if is_sqlite:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    if settings.DEBUG:
        logger.debug("Database connection established")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """
    Handle connection check-in to pool
    """
    if settings.DEBUG:
        logger.debug("Connection returned to pool")


# ==========================================
# Session Configuration
# ==========================================

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


# ==========================================
# Base Model Configuration
# ==========================================

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=convention)

# Create declarative base
Base = declarative_base(metadata=metadata)


# ==========================================
# Database Dependency
# ==========================================

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI routes
    
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


# ==========================================
# Database Utilities
# ==========================================

def init_db():
    """
    Initialize database - create all tables
    Should be called on application startup
    """
    try:
        logger.info(f"Initializing database tables... (Using {'SQLite' if is_sqlite else 'PostgreSQL'})")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


def drop_db():
    """
    Drop all database tables
    WARNING: This will delete all data!
    """
    try:
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Error dropping database: {str(e)}")
        raise


def check_db_connection() -> bool:
    """
    Check if database connection is working
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            if is_sqlite:
                conn.exec_driver_sql("SELECT 1")
            else:
                conn.exec_driver_sql("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


def get_db_info() -> dict:
    """
    Get database information
    
    Returns:
        Dictionary with database info
    """
    try:
        with engine.connect() as conn:
            if is_sqlite:
                result = conn.exec_driver_sql("SELECT sqlite_version()")
                version = f"SQLite {result.fetchone()[0]}"
            else:
                result = conn.exec_driver_sql("SELECT version()")
                version = result.fetchone()[0]
        
        # Get pool info (only for PostgreSQL)
        pool_info = {}
        if not is_sqlite:
            pool_info = {
                "pool_size": engine.pool.size(),
                "checked_in_connections": engine.pool.checkedin(),
                "checked_out_connections": engine.pool.checkedout(),
            }
            
        return {
            "status": "connected",
            "database_type": "SQLite" if is_sqlite else "PostgreSQL",
            "url": settings.database_url.split("@")[1] if "@" in settings.database_url else settings.database_url.replace("sqlite:///", ""),
            "version": version,
            **pool_info
        }
    except Exception as e:
        logger.error(f"Error getting database info: {str(e)}")
        return {
            "status": "disconnected",
            "error": str(e)
        }


# ==========================================
# Context Manager for Database Sessions
# ==========================================

class DatabaseSession:
    """
    Context manager for database sessions
    
    Usage:
        with DatabaseSession() as db:
            user = db.query(User).first()
    """
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self) -> Session:
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
            logger.error(f"Database session error: {exc_val}")
        else:
            self.db.commit()
        self.db.close()


# ==========================================
# Database Transaction Decorator
# ==========================================

from functools import wraps

def transactional(func):
    """
    Decorator to wrap function in database transaction
    Automatically commits on success, rolls back on error
    
    Usage:
        @transactional
        def create_user(db: Session, user_data: dict):
            user = User(**user_data)
            db.add(user)
            return user
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract db session from args or kwargs
        db = None
        for arg in args:
            if isinstance(arg, Session):
                db = arg
                break
        
        if db is None:
            db = kwargs.get('db')
        
        if db is None:
            raise ValueError("No database session found in function arguments")
        
        try:
            result = func(*args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Transaction failed: {str(e)}")
            raise
    
    return wrapper


# ==========================================
# Database Health Check
# ==========================================

async def database_health_check() -> dict:
    """
    Async health check for database
    
    Returns:
        Dictionary with health status
    """
    try:
        check_db_connection()
        info = get_db_info()
        
        return {
            "status": "healthy",
            "details": info
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }