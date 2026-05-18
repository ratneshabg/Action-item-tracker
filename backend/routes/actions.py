"""
Action Items API Routes
Defines all endpoints for managing action items
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
import logging

from models import ActionItemCreate, ActionItemUpdate, ActionItemResponse, ActionItem
from services.action_service import ActionService

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize service
action_service = ActionService()

# ============================================================================
# GET ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[ActionItemResponse])
async def get_all_actions(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    priority_filter: Optional[str] = Query(None, description="Filter by priority"),
    owner_filter: Optional[str] = Query(None, description="Filter by owner")
):
    """
    Get all action items with optional filtering
    
    Query Parameters:
    - skip: Number of items to skip (for pagination)
    - limit: Number of items to return (default: 100)
    - status_filter: Filter by status (Pending, In Progress, Completed, Blocked, Ongoing)
    - priority_filter: Filter by priority (High, Medium, Low)
    - owner_filter: Filter by owner name
    """
    try:
        # Get all actions
        actions = action_service.get_all_actions()
        
        # Apply filters
        if status_filter:
            actions = [a for a in actions if a.status == status_filter]
        if priority_filter:
            actions = [a for a in actions if a.priority == priority_filter]
        if owner_filter:
            actions = [a for a in actions if owner_filter.lower() in a.owner.lower()]
        
        # Apply pagination
        actions = actions[skip:skip + limit]
        
        logger.info(f"Retrieved {len(actions)} actions with filters applied")
        return actions
    except Exception as e:
        logger.error(f"Error in get_all_actions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve actions"
        )

@router.get("/{action_id}", response_model=ActionItemResponse)
async def get_action(action_id: str):
    """
    Get a specific action item by ID
    
    Path Parameters:
    - action_id: Unique identifier of the action item
    """
    try:
        action = action_service.storage_service.get_action_by_id(action_id)
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action with ID {action_id} not found"
            )
        return ActionItem(**action)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_action: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve action"
        )

@router.get("/stats/summary")
async def get_statistics():
    """
    Get action items statistics
    
    Returns:
    - total_actions: Total number of actions
    - completed: Count of completed actions
    - pending: Count of pending actions
    - in_progress: Count of in-progress actions
    - blocked: Count of blocked actions
    - ongoing: Count of ongoing actions
    - high_priority: Count of high priority actions
    - medium_priority: Count of medium priority actions
    - low_priority: Count of low priority actions
    - average_completion: Average completion percentage
    """
    try:
        stats = action_service.get_action_statistics()
        return {"status": "success", "data": stats}
    except Exception as e:
        logger.error(f"Error in get_statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )

# ============================================================================
# POST ENDPOINTS
# ============================================================================

@router.post("/", response_model=ActionItemResponse, status_code=status.HTTP_201_CREATED)
async def create_action(action_create: ActionItemCreate):
    """
    Create a new action item
    
    Request Body:
    - meeting_date: Date of the meeting (format: YYYY-MM-DD)
    - action_item: Action item title (required)
    - action_description: Detailed description (required)
    - owner: Person responsible (required)
    - support: Support details or team
    - status: Status (Pending, In Progress, Completed, Blocked, Ongoing)
    - priority: Priority (High, Medium, Low)
    - due_date: Due date (format: YYYY-MM-DD)
    - completion_percentage: Completion percentage (0-100)
    - remarks: Additional remarks
    """
    try:
        new_action = action_service.create_action(action_create)
        if not new_action:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create action"
            )
        logger.info(f"Created action: {new_action.id}")
        return new_action
    except Exception as e:
        logger.error(f"Error in create_action: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create action"
        )

# ============================================================================
# PUT ENDPOINTS
# ============================================================================

@router.put("/{action_id}", response_model=ActionItemResponse)
async def update_action(action_id: str, action_update: ActionItemUpdate):
    """
    Update an existing action item
    
    Path Parameters:
    - action_id: Unique identifier of the action item
    
    Request Body (all fields optional):
    - meeting_date: Updated meeting date
    - action_item: Updated title
    - action_description: Updated description
    - owner: Updated owner
    - support: Updated support details
    - status: Updated status
    - priority: Updated priority
    - due_date: Updated due date
    - completion_percentage: Updated completion percentage
    - remarks: Updated remarks
    """
    try:
        # Check if action exists
        existing = action_service.storage_service.get_action_by_id(action_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action with ID {action_id} not found"
            )
        
        updated_action = action_service.update_action(action_id, action_update)
        if not updated_action:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update action"
            )
        logger.info(f"Updated action: {action_id}")
        return updated_action
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_action: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update action"
        )

# ============================================================================
# DELETE ENDPOINTS
# ============================================================================

@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action(action_id: str):
    """
    Delete an action item
    
    Path Parameters:
    - action_id: Unique identifier of the action item to delete
    """
    try:
        # Check if action exists
        existing = action_service.storage_service.get_action_by_id(action_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action with ID {action_id} not found"
            )
        
        if not action_service.delete_action(action_id):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete action"
            )
        logger.info(f"Deleted action: {action_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_action: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete action"
        )
