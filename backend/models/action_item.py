"""
Pydantic models for Action Items
Defines data validation and serialization for action items
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import uuid4
from .status import Status, Priority

class ActionItemCreate(BaseModel):
    """Model for creating a new action item"""
    meeting_date: str = Field(..., description="Date of the meeting")
    action_item: str = Field(..., description="Action item title")
    action_description: str = Field(..., description="Detailed description of the action")
    owner: str = Field(..., description="Person responsible for the action")
    support: str = Field("", description="Support details or team")
    status: Status = Field(default=Status.PENDING, description="Current status")
    priority: Priority = Field(default=Priority.MEDIUM, description="Priority level")
    due_date: str = Field(..., description="Due date for the action")
    completion_percentage: int = Field(default=0, ge=0, le=100, description="Completion percentage")
    remarks: str = Field("", description="Additional remarks")
    
    class Config:
        json_schema_extra = {
            "example": {
                "meeting_date": "2024-05-15",
                "action_item": "Setup Database",
                "action_description": "Configure PostgreSQL database for production",
                "owner": "John Doe",
                "support": "DevOps Team",
                "status": "In Progress",
                "priority": "High",
                "due_date": "2024-05-20",
                "completion_percentage": 50,
                "remarks": "Testing in progress"
            }
        }

class ActionItemUpdate(BaseModel):
    """Model for updating an action item"""
    meeting_date: Optional[str] = None
    action_item: Optional[str] = None
    action_description: Optional[str] = None
    owner: Optional[str] = None
    support: Optional[str] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    due_date: Optional[str] = None
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    remarks: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "Completed",
                "completion_percentage": 100,
                "remarks": "Task completed successfully"
            }
        }

class ActionItem(BaseModel):
    """Complete Action Item model with database fields"""
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier")
    meeting_date: str
    action_item: str
    action_description: str
    owner: str
    support: str
    status: Status
    priority: Priority
    due_date: str
    completion_percentage: int
    remarks: str
    created_date: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_date: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "meeting_date": "2024-05-15",
                "action_item": "Setup Database",
                "action_description": "Configure PostgreSQL database for production",
                "owner": "John Doe",
                "support": "DevOps Team",
                "status": "In Progress",
                "priority": "High",
                "due_date": "2024-05-20",
                "completion_percentage": 50,
                "remarks": "Testing in progress",
                "created_date": "2024-05-15T10:30:00",
                "updated_date": "2024-05-15T10:30:00"
            }
        }

class ActionItemResponse(BaseModel):
    """Response model for action items"""
    id: str
    meeting_date: str
    action_item: str
    action_description: str
    owner: str
    support: str
    status: str
    priority: str
    due_date: str
    completion_percentage: int
    remarks: str
    created_date: str
    updated_date: str
    
    class Config:
        from_attributes = True
