"""
Azure Data Lake Storage Service
Handles all interactions with Azure Data Lake Gen2
"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from azure.storage.filedatalake import DataLakeServiceClient
from config import settings

logger = logging.getLogger(__name__)

class AzureStorageService:
    """Service for managing Azure Data Lake Storage operations"""
    
    def __init__(self):
        """Initialize Azure Storage Service"""
        try:
            # Create connection string
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={settings.azure_storage_account_name};AccountKey={settings.azure_storage_account_key};EndpointSuffix=core.windows.net"
            
            # Initialize Data Lake Service Client
            self.service_client = DataLakeServiceClient.from_connection_string(connection_string)
            
            # Get container/filesystem client
            self.file_system_client = self.service_client.get_file_system_client(
                file_system=settings.azure_storage_container_name
            )
            
            logger.info(f"✅ Azure Storage Service initialized for container: {settings.azure_storage_container_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure Storage Service: {str(e)}")
            raise
    
    def _ensure_file_exists(self) -> None:
        """Ensure the data file exists, create if missing"""
        try:
            # Try to get the file
            file_client = self.file_system_client.get_file_client(settings.data_lake_path)
            file_client.get_file_properties()
        except Exception as e:
            # File doesn't exist, create it with empty array
            logger.info(f"File does not exist, creating: {settings.data_lake_path}")
            try:
                # Create directories if needed
                self._create_directories(settings.data_lake_path)
                # Create file with initial data
                file_client = self.file_system_client.get_file_client(settings.data_lake_path)
                file_client.upload_file(json.dumps([], indent=2), overwrite=True)
                logger.info(f"✅ Created new data file: {settings.data_lake_path}")
            except Exception as create_error:
                logger.error(f"❌ Failed to create data file: {str(create_error)}")
                raise
    
    def _create_directories(self, path: str) -> None:
        """Create directory structure if it doesn't exist"""
        try:
            # Extract directory path
            parts = path.strip("/").split("/")
            current_path = ""
            
            # Create each directory level
            for part in parts[:-1]:  # Exclude filename
                current_path += f"/{part}"
                try:
                    self.file_system_client.get_directory_client(current_path).get_directory_properties()
                except Exception:
                    # Directory doesn't exist, create it
                    self.file_system_client.create_directory(current_path)
                    logger.info(f"Created directory: {current_path}")
        except Exception as e:
            logger.warning(f"Could not create directories: {str(e)}")
    
    def read_all_actions(self) -> List[Dict[Any, Any]]:
        """Read all action items from Azure Data Lake"""
        try:
            self._ensure_file_exists()
            
            # Read file from Azure Data Lake
            file_client = self.file_system_client.get_file_client(settings.data_lake_path)
            download = file_client.download_file()
            content = download.readall().decode("utf-8")
            
            # Parse JSON
            actions = json.loads(content) if content.strip() else []
            logger.info(f"✅ Read {len(actions)} actions from Azure Data Lake")
            return actions
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"❌ Error reading from Azure Data Lake: {str(e)}")
            return []
    
    def write_all_actions(self, actions: List[Dict[Any, Any]]) -> bool:
        """Write all action items to Azure Data Lake"""
        try:
            self._ensure_file_exists()
            
            # Convert to JSON
            content = json.dumps(actions, indent=2, default=str)
            
            # Write to Azure Data Lake
            file_client = self.file_system_client.get_file_client(settings.data_lake_path)
            file_client.upload_file(content, overwrite=True)
            
            logger.info(f"✅ Wrote {len(actions)} actions to Azure Data Lake")
            return True
        except Exception as e:
            logger.error(f"❌ Error writing to Azure Data Lake: {str(e)}")
            return False
    
    def get_action_by_id(self, action_id: str) -> Optional[Dict[Any, Any]]:
        """Get a specific action by ID"""
        try:
            actions = self.read_all_actions()
            for action in actions:
                if action.get("id") == action_id:
                    return action
            return None
        except Exception as e:
            logger.error(f"❌ Error getting action by ID: {str(e)}")
            return None
    
    def delete_action_by_id(self, action_id: str) -> bool:
        """Delete a specific action by ID"""
        try:
            actions = self.read_all_actions()
            filtered_actions = [a for a in actions if a.get("id") != action_id]
            
            if len(filtered_actions) == len(actions):
                logger.warning(f"Action not found for deletion: {action_id}")
                return False
            
            return self.write_all_actions(filtered_actions)
        except Exception as e:
            logger.error(f"❌ Error deleting action: {str(e)}")
            return False
    
    def health_check(self) -> bool:
        """Check if Azure Storage is accessible"""
        try:
            self.file_system_client.get_file_system_properties()
            logger.info("✅ Azure Storage health check passed")
            return True
        except Exception as e:
            logger.error(f"❌ Azure Storage health check failed: {str(e)}")
            return False
