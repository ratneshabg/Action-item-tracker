"""
Action Item Service Layer
Handles business logic for action item operations
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from models import ActionItem, ActionItemCreate, ActionItemUpdate
from services.azure_storage_service import AzureStorageService

logger = logging.getLogger(__name__)

class ActionService:
    """Service class for managing action items"""
    
    def __init__(self):
        """Initialize Action Service with Azure Storage"""
        self.storage_service = AzureStorageService()
    
    def get_all_actions(self) -> List[ActionItem]:
        """Retrieve all action items"""
        try:
            actions_data = self.storage_service.read_all_actions()
            actions = [
                ActionItem(**action) for action in actions_data
            ]
            logger.info(f"Retrieved {len(actions)} actions")
            return actions
        except Exception as e:
            logger.error(f"Error retrieving actions: {str(e)}")
            return []
    
    def create_action(self, action_create: ActionItemCreate) -> Optional[ActionItem]:
        """Create a new action item"""
        try:
            # Generate unique ID and timestamps
            action_id = str(uuid4())
            now = datetime.now()
            
            # Create action dictionary
            action_dict = action_create.dict()
            action_dict["id"] = action_id
            action_dict["created_date"] = now.isoformat()
            action_dict["updated_date"] = now.isoformat()
            
            # Read existing actions
            actions_data = self.storage_service.read_all_actions()
            
            # Add new action
            actions_data.append(action_dict)
            
            # Write back to storage
            if self.storage_service.write_all_actions(actions_data):
                logger.info(f"✅ Created action: {action_id}")
                return ActionItem(**action_dict)
            else:
                logger.error("Failed to write action to storage")
                return None
        except Exception as e:
            logger.error(f"Error creating action: {str(e)}")
            return None
    
    def update_action(self, action_id: str, action_update: ActionItemUpdate) -> Optional[ActionItem]:
        """Update an existing action item"""
        try:
            # Read existing actions
            actions_data = self.storage_service.read_all_actions()
            
            # Find and update action
            updated = False
            for action in actions_data:
                if action.get("id") == action_id:
                    # Update fields that are provided
                    update_data = action_update.dict(exclude_unset=True)
                    action.update(update_data)
                    action["updated_date"] = datetime.now().isoformat()
                    updated = True
                    break
            
            if not updated:
                logger.warning(f"Action not found for update: {action_id}")
                return None
            
            # Write back to storage
            if self.storage_service.write_all_actions(actions_data):
                # Get updated action
                updated_action = self.storage_service.get_action_by_id(action_id)
                if updated_action:
                    logger.info(f"✅ Updated action: {action_id}")
                    return ActionItem(**updated_action)
            
            return None
        except Exception as e:
            logger.error(f"Error updating action: {str(e)}")
            return None
    
    def delete_action(self, action_id: str) -> bool:
        """Delete an action item"""
        try:
            if self.storage_service.delete_action_by_id(action_id):
                logger.info(f"✅ Deleted action: {action_id}")
                return True
            else:
                logger.warning(f"Failed to delete action: {action_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting action: {str(e)}")
            return False
    
    def get_action_statistics(self) -> Dict[str, Any]:
        """Get statistics about actions"""
        try:
            actions = self.get_all_actions()
            
            stats = {
                "total_actions": len(actions),
                "completed": sum(1 for a in actions if a.status == "Completed"),
                "pending": sum(1 for a in actions if a.status == "Pending"),
                "in_progress": sum(1 for a in actions if a.status == "In Progress"),
                "blocked": sum(1 for a in actions if a.status == "Blocked"),
                "ongoing": sum(1 for a in actions if a.status == "Ongoing"),
                "high_priority": sum(1 for a in actions if a.priority == "High"),
                "medium_priority": sum(1 for a in actions if a.priority == "Medium"),
                "low_priority": sum(1 for a in actions if a.priority == "Low"),
                "average_completion": round(sum(a.completion_percentage for a in actions) / len(actions), 2) if actions else 0
            }
            
            logger.info(f"Statistics: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            return {}
