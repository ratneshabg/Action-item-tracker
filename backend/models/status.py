"""
Status and Priority enums for action items
Defines allowed values for status and priority fields
"""

from enum import Enum

class Status(str, Enum):
    """Allowed status values for action items"""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    BLOCKED = "Blocked"
    ONGOING = "Ongoing"

class Priority(str, Enum):
    """Allowed priority values for action items"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
