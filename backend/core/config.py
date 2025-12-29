"""
Application configuration using Pydantic Settings
Supports MongoDB Atlas for production and development environments
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
from pathlib import Path
from pydantic import Field, field_validator



class Settings(BaseSettings):
    """
    Application settings with environment variable support
    Compatible with existing .env configuration - now using MongoDB Atlas
    """
    
    # ==========================================
    # Application Settings
    # ==========================================
    APP_NAME: str = Field(default="CirculoMetrix AI", env="APP_NAME")
    VERSION: str = Field(default="1.0.0", env="VITE_APP_VERSION")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    
    # ==========================================
    # Server Settings
    # ==========================================
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_V1_PREFIX: str = Field(default="/api/v1", env="API_V1_PREFIX")
    
    # ==========================================
    # MongoDB Atlas Settings
    # ==========================================
    # MongoDB Atlas connection string
    # Canonical DB URL
    DATABASE_URL: str = Field(
      default="mongodb://localhost:27017",
      env="DATABASE_URL",
      description="MongoDB connection string"
    )

    DATABASE_NAME: str = Field(
    default="CirculoMetrix",
    env="DATABASE_NAME",
    description="MongoDB database name"
    )


# 🔁 Backward compatibility (IMPORTANT)
    MONGODB_URI: Optional[str] = Field(
      default=None,
      env="MONGODB_URI",
      description="Backward-compatible MongoDB URI"
    )
    
    # Optional: Separate read connection for scaling
    DATABASE_READ_URL: Optional[str] = Field(
        default=None,
        env="DATABASE_READ_URL",
        description="Optional read-only MongoDB connection string"
    )
    
    @property
    def database_url(self) -> str:
     return self.MONGODB_URI or self.DATABASE_URL
    
    @property
    def database_name(self) -> str:
        """Get database name"""
        return self.DATABASE_NAME
    
    # MongoDB connection pool settings
    MONGO_MAX_POOL_SIZE: int = Field(default=50, env="MONGO_MAX_POOL_SIZE")
    MONGO_MIN_POOL_SIZE: int = Field(default=10, env="MONGO_MIN_POOL_SIZE")
    MONGO_MAX_IDLE_TIME_MS: int = Field(default=30000, env="MONGO_MAX_IDLE_TIME_MS")
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = Field(default=5000, env="MONGO_SERVER_SELECTION_TIMEOUT_MS")
    MONGO_CONNECT_TIMEOUT_MS: int = Field(default=10000, env="MONGO_CONNECT_TIMEOUT_MS")
    
    # ==========================================
    # Security & Authentication
    # ==========================================
    SECRET_KEY: str = Field(
        default="change-this-in-production-use-strong-secret-key",
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    BCRYPT_ROUNDS: int = Field(default=12, env="BCRYPT_ROUNDS")
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v, info):
       """Warn if using default secret key in production"""
       environment = info.data.get("ENVIRONMENT", "development")
       if environment == "production" and "change-this" in v:
           raise ValueError("Must set a strong SECRET_KEY in production!")
       return v

    
    # ==========================================
    # CORS Settings
    # ==========================================
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        env="ALLOWED_ORIGINS"
    )
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
    
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # ==========================================
    # AI/ML Model Configuration
    # ==========================================
    MODEL_PATH: str = Field(default="./ml_models/predictor.pkl", env="MODEL_PATH")
    SCALER_PATH: str = Field(default="./ml_models/scaler.pkl", env="SCALER_PATH")
    FEATURE_COLUMNS_PATH: str = Field(
        default="./ml_models/feature_columns.json",
        env="FEATURE_COLUMNS_PATH"
    )
    
    # Model training parameters
    ML_RANDOM_STATE: int = Field(default=42, env="ML_RANDOM_STATE")
    ML_TEST_SIZE: float = Field(default=0.2, env="ML_TEST_SIZE")
    ML_N_ESTIMATORS: int = Field(default=100, env="ML_N_ESTIMATORS")
    
    # ==========================================
    # LCA Dataset Paths
    # ==========================================
    DATASET_BASE_PATH: str = Field(default="./datasets", env="DATASET_BASE_PATH")
    METALS_DATASET_PATH: str = Field(default="./datasets/metals", env="METALS_DATASET_PATH")
    LCA_EMISSION_FACTORS_PATH: str = Field(
        default="./datasets/lca_emission_factors.csv",
        env="LCA_EMISSION_FACTORS_PATH"
    )
    TRANSPORT_FACTORS_PATH: str = Field(
        default="./datasets/transport_factors.csv",
        env="TRANSPORT_FACTORS_PATH"
    )
    RECYCLING_EFFICIENCY_PATH: str = Field(
        default="./datasets/recycling_efficiency.csv",
        env="RECYCLING_EFFICIENCY_PATH"
    )
    
    # ==========================================
    # File Upload Settings
    # ==========================================
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, env="MAX_UPLOAD_SIZE_MB")
    ALLOWED_FILE_TYPES: str = Field(default="csv,xlsx,xls,json", env="ALLOWED_FILE_TYPES")
    
    @property
    def max_upload_size(self) -> int:
        """Get max upload size in bytes"""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    
    @property
    def allowed_extensions(self) -> List[str]:
        """Parse allowed file extensions"""
        return [f".{ext.strip()}" for ext in self.ALLOWED_FILE_TYPES.split(",") if ext.strip()]
    
    # ==========================================
    # Email Configuration
    # ==========================================
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_FROM_EMAIL: Optional[str] = Field(default=None, env="SMTP_FROM_EMAIL")
    SMTP_FROM_NAME: str = Field(default="CirculoMetrix AI", env="SMTP_FROM_NAME")
    
    # ==========================================
    # Report Generation
    # ==========================================
    REPORT_OUTPUT_PATH: str = Field(default="./reports", env="REPORT_OUTPUT_PATH")
    REPORT_LOGO_PATH: str = Field(default="./assets/logo.png", env="REPORT_LOGO_PATH")
    REPORT_TEMPLATE_PATH: str = Field(
        default="./templates/report_template.html",
        env="REPORT_TEMPLATE_PATH"
    )
    
    # ==========================================
    # Logging Configuration
    # ==========================================
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE_PATH: str = Field(default="./logs/app.log", env="LOG_FILE_PATH")
    LOG_FILE_MAX_BYTES: int = Field(default=10485760, env="LOG_FILE_MAX_BYTES")
    LOG_FILE_BACKUP_COUNT: int = Field(default=5, env="LOG_FILE_BACKUP_COUNT")
    
    # ==========================================
    # Redis/Cache Settings
    # ==========================================
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    CACHE_ENABLED: bool = Field(default=False, env="CACHE_ENABLED")
    CACHE_TTL_SECONDS: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    
    @property
    def redis_url(self) -> Optional[str]:
        """Construct Redis URL if cache is enabled"""
        if not self.CACHE_ENABLED:
            return None
        
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ==========================================
    # External API Keys
    # ==========================================
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    GOOGLE_MAPS_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_MAPS_API_KEY")
    
    # ==========================================
    # Monitoring & Analytics
    # ==========================================
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    GOOGLE_ANALYTICS_ID: Optional[str] = Field(default=None, env="GOOGLE_ANALYTICS_ID")
    POSTHOG_API_KEY: Optional[str] = Field(default=None, env="POSTHOG_API_KEY")
    
    # ==========================================
    # Rate Limiting
    # ==========================================
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_PERIOD_SECONDS: int = Field(default=60, env="RATE_LIMIT_PERIOD_SECONDS")
    
    # ==========================================
    # Deployment URLs
    # ==========================================
    RENDER_EXTERNAL_URL: Optional[str] = Field(default=None, env="RENDER_EXTERNAL_URL")
    VERCEL_URL: Optional[str] = Field(default=None, env="VERCEL_URL")
    
    # ==========================================
    # Frontend Configuration (Vite)
    # ==========================================
    VITE_API_BASE_URL: str = Field(default="http://localhost:8000", env="VITE_API_BASE_URL")
    VITE_APP_NAME: str = Field(default="CirculoMetrix AI", env="VITE_APP_NAME")
    VITE_ENABLE_ANALYTICS: bool = Field(default=False, env="VITE_ENABLE_ANALYTICS")
    
    # ==========================================
    # Path Properties
    # ==========================================
    @property
    def base_dir(self) -> Path:
        """Get base directory path"""
        return Path(__file__).resolve().parent.parent
    
    @property
    def upload_path(self) -> Path:
        """Get upload directory path"""
        path = self.base_dir / "uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def model_path_dir(self) -> Path:
        """Get model directory path"""
        path = Path(self.MODEL_PATH).parent
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def log_path(self) -> Path:
        """Get log directory path"""
        path = Path(self.LOG_FILE_PATH).parent
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def report_path(self) -> Path:
        """Get report output directory path"""
        path = Path(self.REPORT_OUTPUT_PATH)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def dataset_path(self) -> Path:
        """Get dataset directory path"""
        path = Path(self.DATASET_BASE_PATH)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    # ==========================================
    # Pydantic Configuration
    # ==========================================
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Allow case-insensitive env vars
        extra = "allow"
    
    # ==========================================
    # Helper Methods
    # ==========================================
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT.lower() == "development"
    
    def is_testing(self) -> bool:
        """Check if running in testing"""
        return self.ENVIRONMENT.lower() == "testing"
    
    def get_db_type(self) -> str:
        """Get database type"""
        db_url = self.database_url
        if "mongodb+srv://" in db_url or "mongodb://" in db_url:
            return "mongodb"
        return "unknown"
    
    def is_mongodb_atlas(self) -> bool:
        """Check if using MongoDB Atlas"""
        return "mongodb+srv://" in self.database_url or "mongodb.net" in self.database_url
    
    def print_config(self) -> None:
        """Print configuration summary (for debugging)"""
        print("=" * 60)
        print(f"🚀 {self.APP_NAME} v{self.VERSION}")
        print("=" * 60)
        print(f"Environment:        {self.ENVIRONMENT}")
        print(f"Debug Mode:         {self.DEBUG}")
        print(f"Database Type:      {self.get_db_type()}")
        print(f"Database Name:      {self.DATABASE_NAME}")
        print(f"MongoDB Atlas:      {'Yes' if self.is_mongodb_atlas() else 'No'}")
        print(f"API Endpoint:       http://{self.API_HOST}:{self.API_PORT}")
        print(f"API Prefix:         {self.API_V1_PREFIX}")
        print(f"CORS Origins:       {len(self.cors_origins)} configured")
        print(f"Cache Enabled:      {self.CACHE_ENABLED}")
        print(f"Log Level:          {self.LOG_LEVEL}")
        print(f"Max Upload:         {self.MAX_UPLOAD_SIZE_MB}MB")
        print(f"Pool Size:          {self.MONGO_MAX_POOL_SIZE} (max)")
        print("=" * 60)
    
    def validate_paths(self) -> dict:
        """Validate that required paths and files exist"""
        checks = {
            "model_path": Path(self.MODEL_PATH).exists(),
            "scaler_path": Path(self.SCALER_PATH).exists(),
            "feature_columns_path": Path(self.FEATURE_COLUMNS_PATH).exists(),
            "datasets_exist": Path(self.DATASET_BASE_PATH).exists(),
            "log_dir_writable": Path(self.LOG_FILE_PATH).parent.exists(),
        }
        return checks


# ==========================================
# Create Global Settings Instance
# ==========================================
settings = Settings()


# ==========================================
# Startup validation
# ==========================================
if __name__ == "__main__":
    # Test configuration loading
    settings.print_config()
    print("\n📋 Path Validation:")
    for path_name, exists in settings.validate_paths().items():
        status = "✅" if exists else "⚠️"
        print(f"{status} {path_name}: {exists}")
