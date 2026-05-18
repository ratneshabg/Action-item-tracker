"""
Configuration management using Pydantic Settings
Handles environment variables and application configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Azure Storage Configuration
    azure_storage_account_name: str = "devstoreaccount1"
    azure_storage_account_key: str = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXeOUQQWfsr+0xUQi+KZ98L0jMn1DBMv2Z80CUWZbKo0nK5NLsvp69+Sx==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;FileEndpoint=http://127.0.0.1:10003/devstoreaccount1;"
    azure_storage_container_name: str = "meeting-dashboard"
    
    # Azure AD Configuration (Optional)
    azure_ad_client_id: Optional[str] = None
    azure_ad_client_secret: Optional[str] = None
    azure_ad_tenant_id: Optional[str] = None
    
    # Application Configuration
    app_env: str = "development"
    debug: bool = True
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # API Configuration
    api_port: int = 8000
    api_host: str = "0.0.0.0"
    
    # Data Lake Configuration
    data_lake_path: str = "/meeting-dashboard/data/action_items.json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()

logger.info(f"✅ Configuration loaded: Environment={settings.app_env}")
